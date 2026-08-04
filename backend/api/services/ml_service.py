"""
ml_service.py
Wraps ML model inference for the /api/predict endpoint.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .data_service import get_models, get_centrality_df


def _compute_pagerank(investor_names: list[str]):
    """Return (max_pr, sum_pr, num_investors) with fallback to centrality median."""
    cent = get_centrality_df()
    num_inv = max(len(investor_names), 1)
    if investor_names and not cent.empty:
        median_pr = float(cent["PageRank_Centrality"].median())
        pagers = []
        for inv in investor_names:
            row = cent[cent["Investor_Name"] == inv]["PageRank_Centrality"].values
            pagers.append(float(row[0]) if len(row) > 0 else median_pr)
        return max(pagers), sum(pagers), num_inv
    elif not cent.empty:
        med = float(cent["PageRank_Centrality"].median())
        return med, med, 1
    return 0.0, 0.0, 1


def _build_row(feature_list, base_dict: dict, sector: str, country: str) -> pd.DataFrame:
    """Construct a single-row DataFrame for model inference."""
    row = dict(base_dict)
    for col in feature_list:
        if col.startswith("country_code_cleaned_"):
            row[col] = [1 if col.replace("country_code_cleaned_", "") == country else 0]
        elif col.startswith("Industry_Sector_cleaned_"):
            row[col] = [1 if col.replace("Industry_Sector_cleaned_", "") == sector else 0]
        elif col not in row:
            row[col] = [0]
    return pd.DataFrame(row)[feature_list]


def run_prediction(
    sector: str,
    country: str,
    rounds: int,
    age: int,
    funding_raised: float,
    recession: int,
    tech_boom: int,
    investors: list[str],
) -> dict:
    """Run success classifier + funding regressor and return structured result."""
    success_model, funding_model = get_models()

    if success_model is None or funding_model is None:
        return {
            "error": "ML models not loaded. Run notebooks 05 & 06 first.",
            "successProbability": None,
            "predictedFundingUSD": None,
        }

    max_pr, sum_pr, num_inv = _compute_pagerank(investors)
    log_fund = float(np.log1p(funding_raised))

    base_s = {
        "Total_Funding_Rounds": [rounds],
        "Unique_Investors_Count": [num_inv],
        "Fought_Through_Recession": [recession],
        "Age_at_Latest_Round": [age],
        "Log_Total_Funding": [log_fund],
        "Max_Investor_PageRank": [max_pr],
        "Sum_Investor_PageRank": [sum_pr],
        "Funded_During_Tech_Boom": [tech_boom],
    }
    base_f = {
        "Total_Funding_Rounds": [rounds],
        "Unique_Investors_Count": [num_inv],
        "Fought_Through_Recession": [recession],
        "Age_at_Latest_Round": [age],
        "Max_Investor_PageRank": [max_pr],
        "Sum_Investor_PageRank": [sum_pr],
        "Funded_During_Tech_Boom": [tech_boom],
    }

    in_s = _build_row(success_model.feature_names_in_, base_s, sector, country)
    in_f = _build_row(funding_model.feature_names_in_, base_f, sector, country)

    s_pred = int(success_model.predict(in_s)[0])
    s_prob = float(success_model.predict_proba(in_s)[0][1])
    f_log = float(funding_model.predict(in_f)[0])
    f_usd = float(np.expm1(f_log))

    prob_pct = round(s_prob * 100, 1)
    if prob_pct >= 60:
        verdict = "Strong Exit Signal"
        tier = "HIGH"
    elif prob_pct >= 40:
        verdict = "Moderate Exit Potential"
        tier = "MODERATE"
    else:
        verdict = "Low Exit Likelihood"
        tier = "LOW"

    return {
        "successPrediction": s_pred,
        "successProbability": s_prob,
        "successProbabilityPct": prob_pct,
        "verdict": verdict,
        "tier": tier,
        "predictedFundingUSD": f_usd,
        "predictedFundingLog": f_log,
        "maxInvestorPageRank": max_pr,
        "sumInvestorPageRank": sum_pr,
        "numInvestors": num_inv,
        "logFunding": log_fund,
        "inputs": {
            "sector": sector, "country": country, "rounds": rounds,
            "age": age, "fundingRaised": funding_raised,
            "recession": recession, "techBoom": tech_boom,
            "investors": investors,
        },
    }
