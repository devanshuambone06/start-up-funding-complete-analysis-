"""
main.py — FastAPI Backend for Startup Funding Analytics
Run: uvicorn api.main:app --reload --port 8000
"""
from __future__ import annotations

from fastapi import FastAPI, Query, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import io
import csv

from .services.data_service import (
    get_overview,
    get_funding_trends,
    get_sectors,
    get_startups,
    get_investors,
    get_geographic,
    get_opportunity,
    get_reports,
    get_df,
)
from .services.ml_service import run_prediction
from .services.auth_service import create_access_token, decode_access_token, get_current_user, UserProfile

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Startup Funding Analytics API",
    description="FastAPI backend serving ML predictions and analytics from the Startup Funding dataset.",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request/Response Models ───────────────────────────────────────────────────
class PredictRequest(BaseModel):
    sector: str = "software"
    country: str = "USA"
    rounds: int = 3
    age: int = 4
    fundingRaised: float = 5_000_000.0
    recession: int = 0
    techBoom: int = 1
    investors: List[str] = []


class AddStartupRequest(BaseModel):
    name: str
    sector: str
    country: str = "USA"
    fundingRaised: float
    rounds: int = 1
    isSuccessful: bool = False


class AuthTokenRequest(BaseModel):
    uid: str
    email: Optional[str] = None
    name: Optional[str] = None
    photoURL: Optional[str] = None
    provider: str = "email"


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok", "service": "startup-funding-analytics"}


# ── Authentication Endpoints ───────────────────────────────────────────────────
@app.post("/api/auth/token")
def issue_token(req: AuthTokenRequest):
    """Issue a backend JWT access token for an authenticated user session."""
    try:
        user_data = {
            "sub": req.uid,
            "uid": req.uid,
            "email": req.email,
            "name": req.name,
            "photoURL": req.photoURL,
            "provider": req.provider,
        }
        token = create_access_token(user_data)
        return {"access_token": token, "token_type": "bearer", "user": user_data}
    except Exception as e:
        raise HTTPException(500, f"Token generation failed: {str(e)}")


@app.get("/api/auth/verify")
def verify_token(user: dict = Depends(get_current_user)):
    """Verify backend JWT session token and return user profile."""
    return {"valid": True, "user": user}


# ── Overview KPIs ─────────────────────────────────────────────────────────────
@app.get("/api/overview")
def overview():
    try:
        return get_overview()
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Funding Trends ────────────────────────────────────────────────────────────
@app.get("/api/funding/trends")
def funding_trends():
    try:
        return get_funding_trends()
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Sectors ───────────────────────────────────────────────────────────────────
@app.get("/api/sectors")
def sectors():
    try:
        return get_sectors()
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Startups ──────────────────────────────────────────────────────────────────
@app.get("/api/startups")
def startups(
    search: str = Query("", description="Filter by name or sector"),
    stage: str = Query("", description="Filter by funding stage"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    try:
        return get_startups(search=search, stage=stage, limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(500, str(e))


@app.post("/api/startups/add")
def add_startup(req: AddStartupRequest):
    try:
        from .services.data_service import add_new_startup
        res = add_new_startup(
            name=req.name,
            sector=req.sector,
            country=req.country,
            funding_raised=req.fundingRaised,
            rounds=req.rounds,
            is_successful=req.isSuccessful
        )
        return {"status": "success", "data": res}
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Investors ─────────────────────────────────────────────────────────────────
@app.get("/api/investors")
def investors():
    try:
        return get_investors()
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Geographic ────────────────────────────────────────────────────────────────
@app.get("/api/geographic")
def geographic():
    try:
        return get_geographic()
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Investment Opportunity ────────────────────────────────────────────────────
@app.get("/api/opportunity")
def opportunity():
    try:
        return get_opportunity()
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Reports ───────────────────────────────────────────────────────────────────
@app.get("/api/reports")
def reports():
    try:
        return get_reports()
    except Exception as e:
        raise HTTPException(500, str(e))


# ── ML Prediction ─────────────────────────────────────────────────────────────
@app.post("/api/predict")
def predict(req: PredictRequest):
    try:
        return run_prediction(
            sector=req.sector,
            country=req.country,
            rounds=req.rounds,
            age=req.age,
            funding_raised=req.fundingRaised,
            recession=req.recession,
            tech_boom=req.techBoom,
            investors=req.investors,
        )
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Export CSV ────────────────────────────────────────────────────────────────
@app.get("/api/export/csv")
def export_csv(
    sector: str = Query("", description="Filter by sector"),
    limit: int = Query(1000, ge=1, le=10000),
):
    try:
        df = get_df()
        if df.empty:
            raise HTTPException(404, "No data available")
        if sector:
            df = df[df["Industry_Sector_cleaned"].str.contains(sector, case=False, na=False)]
        df = df.head(limit)
        stream = io.StringIO()
        df.to_csv(stream, index=False)
        stream.seek(0)
        return StreamingResponse(
            iter([stream.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=startup_data.csv"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Investor List (for prediction form) ───────────────────────────────────────
@app.get("/api/investors/list")
def investor_list():
    try:
        invs = get_investors()
        return [i["name"] for i in invs]
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Sector + Country options (for prediction form) ────────────────────────────
@app.get("/api/options")
def options():
    try:
        df = get_df()
        sectors = sorted(df["Industry_Sector_cleaned"].dropna().unique().tolist()) if "Industry_Sector_cleaned" in df.columns else []
        countries = sorted(df["country_code_cleaned"].dropna().unique().tolist()) if "country_code_cleaned" in df.columns else []
        return {"sectors": sectors, "countries": countries}
    except Exception as e:
        raise HTTPException(500, str(e))
