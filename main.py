from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from routes.auth import router as auth_router
from routes.complaints import router as complaints_router
from routes.dashboard import router as dashboard_router
from routes.health import router as health_router
from utils.config import ensure_runtime_directories, settings


ensure_runtime_directories()

app = FastAPI(title=settings.APP_NAME, version="1.0.0")

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(complaints_router)
app.include_router(dashboard_router)


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>SwachhSaathi AI</title>
            <style>
                body { font-family: Arial, sans-serif; background: #0f172a; color: #e2e8f0; margin: 0; }
                .wrap { max-width: 960px; margin: 0 auto; padding: 48px 24px; }
                .hero { background: linear-gradient(135deg, #14532d, #0f766e); border-radius: 24px; padding: 32px; }
                h1 { margin-top: 0; font-size: 2.5rem; }
                .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-top: 24px; }
                .card { background: rgba(15, 23, 42, 0.78); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 18px; padding: 20px; }
                a { color: #7dd3fc; text-decoration: none; }
                .actions { margin-top: 24px; display: flex; flex-wrap: wrap; gap: 12px; }
                .btn { background: #e2e8f0; color: #0f172a; padding: 12px 16px; border-radius: 999px; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="wrap">
                <div class="hero">
                    <h1>SwachhSaathi AI</h1>
                    <p>Complete waste management workflow for citizens and authorities.</p>
                    <div class="actions">
                        <a class="btn" href="/docs">Open API Docs</a>
                        <a class="btn" href="/dashboard/summary">View Dashboard API</a>
                        <a class="btn" href="http://localhost:8501">Open User Dashboard</a>
                    </div>
                </div>
                <div class="grid">
                    <div class="card"><h3>Report Waste Issue</h3><p>Submit text, location, and optional image through the complaint API.</p></div>
                    <div class="card"><h3>Track Complaints</h3><p>Follow each ticket by its ticket ID and monitor status updates.</p></div>
                    <div class="card"><h3>View Insights</h3><p>Authorities can inspect waste trends, risks, and predicted bin alerts.</p></div>
                </div>
            </div>
        </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
