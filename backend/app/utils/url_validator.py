import requests
import random
import time
from typing import List
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# User-Agent pool réaliste (vrais navigateurs, maj récentes)
USER_AGENTS = [
    # Chrome sur Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    # Chrome sur Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    # Firefox sur Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    # Firefox sur Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    # Safari sur Mac
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    # Edge sur Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
]

def get_realistic_headers() -> dict:
    """
    Génère des headers HTTP réalistes pour imiter un vrai navigateur
    """
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }

def is_url_accessible(url: str, timeout: int = 3, session: requests.Session = None) -> bool:
    """
    Vérifie si une URL est accessible ET appropriée pour le scraping
    Filtre les PDFs, fichiers binaires, et contenus trop lourds
    Utilise des headers réalistes pour éviter les blocages anti-bot

    Args:
        url: URL à valider
        timeout: Timeout en secondes
        session: Session requests réutilisable (pour connection pooling)
    """
    try:
        # Filtrer les extensions de fichiers non désirées
        unwanted_extensions = ['.pdf', '.zip', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.exe', '.dmg']
        if any(url.lower().endswith(ext) for ext in unwanted_extensions):
            print(f"[URL Validator] ✗ {url} - unwanted file type")
            return False

        # Utiliser des headers réalistes
        headers = get_realistic_headers()

        # Utiliser session si fournie (connection pooling), sinon requests direct
        requester = session if session else requests

        response = requester.head(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers=headers
        )

        if not (200 <= response.status_code < 400):
            print(f"[URL Validator] ✗ {url} returned {response.status_code}")
            return False

        # Vérifier le Content-Type
        content_type = response.headers.get('Content-Type', '').lower()

        # Bloquer les PDFs et fichiers binaires
        blocked_types = ['application/pdf', 'application/zip', 'application/octet-stream',
                        'application/msword', 'application/vnd.ms-excel', 'application/vnd.openxmlformats']
        if any(blocked in content_type for blocked in blocked_types):
            print(f"[URL Validator] ✗ {url} - blocked content type: {content_type}")
            return False

        # Vérifier la taille du contenu (bloquer > 5MB)
        content_length = response.headers.get('Content-Length')
        if content_length and int(content_length) > 5_000_000:  # 5MB
            print(f"[URL Validator] ✗ {url} - too large: {int(content_length) / 1_000_000:.1f}MB")
            return False

        return True

    except requests.exceptions.Timeout:
        print(f"[URL Validator] ✗ {url} timeout after {timeout}s")
        return False

    except requests.exceptions.ConnectionError:
        print(f"[URL Validator] ✗ {url} connection failed")
        return False

    except Exception as e:
        print(f"[URL Validator] ✗ {url} error: {str(e)[:50]}")
        return False


def filter_accessible_urls(urls: List[str], timeout: int = 3, max_concurrent: int = 5) -> List[str]:
    """
    v3.1: Parallélisé pour -80% de temps (10s → 2s)
    Valide toutes les URLs en parallèle avec ThreadPoolExecutor
    Utilise connection pooling pour optimiser les performances

    Args:
        urls: Liste des URLs à valider
        timeout: Timeout par requête HTTP (secondes)
        max_concurrent: Nombre max d'URLs à retourner (limite de résultats)

    Returns:
        Liste des URLs accessibles (limitée à max_concurrent)
    """
    if not urls:
        return []

    start_time = time.time()
    print(f"[URL Validator] 🚀 Testing {len(urls)} URLs en parallèle (50 workers)...")

    accessible = []

    # Créer une session avec connection pooling pour de meilleures performances
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=50,  # Nombre de connexions à maintenir
        pool_maxsize=50,      # Taille max du pool
        max_retries=0         # Pas de retry (on veut échouer vite)
    )
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    try:
        # Valider TOUTES les URLs en parallèle avec 50 workers
        with ThreadPoolExecutor(max_workers=50) as executor:
            # Soumettre toutes les validations avec la session
            future_to_url = {
                executor.submit(is_url_accessible, url, timeout, session): url
                for url in urls
            }

            # Collecter les résultats au fur et à mesure
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    if future.result():
                        accessible.append(url)
                        print(f"[URL Validator] ✓ {url} accessible")

                        # Arrêter dès qu'on a max_concurrent URLs
                        if len(accessible) >= max_concurrent:
                            print(f"[URL Validator] ⚡ Limite atteinte ({max_concurrent} URLs), arrêt anticipé")
                            break
                except Exception as e:
                    print(f"[URL Validator] ✗ {url} error: {str(e)[:50]}")
    finally:
        # Fermer proprement la session
        session.close()

    validation_time = time.time() - start_time
    print(f"[URL Validator] ⚡ {len(accessible)}/{len(urls)} URLs accessible en {validation_time:.1f}s (parallèle)")

    return accessible


def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def get_domain(url: str) -> str:
    try:
        parsed = urlparse(url)
        return parsed.netloc.replace('www.', '')
    except Exception:
        return ""