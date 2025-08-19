#!/usr/bin/env python3
"""
Main entry point for AI Competitive Intelligence Scraper.
"""

import sys
from datetime import datetime
from scraper import BlogScraper
from report_generator import ReportGenerator


def main():
    """Main function to run the competitive intelligence scraper."""
    print("🤖 AI Competitive Intelligence Scraper Starting...")
    print(f"📅 Run started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialize scraper and report generator
        print("🔧 Initializing scraper...")
        scraper = BlogScraper()
        report_generator = ReportGenerator()
        
        # Run the scraping process
        print("🕷️  Starting web scraping...")
        scraped_data = scraper.scrape_all_companies()
        
        if not scraped_data:
            print("⚠️  No data was scraped. Check your internet connection or target websites.")
            return 1
        
        # Count total posts found
        total_posts = sum(len(posts) for posts in scraped_data.values())
        companies_with_data = len([c for c, posts in scraped_data.items() if posts])
        
        print(f"✅ Scraping completed!")
        print(f"   📊 Found {total_posts} posts across {companies_with_data} companies")
        
        # Generate report
        print("📝 Generating report...")
        report_path = report_generator.generate_report(scraped_data)
        
        print(f"✅ Report generated successfully!")
        print(f"   📁 Saved to: {report_path}")
        
        # Summary of what was found
        print("\n📈 Summary by company:")
        for company, posts in scraped_data.items():
            status = f"{len(posts)} posts" if posts else "no posts"
            print(f"   • {company}: {status}")
        
        print(f"\n🎉 Process completed successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return 0
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Run: pip install -r requirements.txt")
        return 1
        
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
        print(f"🔍 Error type: {type(e).__name__}")
        
        # Print more details for debugging
        import traceback
        print("\n🐛 Full error traceback:")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())