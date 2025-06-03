from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

app = FastAPI(title="Cash Flow Dashboard with XAI")

# Get the absolute path to the templates directory
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Render the main dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/forecast")
async def get_forecast():
    """Get cash flow forecast data."""
    # TODO: Implement forecast logic
    return {"message": "Forecast endpoint - to be implemented"}

@app.get("/api/insights")
async def get_insights():
    """Get XAI insights for the forecast."""
    # TODO: Implement XAI insights logic
    return {"message": "Insights endpoint - to be implemented"} 