import requests
from bs4 import BeautifulSoup

# googlesearch may not be installed in this environment; provide a stub if missing
try:
    from googlesearch import search
except ImportError:
    def search(query, num_results=3):
        print("googlesearch library not available; returning empty results")
        return []

class WebExplorer:
    def __init__(self):
        # no special initialization required for now
        pass

    def search_and_learn(self, topic: str, memory_manager_instance):
        try:
            results = search(topic, num_results=3)
        except Exception as e:
            print(f"Error during search for '{topic}': {e}")
            return

        for i, url in enumerate(results):
            try:
                resp = requests.get(url, timeout=5)
                resp.raise_for_status()
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")
                continue

            try:
                soup = BeautifulSoup(resp.text, "html.parser")
                paragraphs = soup.find_all("p")
                text = "\n".join(p.get_text(strip=True) for p in paragraphs)
                text = " ".join(text.split())  # collapse whitespace
            except Exception as e:
                print(f"Error parsing {url}: {e}")
                continue

            key = f"web_info_{topic}_{i}"
            try:
                memory_manager_instance.store_memory(key, text)
            except Exception as e:
                print(f"Memory store failed for key {key}: {e}")
