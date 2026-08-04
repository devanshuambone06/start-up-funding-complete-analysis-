# Startup Funding Analytics — Production Full-Stack Platform

A production-ready venture intelligence platform built with **FastAPI** (Python backend) and **React + Vite** (frontend), powered by XGBoost machine learning models trained on 31,707 startup funding records.

---

## 🌟 Key Features

- **Production Authentication**:
  - Google OAuth 2.0 Integration
  - Mobile Number OTP (SMS verification via Firebase)
  - Email & Password Login / Registration
  - Password Reset & Session Persistence ("Remember Me")
- **Executive Analytics**: 9 real-time dashboard tabs covering funding growth, sector dynamics, investor centrality (PageRank), and geographic market opportunity.
- **AI Success Predictor**: Dual XGBoost ML engine predicting startup exit probability & funding lifecycles.
- **Professional PDF Reports**: High-quality single-page & paginated PDF report generation using `jsPDF` without blank pages or overflow.
- **Deployment Ready**: Fully configured for Docker Compose, Google Cloud Run, Render, and Railway.

---

## 🛠️ Architecture

```
A:/Startup_Funding_Project/
├── backend/                       ← Python FastAPI Service
│   ├── api/                       ← REST API endpoints & services
│   │   ├── main.py                ← All API routes & CORS setup
│   │   └── services/
│   │       ├── data_service.py    ← Data processing & business logic
│   │       └── ml_service.py      ← XGBoost inference engine
│   ├── data/                      ← Processed & raw CSV datasets
│   ├── models/                    ← Trained XGBoost model binaries (.pkl)
│   ├── Dockerfile.backend
│   └── requirements.txt
│
├── frontend/                      ← React + Vite Web Application
│   ├── src/
│   │   ├── components/            ← UI primitives & design system
│   │   ├── context/
│   │   │   └── AuthContext.jsx    ← Session & Authentication State
│   │   ├── pages/                 ← Dashboard tabs & Auth page
│   │   ├── services/
│   │   │   ├── api.js             ← Centralized Axios API client
│   │   │   └── auth.js            ← Firebase & OAuth handlers
│   │   └── App.jsx
│   ├── Dockerfile.frontend
│   ├── nginx.conf
│   └── package.json
│
├── docker-compose.yml             ← One-command production deployment
├── start.bat                      ← One-click local start script (Windows)
├── .env.example                   ← Environment variables template
└── .gitignore
```

---

## 🚀 Quick Start (Local Development)

### Option A: One-click Start (Windows)
Double-click `start.bat` or run in terminal:
```bat
A:\start.bat
```

### Option B: Manual Start

1. **Backend**:
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate | Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

2. **Frontend**:
```bash
cd frontend
npm install
npm run dev
```

Open:
- **App**: `http://localhost:5173`
- **API Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/health`

---

## 🔐 Setting Up Real Authentication Credentials

The app includes **built-in Demo Mode** out of the box so you can test all features immediately (using demo credentials `demo@vantage.io` / `demo1234` or demo OTP `123456`).

To enable production Google & Mobile OTP Auth:

### 1. Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a project and navigate to **APIs & Services > Credentials**.
3. Create an **OAuth 2.0 Client ID** (Web application).
4. Add `http://localhost:5173` to **Authorized JavaScript origins**.
5. Copy your Client ID into `frontend/.env`:
   ```env
   VITE_GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
   ```

### 2. Firebase Phone Auth (Mobile OTP) Setup
1. Go to [Firebase Console](https://console.firebase.google.com/).
2. Create a project and enable **Authentication > Sign-in method > Phone** and **Google**.
3. Register a Web App in Project Settings and copy the configuration.
4. Fill in the keys in `frontend/.env`:
   ```env
   VITE_FIREBASE_API_KEY=your_api_key
   VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=your_project_id
   VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
   VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
   VITE_FIREBASE_APP_ID=your_app_id
   ```

---

## 🐳 Docker Deployment

To launch both frontend & backend in isolated production containers:

```bash
docker-compose up --build
```

Access the frontend at `http://localhost` and backend at `http://localhost:8000`.

---

## ☁️ Cloud Deployment Instructions

### 1. Deploying to Google Cloud Run
- **Backend**:
  ```bash
  gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/sfa-backend backend/
  gcloud run deploy sfa-backend --image gcr.io/YOUR_PROJECT_ID/sfa-backend --platform managed --allow-unauthenticated --port 8000
  ```
- **Frontend**:
  Set `VITE_API_URL` to your deployed backend URL during build, then submit:
  ```bash
  gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/sfa-frontend frontend/ --build-arg VITE_API_URL=https://sfa-backend-xxx.a.run.app
  gcloud run deploy sfa-frontend --image gcr.io/YOUR_PROJECT_ID/sfa-frontend --platform managed --allow-unauthenticated --port 80
  ```

### 2. Deploying to Render
- **Backend**:
  - Connect repository -> New Web Service -> Root Directory: `backend`
  - Build Command: `pip install -r requirements.txt`
  - Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- **Frontend**:
  - Connect repository -> New Static Site -> Root Directory: `frontend`
  - Build Command: `npm run build`
  - Publish Directory: `dist`
  - Add Environment Variable: `VITE_API_URL=https://your-backend.onrender.com`

### 3. Deploying to Railway
- Deploy backend and frontend as separate services using the provided Dockerfiles (`backend/Dockerfile.backend` and `frontend/Dockerfile.frontend`).

---

## 📄 License & Credits

Built for Venture Capital Analytics and Startup Intelligence.
