import React, { useEffect, useState } from 'react'
import './FundingTrends.css'
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement,
  LineElement, BarElement, ArcElement, Tooltip, Legend,
} from 'chart.js'
import { Line, Bar, Pie } from 'react-chartjs-2'
import { fetchFundingTrends, fetchOverview } from '../../services/api'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Tooltip, Legend)

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { labels: { color: '#fff' } } },
  scales: {
    x: { ticks: { color: '#fff' }, grid: { color: '#2c3550' } },
    y: { ticks: { color: '#fff' }, grid: { color: '#2c3550' } },
  },
}

const pieOptions = {
  responsive: true,
  maintainAspectRatio: false,
  radius: '75%',
  plugins: { legend: { position: 'top', labels: { color: '#fff' } } },
}

export default function FundingTrends() {
  const [stats, setStats] = useState({ totalFunding: 0, totalStartups: 0, activeInvestors: 0, fundingRounds: 0 })
  const [sectorFunding, setSectorFunding] = useState([])
  const [fundingGrowth, setFundingGrowth] = useState([])
  const [fundingStages, setFundingStages] = useState([])
  const [dealSize, setDealSize] = useState({ minDeal: '$0M', avgDeal: '$0M', maxDeal: '$0M', maxDealCompany: '-', totalDeals: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.allSettled([
      fetchOverview(),
      fetchFundingTrends(),
    ]).then(([overviewRes, trendsRes]) => {
      if (overviewRes.status === 'fulfilled' && overviewRes.value) {
        const ov = overviewRes.value
        setStats({
          totalFunding: ov.totalFundingB || 0,
          totalStartups: ov.totalCompanies || 0,
          activeInvestors: ov.activeInvestors || 0,
          fundingRounds: ov.totalRounds || 0,
        })
      }
      if (trendsRes.status === 'fulfilled' && trendsRes.value) {
        const data = trendsRes.value
        if (data.fundingGrowth?.length) setFundingGrowth(data.fundingGrowth)
        if (data.sectorFunding?.length) setSectorFunding(data.sectorFunding)
        if (data.fundingStages?.length) setFundingStages(data.fundingStages)
        if (data.dealSize && Object.keys(data.dealSize).length) setDealSize(data.dealSize)
      }
    })
    .finally(() => setLoading(false))
  }, [])

  const barData = {
    labels: sectorFunding.map((item) => item.sector),
    datasets: [{
      label: 'Funding (Billion $)',
      data: sectorFunding.map((item) => item.amount),
      backgroundColor: ['#8b5cf6','#3b82f6','#22d3a7','#f59e0b','#06b6d4','#ec4899'],
      borderRadius: 8,
    }],
  }

  const lineData = {
    labels: fundingGrowth.map((item) => item.year),
    datasets: [{
      label: 'Funding Growth ($B)',
      data: fundingGrowth.map((item) => item.amount),
      borderColor: '#8b5cf6',
      backgroundColor: 'rgba(139,92,246,.2)',
      fill: true,
      tension: 0.4,
    }],
  }

  const pieData = {
    labels: fundingStages.map((item) => item.stage),
    datasets: [{
      data: fundingStages.map((item) => item.deals || item.percentage),
      backgroundColor: fundingStages.map((item) => item.color || '#6b7280'),
    }],
  }

  return (
    <div className="funding-page">
      <div className="page-title">
        <h1>Funding Trends</h1>
        <p>
          Startup funding analytics and investment insights.
          {loading && <span style={{ color: '#8b5cf6', marginLeft: 8, fontSize: 13 }}>Loading live data…</span>}
        </p>
      </div>

      {/* KPI Cards */}
      <div className="funding-cards">
        <div className="funding-card">
          <h4>Total Funding</h4>
          <h2>${loading ? '...' : stats.totalFunding}B</h2>
        </div>
        <div className="funding-card">
          <h4>Total Startups</h4>
          <h2>{loading ? '...' : stats.totalStartups?.toLocaleString()}</h2>
        </div>
        <div className="funding-card">
          <h4>Active Investors</h4>
          <h2>{loading ? '...' : stats.activeInvestors?.toLocaleString()}</h2>
        </div>
        <div className="funding-card">
          <h4>Funding Rounds</h4>
          <h2>{loading ? '...' : stats.fundingRounds?.toLocaleString()}</h2>
        </div>
      </div>

      {/* Charts */}
      <div className="chart-grid">
        <div className="chart-box">
          <h3>Funding by Sector</h3>
          <div className="chart">
            <Bar data={barData} options={{ ...chartOptions, responsive: true, maintainAspectRatio: false }} />
          </div>
        </div>
        <div className="chart-box">
          <h3>Funding Growth (YoY)</h3>
          <div className="chart">
            <Line data={lineData} options={{ ...chartOptions, responsive: true, maintainAspectRatio: false }} />
          </div>
        </div>
        <div className="chart-box">
          <h3>Funding Stages</h3>
          <div className="pie-chart">
            <Pie data={pieData} options={pieOptions} />
          </div>
        </div>
      </div>

      {/* Deal Size */}
      <div className="deal-box">
        <h2>Deal Statistics</h2>
        <table>
          <tbody>
            <tr><td>Minimum Deal</td><td>{dealSize.minDeal}</td></tr>
            <tr><td>Average Deal</td><td>{dealSize.avgDeal}</td></tr>
            <tr><td>Largest Deal</td><td>{dealSize.maxDeal}</td></tr>
            <tr><td>Company</td><td>{dealSize.maxDealCompany}</td></tr>
            <tr><td>Total Deals</td><td>{dealSize.totalDeals?.toLocaleString()}</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}
