from abc import ABC, abstractmethod
import logging
import aiohttp
import asyncio
from datetime import datetime
from typing import Optional, Dict, List
from ratelimit import limits, sleep_and_retry
from bs4 import BeautifulSoup
from backend.models import Document, Company
from backend.utils.db import SessionLocal

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Base scraper class that all site-specific scrapers must inherit from"""
    
    def __init__(self, company_id: str, rate_limit: int = 3):
        self.company_id = company_id
        self.rate_limit = rate_limit
        self.session = aiohttp.ClientSession(
            headers={
                'User-Agent': 'EULAComparison/1.0 (+https://eulacomparison.com/bot)'
            }
        )
        self.db = SessionLocal()
    
    @abstractmethod
    async def get_document_urls(self) -> List[str]:
        """Get list of document URLs to scrape"""
        pass
    
    @abstractmethod
    async def extract_document_content(self, url: str) -> Dict:
        """Extract content from a document URL"""
        pass
    
    @sleep_and_retry
    @limits(calls=1, period=1)  # Basic rate limiting
    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content with rate limiting and error handling"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                logger.error(f"Failed to fetch {url}: {response.status}")
                return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
            
    async def process_document(self, url: str) -> Optional[Document]:
        """Process a single document URL"""
        content = await self.fetch_page(url)
        if not content:
            return None
            
        doc_data = await self.extract_document_content(url)
        
        # Create document record
        document = Document(
            company_id=self.company_id,
            source_url=url,
            **doc_data
        )
        return document
    
    async def run(self):
        """Main scraping process"""
        try:
            urls = await self.get_document_urls()
            documents = []
            
            for url in urls:
                doc = await self.process_document(url)
                if doc:
                    documents.append(doc)
            
            # Bulk save documents
            self.db.bulk_save_objects(documents)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Scraping failed for company {self.company_id}: {str(e)}")
            self.db.rollback()
        finally:
            await self.session.close()