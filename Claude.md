# AI Competitive Intelligence Scraper

## Project Overview
This application scrapes competitor websites in the AI space and generates daily competitive intelligence reports.

## Target Companies
- OpenAI (openai.com/blog)
- Google AI (ai.google/discover/blog)
- Microsoft AI (blogs.microsoft.com/ai)
- Meta AI (ai.meta.com/blog)

## Technical Stack
- Python 3.8+
- BeautifulSoup4 for web scraping
- Requests for HTTP requests
- Schedule for daily automation
- Markdown for report generation

## Key Features
1. Scrape recent blog posts and announcements
2. Extract titles, dates, and summaries
3. Generate formatted daily reports
4. Save reports with timestamps

## File Structure

## Development Guidelines
- Keep functions small and focused
- Add comments for complex logic
- Handle errors gracefully (websites might be down)
- Generate human-readable reports
- Respect website rate limits (don't spam requests)

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Run scraper: `python src/scraper.py`
3. View reports in the `reports/` folder