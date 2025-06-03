# AI-Powered Cash Flow Dashboard with XAI

A no-cost, mock-data implementation of an AI-powered predictive cash flow dashboard with explainable forecast insights (XAI).

## Features

- Real-time cash flow forecasting
- Explainable AI insights for predictions
- Interactive data visualization
- Pattern recognition and anomaly detection
- Responsive web interface

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the development server:
```bash
uvicorn app.main:app --reload
```

4. Open `http://localhost:8000` in your browser

## Project Structure

```
.
├── app/
│   ├── main.py
│   ├── models/
│   ├── services/
│   └── utils/
├── static/
│   ├── css/
│   ├── js/
│   └── data/
├── templates/
├── tests/
├── docs/
│   └── timeline.md
├── requirements.txt
└── README.md
```

## Development Timeline

See [docs/timeline.md](docs/timeline.md) for a detailed week-by-week implementation plan and progress tracking.

## License

MIT License 