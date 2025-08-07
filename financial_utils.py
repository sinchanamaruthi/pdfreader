import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import re
from typing import Dict, List, Tuple, Optional

class FinancialAnalyzer:
    """Utility class for financial calculations and analysis"""
    
    @staticmethod
    def extract_financial_metrics(text: str) -> Dict[str, float]:
        """Extract common financial metrics from text using regex"""
        metrics = {}
        
        # Revenue patterns
        revenue_patterns = [
            r'revenue[:\s]+\$?([0-9,]+\.?[0-9]*)\s*(million|billion|M|B)?',
            r'sales[:\s]+\$?([0-9,]+\.?[0-9]*)\s*(million|billion|M|B)?',
            r'total revenue[:\s]+\$?([0-9,]+\.?[0-9]*)\s*(million|billion|M|B)?'
        ]
        
        # EPS patterns
        eps_patterns = [
            r'earnings per share[:\s]+\$?([0-9]+\.?[0-9]*)',
            r'EPS[:\s]+\$?([0-9]+\.?[0-9]*)',
            r'diluted EPS[:\s]+\$?([0-9]+\.?[0-9]*)'
        ]
        
        # Net income patterns
        income_patterns = [
            r'net income[:\s]+\$?([0-9,]+\.?[0-9]*)\s*(million|billion|M|B)?',
            r'net earnings[:\s]+\$?([0-9,]+\.?[0-9]*)\s*(million|billion|M|B)?'
        ]
        
        def extract_value(pattern_list: List[str], text: str, metric_name: str):
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    try:
                        value = float(matches[0][0].replace(',', ''))
                        unit = matches[0][1] if len(matches[0]) > 1 else ''
                        
                        # Convert to actual value
                        if unit.lower() in ['billion', 'b']:
                            value *= 1000000000
                        elif unit.lower() in ['million', 'm']:
                            value *= 1000000
                        
                        metrics[metric_name] = value
                        break
                    except (ValueError, IndexError):
                        continue
        
        extract_value(revenue_patterns, text, 'revenue')
        extract_value(eps_patterns, text, 'eps')
        extract_value(income_patterns, text, 'net_income')
        
        return metrics
    
    @staticmethod
    def calculate_financial_ratios(metrics: Dict[str, float]) -> Dict[str, float]:
        """Calculate financial ratios from extracted metrics"""
        ratios = {}
        
        # Price to Earnings ratio (if we have stock price)
        if 'stock_price' in metrics and 'eps' in metrics and metrics['eps'] > 0:
            ratios['pe_ratio'] = metrics['stock_price'] / metrics['eps']
        
        # Revenue growth (if we have current and previous revenue)
        if 'current_revenue' in metrics and 'previous_revenue' in metrics:
            if metrics['previous_revenue'] > 0:
                ratios['revenue_growth'] = ((metrics['current_revenue'] - metrics['previous_revenue']) 
                                          / metrics['previous_revenue']) * 100
        
        # Profit margin
        if 'net_income' in metrics and 'revenue' in metrics and metrics['revenue'] > 0:
            ratios['profit_margin'] = (metrics['net_income'] / metrics['revenue']) * 100
        
        return ratios
    
    @staticmethod
    def get_stock_analysis(symbol: str) -> Dict[str, any]:
        """Get comprehensive stock analysis using yfinance"""
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            history = stock.history(period="1y")
            
            if history.empty:
                return {"error": "No data found for symbol"}
            
            # Calculate technical indicators
            current_price = history['Close'].iloc[-1]
            ma_20 = history['Close'].rolling(window=20).mean().iloc[-1]
            ma_50 = history['Close'].rolling(window=50).mean().iloc[-1]
            
            # Price changes
            price_1d = (current_price - history['Close'].iloc[-2]) / history['Close'].iloc[-2] * 100
            price_1w = (current_price - history['Close'].iloc[-5]) / history['Close'].iloc[-5] * 100
            price_1m = (current_price - history['Close'].iloc[-21]) / history['Close'].iloc[-21] * 100
            
            # Volatility (standard deviation of returns)
            returns = history['Close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252) * 100  # Annualized volatility
            
            analysis = {
                "symbol": symbol,
                "company_name": info.get('longName', 'N/A'),
                "sector": info.get('sector', 'N/A'),
                "current_price": current_price,
                "market_cap": info.get('marketCap', 0),
                "pe_ratio": info.get('trailingPE', 0),
                "price_changes": {
                    "1_day": price_1d,
                    "1_week": price_1w,
                    "1_month": price_1m
                },
                "technical_indicators": {
                    "ma_20": ma_20,
                    "ma_50": ma_50,
                    "volatility": volatility
                },
                "fundamentals": {
                    "eps": info.get('trailingEps', 0),
                    "revenue": info.get('totalRevenue', 0),
                    "profit_margin": info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0,
                    "debt_to_equity": info.get('debtToEquity', 0)
                }
            }
            
            return analysis
            
        except Exception as e:
            return {"error": f"Error fetching stock data: {str(e)}"}
    
    @staticmethod
    def compare_stocks(symbols: List[str]) -> pd.DataFrame:
        """Compare multiple stocks"""
        comparison_data = []
        
        for symbol in symbols:
            analysis = FinancialAnalyzer.get_stock_analysis(symbol)
            if "error" not in analysis:
                comparison_data.append({
                    "Symbol": symbol,
                    "Company": analysis["company_name"],
                    "Price": analysis["current_price"],
                    "Market Cap": analysis["market_cap"],
                    "P/E Ratio": analysis["pe_ratio"],
                    "1D Change %": analysis["price_changes"]["1_day"],
                    "1M Change %": analysis["price_changes"]["1_month"],
                    "Volatility %": analysis["technical_indicators"]["volatility"]
                })
        
        return pd.DataFrame(comparison_data)
    
    @staticmethod
    def identify_document_type(text: str) -> str:
        """Identify the type of financial document"""
        text_lower = text.lower()
        
        if any(term in text_lower for term in ['10-k', 'annual report', 'form 10-k']):
            return "Annual Report (10-K)"
        elif any(term in text_lower for term in ['10-q', 'quarterly report', 'form 10-q']):
            return "Quarterly Report (10-Q)"
        elif any(term in text_lower for term in ['earnings call', 'earnings transcript', 'quarterly earnings']):
            return "Earnings Call Transcript"
        elif any(term in text_lower for term in ['research report', 'analyst report', 'investment research']):
            return "Research Report"
        elif any(term in text_lower for term in ['prospectus', 'offering memorandum']):
            return "Investment Prospectus"
        elif any(term in text_lower for term in ['balance sheet', 'income statement', 'cash flow']):
            return "Financial Statement"
        else:
            return "Financial Document"
    
    @staticmethod
    def extract_key_dates(text: str) -> List[str]:
        """Extract important dates from financial documents"""
        # Date patterns
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
            r'\b\d{4}-\d{1,2}-\d{1,2}\b',  # YYYY-MM-DD
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        
        return list(set(dates))  # Remove duplicates
    
    @staticmethod
    def generate_investment_summary(analysis: Dict) -> str:
        """Generate a concise investment summary"""
        if "error" in analysis:
            return f"Unable to generate summary: {analysis['error']}"
        
        summary = f"""
        📊 **Investment Summary for {analysis['symbol']}**
        
        **Company**: {analysis['company_name']}
        **Sector**: {analysis['sector']}
        **Current Price**: ${analysis['current_price']:.2f}
        
        **Performance**:
        - 1 Day: {analysis['price_changes']['1_day']:+.2f}%
        - 1 Week: {analysis['price_changes']['1_week']:+.2f}%
        - 1 Month: {analysis['price_changes']['1_month']:+.2f}%
        
        **Key Metrics**:
        - P/E Ratio: {analysis['pe_ratio']:.2f}
        - Market Cap: ${analysis['market_cap']:,.0f}
        - Profit Margin: {analysis['fundamentals']['profit_margin']:.2f}%
        - Volatility: {analysis['technical_indicators']['volatility']:.2f}%
        
        **Technical Analysis**:
        - 20-day MA: ${analysis['technical_indicators']['ma_20']:.2f}
        - 50-day MA: ${analysis['technical_indicators']['ma_50']:.2f}
        """
        
        return summary