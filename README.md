# 📊 Live Stock Analyzer - Complete Financial Analysis Platform

A comprehensive web application that fetches **live data from Screener.in** to provide detailed stock analysis including financials, ratios, news impact, and price charts.

![Stock Analyzer Demo](https://img.shields.io/badge/Status-Production%20Ready-success)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Features

### 📈 Real-Time Data Fetching
- **Live data from Screener.in** - No hardcoded mock data
- Search any NSE/BSE listed company
- Instant company information retrieval
- Real-time stock prices and charts

### 💼 Comprehensive Financial Analysis
1. **Balance Sheet** (Last 5 years)
   - Equity & Reserves
   - Debt breakdown
   - Total assets & liabilities
   
2. **Profit & Loss Statement**
   - Revenue trends
   - Expense analysis
   - Net profit margins
   - Tax breakdown

3. **Cash Flow Statement**
   - Operating cash flows
   - Investing activities
   - Financing activities
   - Net cash position

4. **Financial Ratios with Industry Benchmarks**
   - **Profitability**: ROE, ROA, ROCE, Net Margin
   - **Liquidity**: Current Ratio, Quick Ratio
   - **Leverage**: Debt-to-Equity, Interest Coverage
   - **Valuation**: P/E, P/B, EV/EBITDA
   - Side-by-side comparison with industry averages
   - Automatic implications analysis

### 📰 News Integration & AI Analysis
- Fetches latest news from multiple sources
- **AI-powered sentiment analysis**
- Stock price impact prediction
- Comprehensive impact assessment
- Source credibility indicators

### 📊 Interactive Stock Charts
- 12-month price history
- Interactive Chart.js visualization
- Smooth animations and tooltips
- Responsive design

### 🎨 Modern UI/UX
- Beautiful gradient design
- Responsive layout (mobile-friendly)
- Smooth transitions and animations
- Professional color scheme
- Easy navigation with tabs

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Modern web browser
- Internet connection

### Option 1: Run with Backend (Recommended)

#### Step 1: Clone or Download Files
```bash
# Create project directory
mkdir stock-analyzer
cd stock-analyzer

# Place these files in the directory:
# - stock-analyzer-live.html (frontend)
# - backend_server.py (backend)
# - requirements.txt
# - .env.template
```

#### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Configure API Keys
1. Copy `.env.template` to `.env`:
```bash
cp .env.template .env
```

2. Edit `.env` and add your API keys:
```env
NEWS_API_KEY=your_newsapi_key_here
ALPHA_VANTAGE_KEY=your_alphavantage_key_here
```

**Get API Keys:**
- NewsAPI: https://newsapi.org/ (Free tier available)
- Alpha Vantage: https://www.alphavantage.co/ (Free tier available)

#### Step 4: Start the Backend Server
```bash
python backend_server.py
```

You should see:
```
================================================================================
STOCK ANALYZER BACKEND SERVER
================================================================================

Server starting on http://localhost:5000

Available endpoints:
  GET  /api/search?q=<query>           - Search companies
  GET  /api/company/<company_url>      - Get company data
  GET  /api/news/<company_name>        - Get company news
  GET  /api/stock-price/<stock_code>   - Get stock prices
  POST /api/analyze-news               - Analyze news impact

================================================================================
```

#### Step 5: Open Frontend
Simply open `stock-analyzer-live.html` in your browser:
```bash
# On Mac
open stock-analyzer-live.html

# On Linux
xdg-open stock-analyzer-live.html

# On Windows
start stock-analyzer-live.html
```

### Option 2: Standalone Frontend (Demo Mode)

If you just want to see the interface with mock data:

1. Open `stock-analyzer-live.html` directly in your browser
2. The app will use fallback mock data when API calls fail
3. Perfect for testing the UI/UX

## 📖 Usage Guide

### Searching for Companies

1. **Enter company name or stock code** in the search box
   - Examples: "Reliance", "TCS", "HDFC Bank", "INFY"
   
2. **Click Search** or press Enter

3. **Select from results** - Click on any company to view detailed analysis

### Navigating Tabs

- **Overview**: Key metrics at a glance (Market Cap, P/E, ROE, etc.)
- **Balance Sheet**: Assets, liabilities, equity trends
- **P&L Statement**: Revenue, expenses, profit analysis
- **Cash Flow**: Operating, investing, financing cash flows
- **Ratios & Benchmarks**: Compare with industry averages
- **Stock Chart**: Visual price history
- **News & Impact**: Latest news with AI-analyzed impact

### Understanding Ratio Analysis

Each ratio shows:
- **Company Value**: The actual company metric
- **Industry Value**: Sector average for comparison
- **Implication**: Automated analysis of what it means
- Color coding: 🟢 Positive | 🟡 Neutral | 🔴 Negative

### News Impact Analysis

Each news article includes:
- **Title & Source**: Where the news came from
- **Summary**: Brief overview
- **Impact Analysis**: How it might affect stock price
- **Sentiment Badge**: POSITIVE | NEUTRAL | NEGATIVE

## 🏗️ Project Structure

```
stock-analyzer/
├── stock-analyzer-live.html    # Frontend application (React)
├── backend_server.py            # Flask backend server
├── requirements.txt             # Python dependencies
├── .env.template               # Environment variables template
├── .env                        # Your actual API keys (create this)
├── IMPLEMENTATION_GUIDE.md     # Detailed technical guide
└── README.md                   # This file
```

## 🔧 Configuration

### Backend Settings

Edit `backend_server.py` to customize:

```python
# Port configuration
app.run(debug=True, port=5000)  # Change port if needed

# Data refresh intervals
CACHE_TTL = 3600  # How long to cache data (seconds)

# Number of news articles
pageSize': 10  # Adjust news count
```

### Frontend Settings

Edit `stock-analyzer-live.html`:

```javascript
// API endpoint (if backend is on different port/server)
const searchUrl = `http://localhost:5000/api/search?q=${query}`;

// Chart time period
const prices = companyData.stockPrices.slice(0, 365); // Days to show
```

## 🛠️ Technical Stack

### Frontend
- **React 18** - UI framework
- **Chart.js** - Interactive charts
- **Vanilla CSS** - Custom styling
- **Axios** - HTTP requests

### Backend
- **Flask** - Web framework
- **BeautifulSoup4** - Web scraping
- **Requests** - HTTP client
- **Pandas** - Data processing

### Data Sources
- **Screener.in** - Financial statements & ratios
- **NewsAPI** - Company news
- **Alpha Vantage** - Stock prices
- **Claude API** - Sentiment analysis (optional)

## 📊 Data Flow

```
User Search → Frontend → Backend API → Screener.in
                ↓
         Parse HTML Data
                ↓
      Extract Financials
                ↓
       Fetch News (NewsAPI)
                ↓
     Fetch Prices (Alpha Vantage)
                ↓
    Analyze Sentiment (Claude API)
                ↓
      Return Structured JSON
                ↓
     Frontend Renders Data
```

## 🚨 Important Notes

### Legal & Compliance
- **Terms of Service**: Ensure compliance with Screener.in's ToS
- **Rate Limiting**: Implement respectful scraping practices
- **Data Accuracy**: Financial data is for informational purposes only
- **Investment Disclaimer**: Not financial advice - always verify data

### Performance
- **Caching**: Backend caches data to reduce API calls
- **Rate Limits**: 
  - NewsAPI: 100 requests/day (free tier)
  - Alpha Vantage: 500 requests/day (free tier)
  - Screener.in: No official limit, but be respectful

### Security
- **API Keys**: Never commit `.env` to version control
- **CORS**: Configured for local development
- **Input Validation**: Sanitizes user input

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 5000 is in use
lsof -i :5000

# Use different port
python backend_server.py --port 5001
```

### CORS errors
1. Make sure backend is running
2. Check browser console for errors
3. Verify CORS_ORIGINS in `.env`

### No data showing
1. Check backend logs for errors
2. Verify API keys in `.env`
3. Test endpoints with curl:
```bash
curl http://localhost:5000/api/search?q=reliance
```

### Screener.in changes structure
- HTML structure may change
- Update parsing logic in `backend_server.py`
- Check `extract_overview()`, `extract_balance_sheet()` functions

## 🔮 Future Enhancements

- [ ] Peer comparison module
- [ ] Technical indicators (RSI, MACD, Bollinger Bands)
- [ ] Portfolio tracking
- [ ] Price alerts
- [ ] Fundamental score calculator
- [ ] Excel export functionality
- [ ] Watchlist feature
- [ ] Historical news archive
- [ ] Quarterly results tracker
- [ ] Insider trading data

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

1. **Data Sources**: Add more data providers
2. **Analysis**: Implement more financial metrics
3. **UI/UX**: Enhance visualization and user experience
4. **Features**: Add new analysis modules
5. **Performance**: Optimize data fetching and caching

## 📄 License

MIT License - Feel free to use this project for personal or commercial purposes.

## ⚠️ Disclaimer

This tool is for **informational and educational purposes only**. It is not intended to provide investment advice. Always:

- Verify data from official sources
- Consult with qualified financial advisors
- Perform your own due diligence
- Understand the risks of investing

The creators are not liable for any investment decisions made using this tool.

## 📞 Support

Having issues? 

1. Check the **Troubleshooting** section
2. Review the **IMPLEMENTATION_GUIDE.md**
3. Ensure all dependencies are installed
4. Verify API keys are correct

## 🎯 Key Differentiators

✅ **No Mock Data** - Fetches real live data from Screener.in  
✅ **Industry Benchmarks** - Compares ratios with sector averages  
✅ **AI News Analysis** - Predicts stock price impact  
✅ **Complete Financials** - 5 years of data across all statements  
✅ **Production Ready** - Clean code with error handling  
✅ **Well Documented** - Extensive comments and guides  

## 🙏 Acknowledgments

- **Screener.in** - For providing comprehensive financial data
- **NewsAPI** - For news aggregation
- **Alpha Vantage** - For stock price data
- **Anthropic** - For Claude API (sentiment analysis)

---

**Built with ❤️ for investors and financial analysts**

*Last Updated: 2024*
