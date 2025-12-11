import os
import time
import requests
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from firecrawl import Firecrawl
from app.sources import get_all_sources
from app.utils.url_validator import filter_accessible_urls

class ScraperService:
    def __init__(self):
        self.firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')
        self.firecrawl = None
        if self.firecrawl_api_key:
            try:
                self.firecrawl = Firecrawl(api_key=self.firecrawl_api_key)
            except Exception as e:
                print(f"Warning: Firecrawl initialization failed: {e}")

        # ScraperAPI fallback (optional)
        self.scraperapi_key = os.getenv('SCRAPERAPI_KEY')
        if self.scraperapi_key:
            print(f"[ScraperAPI] ✓ Enabled as fallback for blocked URLs")

        # v3.1: Firecrawl Premium configuration
        self.max_concurrent_jobs = int(os.getenv('FIRECRAWL_MAX_CONCURRENT_JOBS', 5))
        self.timeout_seconds = int(os.getenv('FIRECRAWL_TIMEOUT_SECONDS', 45))
        self.rate_limit_seconds = float(os.getenv('FIRECRAWL_RATE_LIMIT_SECONDS', 0))

        print(f"[Firecrawl] Config: {self.max_concurrent_jobs} concurrent jobs, {self.timeout_seconds}s timeout, {self.rate_limit_seconds}s rate limit")

        self.sources = get_all_sources()
        print(f"Loaded {len(self.sources)} source modules: {[s.get_name() for s in self.sources]}")

    def collect_urls_from_sources(self, first_name: str, last_name: str, company: str) -> Dict[str, List[str]]:        
        urls_by_source = {}

        for source in self.sources:
            source_name = source.get_name()
            try:
                urls = source.get_urls(first_name, last_name, company)
                urls_by_source[source_name] = urls
                print(f"Source '{source_name}': {len(urls)} URLs generated")
            except Exception as e:
                print(f"Error getting URLs from source '{source_name}': {e}")
                urls_by_source[source_name] = []

        return urls_by_source

    def scrape_with_scraperapi(self, url: str) -> Optional[str]:
        """
        Fallback scraper using ScraperAPI for sites that block Firecrawl
        ScraperAPI bypasses anti-bot protection (Cloudflare, Datadome, etc.)
        """
        if not self.scraperapi_key:
            return None

        try:
            print(f"[ScraperAPI] Attempting fallback scraping: {url}")

            # ScraperAPI endpoint
            api_url = "https://api.scraperapi.com"
            params = {
                'api_key': self.scraperapi_key,
                'url': url,
                'render': 'false',  # false = plus rapide, true = JS rendering
            }

            response = requests.get(api_url, params=params, timeout=30)

            if response.status_code == 200:
                content = response.text
                print(f"[ScraperAPI] ✓ Success: {len(content)} chars")
                return content
            else:
                print(f"[ScraperAPI] ✗ Error {response.status_code}")
                return None

        except Exception as e:
            print(f"[ScraperAPI] ✗ Exception: {str(e)}")
            return None

    def _scrape_single_url(self, url: str, source_name: str) -> Dict:
        """
        Scrape une URL unique. Utilisé par scraping parallèle et séquentiel.
        Retourne dict avec {url, source, content, success}
        """
        try:
            content = self.scrape_with_firecrawl(url)

            if content:
                content_text = content.markdown if content.markdown is not None else ""

                # Valider contenu exploitable
                if len(content_text.strip()) > 100:
                    return {
                        "source": source_name,
                        "url": url,
                        "content": content_text[:5000],
                        "success": True
                    }
                else:
                    print(f"[Firecrawl] ⚠ Content too short for {url}, skipping")
                    return {"url": url, "success": False}
            else:
                return {"url": url, "success": False}

        except Exception as e:
            print(f"[Firecrawl] ✗ Error scraping {url}: {e}")
            return {"url": url, "success": False}

    def _scrape_parallel(self, urls: List[str], collected_data: Dict, url_to_source: Dict, max_scrapes: int):
        """
        v3.1: Scraping parallèle avec ThreadPoolExecutor.
        Firecrawl Premium supporte 5 jobs simultanés.
        """
        successful_scrapes = 0

        with ThreadPoolExecutor(max_workers=self.max_concurrent_jobs) as executor:
            # Soumettre tous les jobs
            future_to_url = {
                executor.submit(self._scrape_single_url, url, url_to_source.get(url, "unknown")): url
                for url in urls[:max_scrapes]
            }

            # Traiter résultats au fur et à mesure
            for future in as_completed(future_to_url):
                collected_data["stats"]["attempted"] += 1

                if successful_scrapes >= max_scrapes:
                    break

                result = future.result()

                if result.get("success"):
                    collected_data["scraped_content"].append(result)
                    collected_data["sources"].append(result["url"])
                    collected_data["stats"]["successful"] += 1
                    successful_scrapes += 1
                else:
                    collected_data["stats"]["failed"] += 1

    def _scrape_sequential(self, urls: List[str], collected_data: Dict, url_to_source: Dict, max_scrapes: int):
        """
        Scraping séquentiel avec rate limiting (free tier).
        """
        successful_scrapes = 0
        scrape_start_time = time.time()

        for idx, url in enumerate(urls):
            if successful_scrapes >= max_scrapes:
                break

            # Rate limiting
            if idx > 0 and self.rate_limit_seconds > 0:
                elapsed = time.time() - scrape_start_time
                expected_time = idx * self.rate_limit_seconds
                if elapsed < expected_time:
                    wait_time = expected_time - elapsed
                    print(f"[Rate Limit] Waiting {wait_time:.1f}s before next scrape ({idx+1}/{len(urls)})...")
                    time.sleep(wait_time)

            collected_data["stats"]["attempted"] += 1
            source_name = url_to_source.get(url, "unknown")

            result = self._scrape_single_url(url, source_name)

            if result.get("success"):
                collected_data["scraped_content"].append(result)
                collected_data["sources"].append(result["url"])
                collected_data["stats"]["successful"] += 1
                successful_scrapes += 1
            else:
                collected_data["stats"]["failed"] += 1

    def scrape_with_firecrawl(self, url: str, use_fallback: bool = True) -> Optional[Dict]:
        """
        Scrape avec Firecrawl, fallback vers ScraperAPI si 403/blocked.
        v3.1: Supporte timeout configurable pour éviter pages lourdes.
        """
        if not self.firecrawl:
            raise ValueError("Firecrawl API key not configured")

        try:
            print(f"[Firecrawl] Scraping: {url}")
            result = self.firecrawl.scrape(
                url,
                formats=['markdown', 'html'],
                timeout=self.timeout_seconds * 1000  # Firecrawl attend ms
            )

            if result and (result.markdown or result.html):
                print(f"[Firecrawl] ✓ Success: {len(result.markdown or '')} chars")
                return result
            else:
                print(f"[Firecrawl] ✗ Empty result")

                # Fallback vers ScraperAPI si disponible
                if use_fallback and self.scraperapi_key:
                    print(f"[Fallback] Trying ScraperAPI for {url}")
                    scraperapi_content = self.scrape_with_scraperapi(url)
                    if scraperapi_content:
                        # Convertir en format compatible Firecrawl
                        return type('obj', (object,), {
                            'markdown': scraperapi_content[:10000],  # Limiter à 10k chars
                            'html': None
                        })

                return None

        except Exception as e:
            error_msg = str(e).lower()
            print(f"[Firecrawl] ✗ Error: {str(e)}")

            # Si rate limit exceeded, extraire le délai et retourner None (sera géré par la boucle)
            if 'rate limit' in error_msg:
                # On ne retry pas ici, on laisse la boucle gérer avec le délai global
                print(f"[Firecrawl] ⚠ Rate limit hit, will be handled by rate limiting logic")
                return None

            # Si erreur 403/blocked, essayer ScraperAPI
            if use_fallback and self.scraperapi_key and ('403' in error_msg or 'forbidden' in error_msg or 'blocked' in error_msg):
                print(f"[Fallback] Firecrawl blocked (403), trying ScraperAPI")
                scraperapi_content = self.scrape_with_scraperapi(url)
                if scraperapi_content:
                    return type('obj', (object,), {
                        'markdown': scraperapi_content[:10000],
                        'html': None
                    })

            return None

    def scrape_person_data(self, first_name: str, last_name: str, company: str) -> Dict[str, any]:
        if not self.firecrawl:
            raise ValueError("Firecrawl API key not configured. Please set FIRECRAWL_API_KEY in .env")

        print(f"\n=== Scraping Profile: {first_name} {last_name} @ {company} ===")
        urls_by_source = self.collect_urls_from_sources(first_name, last_name, company)

        # Calculer total URLs générées par toutes les sources
        all_urls = [url for urls in urls_by_source.values() for url in urls]

        # Séparer URLs web normales vs URLs de sources avec API/cache
        web_urls = []
        api_urls = []  # LinkedIn, Pappers, DVF, HATVP (déjà collectées via API)
        url_to_source = {}

        # Sources qui utilisent API/cache (pas besoin de validation URL HTTP)
        # LinkedIn: URLs directes de profil à scraper
        # Pappers/DVF/HATVP: URLs fictives "pappers://" avec données en cache
        api_sources = {'linkedin', 'pappers_legal', 'dvf_immobilier', 'hatvp_ppe'}

        for source_name, urls in urls_by_source.items():
            for url in urls:
                url_to_source[url] = source_name

                # v3.1: Ne pas valider URLs de sources API (LinkedIn, Pappers, etc.)
                # Ces données sont déjà collectées/vérifiées, on veut juste scraper les pages
                if source_name in api_sources:
                    api_urls.append(url)
                else:
                    web_urls.append(url)

        print(f"\n=== URL Validation ===")
        print(f"[URL Validator] URLs à valider: {len(web_urls)} web + {len(api_urls)} API/cached (bypassed)")

        # Valider URLs web (incluant résultats Serper)
        # v3.1: Augmentation limite à 200 pour tester toutes URLs importantes
        validated_web_urls = filter_accessible_urls(web_urls, timeout=3, max_concurrent=200) if web_urls else []

        # Combiner URLs validées + URLs API (qui sont déjà vérifiées par les sources)
        accessible_urls = validated_web_urls + api_urls

        print(f"[URL Validator] Total accessible: {len(accessible_urls)} ({len(validated_web_urls)} web + {len(api_urls)} API/cached)")

        if not accessible_urls:
            raise Exception(
                "No accessible URLs found. "
                "All URLs either timed out or returned errors. "
                "This could indicate:\n"
                "1) Network connectivity issues\n"
                "2) All URLs are invalid/dead\n"
                "3) Sites are blocking requests"
            )

        linkedin_data = None
        pappers_data = None
        dvf_data = None
        hatvp_data = None

        for source in self.sources:
            if hasattr(source, 'linkedin_cache') and source.linkedin_cache:
                linkedin_data = source.linkedin_cache
                print(f"[LinkedIn] ✓ Found {linkedin_data['count']} LinkedIn URLs in cache")

            if hasattr(source, 'get_cached_data'):
                cached = source.get_cached_data()
                if cached:
                    source_name = source.get_name()
                    if source_name == 'pappers_legal':
                        pappers_data = cached
                        print(f"[Pappers] ✓ Legal data collected for {cached.get('full_name')}")
                    elif source_name == 'dvf_immobilier':
                        dvf_data = cached
                        print(f"[DVF] ✓ Real estate data collected: {cached.get('count')} mention(s)")
                    elif source_name == 'hatvp_ppe':
                        hatvp_data = cached
                        ppe_status = "DETECTED ⚠" if cached.get('ppe_detected') else "Not detected"
                        print(f"[HATVP] ✓ PPE status: {ppe_status}")

        # v3.1: LinkedIn snippets (Firecrawl ne supporte pas linkedin.com)
        # On utilise les snippets Serper qui contiennent déjà du contenu exploitable
        if linkedin_data and linkedin_data.get('combined_snippet'):
            print(f"[LinkedIn] ✓ Found {linkedin_data['count']} LinkedIn snippets (Firecrawl doesn't support linkedin.com)")

        collected_data = {
            "urls_by_source": urls_by_source,
            "accessible_urls": accessible_urls,
            "scraped_content": [],
            "sources": [],
            "linkedin_data": linkedin_data,
            "pappers_data": pappers_data,
            "dvf_data": dvf_data,
            "hatvp_data": hatvp_data,
            "stats": {
                "total_urls_generated": len(all_urls),
                "accessible": len(accessible_urls),
                "attempted": 0,
                "successful": 0,
                "failed": 0
            }
        }

        max_total_scrapes = int(os.getenv("MAX_TOTAL_SCRAPES", '3'))  # Maximum 3 scrapes

        # v3.1: Filtrer URLs fictives (pappers://, dvf://, hatvp://)
        # Ces URLs servent juste de marqueurs pour les données en cache
        scrapable_urls = [url for url in accessible_urls if url.startswith('http')]

        print(f"\n=== Scraping Queue ===")
        print(f"[Scraper] Total accessible: {len(accessible_urls)} ({len(scrapable_urls)} HTTP + {len(accessible_urls) - len(scrapable_urls)} cached)")
        print(f"[Scraper] Will scrape: {min(len(scrapable_urls), max_total_scrapes)} URLs (limit: {max_total_scrapes})")

        # v3.1: Scraping parallèle avec ThreadPoolExecutor (Premium supporte 5 jobs simultanés)
        scrape_start_time = time.time()

        if self.max_concurrent_jobs > 1:
            print(f"[Firecrawl] ✓ Parallel scraping enabled: {self.max_concurrent_jobs} concurrent jobs")
            self._scrape_parallel(scrapable_urls[:max_total_scrapes], collected_data, url_to_source, max_total_scrapes)
        else:
            print(f"[Firecrawl] Sequential scraping (rate limit: {self.rate_limit_seconds}s)")
            self._scrape_sequential(scrapable_urls[:max_total_scrapes], collected_data, url_to_source, max_total_scrapes)

        scrape_duration = time.time() - scrape_start_time
        avg_time_per_url = scrape_duration / max(collected_data["stats"]["attempted"], 1)

        print(f"\n[Performance] Scraping completed in {scrape_duration:.1f}s")
        print(f"[Performance] Average: {avg_time_per_url:.1f}s per URL")
        print(f"[Performance] Mode: {'Parallel (' + str(self.max_concurrent_jobs) + ' jobs)' if self.max_concurrent_jobs > 1 else 'Sequential'}")

        # Ajouter snippets LinkedIn si disponibles (Firecrawl ne supporte pas LinkedIn)
        if linkedin_data and linkedin_data.get('combined_snippet'):
            collected_data["scraped_content"].append({
                "source": "linkedin_snippets",
                "url": ", ".join(linkedin_data.get('urls', [])[:5]),
                "content": linkedin_data['combined_snippet'][:5000],  # Limiter à 5000 chars
                "success": True
            })
            collected_data["stats"]["successful"] += 1
            # v3.1: Ajouter liste complète des URLs LinkedIn pour traçabilité
            collected_data["linkedin_urls"] = linkedin_data.get('urls', [])
            print(f"[LinkedIn] ✓ Added {linkedin_data['count']} LinkedIn snippets to analysis")

        print(f"\n=== Scraping Stats ===")
        print(f"Attempted: {collected_data['stats']['attempted']}")
        print(f"Successful: {collected_data['stats']['successful']}")
        print(f"Failed: {collected_data['stats']['failed']}")

        if collected_data["stats"]["successful"] == 0:
            raise Exception(
                "Failed to scrape any valid data. "
                "This could be due to: "
                "1) Firecrawl rate limits "
                "2) Invalid URLs "
                "3) Sites blocking scraping. "
                "Please try again in a few moments."
            )

        return collected_data