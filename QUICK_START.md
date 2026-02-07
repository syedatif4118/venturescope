"# VentureScope - Quick Start Guide

## Installation

```bash
cd /app/venturescope

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your HUGGINGFACE_API_KEY
```

## Running the App

```bash
# Start Streamlit app
streamlit run app.py

# App will open at http://localhost:8501
```

## Quick Test

```python
from core.orchestrator import VentureScopeOrchestrator

orchestrator = VentureScopeOrchestrator()
result = orchestrator.analyze_pitch_deck(\"data/sample_pitchdecks/sample.pdf\")

print(f\"Score: {result['final_score']}/100\")
print(f\"Recommendation: {result['recommendation']}\")
```

## Project Structure

```
venturescope/
├── app.py                 # Streamlit UI
├── agents/                # Individual agent implementations
│   ├── document_ingestion.py
│   ├── market_analysis.py
│   ├── team_assessment.py
│   ├── financial_modeling.py
│   ├── risk_flagging.py
│   └── memo_generator.py
├── core/                  # Orchestration & LLM clients
│   ├── orchestrator.py    # Main workflow
│   └── llm_client.py      # HuggingFace Inference API
├── utils/                 # Helper functions
│   ├── pdf_extractor.py
│   └── web_scraper.py
└── data/                  # Sample data
```

## Features

✅ Multi-agent analysis pipeline
✅ HuggingFace Inference API (Llama 3.1 70B)
✅ PDF pitch deck extraction
✅ Market research & competitive analysis
✅ Team assessment with web research
✅ Financial validation
✅ Risk identification
✅ Investment memo generation
✅ Beautiful Streamlit UI

## Tech Stack

- **AI**: LangGraph, LangChain, HuggingFace
- **LLM**: Llama 3.1 70B Instruct
- **Document**: PyMuPDF
- **Web**: BeautifulSoup4, Requests
- **UI**: Streamlit, Plotly

## Next Steps

1. Upload a pitch deck PDF
2. Click \"Analyze\"
3. Review the investment memo
4. Download results

## Troubleshooting

**Issue:** \"API key not found\"
- Solution: Add `HUGGINGFACE_API_KEY` to `.env` file

**Issue:** \"Module not found\"
- Solution: Run `pip install -r requirements.txt`

**Issue:** \"PDF extraction failed\"
- Solution: Ensure PDF is not password-protected

## Credits

Built by **Syed Atif** using cutting-edge AI orchestration.
"