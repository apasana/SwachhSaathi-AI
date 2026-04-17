# SwachhSaathi AI - Smart Waste Management System

SwachhSaathi AI is a complete waste management workflow for citizens and municipal authorities. It combines complaint intake, text and image analysis, bin fill prediction, MongoDB storage, a user portal, and authority insights.

## What the system does
- Citizens report waste issues through a structured complaint API.
- Users can submit text, location, and an optional image.
- AI classifies the complaint, estimates waste type, and assigns risk.
- A scikit-learn prediction model estimates bin fill time.
- MongoDB stores each complaint and tracking record.
- FastAPI exposes complaint, tracking, and dashboard endpoints.
- Streamlit provides the full user-side portal and insights dashboard.

## Stack
- Backend: FastAPI
- Database: MongoDB
- AI: TensorFlow-compatible image classification with heuristic fallback
- Prediction: scikit-learn Linear Regression
- Dashboard: Streamlit + Plotly

## Run the backend
1. Install dependencies: `pip install -r requirement.txt`
2. Start MongoDB locally.
3. Run the API: `uvicorn main:app --reload`

## MongoDB backup and restore
The app already uses the `swachh_saathi` database by default through `MONGO_DB_NAME`.

To export your local database for teammates:
```powershell
mongodump --uri="mongodb://localhost:27017/swachh_saathi" --out="D:\mongo_backup"
```

To restore that dump on another machine:
```powershell
mongorestore --uri="mongodb://localhost:27017" --drop --db="swachh_saathi" "D:\mongo_backup\swachh_saathi"
```

If your MongoDB host, port, or database name is different, set `MONGO_URI` and `MONGO_DB_NAME` before starting the backend.

## Run the user portal and dashboard
1. Start the backend first.
2. Run: `streamlit run dashboard/streamlit_app.py`

## Streamlit sections
- Home
- Report Issue (with optional image upload)
- Track Complaint (by ticket ID)
- Insights (metrics, distributions, and alerts)

## Main endpoints
- `GET /` home screen
- `POST /complaints` submit complaint as JSON
- `POST /complaints/upload` submit complaint with optional image upload
- `GET /complaints/history/{contact_number}` complaint history by phone number
- `GET /complaints/{ticket_id}` track a complaint
- `GET /dashboard/summary` dashboard metrics

## User-side portal features
- Role-based login in Streamlit with backend MongoDB authentication
- Bilingual UI support (English/Hindi)
- Citizen flows: report issue, track complaint, complaint history by contact number
- Authority flows: dashboard insights and complaint status management

## Authentication APIs
- `POST /auth/register`
- `POST /auth/login`

## How to login
- Create account from Streamlit sidebar Register form
- Login using registered username and password

## Project structure
- `main.py`: FastAPI app entrypoint
- `routes/`: complaint, dashboard, and health routes
- `models/`: request and response schemas
- `services/`: AI, prediction, complaint, and dashboard logic
- `database/`: MongoDB connection helpers
- `ai/`: NLP and image classification helpers
- `dashboard/`: Streamlit app
- `utils/`: config and shared helper functions
