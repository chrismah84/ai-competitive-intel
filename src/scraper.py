#!/usr/bin/env python3
"""
AI Competitive Intelligence Web Scraper

This module scrapes AI company blogs to extract recent posts, titles, dates,
and summaries for competitive intelligence reporting.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import time
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BlogScraper:
    """Web scraper for AI company blogs"""
    
    def __init__(self, rate_limit_delay: float = 1.0):
        """Initialize the scraper with rate limiting
        
        Args:
            rate_limit_delay: Delay between requests in seconds
        """
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # News website configurations
        self.companies = {
            'TechCrunch AI': {
                'url': 'https://techcrunch.com/category/artificial-intelligence/',
                'parser': self._parse_generic_blog
            },
            'VentureBeat AI': {
                'url': 'https://venturebeat.com/ai/',
                'parser': self._parse_generic_blog
            },
            'The Verge AI': {
                'url': 'https://www.theverge.com/ai-artificial-intelligence',
                'parser': self._parse_generic_blog
            },
            'Ars Technica': {
                'url': 'https://arstechnica.com/tag/artificial-intelligence/',
                'parser': self._parse_generic_blog
            },
            'MIT Technology Review': {
                'url': 'https://www.technologyreview.com/topic/artificial-intelligence/',
                'parser': self._parse_generic_blog
            },
            'AI News': {
                'url': 'https://www.artificialintelligence-news.com/',
                'parser': self._parse_generic_blog
            }
        }

    def scrape_all_companies(self, days_back: int = 7) -> Dict[str, List[Dict]]:
        """Scrape all configured company blogs
        
        Args:
            days_back: How many days back to look for posts
            
        Returns:
            Dictionary with company names as keys and list of posts as values
        """
        results = {}
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        for company_name, config in self.companies.items():
            logger.info(f"Scraping {company_name}...")
            try:
                posts = self._scrape_company_blog(
                    company_name, 
                    config['url'], 
                    config['parser'],
                    cutoff_date
                )
                results[company_name] = posts
                logger.info(f"Found {len(posts)} recent posts from {company_name}")
            except Exception as e:
                logger.error(f"Failed to scrape {company_name}: {str(e)}")
                results[company_name] = []
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
        
        return results

    def _scrape_company_blog(self, company_name: str, url: str, parser_func, cutoff_date: datetime) -> List[Dict]:
        """Scrape a single company's blog
        
        Args:
            company_name: Name of the company
            url: Blog URL to scrape
            parser_func: Function to parse the specific blog format
            cutoff_date: Only include posts newer than this date
            
        Returns:
            List of post dictionaries
        """
        try:
            response = self._make_request(url)
            if not response:
                return []
            
            posts = parser_func(response.content, url, cutoff_date)
            return posts
            
        except requests.RequestException as e:
            logger.error(f"Network error scraping {company_name}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Parsing error for {company_name}: {str(e)}")
            return []

    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with error handling
        
        Args:
            url: URL to request
            
        Returns:
            Response object or None if failed
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            logger.error(f"Timeout accessing {url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error accessing {url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code} accessing {url}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error accessing {url}: {str(e)}")
            return None

    def _parse_generic_blog(self, html_content: bytes, base_url: str, cutoff_date: datetime) -> List[Dict]:
        """Generic parser for most news/blog websites"""
        posts = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            company = urlparse(base_url).netloc.replace('www.', '').title()
            
            # Multiple selector strategies for different site structures
            selectors = [
                'article',
                '[class*="post"]',
                '[class*="article"]',
                '[class*="story"]',
                '[class*="entry"]',
                '[class*="item"]',
                '[class*="card"]'
            ]
            
            post_elements = []
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    post_elements = elements[:15]  # Limit to prevent overwhelming
                    break
            
            # Fallback: look for any elements with headlines
            if not post_elements:
                post_elements = soup.find_all(['div'], string=re.compile(r'.+'))[:10]
            
            for element in post_elements:
                post = self._extract_post_info(element, base_url, company)
                if post and post.get('title') and len(post['title']) > 10:  # Filter out noise
                    if self._is_recent_post(post.get('date'), cutoff_date):
                        posts.append(post)
                        
        except Exception as e:
            logger.error(f"Error parsing generic blog: {str(e)}")
            
        return posts

    def _extract_post_info(self, element, base_url: str, company: str) -> Optional[Dict]:
        """Extract post information from HTML element
        
        Args:
            element: BeautifulSoup element containing post info
            base_url: Base URL for resolving relative links
            company: Company name
            
        Returns:
            Dictionary with post info or None if extraction failed
        """
        try:
            # Try to find title with multiple strategies
            title_elem = None
            title_selectors = [
                ['h1', 'h2', 'h3', 'h4'], 
                ['a'],
                '[class*="title"]',
                '[class*="headline"]'
            ]
            
            for selectors in title_selectors:
                if isinstance(selectors, list):
                    title_elem = element.find(selectors)
                else:
                    title_elem = element.select_one(selectors)
                if title_elem and title_elem.get_text().strip():
                    break
            
            title = title_elem.get_text().strip() if title_elem else "No title found"
            
            # Clean up title (remove extra whitespace, newlines)
            title = re.sub(r'\s+', ' ', title).strip()
            
            # Try to find link - prefer title links, then any link
            link_elem = None
            if title_elem and title_elem.name == 'a':
                link_elem = title_elem
            else:
                link_elem = element.find('a', href=True)
            
            if link_elem and link_elem.get('href'):
                link = urljoin(base_url, link_elem['href'])
            else:
                link = base_url
            
            # Try to find date
            date_elem = element.find(['time', 'span', 'div'], class_=re.compile(r'date|time|published', re.I))
            if date_elem:
                date_text = date_elem.get('datetime') or date_elem.get_text().strip()
                post_date = self._parse_date(date_text)
            else:
                post_date = None
            
            # Try to find summary/excerpt
            summary_elem = element.find(['p', 'div'], class_=re.compile(r'summary|excerpt|description', re.I))
            if not summary_elem:
                # Fallback to first paragraph
                summary_elem = element.find('p')
            
            summary = summary_elem.get_text().strip()[:200] + "..." if summary_elem else "No summary available"
            
            return {
                'title': title,
                'url': link,
                'date': post_date,
                'summary': summary,
                'company': company,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.debug(f"Failed to extract post info: {str(e)}")
            return None

    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse date from various formats
        
        Args:
            date_text: Date string to parse
            
        Returns:
            Datetime object or None if parsing failed
        """
        if not date_text:
            return None
            
        date_text = date_text.strip()
        
        # Common date formats
        date_formats = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%B %d, %Y',
            '%b %d, %Y',
            '%d %B %Y',
            '%d %b %Y',
            '%m/%d/%Y',
            '%d/%m/%Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_text, fmt)
            except ValueError:
                continue
        
        logger.debug(f"Could not parse date: {date_text}")
        return None

    def _is_recent_post(self, post_date: Optional[datetime], cutoff_date: datetime) -> bool:
        """Check if post is recent enough
        
        Args:
            post_date: Post publication date
            cutoff_date: Cutoff date for recent posts
            
        Returns:
            True if post is recent enough
        """
        if not post_date:
            return True  # Include posts without dates
        return post_date >= cutoff_date

def main():
    """Main function to run the scraper"""
    scraper = BlogScraper()
    
    logger.info("Starting competitive intelligence scraping...")
    results = scraper.scrape_all_companies(days_back=7)
    
    # Print results summary
    total_posts = sum(len(posts) for posts in results.values())
    logger.info(f"Scraping complete. Found {total_posts} total recent posts.")
    
    # Print detailed results
    for company, posts in results.items():
        print(f"\n{company}: {len(posts)} posts")
        for post in posts:
            print(f"  - {post['title']}")
            if post['date']:
                print(f"    Date: {post['date'].strftime('%Y-%m-%d')}")
            print(f"    URL: {post['url']}")
            print(f"    Summary: {post['summary'][:100]}...")
            print()
    
    return results

if __name__ == "__main__":
    main()