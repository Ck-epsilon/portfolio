# Web Scraper Template — Multi-Site + Stealth Mode

Production-ready async web scraper with Playwright, anti-detection, and auto-pagination.

## Quick Start

```bash
pip install -r requirements.txt
playwright install chromium

python run.py --config sites/hackernews.yaml
```

Output appears in `output/` directory. Supports CSV and JSON.

## Project Structure

```
scraper-template/
├── scraper/
│   └── engine.py       # Core: StealthScraper class + ScraperConfig
├── sites/              # YAML config files for target sites
│   └── hackernews.yaml # Example config
├── output/             # Generated CSV/JSON results
├── run.py              # CLI entry point
├── requirements.txt
└── README.md
```

## Usage

### 1. Define a site config (`sites/mytarget.yaml`)

```yaml
name: "my-scraper"
start_urls:
  - "https://example.com/listings"

selectors:
  title: "h2.product-title"
  price: "span.price"

pagination_selector: "a.next-page"   # Optional: auto-paginate
max_pages: 5
delay_min: 1.0                        # Random delay between pages (anti-rate-limit)
delay_max: 2.5
output_format: "csv"                  # csv | json
```

### 2. Run

```bash
python run.py -c sites/mytarget.yaml -o data/output.csv
```

## Anti-Detection Features

- Removes `navigator.webdriver` flag
- Randomized viewport and user-agent
- Random delays between requests
- `domcontentloaded` wait strategy
- No `AutomationControlled` blink feature

## Customization

The `StealthScraper` class in `scraper/engine.py` is designed for extension:

```python
class MyScraper(StealthScraper):
    async def scrape_page(self, url):
        items = await super().scrape_page(url)
        # Add custom cleaning/transformation
        return [self.clean(item) for item in items]
```

## License

MIT — See repository LICENSE file.
