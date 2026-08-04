/**
 * Reports.jsx — Analytics Report Generator
 * Uses jsPDF + html2canvas for real PDF generation (no blank pages).
 */
import { useEffect, useState, useRef } from 'react'
import jsPDF from 'jspdf'
import { fetchReports, fetchOverview, fetchFundingTrends, fetchSectors, getExportUrl } from '../../services/api'
import './Reports.css'

// ── PDF colour palette ────────────────────────────────────────────────────────
const PURPLE = [139, 92, 246]
const BLUE   = [59, 130, 246]
const DARK   = [12, 15, 36]
const MID    = [30, 36, 60]
const LIGHT  = [148, 163, 184]
const WHITE  = [255, 255, 255]

// ── Draw helper: filled rect ──────────────────────────────────────────────────
function rect(doc, x, y, w, h, color) {
  doc.setFillColor(...color)
  doc.rect(x, y, w, h, 'F')
}

// ── Draw helper: gradient-like band (simulate with steps) ─────────────────────
function band(doc, x, y, w, h, c1, c2, steps = 6) {
  for (let i = 0; i < steps; i++) {
    const t = i / (steps - 1)
    const r = Math.round(c1[0] + (c2[0] - c1[0]) * t)
    const g = Math.round(c1[1] + (c2[1] - c1[1]) * t)
    const b = Math.round(c1[2] + (c2[2] - c1[2]) * t)
    doc.setFillColor(r, g, b)
    doc.rect(x + (w / steps) * i, y, w / steps + 1, h, 'F')
  }
}

// ── Draw helper: horizontal bar ───────────────────────────────────────────────
function hBar(doc, x, y, pct, maxW, h, color) {
  doc.setFillColor(30, 36, 60)
  doc.roundedRect(x, y, maxW, h, 1, 1, 'F')
  const filled = Math.max(0, Math.min(1, pct)) * maxW
  if (filled > 0) {
    doc.setFillColor(...color)
    doc.roundedRect(x, y, filled, h, 1, 1, 'F')
  }
}

// ── Main PDF generator ────────────────────────────────────────────────────────
async function generatePDF(overview, trends, sectors, reportTitle = 'Executive Summary') {
  const doc = new jsPDF({ unit: 'mm', format: 'a4', orientation: 'portrait' })
  const PW = doc.internal.pageSize.getWidth()   // 210
  const PH = doc.internal.pageSize.getHeight()  // 297
  const M  = 14   // margin
  const CW = PW - M * 2  // content width
  let y = 0

  // ─── PAGE 1 ────────────────────────────────────────────────────────────────
  // Header band
  band(doc, 0, 0, PW, 38, DARK, [18, 22, 50])
  doc.setFillColor(139, 92, 246)
  doc.circle(M + 7, 19, 7, 'F')
  doc.setTextColor(255, 255, 255)
  doc.setFontSize(10)
  doc.setFont('helvetica', 'bold')
  doc.text('SFA', M + 7, 20.5, { align: 'center' })

  doc.setFontSize(18)
  doc.setFont('helvetica', 'bold')
  doc.text('Startup Funding Analytics', M + 20, 14)
  doc.setFontSize(9)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(...LIGHT)
  doc.text(reportTitle + ' Report  •  ' + new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }), M + 20, 22)
  doc.setFontSize(8)
  doc.text('CONFIDENTIAL — FOR AUTHORISED RECIPIENTS ONLY', M + 20, 30)

  // Decorative accent line
  band(doc, 0, 38, PW, 2, PURPLE, BLUE)

  y = 48

  // ─── KPI Cards (row of 4) ──────────────────────────────────────────────────
  const kpis = [
    { label: 'Total Funding', value: `$${overview?.totalFundingB || 0}B`, color: PURPLE },
    { label: 'Total Startups', value: (overview?.totalCompanies || 0).toLocaleString(), color: BLUE },
    { label: 'Active Investors', value: (overview?.activeInvestors || 0).toString(), color: [16, 185, 129] },
    { label: 'Success Rate', value: `${overview?.successRate || 0}%`, color: [245, 158, 11] },
  ]
  const cardW = (CW - 9) / 4
  kpis.forEach((kpi, i) => {
    const cx = M + i * (cardW + 3)
    rect(doc, cx, y, cardW, 22, MID)
    doc.setDrawColor(...kpi.color)
    doc.setLineWidth(0.5)
    doc.roundedRect(cx, y, cardW, 22, 1.5, 1.5, 'S')
    doc.setFillColor(...kpi.color)
    doc.rect(cx, y, 2, 22, 'F')
    doc.setTextColor(...kpi.color)
    doc.setFontSize(14)
    doc.setFont('helvetica', 'bold')
    doc.text(kpi.value, cx + cardW / 2 + 1, y + 10, { align: 'center' })
    doc.setTextColor(...LIGHT)
    doc.setFontSize(7)
    doc.setFont('helvetica', 'normal')
    doc.text(kpi.label, cx + cardW / 2 + 1, y + 17, { align: 'center' })
  })

  y += 30

  // ─── Section: Funding Growth Chart ────────────────────────────────────────
  doc.setTextColor(...WHITE)
  doc.setFontSize(10)
  doc.setFont('helvetica', 'bold')
  doc.text('Annual Funding Growth', M, y)
  doc.setDrawColor(...PURPLE)
  doc.setLineWidth(0.4)
  doc.line(M, y + 2, M + 55, y + 2)
  y += 6

  const chartH = 42
  const chartW = CW
  rect(doc, M, y, chartW, chartH, MID)

  const growth = (trends?.fundingGrowth || []).slice(-12)
  if (growth.length > 0) {
    const maxAmt = Math.max(...growth.map(d => d.amount), 1)
    const barW = (chartW - 8) / growth.length
    growth.forEach((d, i) => {
      const bh = (d.amount / maxAmt) * (chartH - 14)
      const bx = M + 4 + i * barW
      const by = y + chartH - 8 - bh

      // bar with gradient effect
      const intensity = 0.4 + 0.6 * (d.amount / maxAmt)
      doc.setFillColor(
        Math.round(PURPLE[0] * intensity + BLUE[0] * (1 - intensity)),
        Math.round(PURPLE[1] * intensity + BLUE[1] * (1 - intensity)),
        Math.round(PURPLE[2] * intensity + BLUE[2] * (1 - intensity))
      )
      doc.roundedRect(bx, by, barW - 1.5, bh, 0.5, 0.5, 'F')

      // label
      doc.setTextColor(...LIGHT)
      doc.setFontSize(5.5)
      doc.text(d.year?.toString()?.slice(-2) || '', bx + (barW - 1.5) / 2, y + chartH - 2, { align: 'center' })

      // value on tall bars
      if (bh > 10) {
        doc.setTextColor(...WHITE)
        doc.setFontSize(5)
        doc.text(`$${d.amount}B`, bx + (barW - 1.5) / 2, by - 1, { align: 'center' })
      }
    })
  } else {
    doc.setTextColor(...LIGHT)
    doc.setFontSize(8)
    doc.text('No growth data available', M + chartW / 2, y + chartH / 2, { align: 'center' })
  }

  y += chartH + 8

  // ─── Section: Sector Analysis ──────────────────────────────────────────────
  doc.setTextColor(...WHITE)
  doc.setFontSize(10)
  doc.setFont('helvetica', 'bold')
  doc.text('Top Sectors by Investment Score', M, y)
  doc.setDrawColor(...BLUE)
  doc.setLineWidth(0.4)
  doc.line(M, y + 2, M + 65, y + 2)
  y += 7

  const topSectors = (sectors || []).slice(0, 7)
  const maxScore = Math.max(...topSectors.map(s => s.score || 0), 1)
  const SECTOR_COLORS = [
    [139, 92, 246], [59, 130, 246], [16, 185, 129],
    [245, 158, 11], [236, 72, 153], [6, 182, 212], [99, 102, 241],
  ]

  topSectors.forEach((sec, i) => {
    const rowY = y + i * 10
    const sc = SECTOR_COLORS[i % SECTOR_COLORS.length]

    // Name
    doc.setTextColor(...WHITE)
    doc.setFontSize(8)
    doc.setFont('helvetica', 'bold')
    doc.text(`${i + 1}. ${sec.name || '—'}`, M, rowY + 5)

    // Score pill
    doc.setFillColor(...sc)
    doc.roundedRect(M + 65, rowY + 1, 16, 6, 1.5, 1.5, 'F')
    doc.setTextColor(...WHITE)
    doc.setFontSize(6)
    doc.setFont('helvetica', 'bold')
    doc.text(`${sec.score || 0}`, M + 73, rowY + 5.3, { align: 'center' })

    // Progress bar
    hBar(doc, M + 84, rowY + 2, (sec.score || 0) / maxScore, CW - 84, 4, sc)

    // Funding label
    doc.setTextColor(...LIGHT)
    doc.setFontSize(6.5)
    doc.setFont('helvetica', 'normal')
    doc.text(`$${sec.fundingB || 0}B`, PW - M, rowY + 5, { align: 'right' })
  })

  y += topSectors.length * 10 + 6

  // ─── Section: Funding Stages ───────────────────────────────────────────────
  const stages = trends?.fundingStages || []
  if (stages.length > 0 && y < PH - 50) {
    doc.setTextColor(...WHITE)
    doc.setFontSize(10)
    doc.setFont('helvetica', 'bold')
    doc.text('Funding Stage Distribution', M, y)
    doc.setDrawColor(...PURPLE)
    doc.setLineWidth(0.4)
    doc.line(M, y + 2, M + 65, y + 2)
    y += 8

    const totalDeals = stages.reduce((s, d) => s + (d.deals || 0), 0)
    const stageColors = [[59,130,246],[139,92,246],[16,185,129],[245,158,11]]
    stages.slice(0, 4).forEach((st, i) => {
      const colX = M + i * (CW / 4)
      const colW = CW / 4 - 3
      const colH = 22
      rect(doc, colX, y, colW, colH, MID)
      doc.setFillColor(...(stageColors[i] || PURPLE))
      doc.rect(colX, y, colW, 2, 'F')
      doc.setTextColor(...WHITE)
      doc.setFontSize(12)
      doc.setFont('helvetica', 'bold')
      doc.text(st.stage || '—', colX + colW / 2, y + 11, { align: 'center' })
      doc.setFontSize(8)
      doc.setFont('helvetica', 'normal')
      doc.setTextColor(...LIGHT)
      const pct = totalDeals > 0 ? ((st.deals / totalDeals) * 100).toFixed(1) : '0'
      doc.text(`${st.deals?.toLocaleString()} deals (${pct}%)`, colX + colW / 2, y + 18, { align: 'center' })
    })
    y += 30
  }

  // ─── Section: Key Insights ─────────────────────────────────────────────────
  if (y < PH - 40) {
    doc.setTextColor(...WHITE)
    doc.setFontSize(10)
    doc.setFont('helvetica', 'bold')
    doc.text('Key Insights', M, y)
    doc.setDrawColor(...BLUE)
    doc.setLineWidth(0.4)
    doc.line(M, y + 2, M + 40, y + 2)
    y += 8

    const insights = [
      'AI & ML continues to lead global funding activity with record-high deal volumes.',
      'FinTech remains the strongest investment sector, driven by digital payments growth.',
      `${(overview?.successRate || 0)}% success rate indicates a healthy, competitive ecosystem.`,
      'Geographic expansion into emerging markets is accelerating deal flow.',
    ]

    insights.forEach((ins, i) => {
      rect(doc, M, y, CW, 10, MID)
      doc.setFillColor(...PURPLE)
      doc.circle(M + 3.5, y + 5, 1.5, 'F')
      doc.setTextColor(...WHITE)
      doc.setFontSize(8)
      doc.setFont('helvetica', 'normal')
      const lines = doc.splitTextToSize(ins, CW - 10)
      doc.text(lines[0], M + 8, y + 6)
      y += 12
    })
  }

  // ─── Footer ────────────────────────────────────────────────────────────────
  band(doc, 0, PH - 10, PW, 10, DARK, [18, 22, 50])
  doc.setTextColor(...LIGHT)
  doc.setFontSize(6.5)
  doc.setFont('helvetica', 'normal')
  doc.text('Startup Funding Analytics Platform  |  Confidential', M, PH - 3)
  doc.text('Page 1 of 1', PW - M, PH - 3, { align: 'right' })

  // Save
  const filename = `SFA_${reportTitle.replace(/\s+/g, '_')}_${new Date().toISOString().slice(0, 10)}.pdf`
  doc.save(filename)
}

// ══════════════════════════════════════════════════════════════════════════════
export default function Reports() {
  const [templates, setTemplates] = useState([])
  const [recentReports, setRecentReports] = useState([])
  const [stats, setStats] = useState({ totalReports: 0, templates: 0, generatedThisMonth: 0, totalDownloads: 0 })
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(null)
  const dataRef = useRef({ overview: null, trends: null, sectors: [] })

  useEffect(() => {
    Promise.allSettled([
      fetchReports(),
      fetchOverview(),
      fetchFundingTrends(),
      fetchSectors(),
    ]).then(([rptRes, ovRes, trdRes, secRes]) => {
      if (rptRes.status === 'fulfilled' && rptRes.value) {
        const d = rptRes.value
        if (d?.templates?.length) setTemplates(d.templates)
        if (d?.recent?.length) setRecentReports(d.recent)
        if (d?.stats) setStats(d.stats)
      }
      dataRef.current = {
        overview: ovRes.status === 'fulfilled' ? ovRes.value : null,
        trends: trdRes.status === 'fulfilled' ? trdRes.value : null,
        sectors: secRes.status === 'fulfilled' ? (Array.isArray(secRes.value) ? secRes.value : []) : [],
      }
    }).finally(() => setLoading(false))
  }, [])

  const handleGenerate = async (key, title) => {
    setGenerating(key)
    try {
      await generatePDF(dataRef.current.overview, dataRef.current.trends, dataRef.current.sectors, title)
    } catch (err) {
      console.error('[PDF] Generation failed:', err)
      alert('PDF generation failed. Please try again.')
    }
    setGenerating(null)
  }

  const handleDownloadReport = async (reportName) => {
    setGenerating(reportName)
    try {
      await generatePDF(dataRef.current.overview, dataRef.current.trends, dataRef.current.sectors, reportName)
    } catch (err) {
      console.error('[PDF] Generation failed:', err)
    }
    setGenerating(null)
  }

  const handleDownloadCSV = () => window.open(getExportUrl(), '_blank')

  return (
    <div className="reports-page">
      <div className="page-title">
        <h1>Reports</h1>
        <p>
          Generate and download professional startup ecosystem reports as PDF.
          {loading && <span style={{ color: '#8b5cf6', marginLeft: 8, fontSize: 13 }}>Loading…</span>}
        </p>
      </div>

      <h2 className="section-title">Report Templates</h2>
      <div className="template-grid">
        {templates.map((report) => (
          <div className="template-card" key={report.key}>
            <div className="template-icon">📄</div>
            <h3>{report.title}</h3>
            <p>{report.desc}</p>
            <button
              onClick={() => handleGenerate(report.key, report.title)}
              disabled={generating === report.key}
              style={{ opacity: generating === report.key ? 0.7 : 1, cursor: generating === report.key ? 'wait' : 'pointer' }}
            >
              {generating === report.key ? 'Generating PDF…' : 'Download PDF Report'}
            </button>
          </div>
        ))}
      </div>

      <div className="recent-report-box">
        <div className="recent-header">
          <h2>Recent Reports</h2>
          <button onClick={handleDownloadCSV}>Download Full Dataset (CSV)</button>
        </div>
        <table>
          <thead>
            <tr><th>Report Name</th><th>Date</th><th>Size</th><th>Action</th></tr>
          </thead>
          <tbody>
            {recentReports.map((report, index) => (
              <tr key={index}>
                <td>{report.name}</td>
                <td>{report.date}</td>
                <td>{report.size}</td>
                <td>
                  <button
                    className="download-btn"
                    onClick={() => handleDownloadReport(report.name)}
                    disabled={generating === report.name}
                  >
                    {generating === report.name ? 'Generating…' : 'Download PDF'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="report-stats">
        <div className="stat-card"><h4>Total Reports</h4><h2>{stats.totalReports}</h2></div>
        <div className="stat-card"><h4>Templates</h4><h2>{stats.templates}</h2></div>
        <div className="stat-card"><h4>Generated This Month</h4><h2>{stats.generatedThisMonth}</h2></div>
        <div className="stat-card"><h4>Total Downloads</h4><h2>{stats.totalDownloads}</h2></div>
      </div>

      <div className="tips-box">
        <h2>Reporting Insights</h2>
        <ul>
          <li>AI &amp; ML continues to lead global funding activity.</li>
          <li>FinTech remains the strongest investment sector.</li>
          <li>CleanTech funding has increased significantly this quarter.</li>
          <li>HealthTech investment remains stable across all regions.</li>
          <li>Generate reports monthly to monitor market trends.</li>
        </ul>
      </div>
    </div>
  )
}