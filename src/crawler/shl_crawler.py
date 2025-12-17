"""
Web crawler for SHL product catalog.
Fetches Individual Test Solutions from https://www.shl.com/solutions/products/product-catalog/
"""
import json
import logging
import time
from typing import List, Dict, Optional
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from config.settings import (
    SHL_CATALOG_URL,
    ASSESSMENTS_RAW_FILE,
    CRAWL_TIMEOUT,
    CRAWL_RETRIES,
    CRAWL_MIN_ASSESSMENTS,
    CRAWL_HEADLESS,
)

logger = logging.getLogger(__name__)


class SHLCrawler:
    """Crawler for SHL Assessment Catalog."""
    
    def __init__(self):
        self.base_url = SHL_CATALOG_URL
        self.assessments = []
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def fetch_page_with_requests(self) -> str:
        """
        Fetch the catalog page using requests (simpler approach).
        """
        logger.info(f"Fetching {self.base_url} with requests...")
        
        try:
            response = self.session.get(self.base_url, timeout=CRAWL_TIMEOUT)
            response.raise_for_status()
            logger.info("Page content fetched successfully")
            return response.text
        
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise
    
    def fetch_page_with_selenium(self) -> str:
        """
        Fetch the catalog page using Selenium to handle JavaScript rendering.
        """
        logger.info("Starting Selenium driver to fetch dynamic content...")
        
        chrome_options = Options()
        if CRAWL_HEADLESS:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            driver.get(self.base_url)
            logger.info(f"Opened {self.base_url}")
            
            # Wait for assessment cards to load
            WebDriverWait(driver, CRAWL_TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "product-card"))
            )
            
            # Scroll to load all content (dynamic loading)
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            page_source = driver.page_source
            logger.info("Page content loaded successfully")
            return page_source
        
        except Exception as e:
            logger.error(f"Selenium error: {e}")
            raise
        
        finally:
            driver.quit()
    
    def parse_assessment_cards(self, html_content: str) -> List[Dict]:
        """
        Parse assessment cards from HTML content.
        """
        logger.info("Parsing assessment cards from HTML...")
        soup = BeautifulSoup(html_content, "html.parser")
        assessments = []
        
        # Find all product cards
        product_cards = soup.find_all("div", class_="product-card")
        logger.info(f"Found {len(product_cards)} product cards")
        
        for card in product_cards:
            try:
                # Extract assessment name
                name_elem = card.find("h2") or card.find("h3") or card.find("a", class_="product-link")
                name = name_elem.get_text(strip=True) if name_elem else None
                
                # Extract URL
                link_elem = card.find("a", href=True)
                url = link_elem["href"] if link_elem else None
                if url and not url.startswith("http"):
                    url = urljoin(self.base_url, url)
                
                # Extract description
                desc_elem = card.find("p", class_="description") or card.find("p")
                description = desc_elem.get_text(strip=True) if desc_elem else ""
                
                # Extract metadata (if available)
                test_type = self._extract_test_type(card, name)
                duration = self._extract_duration(card)
                
                if name and url:
                    assessment = {
                        "assessment_name": name,
                        "url": url,
                        "description": description,
                        "test_type": test_type,
                        "duration": duration,
                        "remote_support": None,
                        "adaptive_support": None,
                    }
                    assessments.append(assessment)
            
            except Exception as e:
                logger.warning(f"Error parsing card: {e}")
                continue
        
        logger.info(f"Successfully parsed {len(assessments)} assessments")
        return assessments
    
    def _extract_test_type(self, card_elem, name: Optional[str] = None) -> Optional[str]:
        """
        Extract test type from card element.
        Test types: K (Knowledge), P (Personality/Behavior), Cognitive, etc.
        """
        # Look for test type in card metadata
        type_elem = card_elem.find("span", class_="test-type")
        if type_elem:
            type_text = type_elem.get_text(strip=True).lower()
            if "knowledge" in type_text or "skill" in type_text:
                return "K"
            elif "personality" in type_text or "behavior" in type_text or "people" in type_text:
                return "P"
            elif "cognitive" in type_text:
                return "Cognitive"
        
        # Fallback: infer from name
        if name:
            name_lower = name.lower()
            if "personality" in name_lower or "behavioral" in name_lower or "people" in name_lower:
                return "P"
            elif "reasoning" in name_lower or "programming" in name_lower or "language" in name_lower:
                return "K"
        
        return None
    
    def _extract_duration(self, card_elem) -> Optional[str]:
        """Extract test duration from card element."""
        duration_elem = card_elem.find("span", class_="duration") or card_elem.find("span", string=lambda s: s and "min" in s.lower())
        if duration_elem:
            return duration_elem.get_text(strip=True)
        return None
    
    def filter_individual_solutions(self, assessments: List[Dict]) -> List[Dict]:
        """
        Filter to keep only Individual Test Solutions.
        Remove Pre-packaged Job Solutions.
        """
        logger.info(f"Filtering assessments (input: {len(assessments)})")
        
        filtered = []
        for assessment in assessments:
            name_lower = assessment["assessment_name"].lower()
            
            # Exclude Pre-packaged solutions
            if "pre-packaged" in name_lower or "package" in name_lower:
                logger.debug(f"Excluding pre-packaged: {assessment['assessment_name']}")
                continue
            
            # Include Individual Test Solutions
            if "test" in name_lower or "assessment" in name_lower or "solution" in name_lower:
                filtered.append(assessment)
            elif assessment["test_type"]:  # Has a recognized test type
                filtered.append(assessment)
        
        logger.info(f"Filtered to {len(filtered)} individual solutions")
        return filtered
    
    def deduplicate_by_url(self, assessments: List[Dict]) -> List[Dict]:
        """Remove duplicate assessments by URL."""
        logger.info(f"Deduplicating assessments (input: {len(assessments)})")
        
        seen_urls = set()
        unique = []
        
        for assessment in assessments:
            url = assessment["url"]
            if url not in seen_urls:
                seen_urls.add(url)
                unique.append(assessment)
            else:
                logger.debug(f"Duplicate URL: {url}")
        
        logger.info(f"After deduplication: {len(unique)} unique assessments")
        return unique
    
    def save_assessments(self, assessments: List[Dict]) -> Path:
        """Save raw assessments to JSON file."""
        output_file = ASSESSMENTS_RAW_FILE
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(assessments, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(assessments)} assessments to {output_file}")
        return output_file
    
    def crawl(self) -> List[Dict]:
        """
        Main crawl method. Orchestrates the entire crawling process.
        """
        logger.info("Starting SHL catalog crawl...")
        
        for attempt in range(CRAWL_RETRIES):
            try:
                # Try requests first (simpler, faster)
                try:
                    html_content = self.fetch_page_with_requests()
                except Exception as e:
                    logger.warning(f"Requests failed, falling back to Selenium: {e}")
                    html_content = self.fetch_page_with_selenium()
                
                # Parse assessments
                self.assessments = self.parse_assessment_cards(html_content)
                
                # Filter and deduplicate
                self.assessments = self.filter_individual_solutions(self.assessments)
                self.assessments = self.deduplicate_by_url(self.assessments)
                
                # Validate count
                if len(self.assessments) < CRAWL_MIN_ASSESSMENTS:
                    logger.warning(
                        f"Only found {len(self.assessments)} assessments, "
                        f"expected ≥{CRAWL_MIN_ASSESSMENTS}"
                    )
                else:
                    logger.info(f"✓ Successfully crawled {len(self.assessments)} assessments")
                
                # Save
                self.save_assessments(self.assessments)
                
                return self.assessments
            
            except Exception as e:
                logger.error(f"Crawl attempt {attempt + 1} failed: {e}")
                if attempt == CRAWL_RETRIES - 1:
                    raise
                time.sleep(5)


def main():
    """Entry point for crawler."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    crawler = SHLCrawler()
    assessments = crawler.crawl()
    
    logger.info("Crawl complete!")
    logger.info(f"Total assessments: {len(assessments)}")
    logger.info(f"Sample assessment: {json.dumps(assessments[0], indent=2)}")


if __name__ == "__main__":
    main()
