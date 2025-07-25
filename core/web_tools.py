import requests
import re
from bs4 import BeautifulSoup

def google_search(query, api_key, cse_id, num_results=3):
    if not api_key or not cse_id:
        return []
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={query}&num={num_results}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        search_results = response.json()
        snippets = []
        if 'items' in search_results:
            for item in search_results['items']:
                snippets.append(item.get('snippet', 'No snippet available.') + f" (Source: {item.get('displayLink', 'N/A')})")
        return snippets
    except Exception:
        return []

def fetch_url_content(url, max_chars=3000):
    try:
        if "github.com" in url:
            m = re.match(r'https?://github.com/([^/]+)/([^/]+)', url)
            if m:
                user, repo = m.group(1), m.group(2)
                raw_url = f"https://raw.githubusercontent.com/{user}/{repo}/main/README.md"
                resp = requests.get(raw_url, timeout=10)
                if resp.ok and resp.text.strip():
                    return f"README.md content from {repo} repository:\n\n" + resp.text[:max_chars] + ("..." if len(resp.text) > max_chars else "")
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator='\n')
        clean_text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        return clean_text[:max_chars] + ("..." if len(clean_text) > max_chars else "")
    except Exception as e:
        return f"[ERROR] Failed to read page {url}: {e}"
