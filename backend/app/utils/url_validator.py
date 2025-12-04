import requests
from typing import List
from urllib.parse import urlparse

def is_url_accessible(url: str, timeout: int = 3) -> bool:
    try:
        response = requests.head(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={'User-Agent': 'Mozilla/5.0'}
        )

        if 200 <= response.status_code < 400:
            return True
        else:
            print(f"[URL Validator] ✗ {url} returned {response.status_code}")
            return False

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
    accessible = []

    print(f"[URL Validator] Testing {len(urls)} URLs...")

    for url in urls:
        if len(accessible) >= max_concurrent:
            break

        if is_url_accessible(url, timeout):
            print(f"[URL Validator] ✓ {url} accessible")
            accessible.append(url)
        else:
            print(f"[URL Validator] ⏭ Skipping {url}")

    print(f"[URL Validator] {len(accessible)}/{len(urls)} URLs accessible")
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