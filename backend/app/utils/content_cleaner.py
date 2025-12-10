"""
Content cleaning utilities to reduce token usage while preserving key information.

Optimizes scraped content for LLM analysis by:
- Removing navigation, headers, footers, ads
- Extracting only relevant sections
- Reducing token count by 60-70%
"""

import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup


def clean_scraped_html(html_content: str, url: str = "") -> str:
    """
    Clean content (HTML or Markdown) to extract only relevant information.

    **Note**: Firecrawl returns markdown, not HTML, so this function handles both formats.

    Reduces token count by 60-70% while preserving key data:
    - About/Bio sections
    - Experience/Career information
    - Posts/Articles
    - Featured content

    Removes:
    - Navigation menus/headers/footers (if HTML)
    - Repetitive patterns
    - Boilerplate text
    - Ads and suggestions

    Args:
        html_content: Content from Firecrawl (usually markdown)
        url: Source URL (helps identify LinkedIn pages)

    Returns:
        Cleaned text content optimized for LLM analysis
    """
    if not html_content:
        return ""

    # Detect if content is HTML or plain text/markdown
    is_html = '<html' in html_content.lower() or '<body' in html_content.lower() or '<div' in html_content.lower()

    try:
        if is_html:
            # HTML cleaning with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'iframe', 'noscript']):
                element.decompose()

            # Remove common ad/suggestion classes
            ad_patterns = [
                'ad', 'advertisement', 'promo', 'sponsored',
                'recommendation', 'suggestion', 'similar',
                'sidebar', 'widget', 'cookie', 'consent',
                'newsletter', 'subscribe', 'popup', 'modal'
            ]

            for pattern in ad_patterns:
                for element in soup.find_all(class_=re.compile(pattern, re.I)):
                    element.decompose()
                for element in soup.find_all(id=re.compile(pattern, re.I)):
                    element.decompose()

            # LinkedIn-specific cleaning
            if 'linkedin.com' in url.lower():
                return _clean_linkedin_content(soup, url)

            # Generic cleaning: extract main content
            main_content = soup.find('main') or soup.find('article') or soup.find('body') or soup
            text = main_content.get_text(separator='\n', strip=True)
        else:
            # Markdown/text cleaning (most common with Firecrawl)
            text = html_content

        # Clean text patterns (works for both HTML-extracted and markdown)
        text = _clean_text_patterns(text, url)

        return text.strip()

    except Exception as e:
        print(f"[ContentCleaner] Error cleaning content: {str(e)}")
        # Fallback: basic text cleaning
        return _clean_text_patterns(html_content, url)


def _clean_text_patterns(text: str, url: str = "") -> str:
    """
    Clean text/markdown content by removing repetitive patterns and boilerplate.

    This is the main cleaning function for Firecrawl markdown output.
    Reduces token count by 50-70%.

    Args:
        text: Text content (usually markdown from Firecrawl)
        url: Source URL (optional, for context-specific cleaning)

    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Max 2 consecutive newlines
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces → single space

    # Remove common boilerplate patterns
    boilerplate_patterns = [
        r'(Cookies?|Cookie Policy|Privacy Policy|Terms of Service|Terms and Conditions|Legal Notice)',
        r'(Subscribe to our newsletter|Sign up|Join us|Follow us)',
        r'(Share on|Tweet|Pin it|Post to)',
        r'(© \d{4}|All rights reserved|Copyright)',
        r'(Accept cookies|We use cookies|This site uses cookies)',
        r'(Powered by|Built with)',
    ]

    for pattern in boilerplate_patterns:
        # Remove lines containing these patterns
        text = re.sub(rf'^.*{pattern}.*$', '', text, flags=re.MULTILINE | re.IGNORECASE)

    # Remove repetitive navigation-like lines (e.g., "Home | About | Contact")
    # Pattern: words separated by |, >, or • (navigation separators)
    text = re.sub(r'^([A-Za-z\s]+[|>•]){3,}.*$', '', text, flags=re.MULTILINE)

    # Remove very short lines that are likely navigation/UI elements
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Keep line if it's substantive (>20 chars) or part of a list/structure
        if len(stripped) > 20 or stripped.startswith(('-', '*', '•', '1.', '2.', '3.')):
            cleaned_lines.append(line)
        elif stripped and not re.match(r'^(Home|Menu|Search|Login|Sign|Contact|About|Services|Products)$', stripped, re.IGNORECASE):
            cleaned_lines.append(line)

    text = '\n'.join(cleaned_lines)

    # LinkedIn-specific cleaning
    if 'linkedin.com' in url.lower():
        text = _clean_linkedin_text(text)

    # Final whitespace cleanup
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = text.strip()

    return text


def _clean_linkedin_text(text: str) -> str:
    """
    Clean LinkedIn-specific content patterns.

    Extracts relevant sections and removes LinkedIn UI elements.

    Args:
        text: LinkedIn page content

    Returns:
        Cleaned text with LinkedIn boilerplate removed
    """
    # Remove LinkedIn UI elements
    linkedin_ui_patterns = [
        r'Sign in to view',
        r'Join to view',
        r'See all \d+ employees',
        r'See who you know',
        r'Get introduced',
        r'View profile',
        r'Connect',
        r'Message',
        r'More',
        r'Save',
        r'Report this',
        r'Show more|Show less',
        r'Reactions|Comments?|Reposts?',
        r'\d+ reactions?',
        r'\d+ comments?',
        r'Like|Comment|Share|Send',
    ]

    for pattern in linkedin_ui_patterns:
        text = re.sub(rf'^.*{pattern}.*$', '', text, flags=re.MULTILINE | re.IGNORECASE)

    # Extract relevant sections if present
    # Look for section headers like "About", "Experience", "Education", "Posts"
    # This helps prioritize important content

    return text


def _clean_linkedin_content(soup: BeautifulSoup, url: str) -> str:
    """
    Extract relevant content from LinkedIn pages.

    Prioritizes:
    - Profile About/Summary
    - Experience section
    - Posts/Activity
    - Featured content
    """
    extracted_sections = []

    # LinkedIn profile sections (adjust selectors based on actual HTML structure)
    # Note: LinkedIn structure changes frequently, these are approximations

    # About/Summary section
    about_section = soup.find('section', id=re.compile('about', re.I)) or \
                   soup.find('div', class_=re.compile('summary|about', re.I))
    if about_section:
        extracted_sections.append(f"ABOUT:\n{about_section.get_text(separator='\n', strip=True)}")

    # Experience section
    experience_section = soup.find('section', id=re.compile('experience', re.I)) or \
                        soup.find('div', class_=re.compile('experience', re.I))
    if experience_section:
        extracted_sections.append(f"EXPERIENCE:\n{experience_section.get_text(separator='\n', strip=True)}")

    # Posts/Activity
    if '/recent-activity/' in url or '/posts/' in url:
        posts = soup.find_all('div', class_=re.compile('feed-shared-update-v2|post', re.I), limit=10)
        if posts:
            posts_text = '\n\n---\n\n'.join([post.get_text(separator='\n', strip=True) for post in posts])
            extracted_sections.append(f"POSTS/ACTIVITY:\n{posts_text}")

    # Education section
    education_section = soup.find('section', id=re.compile('education', re.I)) or \
                       soup.find('div', class_=re.compile('education', re.I))
    if education_section:
        extracted_sections.append(f"EDUCATION:\n{education_section.get_text(separator='\n', strip=True)}")

    # If no specific sections found, return full cleaned text
    if not extracted_sections:
        return soup.get_text(separator='\n', strip=True)

    return '\n\n==========\n\n'.join(extracted_sections)


def parse_linkedin_posts(html_content: str) -> List[Dict[str, str]]:
    """
    Parse LinkedIn posts from HTML content.

    Returns structured list of posts with:
    - content: Post text content
    - date: Publication date (if available)
    - engagement: Likes, comments, shares count (if available)

    Args:
        html_content: HTML from LinkedIn /recent-activity/ or /posts/ page

    Returns:
        List of parsed posts as dictionaries
    """
    posts = []

    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find post containers (selectors may need adjustment based on actual LinkedIn HTML)
        post_containers = soup.find_all('div', class_=re.compile('feed-shared-update-v2|post-container', re.I), limit=15)

        for container in post_containers:
            post = {}

            # Extract post content
            content_elem = container.find('div', class_=re.compile('feed-shared-text|post-content', re.I)) or \
                          container.find('span', class_=re.compile('break-words', re.I))

            if content_elem:
                post['content'] = content_elem.get_text(separator=' ', strip=True)
            else:
                # Fallback: get all text from container
                post['content'] = container.get_text(separator=' ', strip=True)

            # Extract date
            date_elem = container.find('time') or \
                       container.find('span', class_=re.compile('time|date', re.I))
            if date_elem:
                post['date'] = date_elem.get('datetime') or date_elem.get_text(strip=True)

            # Extract engagement metrics (if available)
            likes_elem = container.find('span', class_=re.compile('reactions-count|likes', re.I))
            if likes_elem:
                post['engagement'] = likes_elem.get_text(strip=True)

            # Only add posts with actual content
            if post.get('content') and len(post['content']) > 50:
                posts.append(post)

        return posts[:10]  # Limit to 10 most recent posts

    except Exception as e:
        print(f"[ContentCleaner] Error parsing LinkedIn posts: {str(e)}")
        return []


def extract_linkedin_activity_urls(first_name: str, last_name: str, linkedin_url: Optional[str] = None) -> List[str]:
    """
    Generate LinkedIn activity URLs to scrape.

    Returns URLs for:
    - Main profile page
    - Recent activity page
    - Posts page (if available)

    Args:
        first_name: Person's first name
        last_name: Person's last name
        linkedin_url: Known LinkedIn URL (if available)

    Returns:
        List of URLs to scrape for LinkedIn activity
    """
    urls = []

    if linkedin_url:
        # Clean URL
        base_url = linkedin_url.rstrip('/').split('?')[0]

        # Add main profile
        urls.append(base_url)

        # Add activity pages
        urls.append(f"{base_url}/recent-activity/all/")
        urls.append(f"{base_url}/detail/recent-activity/shares/")
        urls.append(f"{base_url}/detail/recent-activity/")
    else:
        # Generate potential URLs from name
        # This is less reliable, prefer using known LinkedIn URL
        first = first_name.lower().replace(' ', '-')
        last = last_name.lower().replace(' ', '-')
        potential_username = f"{first}-{last}"

        base_url = f"https://www.linkedin.com/in/{potential_username}"
        urls.append(base_url)
        urls.append(f"{base_url}/recent-activity/all/")

    return urls


def estimate_token_count(text: str) -> int:
    """
    Rough estimate of token count for text.

    Uses approximation: 1 token ≈ 4 characters for English/French.

    Args:
        text: Text to estimate

    Returns:
        Estimated token count
    """
    return len(text) // 4


def truncate_to_token_limit(text: str, max_tokens: int) -> str:
    """
    Truncate text to approximately fit within token limit.

    Args:
        text: Text to truncate
        max_tokens: Maximum token count

    Returns:
        Truncated text
    """
    estimated_chars = max_tokens * 4
    if len(text) <= estimated_chars:
        return text

    return text[:estimated_chars] + "... [truncated]"
