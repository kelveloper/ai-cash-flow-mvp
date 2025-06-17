# AI-Powered Cash Flow Dashboard

A modern cash flow dashboard with AI-powered insights, built with FastAPI and React.

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **Database**: SQLite (via SQLAlchemy ORM)
- **Data Processing**: Pandas, NumPy
- **API Documentation**: Swagger UI (OpenAPI)
- **Testing**: Pytest

### Frontend
- **Framework**: React 18
- **Styling**: Tailwind CSS
- **Charts**: Chart.js
- **State Management**: React Query
- **UI Components**: Headless UI

### Development Tools
- **Package Manager**: pip (Python), npm (Node.js)
- **Version Control**: Git
- **Code Quality**: 
  - Python: Black, Flake8, isort
  - JavaScript: ESLint, Prettier
- **Environment Management**: 
  - Python: venv
  - Node: nvm

## Project Structure
```
ai-cash-flow-mvp/
├── app/                    # Backend application
│   ├── main.py            # FastAPI application
│   ├── models/            # Pydantic models
│   ├── services/          # Business logic
│   └── utils/             # Utility functions
├── data/                  # Data files
│   ├── transactions.csv   # Simulated transaction data
│   ├── forecast.csv       # Simulated forecast data
│   └── insights.csv       # Simulated AI insights
├── scripts/               # Utility scripts
│   └── generate_realistic_data.py  # Advanced data simulation script
├── static/               # Static files
│   ├── css/
│   └── js/
├── templates/            # HTML templates
├── tests/               # Test files
└── docs/               # Documentation
```

## API Endpoints

### Transaction Management
- `GET /api/transactions` - List transactions with filtering
- `POST /api/transactions` - Create new transaction
- `GET /api/transactions/{id}` - Get transaction details
- `PUT /api/transactions/{id}` - Update transaction
- `DELETE /api/transactions/{id}` - Delete transaction

### Account Summary
- `GET /api/account-summary` - Get account overview
- `GET /api/categories` - List transaction categories
- `GET /api/forecast` - Get cash flow forecast
- `GET /api/insights` - Get AI-powered insights

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-cash-flow-mvp.git
cd ai-cash-flow-mvp
```

2. Set up Python environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Generate realistic simulated data:
```bash
python scripts/generate_realistic_data.py
```
_Note: This script generates highly realistic, business-like data for development and testing purposes._

4. Start the backend server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development Workflow

1. Create a new branch for features:
```bash
git checkout -b feature/your-feature-name
```

2. Run tests:
```bash
pytest
```

3. Format code:
```bash
# Python
black .
isort .

# JavaScript
npm run format
```

4. Submit a pull request

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 