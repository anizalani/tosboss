from typing import Dict, Type
import logging
from .base import BaseScraper
from .sites import GoogleScraper, MicrosoftScraper, AppleScraper
from backend.models import Company
from backend.utils.db import SessionLocal

logger = logging.getLogger(__name__)

class ScraperManager:
    """Manages scraper instances and coordinates scraping jobs"""
    
    SCRAPERS: Dict[str, Type[BaseScraper]] = {
        'google.com': GoogleScraper,
        'microsoft.com': MicrosoftScraper,
        'apple.com': AppleScraper
    }
    
    def __init__(self):
        self.db = SessionLocal()
    
    async def scrape_company(self, company_id: str) -> bool:
        """Scrape documents for a specific company"""
        try:
            company = self.db.query(Company).get(company_id)
            if not company:
                logger.error(f"Company not found: {company_id}")
                return False
                
            scraper_class = self._get_scraper_class(company.domain)
            if not scraper_class:
                logger.error(f"No scraper available for domain: {company.domain}")
                return False
                
            scraper = scraper_class(company_id)
            await scraper.run()
            return True
            
        except Exception as e:
            logger.error(f"Scraping failed for company {company_id}: {str(e)}")
            return False
    
    def _get_scraper_class(self, domain: str) -> Type[BaseScraper]:
        """Get appropriate scraper class for domain"""
        return self.SCRAPERS.get(domain)