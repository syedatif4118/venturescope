 🎯 VentureScope

**AI-Powered VC Deal Flow Intelligence Platform**



VentureScope is an autonomous multi-agent AI system that analyzes startup pitch decks and generates structured investment memos in minutes — simulating how real venture capital analysts evaluate opportunities.

Instead of manually reviewing pitch decks, market reports, and financial assumptions, VentureScope orchestrates specialized AI agents to extract insights, assess risk, and produce investment-ready analysis.


## 🚀 Features

### Multi-Agent Analysis Pipeline
- **📄 Document Ingestion Agent**: Extracts structured data from pitch decks (PDF, PPTX)
- **📊 Market Analysis Agent**: Researches TAM, competitors, market trends
- **👥 Team Assessment Agent**: Analyzes founder backgrounds and team composition
- **💰 Financial Modeling Agent**: Validates projections and unit economics
- **⚠️ Risk Flagging Agent**: Identifies red flags and potential concerns
- **📝 Investment Memo Generator**: Synthesizes analysis into actionable memos

### Scoring System
- **0-100 Investment Score** based on:
  - Team Quality (25%)
  - Market Opportunity (25%)
  - Traction & Growth (25%)
  - Financial Health (25%)

### Outputs
- Comprehensive investment memos (Markdown/PDF)
- Competitive landscape visualization
- Risk dashboard
- Financial projections analysis

## 🏗️ Architecture

```
VentureScope/
├── agents/              # Individual agent implementations
│   ├── document_ingestion.py
│   ├── market_analysis.py
│   ├── team_assessment.py
│   ├── financial_modeling.py
│   ├── risk_flagging.py
│   └── memo_generator.py
├── core/                # Orchestration & LLM clients
│   ├── orchestrator.py  # LangGraph workflow
│   └── llm_client.py    # HuggingFace Inference API
├── skills/              # Upskill-generated agent skills
├── utils/               # Helper functions
│   ├── pdf_extractor.py
│   └── web_scraper.py
├── data/                # Sample data & research
└── outputs/             # Generated memos
```

## 🛠️ Tech Stack

- **AI Orchestration**: LangGraph, LangChain
- **LLM Provider**: HuggingFace Inference API (Llama 3.1 70B)
- **Agent Skills**: HuggingFace Upskill
- **Vector Store**: FAISS + ChromaDB
- **Document Processing**: PyMuPDF, PDFPlumber
- **Web Scraping**: BeautifulSoup, Playwright
- **UI**: Streamlit
- **Visualization**: Plotly, Matplotlib

## 📦 Installation

### Prerequisites
- Python 3.9+
- HuggingFace API key (free tier available)

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/venturescope.git
cd venturescope

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Mac/Linux
# venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your HUGGINGFACE_API_KEY

# Run the app
streamlit run app.py
```

## 🎯 Usage

### Web Interface
1. Launch Streamlit app: `streamlit run app.py`
2. Upload a pitch deck (PDF)
3. Click "Analyze"
4. Review the generated investment memo

### Python API

```python
from core.orchestrator import VentureScopeOrchestrator

orchestrator = VentureScopeOrchestrator()
result = orchestrator.analyze_pitch_deck(
    pitch_deck_path="data/sample_pitchdecks/startup_x.pdf"
)

print(f"Investment Score: {result['score']}/100")
print(f"Recommendation: {result['recommendation']}")
print(f"\nMemo:\n{result['memo']}")
```

## 📊 Sample Output

```markdown
# Investment Memo: TechStartup Inc.

## Executive Summary
Investment Score: 78/100 | Recommendation: **STRONG CONSIDER**

## Key Highlights
✅ Strong founding team with 2 exits
✅ $5B TAM in growing market (25% CAGR)
✅ 200% YoY revenue growth
⚠️ Competitive landscape is crowded

## Detailed Analysis
### Market (22/25)
- TAM: $5B, SAM: $500M, SOM: $50M
- Key trends: AI adoption, cloud migration
- Competitors: CompanyA, CompanyB

### Team (23/25)
- CEO: Jane Doe (ex-Google, sold previous startup)
- CTO: John Smith (10+ years ML experience)
- Advisors: 3 industry veterans

[...full memo...]
```

## 🧪 Testing

Sample pitch decks from Y Combinator companies are included in `data/sample_pitchdecks/` for testing.

```bash
pytest tests/
```

## 🎓 Educational Value

This project demonstrates:
- ✅ **Autonomous AI Agents** with LangGraph
- ✅ **Upskill Framework** for agent skill generation
- ✅ **Production-grade LLM Integration** (HuggingFace)
- ✅ **Multi-agent Orchestration** patterns
- ✅ **Document Intelligence** (OCR, extraction, parsing)
- ✅ **RAG Architecture** for market research
- ✅ **Structured Output Generation** with Pydantic

## 📈 Portfolio Impact

Built to showcase:
1. **Financial domain expertise** (VC/investment analysis)
2. **Cutting-edge AI skills** (LangGraph, Upskill)
3. **End-to-end product thinking** (problem → solution → UI)
4. **Production-quality code** (testing, documentation, architecture)

## 🚀 Future Enhancements

- [ ] Multi-document analysis (pitch deck + financials + news)
- [ ] Real-time company monitoring
- [ ] Portfolio management dashboard
- [ ] Integration with Crunchbase/PitchBook APIs
- [ ] Comparative analysis across sectors
- [ ] Email digests for new deals




## 👤 Author

**Syed Atif**
- AI/ML Engineer specializing in LLM-based agent systems
- LinkedIn: https://www.linkedin.com/in/syedatif001/


## 🙏 Acknowledgments

- HuggingFace for Inference API and Upskill framework
- LangChain team for LangGraph

---

**Built with ❤️ for the future of VC intelligence**
