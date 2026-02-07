"""
============================================================================
STOCK ANALYZER BACKEND SERVER
============================================================================
This Flask server provides API endpoints to fetch live data from:
1. Screener.in - Company financials, ratios, balance sheets
2. News APIs - Recent company news
3. Stock price APIs - Historical price data

The server handles CORS and acts as a proxy to avoid browser restrictions
============================================================================
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
# Add to backend_server.py
import anthropic

def analyze_news_with_claude(article, company_name):
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"""Analyze this news article about {company_name}:
            
            Title: {article['title']}
            Content: {article['summary']}
            
            Provide:
            1. Sentiment (positive/negative/neutral)
            2. Stock price impact prediction (2-3 sentences)
            3. Confidence score (0-1)
            
            Format as JSON."""
        }]
    )
    
    return json.loads(message.content[0].text)
# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# ============================================================================
# CONFIGURATION
# ============================================================================

# API Keys (Load from environment variables)
NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'your_newsapi_key_here')
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY', 'your_alphavantage_key_here')

# Base URLs
SCREENER_BASE_URL = 'https://www.screener.in'
NEWS_API_URL = 'https://newsapi.org/v2/everything'


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def clean_number(text):
    """
    Convert text like '1,234.56 Cr' or '12.5%' to float
    """
    if not text or text == '-' or text == 'N/A':
        return None
    
    # Remove common suffixes and commas
    text = text.replace(',', '').replace('Cr', '').replace('%', '').strip()
    
    try:
        return float(text)
    except ValueError:
        return None


# ============================================================================
# SCREENER.IN API ENDPOINTS
# ============================================================================

@app.route('/api/search', methods=['GET'])
def search_companies():
    """
    Search for companies on Screener.in
    GET /api/search?q=reliance
    
    Returns: List of matching companies with name, code, and URL
    """
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    try:
        # Screener.in search API endpoint
        search_url = f'{SCREENER_BASE_URL}/api/company/search/?q={query}'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Format the response
        results = []
        for company in data:
            # Extract stock code from URL
            url = company.get('url', '')
            code = 'N/A'
            if '/company/' in url:
                code = url.split('/company/')[1].replace('/', '').upper()
            
            results.append({
                'id': company.get('id'),
                'name': company.get('name'),
                'url': url,
                'code': code
            })
        
        return jsonify(results)
    
    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({'error': f'Failed to search companies: {str(e)}'}), 500


@app.route('/api/company/<path:company_url>', methods=['GET'])
def get_company_data(company_url):
    """
    Fetch complete company data from Screener.in
    GET /api/company/RELIANCE or GET /api/company//company/RELIANCE/
    
    Returns: Complete financial data including balance sheet, P&L, cash flow, ratios
    """
    try:
        # Construct full URL
        if not company_url.startswith('/company/'):
            company_url = f'/company/{company_url}/'
        
        if not company_url.endswith('/'):
            company_url += '/'
        
        full_url = f'{SCREENER_BASE_URL}{company_url}'
        
        print(f"Fetching data from: {full_url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(full_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract all data
        data = {
            'overview': extract_overview(soup),
            'balanceSheet': extract_balance_sheet(soup),
            'profitLoss': extract_profit_loss(soup),
            'cashFlow': extract_cash_flow(soup),
            'ratios': extract_ratios(soup),
            'quarters': extract_quarterly_results(soup)
        }
        
        print("Data extraction successful")
        return jsonify(data)
    
    except Exception as e:
        print(f"Company data error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to fetch company data: {str(e)}'}), 500


def extract_overview(soup):
    """
    Extract key metrics from company overview section
    """
    overview = {}
    
    try:
        # Extract from top ratios section
        top_ratios = soup.find('ul', id='top-ratios')
        if top_ratios:
            items = top_ratios.find_all('li')
            for item in items:
                label_span = item.find('span', class_='name')
                value_span = item.find('span', class_='number')
                
                if label_span and value_span:
                    key = label_span.text.strip().lower().replace(' ', '_').replace('/', '_')
                    overview[key] = value_span.text.strip()
        
        # Extract from company ratios section
        company_ratios = soup.find('div', class_='company-ratios')
        if company_ratios:
            ratio_items = company_ratios.find_all('li', class_='flex')
            for ratio in ratio_items:
                spans = ratio.find_all('span')
                if len(spans) >= 2:
                    key = spans[0].text.strip().lower().replace(' ', '_').replace('/', '_')
                    value = spans[1].text.strip()
                    overview[key] = value
        
        # Extract sector information
        sub_header = soup.find('p', class_='sub')
        if sub_header:
            overview['sector'] = sub_header.text.strip()
        
        # Extract company name
        company_name = soup.find('h1', class_='h2')
        if company_name:
            overview['company_name'] = company_name.text.strip()
    
    except Exception as e:
        print(f"Overview extraction error: {str(e)}")
    
    return overview


def extract_balance_sheet(soup):
    """
    Extract balance sheet data from annual financials
    """
    balance_sheet = []
    
    try:
        # Find the balance sheet section
        section = soup.find('section', id='balance-sheet')
        if not section:
            print("Balance sheet section not found")
            return balance_sheet
        
        table = section.find('table')
        if not table:
            print("Balance sheet table not found")
            return balance_sheet
        
        # Get headers (years)
        headers = []
        header_row = table.find('thead')
        if header_row:
            for th in header_row.find_all('th'):
                headers.append(th.text.strip())
        
        if len(headers) < 2:
            print("No headers found in balance sheet")
            return balance_sheet
        
        years = headers[1:]  # First column is metric name
        
        # Initialize data structure
        data = {year: {} for year in years}
        
        # Extract rows
        tbody = table.find('tbody')
        if tbody:
            for row in tbody.find_all('tr'):
                cells = row.find_all('td')
                if not cells:
                    continue
                
                metric = cells[0].text.strip()
                
                # Store values for each year
                for i, cell in enumerate(cells[1:], 0):
                    if i < len(years):
                        value = clean_number(cell.text.strip())
                        data[years[i]][metric] = value
        
        # Convert to list format
        for year in years:
            balance_sheet.append({
                'year': year,
                'equity': data[year].get('Equity Capital') or data[year].get('Equity Share Capital') or 0,
                'reserves': data[year].get('Reserves') or data[year].get('Reserves and Surplus') or 0,
                'debt': (data[year].get('Borrowings') or 0) + (data[year].get('Total Debt') or 0),
                'assets': data[year].get('Total Assets') or 0
            })
        
        print(f"Extracted {len(balance_sheet)} years of balance sheet data")
    
    except Exception as e:
        print(f"Balance sheet extraction error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return balance_sheet


def extract_profit_loss(soup):
    """
    Extract P&L statement data
    """
    profit_loss = []
    
    try:
        section = soup.find('section', id='profit-loss')
        if not section:
            print("P&L section not found")
            return profit_loss
        
        table = section.find('table')
        if not table:
            print("P&L table not found")
            return profit_loss
        
        # Get years
        headers = []
        header_row = table.find('thead')
        if header_row:
            for th in header_row.find_all('th'):
                headers.append(th.text.strip())
        
        years = headers[1:]
        
        # Initialize data structure
        data = {year: {} for year in years}
        
        # Extract rows
        tbody = table.find('tbody')
        if tbody:
            for row in tbody.find_all('tr'):
                cells = row.find_all('td')
                if not cells:
                    continue
                
                metric = cells[0].text.strip()
                
                for i, cell in enumerate(cells[1:], 0):
                    if i < len(years):
                        value = clean_number(cell.text.strip())
                        data[years[i]][metric] = value
        
        # Convert to list format
        for year in years:
            profit_loss.append({
                'year': year,
                'revenue': data[year].get('Sales') or data[year].get('Revenue') or data[year].get('Net Sales') or 0,
                'expenses': data[year].get('Expenses') or data[year].get('Total Expenses') or data[year].get('Operating Expenses') or 0,
                'profit': data[year].get('Profit before tax') or data[year].get('PBT') or 0,
                'tax': data[year].get('Tax') or data[year].get('Tax %') or 0,
                'netProfit': data[year].get('Net Profit') or data[year].get('Profit After Tax') or 0
            })
        
        print(f"Extracted {len(profit_loss)} years of P&L data")
    
    except Exception as e:
        print(f"P&L extraction error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return profit_loss


def extract_cash_flow(soup):
    """
    Extract cash flow statement
    """
    cash_flow = []
    
    try:
        section = soup.find('section', id='cash-flow')
        if not section:
            print("Cash flow section not found")
            return cash_flow
        
        table = section.find('table')
        if not table:
            print("Cash flow table not found")
            return cash_flow
        
        # Get years
        headers = []
        header_row = table.find('thead')
        if header_row:
            for th in header_row.find_all('th'):
                headers.append(th.text.strip())
        
        years = headers[1:]
        
        # Initialize data structure
        data = {year: {} for year in years}
        
        # Extract rows
        tbody = table.find('tbody')
        if tbody:
            for row in tbody.find_all('tr'):
                cells = row.find_all('td')
                if not cells:
                    continue
                
                metric = cells[0].text.strip()
                
                for i, cell in enumerate(cells[1:], 0):
                    if i < len(years):
                        value = clean_number(cell.text.strip())
                        data[years[i]][metric] = value
        
        # Convert to list format
        for year in years:
            operating = data[year].get('Cash from Operating Activity') or 0
            investing = data[year].get('Cash from Investing Activity') or 0
            financing = data[year].get('Cash from Financing Activity') or 0
            net_cash = data[year].get('Net Cash Flow') or (operating + investing + financing)
            
            cash_flow.append({
                'year': year,
                'operating': operating,
                'investing': investing,
                'financing': financing,
                'netCash': net_cash
            })
        
        print(f"Extracted {len(cash_flow)} years of cash flow data")
    
    except Exception as e:
        print(f"Cash flow extraction error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return cash_flow


def extract_ratios(soup):
    """
    Extract financial ratios and create industry comparison
    """
    ratios = {
        'profitability': [],
        'liquidity': [],
        'leverage': [],
        'valuation': []
    }
    
    try:
        # Extract ratios from the page
        # Note: Industry averages would need to be fetched separately
        # For now, using typical industry benchmarks
        
        # Helper to get ratio value
        def get_ratio_value(label):
            elements = soup.find_all('span', class_='number')
            for el in elements:
                parent = el.find_parent()
                if parent and label.lower() in parent.text.lower():
                    return el.text.strip()
            return 'N/A'
        
        # Profitability ratios
        ratios['profitability'] = [
            {
                'metric': 'Net Profit Margin',
                'company': get_ratio_value('OPM') or get_ratio_value('Net Profit Margin'),
                'industry': '12.5%',
                'implication': 'Comparison with industry average'
            },
            {
                'metric': 'ROE',
                'company': get_ratio_value('ROE'),
                'industry': '15.2%',
                'implication': 'Return on equity compared to sector'
            },
            {
                'metric': 'ROCE',
                'company': get_ratio_value('ROCE'),
                'industry': '18.5%',
                'implication': 'Return on capital employed analysis'
            }
        ]
        
        # Liquidity ratios
        ratios['liquidity'] = [
            {
                'metric': 'Current Ratio',
                'company': get_ratio_value('Current Ratio'),
                'industry': '1.8',
                'implication': 'Short-term liquidity position'
            },
            {
                'metric': 'Quick Ratio',
                'company': get_ratio_value('Quick Ratio'),
                'industry': '1.2',
                'implication': 'Immediate liquidity strength'
            }
        ]
        
        # Leverage ratios
        ratios['leverage'] = [
            {
                'metric': 'Debt to Equity',
                'company': get_ratio_value('Debt to Equity'),
                'industry': '0.65',
                'implication': 'Financial leverage comparison'
            }
        ]
        
        # Valuation ratios
        ratios['valuation'] = [
            {
                'metric': 'P/E Ratio',
                'company': get_ratio_value('Stock P/E') or get_ratio_value('PE'),
                'industry': '22.3',
                'implication': 'Valuation vs sector average'
            },
            {
                'metric': 'P/B Ratio',
                'company': get_ratio_value('Price to Book') or get_ratio_value('PB'),
                'industry': '2.8',
                'implication': 'Price to book value analysis'
            }
        ]
    
    except Exception as e:
        print(f"Ratios extraction error: {str(e)}")
    
    return ratios


def extract_quarterly_results(soup):
    """
    Extract quarterly financial results
    """
    quarters = []
    
    try:
        section = soup.find('section', id='quarters')
        if not section:
            return quarters
        
        table = section.find('table')
        if not table:
            return quarters
        
        # Similar extraction logic for quarterly data
        # Implementation depends on table structure
    
    except Exception as e:
        print(f"Quarterly results extraction error: {str(e)}")
    
    return quarters


# ============================================================================
# NEWS API ENDPOINTS
# ============================================================================

@app.route('/api/news/<company_name>', methods=['GET'])
def get_company_news(company_name):
    """
    Fetch recent news about the company from NewsAPI
    GET /api/news/Reliance
    
    Returns: List of recent news articles
    """
    try:
        params = {
            'q': company_name,
            'sortBy': 'publishedAt',
            'language': 'en',
            'pageSize': 10,
            'apiKey': NEWS_API_KEY
        }
        
        response = requests.get(NEWS_API_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        articles = []
        for article in data.get('articles', [])[:5]:
            articles.append({
                'title': article.get('title'),
                'date': article.get('publishedAt'),
                'source': article.get('source', {}).get('name'),
                'summary': article.get('description') or article.get('content', '')[:200],
                'url': article.get('url'),
                'imageUrl': article.get('urlToImage'),
                # Add mock sentiment analysis
                'sentiment': 'neutral',
                'impact': 'Impact analysis requires sentiment analysis integration'
            })
        
        return jsonify(articles)
    
    except Exception as e:
        print(f"News fetch error: {str(e)}")
        return jsonify({'error': f'Failed to fetch news: {str(e)}'}), 500


# ============================================================================
# STOCK PRICE DATA
# ============================================================================

@app.route('/api/stock-price/<stock_code>', methods=['GET'])
def get_stock_price(stock_code):
    """
    Fetch historical stock prices from Alpha Vantage
    GET /api/stock-price/RELIANCE
    
    Returns: Daily prices for the last year
    """
    try:
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': f'{stock_code}.BSE',
            'outputsize': 'full',
            'apikey': ALPHA_VANTAGE_KEY
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        if 'Error Message' in data:
            return jsonify({'error': 'Invalid stock symbol'}), 400
        
        time_series = data.get('Time Series (Daily)', {})
        
        prices = []
        for date, values in list(time_series.items())[:365]:
            prices.append({
                'date': date,
                'price': float(values['4. close'])
            })
        
        prices.reverse()  # Chronological order
        
        return jsonify(prices)
    
    except Exception as e:
        print(f"Stock price fetch error: {str(e)}")
        return jsonify({'error': f'Failed to fetch stock prices: {str(e)}'}), 500


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API documentation"""
    return jsonify({
        'message': 'Stock Analyzer Backend API',
        'version': '1.0.0',
        'endpoints': {
            'search': 'GET /api/search?q=<query>',
            'company': 'GET /api/company/<company_url>',
            'news': 'GET /api/news/<company_name>',
            'stock_price': 'GET /api/stock-price/<stock_code>',
            'health': 'GET /health'
        }
    })


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("STOCK ANALYZER BACKEND SERVER")
    print("=" * 80)
    print(f"\nServer starting on http://localhost:5000")
    print("\nAvailable endpoints:")
    print("  GET  /api/search?q=<query>           - Search companies")
    print("  GET  /api/company/<company_url>      - Get company data")
    print("  GET  /api/news/<company_name>        - Get company news")
    print("  GET  /api/stock-price/<stock_code>   - Get stock prices")
    print("\nMake sure to configure your API keys in .env file!")
    print("=" * 80 + "\n")
    
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    app.run(debug=debug, port=port, host='0.0.0.0')
