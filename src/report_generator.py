import os
from datetime import datetime
from typing import Dict, List, Any


class ReportGenerator:
    def __init__(self, reports_dir: str = "reports"):
        self.reports_dir = reports_dir
        self._ensure_reports_dir()
    
    def _ensure_reports_dir(self):
        """Create reports directory if it doesn't exist."""
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)
    
    def generate_report(self, scraped_data: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Generate markdown report from scraped data.
        
        Args:
            scraped_data: Dict with company names as keys and list of posts as values
                         Each post should have: title, url, date, summary
        
        Returns:
            Path to generated report file
        """
        today = datetime.now()
        report_content = self._build_report_content(scraped_data, today)
        
        filename = f"competitive_intel_{today.strftime('%Y%m%d_%H%M%S')}.md"
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return filepath
    
    def _build_report_content(self, scraped_data: Dict[str, List[Dict[str, Any]]], date: datetime) -> str:
        """Build the markdown content for the report."""
        content = []
        
        # Header with today's date
        content.append(f"# AI Competitive Intelligence Report")
        content.append(f"**Generated on:** {date.strftime('%B %d, %Y at %I:%M %p')}")
        content.append("")
        
        # Summary section
        total_posts = sum(len(posts) for posts in scraped_data.values())
        content.append(f"## Summary")
        content.append(f"- **Total posts analyzed:** {total_posts}")
        content.append(f"- **Companies monitored:** {len(scraped_data)}")
        content.append("")
        
        # Company sections
        for company, posts in scraped_data.items():
            content.append(f"## {company}")
            content.append("")
            
            if not posts:
                content.append("*No recent posts found.*")
                content.append("")
                continue
            
            content.append(f"**Recent posts ({len(posts)}):**")
            content.append("")
            
            for post in posts:
                content.append(f"### {post.get('title', 'Untitled')}")
                
                if post.get('date'):
                    content.append(f"**Date:** {post['date']}")
                
                if post.get('url'):
                    content.append(f"**Link:** [{post['url']}]({post['url']})")
                
                if post.get('summary'):
                    content.append(f"**Summary:** {post['summary']}")
                else:
                    content.append("**Summary:** *No summary available*")
                
                content.append("")
        
        # Footer
        content.append("---")
        content.append("*Report generated automatically by AI Competitive Intelligence Scraper*")
        
        return "\n".join(content)