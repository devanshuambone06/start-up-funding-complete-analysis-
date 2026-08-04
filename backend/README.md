# 🚀 Startup Funding Analysis

> **An end-to-end Data Science project** — from raw startup funding data to an interactive multi-page Streamlit intelligence dashboard with ML-powered predictions.

---

## 📁 Project Structure

```
Startup_Funding_Analysis/
├── data/
│   ├── raw/
│   │   └── Startup_Funding_Cleaned.csv       ← Raw input dataset
│   └── processed/
│       ├── cleaned_data.csv                  ← ML-ready feature matrix
│       ├── investor_network_edges.csv        ← Co-investment graph edges
│       └── investor_centrality.csv           ← PageRank & centrality scores
│
├── notebooks/
│   ├── 01_EDA.ipynb                          ← Exploratory Data Analysis (16 cells)
│   ├── 02_Data_Cleaning.ipynb                ← Data Cleaning Pipeline (15 cells)
│   ├── 04_Feature_Engineering.ipynb          ← Feature Engineering (22 cells)
│   ├── 05_Machine_Learning.ipynb             ← XGBoost Classifier (success prediction)
│   ├── 06_Forecasting.ipynb                  ← XGBoost Regressor (funding forecast)
│   ├── 07_Investor_Network.ipynb             ← Network graph analysis
│   └── 08_Final_Analysis.ipynb               ← Summary & insights
│
├── dashboard/
│   └── app.py                                ← 7-page Streamlit dashboard
│
├── models/
│   ├── success_model.pkl                     ← Trained XGBoost classifier
│   └── funding_model.pkl                     ← Trained XGBoost regressor
│
├── reports/                                  ← Auto-generated analysis reports
├── visualizations/                           ← Exported chart images (PNG)
├── requirements.txt                          ← Python dependencies
├── run_dashboard.bat                         ← Windows launch script
└── README.md                                 ← This file
```

---

## 🗺️ Dashboard Pages

| Page | Description |
|------|-------------|
| 🏠 **Executive Overview** | KPI cards, sector & country distribution, ecosystem insights |
| 📈 **Funding Trends** | Funding distributions, round analysis, success correlations |
| 🏭 **Sector Intelligence** | Per-sector success rates, capital deployed, leaderboards |
| 🌍 **Geographic Analysis** | Country-level intelligence tables and charts |
| 🤝 **Investor Network** | PageRank centrality, co-investment syndicates, investor lookup |
| 🔮 **Predictive ML Engine** | Interactive startup success probability & funding forecast |
| 📋 **Data Explorer** | Filterable full dataset with column selector & CSV export |

---

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Notebooks (in order)
```
01_EDA.ipynb  →  02_Data_Cleaning.ipynb  →  04_Feature_Engineering.ipynb
→  05_Machine_Learning.ipynb  →  06_Forecasting.ipynb
```

### 3. Launch Dashboard

**Windows:**
```
Double-click: run_dashboard.bat
```

**Terminal:**
```bash
streamlit run dashboard/app.py
```

---

## 🧠 ML Model Details

### Success Classifier (XGBoost)
- **Task:** Binary classification — predict whether a startup will exit (Acquisition/IPO)
- **Target:** `is_successful` (1 = acquired/IPO, 0 = otherwise)
- **Key features:** Funding rounds, investor count, PageRank centrality, sector, country, recession exposure
- **Technique:** Class-weighted XGBoost to handle target imbalance

### Funding Forecaster (XGBoost Regressor)
- **Task:** Predict the lifetime funding amount a startup will raise
- **Target:** `Log_Total_Funding` (log-normalized to handle right skew)
- **Output:** Converted back to USD scale using `np.expm1()`

---

## 🌐 Investor Network Analysis

The investor co-investment network is modelled as an undirected weighted graph:
- **Nodes** = Individual investors
- **Edges** = Co-investments in the same funding round
- **Edge weight** = Number of shared rounds

**PageRank centrality** is computed using the NetworkX library with `alpha=0.85`. High PageRank investors have co-invested with other high-influence investors, making their participation a strong signal of startup credibility.

---

## 📊 Key Findings

- **USA dominates** global startup funding, accounting for ~60%+ of all tracked companies
- **Software, Biotech, and Mobile** are the top-funded sectors globally
- **More funding rounds** strongly correlates with higher exit success probability
- **Investor network quality** (PageRank) is a significant predictor of success
- The **2008–09 recession** caused a measurable dip in deal volumes but not in median deal size
- **Log-transformation** of funding amounts is essential — raw amounts are extremely right-skewed

---

## 🛠 Technology Stack

| Layer | Technology |
|-------|------------|
| Data Processing | Pandas, NumPy |
| Machine Learning | XGBoost, Scikit-learn |
| Network Analysis | NetworkX |
| Dashboard | Streamlit |
| Visualization | Matplotlib, Seaborn |
| Environment | Jupyter Notebook |

---

## 📄 License

This project is for educational and portfolio demonstration purposes.
