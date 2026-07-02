import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time
from typing import List, Dict
import os

class AtlanDocsCrawler:
    def __init__(self, max_pages=50):
        self.base_urls = [
            "https://docs.atlan.com/",
            "https://developer.atlan.com/"
        ]
        self.visited = set()
        self.max_pages = max_pages
        self.docs = []
        
    def is_valid_url(self, url: str) -> bool:
        """Check if URL belongs to Atlan docs"""
        parsed = urlparse(url)
        return any(base in url for base in self.base_urls) and parsed.scheme in ['http', 'https']
    
    def crawl_page(self, url: str) -> Dict:
        """Crawl a single page and extract content"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('h1')
            title_text = title.get_text().strip() if title else "Untitled"
            
            # Remove script, style, nav elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Extract main content
            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            text = main_content.get_text(separator=' ', strip=True) if main_content else ""
            
            # Clean text
            text = ' '.join(text.split())
            
            return {
                'url': url,
                'title': title_text,
                'text': text
            }
            
        except Exception as e:
            print(f"Error crawling {url}: {e}")
            return None
    
    def get_links(self, url: str, html_content: str) -> List[str]:
        """Extract links from page"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = []
        
        for link in soup.find_all('a', href=True):
            absolute_url = urljoin(url, link['href'])
            # Remove fragments and query params for deduplication
            clean_url = absolute_url.split('#')[0].split('?')[0]
            
            if self.is_valid_url(clean_url) and clean_url not in self.visited:
                links.append(clean_url)
        
        return links
    
    def crawl(self):
        """Main crawling function"""
        to_visit = self.base_urls.copy()
        
        while to_visit and len(self.visited) < self.max_pages:
            url = to_visit.pop(0)
            
            if url in self.visited:
                continue
            
            print(f"Crawling ({len(self.visited)+1}/{self.max_pages}): {url}")
            self.visited.add(url)
            
            doc = self.crawl_page(url)
            if doc and len(doc['text']) > 100:  # Only keep pages with substantial content
                self.docs.append(doc)
            
            # Get new links
            try:
                response = requests.get(url, timeout=10)
                new_links = self.get_links(url, response.text)
                to_visit.extend(new_links)
            except:
                pass
            
            time.sleep(0.5)  # Be polite
        
        return self.docs
    
    def save_docs(self, filename='data/raw_docs.json'):
        """Save crawled docs to JSON"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.docs, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(self.docs)} documents to {filename}")


crawler = AtlanDocsCrawler(max_pages=50)
docs = crawler.crawl()
crawler.save_docs()
print(f"Total documents crawled: {len(docs)}")