# AI-Powered Cash Flow Dashboard

This project is a sophisticated, AI-powered cash flow dashboard designed to provide insightful and actionable financial analysis. It emulates the user experience of leading financial platforms like Capital One, enhanced with a powerful AI engine for transaction categorization, forecasting, and anomaly detection.

## Key Features

- **Capital One-Inspired UI**: A familiar and intuitive interface for a seamless user experience.
- **AI-Powered Transaction Categorization**: Automatically categorizes transactions with high accuracy using a multi-layered approach (Genify API, local ML model, keyword matching).
- **Intelligent Insights Panel**: Provides actionable insights, such as top spending categories, largest transactions, and recurring subscriptions.
- **Transaction Reporting**: Generate PDF reports of monthly transactions for easy record-keeping.
- **Advanced Filtering**: Comprehensive filtering options for transactions, including by date, amount, category, and account type.
- **CSV Data Fallback**: Robust CSV data handling ensures the application is fully testable without a database connection.
- **Detailed Logging**: In-depth logging for all AI and backend processes, providing full transparency.

## Tech Stack

- **Frontend**: React, Vite, Tailwind CSS
- **Backend**: Python, FastAPI
- **AI/ML**: Scikit-learn, Pandas, NumPy
- **PDF Generation**: jsPDF, jspdf-autotable

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ai-cash-flow-mvp
   ```
2. **Set up the backend:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Set up the frontend:**
   ```bash
   npm install
   ```
4. **Run the application:**
   ```bash
   npm run dev
   ```
This will start both the FastAPI backend (on port 8000) and the React frontend (on port 3000).

## Project Status

This project has successfully implemented all core features outlined in the initial timeline. The AI categorization system is highly accurate and performant, and the application provides a robust and intuitive user experience.

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