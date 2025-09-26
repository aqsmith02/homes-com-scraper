# Buncombe County Real Estate Scraper

A Python web scraper that collects comprehensive data on sold homes in Buncombe County, North Carolina from homes.com. The scraper extracts housing details to enable real estate market analysis.

## Overview

This scraper uses Playwright to automate browser interactions and extract detailed information from homes.com listings. It's designed to handle the site's anti-bot measures through human-like browsing behavior and VPN rotation requirements.

## Features

### Variables Collected
- **Property Details**: Address, price, square footage, bedrooms, bathrooms, year built, price per square foot
- **Market Metrics**: Days on market
- **Location Scores**: Crime, walkability, environmental factors (sound, flood, fire, heat, wind, air quality)
- **School Information**: Elementary, middle, and high school assignments with ratings and commute times
- **Transportation**: Airport commute times

### Performance & Anti-Detection
- **Multi-processing**: Uses 4 parallel processes to scrape 5 houses simultaneously
- **Human-like Behavior**: Random delays and scrolling patterns to avoid detection
- **VPN Integration**: Built-in prompts for VPN location changes to prevent IP blocking
- **Robust Error Handling**: Continues operation even when individual data points fail to load

## Requirements

### Python Dependencies
```bash
pip install playwright pandas
```

### Playwright Browser Setup
```bash
playwright install chromium
```

### Additional Requirements
- **VPN Service**: Required for IP rotation during scraping
- **Stable Internet Connection**: Essential for consistent data collection

## Data Structure

### Price Range Segmentation
The scraper divides properties into 4 price ranges to work within homes.com's 720-property display limit:

1. **Range 1**: Under $430,000
2. **Range 2**: $430,000 - $630,000  
3. **Range 3**: $630,000 - $1,000,000
4. **Range 4**: Over $1,000,000

### Output Format
Each completed page generates a CSV file with 27 columns of data per property:
- Basic property info (address, price, specs)
- Market data (days on market, price per sq ft)
- Area scores (crime, walkability, environmental factors)
- School data (names, ratings, commute times)
- Original listing URLs

## Usage

### Basic Usage
```python
from sold_homes_scraper import scrape_all

# Scrape pages 1-5 for price range 1 (under $430k)
scrape_all(price_range=1, page_start=1, page_end=6, skip_first_half=False)
```

### Function Parameters

#### `scrape_all(price_range, page_start, page_end, skip_first_half)`
- **`price_range`** (int): Price filter (1-4)
- **`page_start`** (int): Starting page number  
- **`page_end`** (int): Ending page number (exclusive)
- **`skip_first_half`** (bool): Skip first 20 houses on starting page (useful for resuming after crashes)

#### `scrape_5_houses(price_range, page, eighth)`
- **`price_range`** (int): Price filter (1-4)
- **`page`** (int): Page number to scrape
- **`eighth`** (int): Which group of 5 houses to scrape (1-8)

## Operation Workflow

### Automated Process
1. **Page Loading**: Opens homes.com search results for specified price range and page
2. **Data Extraction**: Scrapes basic info from property cards on main page
3. **Individual Property Visits**: Navigates to each property's detail page for additional data
4. **Multi-processing**: Runs 4 parallel processes handling 5 properties each
5. **File Consolidation**: Combines individual CSV files into single page file
6. **VPN Rotation**: Prompts for VPN location change every 20 properties

### Progress Tracking
- Prints current house number being scraped (1-40 per page)
- Displays completion messages every 20 houses
- Automatic 2-minute pause for VPN changes

## Important Usage Notes

### Anti-Detection Requirements
- **Change VPN locations every 20 houses** when prompted

### Technical Limitations
- **40 houses per page maximum**: homes.com limitation
- **Cannot handle partial final pages**: Expects exactly 40 properties per page
- **720 property search limit**: Requires price range segmentation for complete coverage
- **Buncombe County only**: URL builder configured specifically for this area

### Customization Options
- **Different counties**: Modify `BASE_MAIN_LINK` in `scrape_5_houses()`
- **Price ranges**: Adjust price filters in URL builder section
- **Property types**: Currently set to single-family homes (`property_type=1`)

## Error Recovery

### Resuming After Crashes
```python
# If crash occurred on page 3, second half
scrape_all(price_range=1, page_start=3, page_end=6, skip_first_half=True)
```

### Common Issues
- **TimeoutError**: Normal for missing data fields, automatically handled
- **Process hanging**: Usually indicates IP blocking - change VPN location
- **Incomplete final pages**: Manually adjust for pages with fewer than 40 properties

## Output Files

### Temporary Files
- `{price_range}_{page}_{eighth}_homes.csv`: Individual process outputs (automatically deleted)

### Final Output
- `{price_range}_{page}.csv`: Consolidated data for entire page (40 properties)

## Performance

### Speed Estimates
- **~20 properties per 10-15 minutes** (including VPN change breaks)
- **Full page (40 properties)**: ~25-30 minutes

### Resource Usage
- **4 concurrent browser instances** during active scraping
- **Moderate CPU/memory usage** from parallel processing
- **Network intensive** due to detailed page visits

## Author
- Andrew Smith  
