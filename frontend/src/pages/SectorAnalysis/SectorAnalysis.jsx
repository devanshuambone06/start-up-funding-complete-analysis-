import React, { useEffect, useState } from 'react'
import './SectorAnalysis.css'
import {
  Chart as ChartJS, CategoryScale, LinearScale, BarElement,
  LineElement, PointElement, ArcElement, Tooltip, Legend,
} from 'chart.js'
import { Bar, Line, Pie } from 'react-chartjs-2'
import { fetchSectors, fetchFundingTrends, fetchStartups } from '../../services/api'

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, ArcElement, Tooltip, Legend)

const chartColors = ['#8b5cf6','#3b82f6','#22d3a7','#06b6d4','#f59e0b','#ec4899']

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { labels: { color: '#fff' } } },
  scales: {
    x: { ticks: { color: '#fff' }, grid: { color: '#303b62' } },
    y: { ticks: { color: '#fff' }, grid: { color: '#303b62' } },
  },
}

export default function Sectors() {
  const [sectors, setSectors] = useState([])
  const [sectorFunding, setSectorFunding] = useState([])
  const [fundingGrowth, setFundingGrowth] = useState([])
  const [topStartups, setTopStartups] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.allSettled([
      fetchSectors(),
      fetchFundingTrends(),
      fetchStartups({ limit: 10 }),
    ]).then(([secRes, trendsRes, startupsRes]) => {
      if (secRes.status === 'fulfilled' && secRes.value?.length) {
        setSectors(secRes.value)
        setSectorFunding(secRes.value.map(s => ({ sector: s.name, amount: s.fundingB || 0 })))
      }
      if (trendsRes.status === 'fulfilled' && trendsRes.value?.fundingGrowth?.length) {
        setFundingGrowth(trendsRes.value.fundingGrowth)
      }
      if (startupsRes.status === 'fulfilled' && startupsRes.value?.data?.length) {
        setTopStartups(startupsRes.value.data.slice(0, 10).map((s, i) => ({ ...s, rank: i + 1 })))
      }
    }).finally(() => setLoading(false))
  }, [])

  const barData = {
    labels: sectorFunding.map(i => i.sector),
    datasets: [{ label: 'Funding ($B)', data: sectorFunding.map(i => i.amount), backgroundColor: chartColors, borderRadius: 10 }],
  }
  const lineData = {
    labels: fundingGrowth.map(i => i.year),
    datasets: [{ label: 'Growth ($B)', data: fundingGrowth.map(i => i.amount), borderColor: '#8b5cf6', backgroundColor: 'rgba(139,92,246,.2)', fill: true, tension: 0.4 }],
  }
  const pieData = {
    labels: sectorFunding.map(i => i.sector),
    datasets: [{ data: sectorFunding.map(i => i.amount), backgroundColor: chartColors }],
  }

  return (
    <div className="sector-page">
      <div className="page-title">
        <h1>Sector Analysis</h1>
        <p>
          Performance and funding across major startup sectors.
          {loading && <span style={{ color: '#8b5cf6', marginLeft: 8, fontSize: 13 }}>Loading live data…</span>}
        </p>
      </div>

      {/* Sector Cards */}
      <div className="sector-cards">
        {sectors.map((sector) => (
          <div className="sector-card" key={sector.rank || sector.name}>
            <h2>{sector.name}</h2>
            <h3>{sector.score}/100</h3>
            <span>{sector.status}</span>
            <p>{sector.change > 0 ? '+' : ''}{sector.change}% Growth</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="chart-grid">
        <div className="chart-box">
          <h3>Sector Funding</h3>
          <div className="chart"><Bar data={barData} options={options} /></div>
        </div>
        <div className="chart-box">
          <h3>Sector Growth</h3>
          <div className="chart"><Line data={lineData} options={options} /></div>
        </div>
        <div className="chart-box">
          <h3>Funding Distribution</h3>
          <div className="pie-chart">
            <Pie data={pieData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top', labels: { color: '#fff' } } } }} />
          </div>
        </div>
      </div>

      {/* Top Startups */}
      <div className="startup-table">
        <h2>Top Funded Startups</h2>
        <table>
          <thead>
            <tr><th>Rank</th><th>Name</th><th>Sector</th><th>Funding</th><th>Stage</th></tr>
          </thead>
          <tbody>
            {topStartups.map((startup) => (
              <tr key={startup.rank || startup.id || startup.name}>
                <td>{startup.rank}</td>
                <td>{startup.name}</td>
                <td>{startup.sector}</td>
                <td>{startup.totalFunding}</td>
                <td>{startup.stage}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
