# AI-Powered Investment Advisor

Interactive Streamlit application for AI-driven stock investment recommendations built on Databricks Lakehouse.

## 🚀 Features

* 📈 Real-time investment recommendations (BUY/HOLD/AVOID)
* 📊 Interactive data visualizations with Plotly
* 🔍 Individual stock analysis with historical performance
* 📉 Sector-level market analytics
* 🤖 ML model performance tracking
* ⚡ Built on Databricks Lakehouse architecture

## 📁 Project Structure

```
investment-advisor/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .env.example           # Configuration template
├── .gitignore             # Git ignore file
├── components/
│   ├── __init__.py
│   ├── charts.py          # Plotly visualization components
│   └── metrics.py         # KPI and metric display components
└── data/
    ├── __init__.py
    ├── database.py        # Database connection using Databricks SDK
    └── queries.py         # SQL query functions
```

## 🔧 Prerequisites

* Python 3.11+
* Databricks workspace with:
  * SQL Warehouse access
  * Tables: `workspace.investment_db.investment_recommendations`, `workspace.investment_db.gold_stock_features`, `workspace.investment_db.model_comparison`
* Databricks Personal Access Token

## 📦 Installation & Setup

### Step 1: Extract and Navigate

```bash
unzip investment-advisor.zip
cd investment-advisor
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Databricks Authentication

**Option A: Environment Variables (Recommended)**

```bash
# Set these in your terminal
export DATABRICKS_HOST="https://dbc-3197f21b-d683.cloud.databricks.com"
export DATABRICKS_TOKEN="your_personal_access_token"
```

On Windows PowerShell:
```powershell
$env:DATABRICKS_HOST="https://dbc-3197f21b-d683.cloud.databricks.com"
$env:DATABRICKS_TOKEN="your_personal_access_token"
```

**Option B: Create .env File (Persistent)**

```bash
cp .env.example .env
# Edit .env and add your token
```

**Option C: Databricks Config File**

Create `~/.databrickscfg`:
```ini
[DEFAULT]
host = https://dbc-3197f21b-d683.cloud.databricks.com
token = your_personal_access_token
```

**How to get your Personal Access Token:**
1. Log into Databricks workspace
2. Go to User Settings → Developer → Access Tokens
3. Click "Generate New Token"
4. Copy the token immediately (you won't see it again!)

### Step 5: Run the Application

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`

## 🎯 Application Pages

### 📈 Overview Dashboard
* KPI metrics (total stocks, recommendations breakdown)
* Top BUY and AVOID recommendations
* Sector performance charts
* Risk vs Return scatter plot

### 📋 Recommendations
* Filterable list of all stocks
* Filter by Ticker, Sector, Recommendation, Risk Level
* Detailed analysis for each stock

### 🔍 Stock Explorer
* Deep dive into individual stocks
* Historical price charts
* Daily returns, volatility, moving averages
* Technical indicators

### 📊 Market Analytics
* Sector-level performance
* Top and bottom performers
* Market-wide risk/return analysis

### 🤖 Model Performance
* ML model comparison
* RMSE, MAE, R² metrics
* Visual performance charts

### ℹ️ About
* System architecture
* Methodology documentation
* Technology stack

## ⚙️ Configuration

### Change SQL Warehouse ID

Edit `data/database.py`:
```python
self.warehouse_id = 'your_warehouse_id_here'
```

### Change Database/Schema

Update table references in `data/queries.py`:
```python
FROM workspace.investment_db.investment_recommendations
# Change to:
FROM your_catalog.your_schema.your_table
```

### Change Port

```bash
streamlit run app.py --server.port 8080
```

## 🌐 Deployment Options

### Deploy to Streamlit Cloud

1. Push code to GitHub repository
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Create new app from your repo
4. Add secrets in app settings:
   ```toml
   DATABRICKS_HOST = "https://your-workspace.cloud.databricks.com"
   DATABRICKS_TOKEN = "your_token"
   ```
5. Deploy!

### Deploy with Docker

1. Create Dockerfile:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. Build and run:
```bash
docker build -t investment-advisor .
docker run -p 8501:8501 -e DATABRICKS_HOST="..." -e DATABRICKS_TOKEN="..." investment-advisor
```

## 🐛 Troubleshooting

### "Authentication failed"
* Verify `DATABRICKS_HOST` is correct (include https://)
* Check that your Personal Access Token is valid
* Ensure token has permission to access SQL Warehouse

### "Table not found"
* Verify table names in `data/queries.py` match your workspace
* Check that you have SELECT permissions on the tables
* Ensure tables exist: run `SHOW TABLES IN workspace.investment_db` in SQL Editor

### "SQL Warehouse not found"
* Update `warehouse_id` in `data/database.py`
* Verify you have CAN_USE permission on the warehouse
* Check warehouse ID in Databricks SQL Warehouses page

### "Module not found"
* Ensure virtual environment is activated
* Reinstall dependencies: `pip install -r requirements.txt`

## 📊 Expected Data Schema

The app expects these tables:

**investment_recommendations**
```sql
Date, Ticker, Sector, Close, Predicted_Return, 
Recommendation, Confidence_Score, Risk_Level, 
Explanation, Volatility
```

**gold_stock_features**
```sql
Date, Close, High, Low, Open, Volume, Ticker, 
Sector, Daily_Return, SMA_7, SMA_30, Volatility
```

**model_comparison**
```sql
Model, RMSE, MAE, R2
```

## ⚠️ Disclaimer

**This application is for EDUCATIONAL and RESEARCH purposes only.**

* Predictions are based on historical data
* Past performance does NOT guarantee future results
* Stock market investing involves risk of loss
* This is NOT financial advice
* Always consult a qualified financial advisor before making investment decisions

## 📄 License

MIT License - feel free to modify and use for your own projects!

## 🤝 Support

For issues related to:
* **Databricks**: Contact Databricks Support
* **Application bugs**: Check logs with `streamlit run app.py --logger.level=debug`
* **Data issues**: Verify table schemas and permissions in your Databricks workspace
