import yfinance as yf
import pandas as pd
import json
import sys
import requests
from datetime import datetime

# Set User-Agent that bypasses Yahoo Finance bot detection (from GitHub issue #2297)
# This specific older IE User-Agent has been reported to work consistently
yf.utils.user_agent = 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.0.3705;)'

def serialize_value(v, key=None):
    if isinstance(v, pd.Timestamp):
        return v.strftime('%Y-%m-%d')
    elif isinstance(v, datetime):
        return v.strftime('%Y-%m-%d')
    elif isinstance(v, pd.Series):
        return v.to_dict()
    elif isinstance(v, float) and pd.isna(v):
        return None
    elif isinstance(v, pd.DataFrame):
        return v.to_dict()
    elif key == 'longBusinessSummary' and isinstance(v, str):
        # If text is longer than 250 bytes
        if len(v.encode('utf-8')) > 500:
            # Find the last period after 250 bytes
            text = v[:500]  # Get first 250 characters as starting point
            last_period = text.rfind('.')
            if last_period != -1:
                return v[:last_period + 1]  # Include the period
            else:
                # If no period found, find the nearest space after 250 bytes
                space_pos = v.find(' ', 500)
                if space_pos != -1:
                    return v[:space_pos] + '...'
                else:
                    return v[:500] + '...'
        return v
    else:
        return v

def get_usd_to_inr_rate():
    """
    Fetch the latest USD to INR exchange rate from exchangerate-api.com
    
    Returns:
        float: USD to INR conversion rate, or None if failed
    """
    try:
        url = "https://v6.exchangerate-api.com/v6/3f2f57927a3c29e06bee862d/latest/USD"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if data.get('result') == 'success':
            inr_rate = data.get('conversion_rates', {}).get('INR')
            if inr_rate:
                # Only log to stderr to avoid interfering with JSON output
                print(f"Fetched USD to INR rate: {inr_rate}", file=sys.stderr)
                return float(inr_rate)
        
        print("Failed to get valid exchange rate from API", file=sys.stderr)
        return None
        
    except Exception as e:
        print(f"Error fetching exchange rate: {str(e)}", file=sys.stderr)
        return None

def convert_financial_value(value, exchange_rate):
    """
    Convert a financial value from USD to INR
    
    Args:
        value: The value to convert (can be None, number, or string)
        exchange_rate (float): USD to INR conversion rate
    
    Returns:
        Converted value or None if input is None
    """
    if value is None or pd.isna(value):
        return None
    
    try:
        # Handle different value types
        if isinstance(value, (int, float)):
            return round(float(value) * exchange_rate, 2)
        elif isinstance(value, str):
            try:
                numeric_value = float(value)
                return round(numeric_value * exchange_rate, 2)
            except ValueError:
                return value  # Return as-is if not numeric
        else:
            return value  # Return as-is for non-numeric types
    except Exception:
        return value

def should_convert_currency(symbol):
    """
    Determine if the symbol needs currency conversion from USD to INR
    
    Args:
        symbol (str): Stock symbol
    
    Returns:
        bool: True if conversion is needed, False otherwise
    """
    # INFY.NS comes in USD but should be converted to INR
    usd_symbols = ['INFY.NS']
    return symbol.upper() in [s.upper() for s in usd_symbols]

def convert_financial_data(data, exchange_rate):
    """
    Convert financial data from USD to INR for specific financial fields
    
    Args:
        data (dict): Financial data dictionary
        exchange_rate (float): USD to INR conversion rate
    
    Returns:
        dict: Converted financial data
    """
    if not exchange_rate:
        return data
    
    # Define fields that should be converted (financial/monetary values)
    financial_fields = [
        # Income Statement fields
        'Net Income From Continuing Operation Net Minority Interest',
        'EBITDA', 'EBIT', 'Interest Expense', 'Interest Income',
        'Net Income From Continuing And Discontinued Operation',
        'Net Income Common Stockholders', 'Net Income',
        'Net Income Including Noncontrolling Interests',
        'Tax Provision', 'Operating Income', 'Operating Expense',
        'Depreciation And Amortization In Income Statement',
        'Amortization', 'Depreciation Income Statement',
        'Selling General And Administration', 'Selling And Marketing Expense',
        'General And Administrative Expense', 'Gross Profit',
        'Cost Of Revenue', 'Total Revenue', 'Operating Revenue',
        
        # Balance Sheet fields
        'Net Debt', 'Total Debt', 'Tangible Book Value', 'Working Capital',
        'Net Tangible Assets', 'Capital Lease Obligations',
        'Common Stock Equity', 'Stockholders Equity', 'Other Equity Interest',
        'Retained Earnings', 'Total Liabilities Net Minority Interest',
        'Other Non Current Liabilities', 'Long Term Debt And Capital Lease Obligation',
        'Long Term Debt', 'Long Term Provisions', 'Current Liabilities',
        'Current Debt And Capital Lease Obligation', 'Current Debt',
        'Payables', 'Dividends Payable', 'Total Tax Payable',
        'Accounts Payable', 'Total Assets', 'Total Non Current Assets',
        'Other Non Current Assets', 'Goodwill And Other Intangible Assets',
        'Other Intangible Assets', 'Goodwill', 'Net PPE', 'Current Assets',
        'Other Current Assets', 'Inventory', 'Other Receivables',
        'Taxes Receivable', 'Accounts Receivable', 'Gross Accounts Receivable',
        'Cash Cash Equivalents And Short Term Investments',
        'Other Short Term Investments', 'Cash And Cash Equivalents', 'Cash Equivalents',
        
        # Cash Flow fields
        'Free Cash Flow', 'Repayment Of Debt', 'Issuance Of Debt',
        'Capital Expenditure', 'Changes In Cash',
        'Financing Cash Flow', 'Cash Dividends Paid', 'Long Term Debt Payments', 'Sale Of Investment',
        'Purchase Of Investment', 'Net Business Purchase And Sale',
        'Sale Of Business', 'Purchase Of Business', 'Net PPE Purchase And Sale',
        'Capital Expenditure Reported', 'Operating Cash Flow',
        'Change In Working Capital', 'Change In Other Current Assets',
        'Change In Payable', 'Change In Receivables',
        'Depreciation And Amortization', 'Net Income From Continuing Operations',
        
        # Info fields
        # 'currentPrice', 'dayHigh', 'dayLow', 'previousClose',
        # 'dividendRate', 'marketCap', 'fiftyTwoWeekLow', 'fiftyTwoWeekHigh',
        # 'fiftyDayAverage', 'twoHundredDayAverage', 'regularMarketPrice',
        'bookValue','totalCash','totalDebt', 'grossProfits',
        
        # Quarterly fields
        'Pretax Income', 'Net Income Continuous Operations',
        'Basic EPS', 'Net Interest Income', 'Reconciled Cost Of Revenue',
        'Reconciled Depreciation', 'Total Unusual Items Excluding Goodwill',
        'Normalized EBITDA'
    ]
    
    def convert_nested_data(obj):
        """Recursively convert financial values in nested dictionaries"""
        if isinstance(obj, dict):
            converted = {}
            for key, value in obj.items():
                if key in financial_fields:
                    converted[key] = convert_financial_value(value, exchange_rate)
                else:
                    converted[key] = convert_nested_data(value)
            return converted
        elif isinstance(obj, (list, tuple)):
            return [convert_nested_data(item) for item in obj]
        else:
            return obj
    
    return convert_nested_data(data)

def get_company_latestPrice(symbol):
    try:
        company = yf.Ticker(symbol)
        info = company.info
        
        price_info = {
            'currentPrice': info.get('currentPrice'),
            'dayHigh': info.get('dayHigh'),
            'dayLow': info.get('dayLow'),
            'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh'),
            'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow'),
            'previousClose': info.get('previousClose')
        }
        return json.dumps(price_info)
    except Exception as e:
        return json.dumps({"error": str(e)})

def get_company_financials(symbol):
    try:
        # Check if currency conversion is needed
        needs_conversion = should_convert_currency(symbol)
        exchange_rate = None
        
        if needs_conversion:
            exchange_rate = get_usd_to_inr_rate()
            if not exchange_rate:
                print(f"Warning: Could not fetch exchange rate for {symbol}. Data will remain in USD.", file=sys.stderr)
        
        # Fetch company data
        company = yf.Ticker(symbol)
        
        # Get different types of financial data
        data = {
            'income_statement': company.income_stmt,
            'balance_sheet': company.balance_sheet,
            'cash_flow': company.cash_flow,
            'info': company.info
        }
        
        # Define key fields to extract
        key_fields = {
            'income_statement': [
                'Tax Rate For Calcs',
                'Net Income From Continuing Operation Net Minority Interest',
                'Reconciled Depreciation',
                'EBITDA',
                'EBIT',
                'Interest Expense',
                'Interest Income',
                'Net Income From Continuing And Discontinued Operation',
                'Diluted Average Shares',
                'Basic Average Shares',
                'Diluted EPS',
                'Basic EPS',
                'Net Income Common Stockholders',
                'Net Income',
                'Net Income Including Noncontrolling Interests',
                'Tax Provision',
                'Pretax Income',
                'Operating Income',
                'Operating Expense',
                'Depreciation And Amortization In Income Statement',
                'Amortization',
                'Depreciation Income Statement',
                'Selling General And Administration',
                'Selling And Marketing Expense',
                'General And Administrative Expense',
                'Gross Profit',
                'Cost Of Revenue',
                'Total Revenue',
                'Operating Revenue'
            ],
            'balance_sheet': [
                'Share Issued',
                'Net Debt',
                'Total Debt',
                'Tangible Book Value',
                'Working Capital',
                'Net Tangible Assets',
                'Capital Lease Obligations',
                'Common Stock Equity',
                'Stockholders Equity',
                'Other Equity Interest',
                'Retained Earnings',
                'Total Liabilities Net Minority Interest',
                'Other Non Current Liabilities',
                'Non Current Deferred Liabilities',
                'Long Term Debt And Capital Lease Obligation',
                'Long Term Debt',
                'Long Term Provisions',
                'Current Liabilities',
                'Current Debt And Capital Lease Obligation',
                'Current Debt',
                'Payables',
                'Dividends Payable',
                'Total Tax Payable',
                'Accounts Payable',
                'Total Assets',
                'Total Non Current Assets',
                'Other Non Current Assets',
                'Goodwill And Other Intangible Assets',
                'Other Intangible Assets',
                'Available For Sale Securities',
                'Trading Securities',
                'Goodwill',
                'Net PPE',
                'Current Assets',
                'Other Current Assets',
                'Inventory',
                'Other Receivables',
                'Taxes Receivable',
                'Accounts Receivable',
                'Gross Accounts Receivable',
                'Cash Cash Equivalents And Short Term Investments',
                'Other Short Term Investments',
                'Cash And Cash Equivalents',
                'Cash Equivalents'
            ],
            'cash_flow': [
                'Free Cash Flow',
                'Repayment Of Debt',
                'Issuance Of Debt',
                'Capital Expenditure',
                'Changes In Cash',
                'Financing Cash Flow',
                'Cash Dividends Paid',
                'Long Term Debt Payments',
                'Sale Of Investment',
                'Purchase Of Investment',
                'Net Business Purchase And Sale',
                'Sale Of Business',
                'Purchase Of Business',
                'Net PPE Purchase And Sale',
                'Capital Expenditure Reported',
                'Operating Cash Flow',
                'Change In Working Capital',
                'Change In Other Current Assets',
                'Change In Payable',
                'Change In Receivables',
                'Depreciation And Amortization',
                'Net Income From Continuing Operations',
           ],
            'info': [
                'website',
                'industry',
                'longBusinessSummary',
                'fullTimeEmployees',
                'previousClose',
                'open',
                'dayLow',
                'dayHigh',
                'dividendRate',
                'dividendYield',
                'payoutRatio', 
                'beta',
                'volume',
                'marketCap',
                'fiftyTwoWeekLow',
                'fiftyTwoWeekHigh',
                'fiftyDayAverage',
                'twoHundredDayAverage',
                'currency',
                'sharesOutstanding',
                'heldPercentInsiders',
                'heldPercentInstitutions',
                'bookValue',
                'priceToBook',
                'trailingEps',
                'forwardEps',
                'lastSplitFactor',
                'lastSplitDate',
                'lastDividendDate',
                'quoteType',
                'currentPrice',
                'recommendationKey',
                'totalCash',
                'totalDebt',
                'quickRatio',
                'currentRatio',
                'debtToEquity',
                'returnOnAssets',
                'returnOnEquity',
                'grossProfits',
                'earningsGrowth',
                'revenueGrowth',
                'grossMargins',
                'ebitdaMargins',
                'operatingMargins',
                'financialCurrency',
                'shortName',
                'regularMarketPrice',
                'fullExchangeName',
                'epsCurrentYear',
                'priceEpsCurrentYear',
                'fiftyDayAverageChange',]
        }

        # Convert each DataFrame to dict and handle special types
        result = {}
        for key, value in data.items():
            if isinstance(value, pd.DataFrame) and key in key_fields:
                # Convert DataFrame to dict and filter only desired fields
                df_dict = value.to_dict()
                filtered_data = {
                    str(k): {
                        str(inner_k): serialize_value(inner_v)
                        for inner_k, inner_v in v.items()
                        if inner_k in key_fields[key]
                    }
                    for k, v in df_dict.items()
                }
                result[key] = filtered_data
            elif isinstance(value, dict) and key in key_fields:
                # Handle info dict with filtering
                result[key] = {
                    k: serialize_value(v, key=k)
                    for k, v in value.items()
                    if k in key_fields[key]  # Only include fields that are in key_fields
                }
            else:
                result[key] = value
        
        # Apply currency conversion if needed
        if needs_conversion and exchange_rate:
            print(f"Converting financial data for {symbol} from USD to INR using rate: {exchange_rate}", file=sys.stderr)
            result = convert_financial_data(result, exchange_rate)
            # Add conversion metadata
            result['currency_conversion'] = {
                'applied': True,
                'from_currency': 'USD',
                'to_currency': 'INR',
                'exchange_rate': exchange_rate,
                'conversion_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            result['currency_conversion'] = {
                'applied': False,
                'reason': 'No conversion needed' if not needs_conversion else f'Exchange rate not available'
            }
        
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

def get_company_quarterly_financials(symbol):
    """
    Extract quarterly income statement data for the latest 4 quarters with specific fields
    
    Args:
        symbol (str): Stock symbol (e.g., 'AAPL', 'INFY.NS')
    
    Returns:
        str: JSON string containing quarterly financial data
    """
    try:
        # Check if currency conversion is needed
        needs_conversion = should_convert_currency(symbol)
        exchange_rate = None
        
        if needs_conversion:
            exchange_rate = get_usd_to_inr_rate()
            if not exchange_rate:
                print(f"Warning: Could not fetch exchange rate for {symbol}. Data will remain in USD.", file=sys.stderr)
        
        # Fetch company data
        company = yf.Ticker(symbol)
        
        # Get quarterly income statement data
        quarterly_income = company.quarterly_income_stmt
        
        if quarterly_income.empty:
            return json.dumps({"error": "No quarterly income statement data available"})
        
        # Define the specific fields to extract
        target_fields = [
            'Total Revenue',
            'Cost Of Revenue', 
            'Gross Profit',
            'Selling General And Administration',
            'Depreciation And Amortization In Income Statement',
            'Operating Expense',
            'Other Operating Expense',
            'Operating Income',
            'Pretax Income',
            'Tax Provision',
            'Net Income Continuous Operations',
            'Net Income Including Noncontrolling Interests',
            'Net Income Common Stockholders',
            'Basic Average Shares',
            'Basic EPS',
            'Net Income From Continuing And Discontinued Operation',
            'Interest Expense',
            'Net Interest Income',
            'EBIT',
            'EBITDA',
            'Reconciled Cost Of Revenue',
            'Reconciled Depreciation',
            'Net Income From Continuing Operation Net Minority Interest',
            'Total Unusual Items Excluding Goodwill',
            'Normalized EBITDA'
        ]
        
        # Get the latest 4 quarters (columns are sorted by date, latest first)
        latest_quarters = quarterly_income.columns[:4] if len(quarterly_income.columns) >= 4 else quarterly_income.columns
        
        # Filter data for target fields and latest quarters
        filtered_data = {}
        
        for quarter in latest_quarters:
            quarter_data = {}
            for field in target_fields:
                # Check if field exists in the data (case-insensitive and flexible matching)
                matching_field = None
                for available_field in quarterly_income.index:
                    if field.lower().replace(' ', '').replace('_', '') == available_field.lower().replace(' ', '').replace('_', ''):
                        matching_field = available_field
                        break
                
                if matching_field is not None:
                    value = quarterly_income.loc[matching_field, quarter]
                    quarter_data[field] = serialize_value(value)
                else:
                    quarter_data[field] = None
            
            # Convert quarter timestamp to string
            quarter_str = quarter.strftime('%Y-%m-%d') if hasattr(quarter, 'strftime') else str(quarter)
            filtered_data[quarter_str] = quarter_data
        
        # Prepare result with metadata
        result = {
            'symbol': symbol,
            'data_type': 'quarterly_income_statement',
            'quarters_count': len(latest_quarters),
            'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'quarterly_data': filtered_data
        }
        
        # Apply currency conversion if needed
        if needs_conversion and exchange_rate:
            print(f"Converting quarterly financial data for {symbol} from USD to INR using rate: {exchange_rate}", file=sys.stderr)
            result = convert_financial_data(result, exchange_rate)
            # Add conversion metadata
            result['currency_conversion'] = {
                'applied': True,
                'from_currency': 'USD',
                'to_currency': 'INR',
                'exchange_rate': exchange_rate,
                'conversion_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            result['currency_conversion'] = {
                'applied': False,
                'reason': 'No conversion needed' if not needs_conversion else f'Exchange rate not available'
            }
        
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({"error": str(e)})

def get_latest_stock_indices():
    """
    Fetch latest quotes for major stock indices (NSE, BSE, NYSE, NASDAQ) and extract key fields.
    Returns a list of dicts, one per index.
    """
    indices = {
        "NIFTY 50": "^NSEI",
        "NIFTY BANK": "^NSEBANK",
        "NIFTY IT": "^CNXIT",
        "NIFTY MIDCAP 50": "^NSEMDCP50",
        "BSE SENSEX": "^BSESN",
        "NYSE": "^NYA",
        "NASDAQ": "^IXIC"
    }
    fields = [
        'shortName',
        'fullExchangeName',
        'regularMarketPrice',
        'regularMarketPreviousClose',
        'regularMarketOpen',
        'regularMarketDayLow',
        'regularMarketDayHigh',
        'fiftyTwoWeekLow',
        'fiftyTwoWeekHigh',
        'fiftyDayAverage',
        'twoHundredDayAverage',
    ]
    results = []
    for name, symbol in indices.items():
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            index_data = {'name': name, 'symbol': symbol}
            for field in fields:
                index_data[field] = info.get(field)
            results.append(index_data)
        except Exception as e:
            results.append({'name': name, 'symbol': symbol, 'error': str(e)})
    return results

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--get-latest-indices":
            indices = get_latest_stock_indices()
            print(json.dumps(indices, ensure_ascii=False))
        else:
            symbol = sys.argv[1]
            command = sys.argv[2] if len(sys.argv) > 2 else "financials"
            if command == "price":
                print(get_company_latestPrice(symbol))
            elif command == "quarterly":
                print(get_company_quarterly_financials(symbol))
            else:
                print(get_company_financials(symbol))
