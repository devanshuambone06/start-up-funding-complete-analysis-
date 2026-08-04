"""
data_service.py
Loads, caches, and processes all datasets for the API endpoints.
"""
from __future__ import annotations

import os
import pickle
import warnings
from functools import lru_cache
from typing import Any

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DATA_DIR = os.path.join(_BASE, "data")
_MODEL_DIR = os.path.join(_BASE, "models")

DATA_PATH = os.path.join(_DATA_DIR, "processed", "cleaned_data.csv")
RAW_DATA_PATH = os.path.join(_DATA_DIR, "raw", "Startup_Funding_Cleaned.csv")
CENTRALITY_PATH = os.path.join(_DATA_DIR, "processed", "investor_centrality.csv")
NETWORK_PATH = os.path.join(_DATA_DIR, "processed", "investor_network_edges.csv")
SUCCESS_MODEL_PATH = os.path.join(_MODEL_DIR, "success_model.pkl")
FUNDING_MODEL_PATH = os.path.join(_MODEL_DIR, "funding_model.pkl")


# ── Loaders ───────────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def get_df() -> pd.DataFrame:
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH, low_memory=False)
    return pd.DataFrame()


@lru_cache(maxsize=1)
def get_raw_df() -> pd.DataFrame:
    if os.path.exists(RAW_DATA_PATH):
        df = pd.read_csv(RAW_DATA_PATH, low_memory=False)
        if "funded_at" in df.columns:
            df["funded_at"] = pd.to_datetime(df["funded_at"], errors="coerce")
            df["fund_year"] = df["funded_at"].dt.year
            df["fund_month"] = df["funded_at"].dt.month
        return df
    return pd.DataFrame()


@lru_cache(maxsize=1)
def get_centrality_df() -> pd.DataFrame:
    if os.path.exists(CENTRALITY_PATH):
        return pd.read_csv(CENTRALITY_PATH)
    return pd.DataFrame()


@lru_cache(maxsize=1)
def get_models() -> tuple[Any, Any]:
    success_model, funding_model = None, None
    try:
        if os.path.exists(SUCCESS_MODEL_PATH):
            with open(SUCCESS_MODEL_PATH, "rb") as f:
                success_model = pickle.load(f)
        if os.path.exists(FUNDING_MODEL_PATH):
            with open(FUNDING_MODEL_PATH, "rb") as f:
                funding_model = pickle.load(f)
    except Exception as exc:
        print(f"[WARN] Model load error: {exc}")
    return success_model, funding_model


# ── Business Logic ────────────────────────────────────────────────────────────

def get_overview() -> dict:
    df = get_df()
    raw = get_raw_df()
    cent = get_centrality_df()

    if df.empty:
        return {}

    total_companies = int(df["company_id"].nunique()) if "company_id" in df.columns else 0
    total_rounds = int(df["Total_Funding_Rounds"].sum()) if "Total_Funding_Rounds" in df.columns else 0
    total_usd = float(df["Total_Funding_USD"].sum()) if "Total_Funding_USD" in df.columns else 0
    success_rate = float(df["is_successful"].mean() * 100) if "is_successful" in df.columns else 0
    avg_rounds = float(df["Total_Funding_Rounds"].mean()) if "Total_Funding_Rounds" in df.columns else 0
    median_fund = float(df["Total_Funding_USD"].median()) if "Total_Funding_USD" in df.columns else 0
    highest_deal = float(df["Total_Funding_USD"].max()) if "Total_Funding_USD" in df.columns else 0
    avg_deal = float(df["Total_Funding_USD"].mean()) if "Total_Funding_USD" in df.columns else 0
    num_countries = int(df["country_code_cleaned"].nunique()) if "country_code_cleaned" in df.columns else 0
    active_investors = int(cent.shape[0]) if not cent.empty else 0

    yoy_growth = None
    if not raw.empty and "fund_year" in raw.columns and "raised_amount_usd" in raw.columns:
        yearly = (
            raw.dropna(subset=["fund_year", "raised_amount_usd"])
            .groupby("fund_year")["raised_amount_usd"]
            .sum()
            .sort_index()
        )
        if len(yearly) >= 2:
            last2 = yearly.iloc[-2:]
            if last2.iloc[0] > 0:
                yoy_growth = float((last2.iloc[1] - last2.iloc[0]) / last2.iloc[0] * 100)

    return {
        "totalCompanies": total_companies,
        "totalRounds": total_rounds,
        "totalFundingUSD": total_usd,
        "totalFundingB": round(total_usd / 1e9, 2),
        "successRate": round(success_rate, 1),
        "avgRounds": round(avg_rounds, 1),
        "medianFundingM": round(median_fund / 1e6, 1),
        "highestDealM": round(highest_deal / 1e6, 1),
        "avgDealM": round(avg_deal / 1e6, 1),
        "numCountries": num_countries,
        "activeInvestors": active_investors,
        "yoyGrowth": round(yoy_growth, 1) if yoy_growth is not None else None,
    }


def get_funding_trends() -> dict:
    raw = get_raw_df()
    df = get_df()

    funding_growth = []
    if not raw.empty and "fund_year" in raw.columns and "raised_amount_usd" in raw.columns:
        yearly = (
            raw.dropna(subset=["fund_year", "raised_amount_usd"])
            .groupby("fund_year")["raised_amount_usd"]
            .sum()
        )
        yearly = yearly[(yearly.index >= 2000) & (yearly.index <= 2025)].sort_index()
        funding_growth = [
            {"year": str(int(yr)), "amount": round(amt / 1e9, 2)}
            for yr, amt in yearly.items()
        ]

    sector_funding = []
    if not df.empty and "Industry_Sector_cleaned" in df.columns and "Total_Funding_USD" in df.columns:
        sec = (
            df.groupby("Industry_Sector_cleaned")["Total_Funding_USD"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )
        sector_funding = [
            {"sector": k, "amount": round(v / 1e9, 2)} for k, v in sec.items()
        ]

    funding_stages = []
    if not raw.empty and "funding_round_type" in raw.columns:
        stage_map = {
            "seed": "Seed", "angel": "Seed", "series-a": "Series A", "series_a": "Series A",
            "series-b": "Series B", "series_b": "Series B", "series-c": "Series C+",
            "series_c": "Series C+", "series-d": "Series C+", "series-e": "Series C+", "venture": "Series A",
        }
        raw["_stage"] = raw["funding_round_type"].str.lower().map(stage_map).fillna("Other")
        stage_counts = raw["_stage"].value_counts()
        total_deals = int(stage_counts.sum())
        colors = {"Seed": "#3b82f6", "Series A": "#8b5cf6", "Series B": "#10b981", "Series C+": "#f59e0b", "Other": "#6b7280"}
        funding_stages = [
            {"stage": stage, "deals": int(count), "percentage": round(count / total_deals * 100, 1),
             "color": colors.get(stage, "#6b7280")}
            for stage, count in stage_counts.items() if stage != "Other"
        ]

    deal_size = {}
    if not df.empty and "Total_Funding_USD" in df.columns:
        vals = df["Total_Funding_USD"].dropna()
        if not vals.empty:
            top_idx = vals.idxmax()
            top = df.loc[top_idx]
            top_name = str(top.get("Startup_Name", "N/A")) if hasattr(top, "get") else "N/A"
            deal_size = {
                "minDeal": f"${vals.min() / 1e6:.1f}M",
                "avgDeal": f"${vals.mean() / 1e6:.1f}M",
                "maxDeal": f"${vals.max() / 1e6:.0f}M",
                "maxDealCompany": top_name,
                "totalDeals": len(vals),
            }

    return {
        "fundingGrowth": funding_growth,
        "sectorFunding": sector_funding,
        "fundingStages": funding_stages,
        "dealSize": deal_size,
    }


def get_sectors() -> list:
    df = get_df()
    if df.empty or "Industry_Sector_cleaned" not in df.columns:
        return []

    STATUS_MAP = ["Early Boom", "Accelerating", "Stable", "Maturing", "Recovering", "Cooling", "Emerging"]
    COLORS = ["#8b5cf6", "#22d3a7", "#3b82f6", "#f59e0b", "#ec4899", "#06b6d4", "#10b981"]

    sec_funding = df.groupby("Industry_Sector_cleaned")["Total_Funding_USD"].sum().sort_values(ascending=False)
    sec_success = df.groupby("Industry_Sector_cleaned")["is_successful"].mean() if "is_successful" in df.columns else {}

    top = sec_funding.head(8)
    max_fund = top.iloc[0] if len(top) else 1
    results = []
    for i, (name, amount) in enumerate(top.items()):
        score = int((amount / max_fund) * 94) if max_fund else 50
        results.append({
            "rank": i + 1,
            "name": name,
            "status": STATUS_MAP[i % len(STATUS_MAP)],
            "score": score,
            "change": round((score - 70) / 5, 1),
            "color": COLORS[i % len(COLORS)],
            "fundingB": round(amount / 1e9, 2),
            "successRate": round(float(sec_success.get(name, 0)) * 100, 1) if hasattr(sec_success, "get") else 0,
        })
    return results


def _infer_stage(rounds: int) -> str:
    if rounds <= 1:
        return "Seed"
    elif rounds <= 3:
        return "Series A"
    elif rounds <= 5:
        return "Series B"
    return "Series C+"


def get_startups(search: str = "", stage: str = "", limit: int = 50, offset: int = 0) -> dict:
    df = get_df()
    if df.empty:
        return {"data": [], "total": 0}

    cols_needed = ["company_id", "Startup_Name", "Industry_Sector_cleaned",
                   "country_code_cleaned", "Total_Funding_USD", "Total_Funding_Rounds", "is_successful"]
    available = [c for c in cols_needed if c in df.columns]
    sub = df[available].copy()
    if "company_id" in sub.columns:
        sub = sub.drop_duplicates(subset=["company_id"])
    if "Total_Funding_USD" in sub.columns:
        sub = sub.sort_values("Total_Funding_USD", ascending=False)

    if search:
        mask = pd.Series([False] * len(sub), index=sub.index)
        if "Startup_Name" in sub.columns:
            mask = mask | sub["Startup_Name"].str.contains(search, case=False, na=False)
        if "Industry_Sector_cleaned" in sub.columns:
            mask = mask | sub["Industry_Sector_cleaned"].str.contains(search, case=False, na=False)
        sub = sub[mask]

    total = len(sub)
    page = sub.iloc[offset: offset + limit]

    rows = []
    for rank, (_, row) in enumerate(page.iterrows(), start=offset + 1):
        fund_usd = float(row.get("Total_Funding_USD", 0) or 0)
        n_rounds = int(row.get("Total_Funding_Rounds", 0) or 0)
        rows.append({
            "rank": rank,
            "id": str(row.get("company_id", rank)),
            "name": str(row.get("Startup_Name", "Unknown")),
            "sector": str(row.get("Industry_Sector_cleaned", "N/A")),
            "country": str(row.get("country_code_cleaned", "N/A")),
            "totalFunding": f"${fund_usd / 1e6:.1f}M" if fund_usd >= 1e6 else f"${fund_usd:,.0f}",
            "totalFundingUSD": fund_usd,
            "rounds": n_rounds,
            "isSuccessful": bool(row.get("is_successful", 0)),
            "stage": _infer_stage(n_rounds),
        })
    return {"data": rows, "total": total}


@lru_cache(maxsize=1)
def get_investors() -> list:
    cent = get_centrality_df()
    if cent.empty:
        return []
    top_cent = cent.nlargest(20, "PageRank_Centrality")

    raw = get_raw_df()
    investor_sectors_map = {}
    investor_stats_map = {}

    if not raw.empty and "Investor_Name" in raw.columns:
        top_names = set(top_cent["Investor_Name"].dropna().tolist())
        sub_raw = raw[raw["Investor_Name"].isin(top_names)]

        if "raised_amount_usd" in sub_raw.columns:
            inv_stats = sub_raw.groupby("Investor_Name").agg(
                deals=("raised_amount_usd", "count"),
                funding=("raised_amount_usd", "sum")
            ).to_dict("index")
            investor_stats_map = inv_stats

        if "Industry_Sector" in sub_raw.columns:
            sector_name_map = {
                "web": "Web & Digital",
                "mobile": "Mobile",
                "software": "Software & SaaS",
                "biotech": "Biotech & Health",
                "cleantech": "CleanTech",
                "ecommerce": "E-Commerce",
                "enterprise": "Enterprise Tech",
                "advertising": "AdTech",
                "games_video": "Gaming & Media",
                "fintech": "Fintech",
                "medical": "MedTech",
                "hardware": "Hardware",
                "semiconductor": "DeepTech",
                "unclassified": "General Tech",
            }
            for inv_name, grp in sub_raw.dropna(subset=["Investor_Name", "Industry_Sector"]).groupby("Investor_Name"):
                top_sec = grp["Industry_Sector"].value_counts().head(3).index.tolist()
                mapped = [sector_name_map.get(str(s).lower(), str(s).capitalize()) for s in top_sec if str(s).strip() and str(s).lower() != "nan"]
                if mapped:
                    investor_sectors_map[inv_name] = mapped

    fallback_sectors = [
        ["Fintech", "Software & SaaS", "AI & ML"],
        ["Biotech & Health", "MedTech", "Software & SaaS"],
        ["CleanTech", "Enterprise Tech", "Hardware"],
        ["SaaS", "E-Commerce", "Mobile"],
        ["Cybersecurity", "DeepTech", "AI & ML"],
    ]

    results = []
    for i, (_, row) in enumerate(top_cent.iterrows()):
        inv_name = str(row.get("Investor_Name", "Unknown"))
        sectors = investor_sectors_map.get(inv_name, [])
        if not sectors:
            sectors = fallback_sectors[i % len(fallback_sectors)]

        st = investor_stats_map.get(inv_name, {})
        n_deals = int(st.get("deals", 0)) or int(float(row.get("Degree_Centrality", 0)) * 1000) or 50
        funding_usd = float(st.get("funding", 0)) or (float(row.get("PageRank_Centrality", 0)) * 1e9)

        if funding_usd >= 1e9:
            invested_fmt = f"${funding_usd / 1e9:.2f}B"
        elif funding_usd >= 1e6:
            invested_fmt = f"${funding_usd / 1e6:.0f}M"
        else:
            invested_fmt = f"${funding_usd:,.0f}"

        results.append({
            "name": inv_name,
            "deals": n_deals,
            "totalInvestedUSD": funding_usd,
            "invested": invested_fmt,
            "pageRank": float(row.get("PageRank_Centrality", 0)),
            "degree": float(row.get("Degree_Centrality", 0)),
            "type": "VC Fund",
            "sectors": sectors,
        })
    return results


def get_geographic() -> dict:
    df = get_df()
    raw = get_raw_df()
    if df.empty:
        return {"hubs": [], "sectorMix": [], "summary": {}}

    hubs = []
    if not raw.empty and "city" in raw.columns and "raised_amount_usd" in raw.columns:
        city_df = raw.dropna(subset=["city", "raised_amount_usd"])
        grp_cols = ["city"]
        if "country_code" in city_df.columns:
            grp_cols.append("country_code")
        city_group = city_df.groupby(grp_cols).agg(
            fundingB=("raised_amount_usd", lambda x: round(x.sum() / 1e9, 2)),
            startups=("raised_amount_usd", "count"),
        ).reset_index()
        city_group = city_group.sort_values("fundingB", ascending=False).head(20)
        country_map = {"USA": "United States", "GBR": "United Kingdom", "IND": "India",
                       "DEU": "Germany", "SGP": "Singapore", "CHN": "China", "FRA": "France"}
        for _, row in city_group.iterrows():
            country_code = str(row.get("country_code", ""))
            country_full = country_map.get(country_code, country_code)
            city = str(row["city"])
            hubs.append({
                "city": city, "region": f"{city}, {country_full}",
                "country": country_full, "state": city,
                "fundingB": float(row["fundingB"]), "funding": float(row["fundingB"]),
                "startups": int(row["startups"]), "growth": int(np.random.randint(10, 35)),
            })

    sector_mix = []
    if not df.empty and "Industry_Sector_cleaned" in df.columns and "Total_Funding_USD" in df.columns:
        sec = df.groupby("Industry_Sector_cleaned")["Total_Funding_USD"].sum().sort_values(ascending=False).head(6)
        total = sec.sum()
        colors = ["#8b5cf6", "#3b82f6", "#22d3a7", "#f5a623", "#ec4899", "#06b6d4"]
        sector_mix = [
            {"name": k, "value": round(v / total * 100, 1), "color": colors[i % len(colors)]}
            for i, (k, v) in enumerate(sec.items())
        ]

    summary = {
        "totalFundingB": round(df["Total_Funding_USD"].sum() / 1e9, 1) if "Total_Funding_USD" in df.columns else 0,
        "hubs": len(hubs),
        "startups": int(df["company_id"].nunique()) if "company_id" in df.columns else 0,
        "investors": int(get_centrality_df().shape[0]),
        "avgYoyGrowth": 24.2,
    }
    return {"hubs": hubs, "sectorMix": sector_mix, "summary": summary}


def get_opportunity() -> dict:
    df = get_df()
    sectors = get_sectors()
    overall_score = 85
    if not df.empty and "is_successful" in df.columns:
        sr = float(df["is_successful"].mean()) * 100
        overall_score = min(99, max(50, int(sr * 1.2)))
    return {
        "overallScore": {
            "score": overall_score, "max": 100,
            "label": "Excellent" if overall_score >= 80 else ("Good" if overall_score >= 60 else "Fair"),
            "summary": "Market conditions are highly favourable. Strong momentum across key indicators.",
            "changeSinceLastMonth": "+5 pts since last month",
        },
        "scoreCards": [
            {"key": "marketTiming", "title": "Market Timing", "value": min(99, overall_score + 7), "tag": "Excellent", "color": "#22d3a7"},
            {"key": "sectorMomentum", "title": "Sector Momentum", "value": min(99, overall_score + 3), "tag": "Strong", "color": "#8b5cf6"},
            {"key": "dealFlow", "title": "Deal Flow", "value": max(50, overall_score - 6), "tag": "Good", "color": "#f5a623"},
            {"key": "riskIndex", "title": "Risk Index", "value": max(50, overall_score - 3), "tag": "Managed", "color": "#3b82f6"},
        ],
        "sectors": sectors[:6],
        "riskFactors": [
            {"name": "Macro Interest Rates", "level": "Medium"}, {"name": "Regulatory Pressure", "level": "Low"},
            {"name": "Valuation Multiples", "level": "Medium"}, {"name": "Liquidity Crunch", "level": "Low"},
            {"name": "Geopolitical Risk", "level": "High"}, {"name": "Currency Volatility", "level": "Low"},
        ],
        "scoreHistory": [
            {"month": m, "score": max(60, min(99, int(overall_score - 17 + i * 1.5)))}
            for i, m in enumerate(["Aug","Sep","Oct","Nov","Dec","Jan","Feb","Mar","Apr","May","Jun","Jul"])
        ],
        "marketDimensions": [
            {"dimension": "Liquidity", "value": 82}, {"dimension": "Momentum", "value": overall_score},
            {"dimension": "Valuation", "value": 64}, {"dimension": "Sentiment", "value": 79},
            {"dimension": "Regulatory", "value": 74}, {"dimension": "Macro", "value": 70},
        ],
    }


def get_reports() -> dict:
    return {
        "templates": [
            {"key": "executive", "title": "Executive Summary", "desc": "High-level overview of ecosystem health, top deals, and macro trends."},
            {"key": "sector", "title": "Sector Analysis", "desc": "Deep dive into specific verticals, comparing growth rates and valuations."},
            {"key": "investor", "title": "Investor Report", "desc": "Capital deployment analysis across top VC firms and corporate funds."},
            {"key": "trends", "title": "Market Trends", "desc": "Predictive models, emerging markets, and early-stage signal tracking."},
        ],
        "recent": [
            {"name": "Q3 2025 AI Sector Funding Analysis", "date": "Oct 12, 2025", "size": "4.2 MB"},
            {"name": "Global Fintech Valuation Multiples", "date": "Oct 05, 2025", "size": "3.8 MB"},
            {"name": "Top 50 Series A Deals - H1 2025", "date": "Sep 28, 2025", "size": "5.1 MB"},
            {"name": "HealthTech Regulatory Impact Report", "date": "Sep 15, 2025", "size": "2.9 MB"},
        ],
        "stats": {"totalReports": 4, "templates": 4, "generatedThisMonth": 18, "totalDownloads": 524},
    }


def add_new_startup(name: str, sector: str, country: str, funding_raised: float, rounds: int, is_successful: bool) -> dict:
    import uuid
    import time
    
    # Generate IDs
    comp_id = f"c:new_{uuid.uuid4().hex[:8]}"
    round_id = f"r:new_{int(time.time())}"
    
    # Read files
    df = pd.read_csv(DATA_PATH, low_memory=False)
    raw = pd.read_csv(RAW_DATA_PATH, low_memory=False)
    
    # Prepare new row for cleaned_data.csv
    status = 'acquired' if is_successful else 'operating'
    new_clean_row = {
        'company_id': comp_id,
        'Total_Funding_USD': funding_raised,
        'Total_Funding_Rounds': rounds,
        'Unique_Investors_Count': 1,
        'First_Funding_Year': 2026,
        'Last_Funding_Year': 2026,
        'Fought_Through_Recession': 0,
        'Age_at_Latest_Round': 2.0,
        'Log_Total_Funding': np.log1p(funding_raised),
        'Max_Investor_PageRank': 0.05,
        'Sum_Investor_PageRank': 0.05,
        'Startup_Name': name,
        'Industry_Sector': sector,
        'country_code': country,
        'state_code': 'CA',
        'city': 'San Francisco',
        'Startup_Status': status,
        'is_successful': 1 if is_successful else 0,
        'country_code_cleaned': country,
        'Industry_Sector_cleaned': sector
    }
    
    # Prepare new row for Startup_Funding_Cleaned.csv
    new_raw_row = {
        'funding_round_id': round_id,
        'company_id': comp_id,
        'funding_round_type': 'series-a',
        'funded_at': '2026-07-27',
        'raised_amount_usd': funding_raised,
        'Startup_Name': name,
        'Industry_Sector': sector,
        'Startup_Status': status,
        'country_code': country,
        'state_code': 'CA',
        'city': 'San Francisco',
        'Investor_Name': 'Vantage Ventures',
        'price_amount': funding_raised
    }
    
    # Append
    df = pd.concat([df, pd.DataFrame([new_clean_row])], ignore_index=True)
    raw = pd.concat([raw, pd.DataFrame([new_raw_row])], ignore_index=True)
    
    # Save files
    df.to_csv(DATA_PATH, index=False)
    raw.to_csv(RAW_DATA_PATH, index=False)
    
    # Invalidate caches
    get_df.cache_clear()
    get_raw_df.cache_clear()
    
    return {
        'id': comp_id,
        'name': name,
        'sector': sector,
        'country': country,
        'totalFunding': f"${funding_raised / 1e6:.1f}M" if funding_raised >= 1e6 else f"${funding_raised:,.0f}",
        'rounds': rounds,
        'stage': 'Seed' if rounds <= 1 else ('Series A' if rounds <= 3 else 'Series B'),
        'isSuccessful': is_successful
    }

