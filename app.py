import streamlit as st
import fitz  # PyMuPDF
import base64
import openai
import tempfile
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import yfinance as yf
from typing import List, Dict, Any
import re
import json
from financial_utils import FinancialAnalyzer

# Configure page
st.set_page_config(
    page_title="Financial Stock Assistant", 
    page_icon="📈", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'pdf_content' not in st.session_state:
    st.session_state.pdf_content = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'processed_pdf' not in st.session_state:
    st.session_state.processed_pdf = False

class FinancialPDFAssistant:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        
    def extract_pdf_content(self, pdf_file) -> Dict[str, Any]:
        """Extract both text and images from PDF"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_file.read())
            tmp_path = tmp_file.name

        doc = fitz.open(tmp_path)
        
        # Extract text
        full_text = ""
        for page_num in range(len(doc)):
            page = doc[page_num]
            full_text += f"\n--- Page {page_num + 1} ---\n"
            full_text += page.get_text()
        
        # Extract images as base64
        images = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap(dpi=150)
            img_bytes = pix.tobytes("png")
            b64_img = base64.b64encode(img_bytes).decode("utf-8")
            images.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{b64_img}",
                    "detail": "high"
                }
            })
        
        doc.close()
        os.unlink(tmp_path)
        
        return {
            "text": full_text,
            "images": images,
            "page_count": len(doc)
        }
    
    def analyze_financial_document(self, content: Dict[str, Any]) -> str:
        """Send document to GPT for initial analysis"""
        
        # Use FinancialAnalyzer to extract metrics and identify document type
        extracted_metrics = FinancialAnalyzer.extract_financial_metrics(content['text'])
        doc_type = FinancialAnalyzer.identify_document_type(content['text'])
        key_dates = FinancialAnalyzer.extract_key_dates(content['text'])
        
        system_prompt = f"""You are an expert financial analyst assistant specializing in stock market analysis, 
        financial reports, and investment research. You can read and analyze financial documents including:
        
        - Annual reports (10-K)
        - Quarterly reports (10-Q) 
        - Earnings reports
        - Stock research reports
        - Financial statements
        - Investment prospectuses
        - Market analysis documents
        
        Document Analysis Context:
        - Document Type: {doc_type}
        - Extracted Financial Metrics: {extracted_metrics}
        - Key Dates Found: {key_dates[:5]}  # Show first 5 dates
        
        When analyzing documents:
        1. Identify the type of financial document
        2. Extract key financial metrics, ratios, and data points
        3. Identify company names, stock symbols, and sectors mentioned
        4. Summarize key findings, trends, and insights
        5. Note any charts, graphs, or visual data in images
        6. Highlight important risk factors or opportunities
        7. Use the extracted metrics to provide quantitative analysis
        
        Provide clear, actionable insights that would be valuable for investment decisions."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {
                    "type": "text", 
                    "text": f"Please analyze this financial document. Here's the extracted text:\n\n{content['text'][:8000]}..."
                },
                *content['images'][:5]  # Limit to first 5 images to avoid token limits
            ]}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.1,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing document: {str(e)}"
    
    def answer_question(self, question: str, content: Dict[str, Any], context: str = "") -> str:
        """Answer specific questions about the document"""
        system_prompt = """You are a financial expert assistant. Use the provided document content and context 
        to answer questions accurately. Focus on:
        
        - Providing specific data points and numbers when available
        - Explaining financial concepts clearly
        - Giving actionable insights
        - Citing specific parts of the document when relevant
        - If asked about stock prices or market data not in the document, indicate you need current market data
        
        Be precise and professional in your responses."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""
            Document Context: {context}
            
            Document Text: {content['text'][:6000]}
            
            Question: {question}
            
            Please answer based on the document content provided.
            """}
        ]
        
        # Add images if the question might relate to charts/graphs
        if any(word in question.lower() for word in ['chart', 'graph', 'image', 'figure', 'visual', 'table']):
            messages[1]["content"] = [
                {"type": "text", "text": messages[1]["content"]},
                *content['images'][:3]
            ]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.1,
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error answering question: {str(e)}"

def get_stock_data(symbol: str, period: str = "1y"):
    """Fetch stock data using yfinance"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)
        info = stock.info
        return data, info
    except:
        return None, None

def main():
    st.title("📈 Financial Stock Assistant")
    st.markdown("Upload financial documents and get AI-powered analysis and insights!")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input("OpenAI API Key", type="password", help="Enter your OpenAI API key")
        
        if not api_key:
            st.warning("Please enter your OpenAI API key to continue")
            return
        
        st.header("📊 Quick Stock Lookup")
        stock_symbol = st.text_input("Stock Symbol (e.g., AAPL)")
        if stock_symbol:
            # Use enhanced stock analysis
            analysis = FinancialAnalyzer.get_stock_analysis(stock_symbol.upper())
            
            if "error" not in analysis:
                st.success(f"Found: {analysis['company_name']}")
                
                # Display key metrics in columns
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        label="Current Price",
                        value=f"${analysis['current_price']:.2f}",
                        delta=f"{analysis['price_changes']['1_day']:+.2f}%"
                    )
                with col2:
                    st.metric(
                        label="P/E Ratio",
                        value=f"{analysis['pe_ratio']:.2f}" if analysis['pe_ratio'] else "N/A"
                    )
                with col3:
                    st.metric(
                        label="Market Cap",
                        value=f"${analysis['market_cap']/1e9:.1f}B" if analysis['market_cap'] else "N/A"
                    )
                
                # Enhanced price chart with moving averages
                data, _ = get_stock_data(stock_symbol.upper())
                if data is not None:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=data.index, y=data['Close'],
                        mode='lines', name='Price',
                        line=dict(color='blue', width=2)
                    ))
                    
                    # Add moving averages
                    ma_20 = data['Close'].rolling(window=20).mean()
                    ma_50 = data['Close'].rolling(window=50).mean()
                    
                    fig.add_trace(go.Scatter(
                        x=data.index, y=ma_20,
                        mode='lines', name='MA 20',
                        line=dict(color='orange', width=1, dash='dash')
                    ))
                    fig.add_trace(go.Scatter(
                        x=data.index, y=ma_50,
                        mode='lines', name='MA 50',
                        line=dict(color='red', width=1, dash='dash')
                    ))
                    
                    fig.update_layout(
                        title=f"{stock_symbol} Stock Price with Moving Averages",
                        xaxis_title="Date",
                        yaxis_title="Price ($)",
                        height=300
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Investment summary
                with st.expander("📈 Investment Summary"):
                    summary = FinancialAnalyzer.generate_investment_summary(analysis)
                    st.markdown(summary)
            else:
                st.error(f"Error: {analysis['error']}")
    
    # Initialize assistant
    if api_key:
        assistant = FinancialPDFAssistant(api_key)
        
        # Main content area
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.header("📄 Document Upload")
            uploaded_file = st.file_uploader(
                "Upload Financial Document", 
                type=["pdf"],
                help="Upload annual reports, earnings reports, research documents, etc."
            )
            
            if uploaded_file:
                if st.button("🔍 Process Document", type="primary"):
                    with st.spinner("Processing document..."):
                        content = assistant.extract_pdf_content(uploaded_file)
                        st.session_state.pdf_content = content
                        
                        # Get initial analysis
                        analysis = assistant.analyze_financial_document(content)
                        st.session_state.document_analysis = analysis
                        st.session_state.processed_pdf = True
                        
                    st.success("✅ Document processed successfully!")
                    st.rerun()
        
        with col2:
            if st.session_state.processed_pdf and st.session_state.pdf_content:
                st.header("🤖 Document Analysis")
                
                # Show initial analysis
                with st.expander("📋 Initial Document Analysis", expanded=True):
                    st.write(st.session_state.document_analysis)
                
                # Q&A Section
                st.header("💬 Ask Questions")
                
                # Display chat history
                for i, (q, a) in enumerate(st.session_state.chat_history):
                    with st.chat_message("user"):
                        st.write(q)
                    with st.chat_message("assistant"):
                        st.write(a)
                
                # New question input
                question = st.chat_input("Ask a question about the document...")
                
                if question:
                    with st.chat_message("user"):
                        st.write(question)
                    
                    with st.chat_message("assistant"):
                        with st.spinner("Analyzing..."):
                            answer = assistant.answer_question(
                                question, 
                                st.session_state.pdf_content,
                                st.session_state.document_analysis
                            )
                            st.write(answer)
                            
                            # Add to chat history
                            st.session_state.chat_history.append((question, answer))
            else:
                st.info("👆 Please upload and process a financial document to start the analysis")
        
        # Document stats
        if st.session_state.pdf_content:
            st.header("📊 Document Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Pages", st.session_state.pdf_content['page_count'])
            with col2:
                st.metric("Text Length", f"{len(st.session_state.pdf_content['text']):,} chars")
            with col3:
                st.metric("Images", len(st.session_state.pdf_content['images']))
            with col4:
                st.metric("Questions Asked", len(st.session_state.chat_history))

if __name__ == "__main__":
    main()
