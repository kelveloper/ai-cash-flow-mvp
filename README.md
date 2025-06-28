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
- **Build Tool**: Vite (Lightning Fast HMR)
- **Styling**: Tailwind CSS
- **Charts**: Chart.js with react-chartjs-2
- **State Management**: React Query (@tanstack/react-query)
- **UI Components**: Headless UI
- **Routing**: React Router Dom
- **HTTP Client**: Axios

### Development Tools
- **Package Manager**: npm (Node.js)
- **Version Control**: Git
- **Code Quality**: ESLint for React
- **Environment Management**: Python venv

## Project Structure
```
ai-cash-flow-mvp/
├── app/                           # Backend application
│   ├── main.py                   # FastAPI application with dual routing
│   ├── models/                   # Pydantic models
│   ├── services/                 # Business logic
│   ├── templates/                # HTML templates (legacy fallback)
│   └── utils/                    # Utility functions
├── frontend/                     # React application
│   ├── src/
│   │   ├── components/           # React components
│   │   │   ├── ai/              # AI-related components
│   │   │   ├── layout/          # Layout components
│   │   │   ├── transactions/    # Transaction components
│   │   │   └── ui/              # Reusable UI components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── pages/               # Page components
│   │   ├── services/            # API services
│   │   └── utils/               # Frontend utilities
│   ├── index.html               # React app entry point
│   └── vite.config.js           # Vite configuration
├── dist/                        # Built React app (production)
├── data/                        # Data files
├── scripts/                     # Utility scripts
├── tests/                       # Test files
└── docs/                        # Documentation
```

## Architecture Highlights

### 🔄 Dual Routing System
The app uses a smart routing strategy that serves React components in production while maintaining template fallbacks:
- **React Routes**: `/`, `/transactions`, `/ai-categorization` → Serve built React app
- **Legacy Routes**: `/checking-transactions`, `/credit-transactions` → HTML templates
- **API Routes**: `/api/*` → FastAPI backend

### 🚀 Modern React Features
- **Unified Transactions Page**: Single page with checking/credit account toggle
- **Integrated AI Chatbot**: Floating AI assistant accessible from transactions
- **Component Architecture**: Reusable, composable React components
- **State Management**: React Query for server state + React hooks for UI state
- **Real-time Updates**: Optimistic updates and automatic cache invalidation

### 🤖 AI Integration
- **Dex AI Assistant**: Floating chatbot integrated with transaction views
- **Smart Categorization**: ML-powered transaction categorization
- **Real-time Insights**: AI-driven financial recommendations

## Setup Instructions

### 1. Clone and Setup Backend
```bash
git clone https://github.com/yourusername/ai-cash-flow-mvp.git
cd ai-cash-flow-mvp

# Set up Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Setup Frontend (React)
```bash
# Install Node.js dependencies
npm install
```

### 3. Development Mode (Recommended)
```bash
# Start both frontend and backend in development mode
npm run dev

# This runs:
# - React dev server (Vite) on http://localhost:3000
# - FastAPI backend on http://localhost:8000
# - Hot reload for both React and Python changes
```

### 4. Alternative: Start Separately
```bash
# Terminal 1: Start React dev server
npm run dev:frontend

# Terminal 2: Start FastAPI backend
npm run dev:backend
# or manually: source venv/bin/activate && python3 -m uvicorn app.main:app --reload
```

### 5. Production Build
```bash
# Build React app for production
npm run build

# Start backend (will serve built React app)
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 6. Generate Sample Data (Optional)
```bash
python scripts/generate_realistic_data.py
```

## Development Workflow

### React Development
- React app runs on `http://localhost:3000`
- Hot module replacement for instant updates
- API calls automatically proxied to backend
- Components organized by feature

### Backend Development
- FastAPI runs on `http://localhost:8000`
- Auto-reload on Python file changes
- API docs available at `/docs`
- Dual routing serves React or templates

### Key Development Features
- **Fast Refresh**: React changes appear instantly
- **API Proxy**: No CORS issues during development
- **TypeScript Ready**: Easy upgrade path to TypeScript
- **Component Hot Reload**: State preserved during development

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

### AI Features
- `POST /api/categorize-transaction` - Categorize single transaction
- `POST /api/categorize-month` - Categorize month's transactions
- `GET /api/forecast` - Get cash flow forecast
- `GET /api/insights` - Get AI-powered insights

## User Experience Features

### 🎯 Unified Transaction Interface
- **Account Toggle**: Switch between checking/credit in same page
- **Smart Filtering**: Real-time search and category filters
- **Month Navigation**: Easy month-to-month browsing
- **Sortable Columns**: Click headers to sort data

### 🤖 Integrated AI Assistant (Dex)
- **Floating Chat**: Always accessible from transaction page
- **Context Aware**: Knows current account type and month
- **Smart Responses**: Handles categorization requests intelligently
- **Visual Feedback**: Typing indicators and timestamps

### 🚀 Performance Optimizations
- **React Query Caching**: Smart data caching and background updates
- **Optimistic Updates**: UI updates before server confirmation
- **Bundle Splitting**: Efficient code loading
- **Tailwind CSS**: Minimal CSS bundle size

## Migration Benefits Achieved

✅ **Same-page Experience**: Transaction table + AI chatbot together  
✅ **Account Type Toggle**: Single page for both checking/credit  
✅ **Component Reusability**: DRY principle with shared components  
✅ **Modern Architecture**: React hooks, better state management  
✅ **Improved UX**: No page navigation needed for AI features  
✅ **Developer Experience**: Hot reload, better debugging, TypeScript ready  
✅ **Risk Mitigation**: Dual-system approach allows instant rollback  

## Access Points

- **React App (Development)**: http://localhost:3000
- **React App (Production)**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Legacy Templates**: http://localhost:8000/checking-transactions

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/your-feature-name`
3. Make changes (React components in `frontend/src/`, Python in `app/`)
4. Test both frontend and backend
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Temporary Categorization System 🔄

This application now features a **temporary categorization system** that allows you to experiment with AI categorization and manual edits without permanently modifying your original data.

### How It Works

- **During App Session**: All categorization changes (AI suggestions and manual edits) are stored temporarily in memory
- **When App Stops**: All changes are automatically reset to the original Supabase/CSV data
- **Visual Indicators**: 
  - Yellow warning badges show when temporary changes are active
  - Clear notifications in edit modals explain the temporary nature
  - Global header badge shows count of temporary changes

### Key Features

1. **Smart Categorization**: AI analyzes transactions and suggests categories
2. **Manual Overrides**: Edit any transaction category manually  
3. **Batch Operations**: Apply AI categorization to entire months
4. **Reset Functionality**: Clear all temporary changes with one click
5. **Original Data Protection**: Your Supabase and CSV data remains unchanged

### Usage

1. Start the app: `npm run dev`
2. Make categorization changes (AI or manual)
3. See temporary changes reflected immediately in the UI
4. Stop the app to reset everything back to original state

This design allows safe experimentation and testing without risk of data corruption.

---

## Original Documentation

// ... existing README content ... 