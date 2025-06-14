from ..base import BaseScraper
from bs4 import BeautifulSoup
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class AppleScraper(BaseScraper):
    """Scraper implementation for Apple's terms and policies"""
    
    BASE_URL = "https://www.apple.com/legal"
    
    async def get_document_urls(self) -> List[str]:
        """Get Apple's policy document URLs"""
        content = await self.fetch_page(f"{self.BASE_URL}/")
        if not content:
            return []
            
        soup = BeautifulSoup(content, 'html.parser')
        urls = []
        
        # Find policy links on Apple's legal page
        for link in soup.find_all('a', href=True):
            href = link['href']
            if any(term in href.lower() for term in [
                'terms-of-service', 
                'privacy-policy',
                'sla',
                'terms-conditions'
            ]):
                if not href.startswith('http'):
                    href = f"{self.BASE_URL}/{href.lstrip('/')}"
                urls.append(href)
                
        return list(set(urls))

    async def extract_document_content(self, url: str) -> Dict:
        """Extract content from Apple policy pages"""
        content = await self.fetch_page(url)
        if not content:
            return {}
            
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove navigation and unnecessary elements
        for elem in soup.select('.ac-gn-header, .ac-gn-footer, .footer'):
            elem.decompose()
            
        main_content = soup.find('main') or soup.find('div', class_='main')
        
        return {
            'title': self._extract_title(soup),
            'content': main_content.get_text(strip=True) if main_content else '',
            'document_type': self._determine_document_type(url),
            'language': 'en',
            'effective_date': self._extract_date(soup),
            'version_identifier': self._extract_version(soup)
        }
        
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract document title from page"""
        title_elem = soup.find('h1')
        return title_elem.get_text(strip=True) if title_elem else ''
        
    def _determine_document_type(self, url: str) -> str:
        """Determine document type from URL"""
        url_lower = url.lower()
        if 'privacy' in url_lower:
            return 'privacy_policy'
        elif 'terms' in url_lower or 'sla' in url_lower:
            return 'terms_of_service'
        return 'other'
        
    def _extract_date(self, soup: BeautifulSoup) -> str:
        """Extract effective date from document"""
        date_patterns = ['Last updated', 'Effective', 'Updated']
        for pattern in date_patterns:
            date_elem = soup.find(text=lambda t: t and pattern in t)
            if date_elem:
                return date_elem.strip()
        return None
        
    def _extract_version(self, soup: BeautifulSoup) -> str:
        """Extract version identifier from document"""
        version_elem = soup.find(text=lambda t: t and 'Version' in t)
        return version_elem.strip() if version_elem else None