# 📈 Financial Stock Assistant

A comprehensive AI-powered financial document analysis tool that can read PDFs (including text and images) and provide intelligent insights about financial reports, earnings statements, and stock research documents.

## 🚀 Features

- **PDF Processing**: Extract and analyze both text and images from financial documents
- **AI-Powered Analysis**: Uses GPT-4o to provide intelligent insights and answer questions
- **Financial Focus**: Specialized prompts for financial document analysis
- **Interactive Chat**: Ask questions about uploaded documents and get detailed answers
- **Stock Data Integration**: Quick stock lookup with real-time price data and charts
- **Multi-Modal**: Analyzes charts, graphs, tables, and text content
- **Session Memory**: Maintains conversation history for context-aware responses

## 📋 Supported Document Types

- Annual Reports (10-K)
- Quarterly Reports (10-Q)
- Earnings Reports
- Stock Research Reports
- Financial Statements
- Investment Prospectuses
- Market Analysis Documents
- Any PDF with financial content

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd financial-stock-assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to the `.env` file
   - Or enter it directly in the app's sidebar

## 🎯 Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Enter your OpenAI API key in the sidebar

3. Upload a financial PDF document

4. Click "Process Document" to analyze the content

5. Ask questions about the document in the chat interface

6. Use the stock lookup feature for quick market data

## 💡 Example Questions

- "What are the key financial metrics mentioned in this report?"
- "What is the revenue growth trend shown in the charts?"
- "What are the main risk factors identified?"
- "Summarize the earnings per share data"
- "What does the cash flow statement indicate?"
- "Explain the debt-to-equity ratio trends"

## 🔧 Technical Details

### PDF Processing
- Uses PyMuPDF for text and image extraction
- High-resolution image capture (150 DPI)
- Page-by-page text extraction with clear delimiters

### AI Integration
- OpenAI GPT-4o for document analysis
- Specialized financial analysis prompts
- Context-aware question answering
- Image analysis for charts and graphs

### Stock Data
- Yahoo Finance integration for real-time stock data
- Interactive price charts using Plotly
- Key metrics display

## 📊 Architecture

```
Financial Stock Assistant
├── PDF Upload & Processing
│   ├── Text Extraction
│   └── Image Extraction (Base64)
├── AI Analysis Engine
│   ├── Initial Document Analysis
│   └── Question-Answer System
├── Stock Data Integration
│   └── Real-time Price Data
└── Streamlit UI
    ├── Document Upload
    ├── Chat Interface
    └── Stock Lookup
```

## 🔐 Security

- API keys are handled securely
- Temporary files are automatically cleaned up
- No document content is stored permanently

## 🚧 Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for stock data

## 📈 Future Enhancements

- Support for Excel and CSV files
- Advanced financial ratio calculations
- Portfolio analysis features
- Integration with more financial data sources
- Export analysis reports
- Batch document processing

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.