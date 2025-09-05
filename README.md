# Error Detection API

AI-powered error detection API for educational platforms using OpenAI GPT-4o Vision + GPT-4 text analysis.

## Quick Start

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.sample .env
# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Run Demo
```bash
python demo.py
```

### 3. Start API Server
```bash
# Using make
make run

# Or directly
python -m src.main
```
Server runs on http://localhost:8000

### 4. Run Evaluation
```bash
# Full ML evaluation (baseline vs improved)
make eval

# Or directly
python -m eval.run_eval
```

## API Usage

### Test Endpoint
```bash
curl -X POST "http://localhost:8000/detect-error" \
  -H "x-api-key: default-key" \
  -H "Content-Type: application/json" \
  -d '{
    "question_url": "https://example.com/question.png",
    "solution_url": "https://example.com/solution.png",
    "bounding_box": {"minX": 100, "maxX": 300, "minY": 50, "maxY": 100}
  }'
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Commands Reference

### Make Commands
```bash
make setup        # Install dependencies
make run          # Start API server
make eval         # Run ML evaluation
make test         # Run unit tests
make test-verbose # Run tests with verbose output
```

### Python Commands
```bash
# Core functionality
python demo.py                    # Simple demo
python -m src.main                # Start API server
python -m eval.run_eval           # ML evaluation harness

# Development
pytest                            # Unit tests
pytest -v -s                      # Verbose unit tests
python -c "import src; print('OK')" # Import test
```

## Project Structure

```
src/
├── main.py          # API server entry point
├── api.py           # FastAPI endpoints
├── detector.py      # Main error detection logic
├── detector_variants.py # Baseline vs improved variants
├── ocr.py           # OpenAI Vision API integration
├── llm.py           # GPT-4 error analysis
├── models.py        # Request/response models
├── storage.py       # File-based persistence
├── logging.py       # Structured logging
└── config.py        # Configuration

eval/
├── run_eval.py      # ML evaluation harness
├── dataset.py       # Test data management
└── metrics.py       # Performance metrics

data/
├── test_cases.json  # Labeled test dataset
└── requests/        # Audit logs
```

## Documentation

- [Architecture.md](Architecture.md) - System design and scaling
- [Report.md](Report.md) - Implementation details and results
- `.env.sample` - Environment configuration template

## Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for API calls

## Performance Targets

- P95 latency ≤ 10s
- 5 concurrent requests
- ~$0.02 cost per request
- 80%+ accuracy on mathematical error detection