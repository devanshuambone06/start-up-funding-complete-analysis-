import React, { useEffect, useState } from 'react'
import { Clock, TrendingUp, BarChart3, ShieldCheck, Zap, AlertTriangle, CheckCircle2 } from 'lucide-react'
import { Card, Badge, ProgressBar, ScoreStat, SectionHeader, levelTone } from '../../components/ui'
import {
  ResponsiveContainer, RadialBarChart, RadialBar, AreaChart, Area,
  XAxis, YAxis, Tooltip, RadarChart, PolarGrid, PolarAngleAxis, Radar,
} from 'recharts'
import { fetchOpportunity } from '../../services/api'

const icons = { marketTiming: Clock, sectorMomentum: TrendingUp, dealFlow: BarChart3, riskIndex: ShieldCheck }

const DEFAULT_OVERALL = { score: 84, max: 100, label: 'High Opportunity Potential', summary: 'Favorable macroeconomic tailwinds and strong institutional deal flow in AI & Fintech.', changeSinceLastMonth: '+4.2%' }
const DEFAULT_SCORE_CARDS = [
  { key: 'marketTiming', title: 'Market Timing', value: 88, tag: 'Optimal', color: '#8b5cf6', summary: 'Optimal entry window for Series A & B funding rounds.' },
  { key: 'sectorMomentum', title: 'Sector Momentum', value: 92, tag: 'Strong', color: '#22d3a7', summary: 'AI and DeepTech experiencing historic capital velocity.' },
  { key: 'dealFlow', title: 'Deal Flow Quality', value: 79, tag: 'High', color: '#3b82f6', summary: 'High density of top-tier syndicate co-investments.' },
  { key: 'riskIndex', title: 'Risk Index', value: 68, tag: 'Controlled', color: '#f59e0b', summary: 'Controlled exposure across geographic hubs.' },
]
const DEFAULT_SECTORS = [
  { name: 'Artificial Intelligence', rank: 1, score: 95, status: 'Hypergrowth', color: '#8b5cf6', change: 8.4 },
  { name: 'Fintech & Payments', rank: 2, score: 89, status: 'Strong', color: '#3b82f6', change: 5.2 },
  { name: 'HealthTech & Bio', rank: 3, score: 82, status: 'Steady', color: '#22d3a7', change: 3.1 },
  { name: 'Cybersecurity', rank: 4, score: 87, status: 'Growing', color: '#f59e0b', change: 4.8 },
  { name: 'CleanTech & Energy', rank: 5, score: 76, status: 'Emerging', color: '#ec4899', change: 2.9 },
]
const DEFAULT_RISK_FACTORS = [
  { name: 'Valuation Premium', level: 'Medium', impact: 'High valuation multiples in late-stage AI deals.' },
  { name: 'Macro Interest Rates', level: 'Low', impact: 'Stabilizing central bank rates improving liquidity.' },
  { name: 'Regulatory Horizon', level: 'Low', impact: 'Clearer EU & US AI safety compliance frameworks.' },
  { name: 'Geopolitical Risk', level: 'Medium', impact: 'Ongoing supply chain disruptions in Asia.' },
]
const DEFAULT_HISTORY = [
  { month: 'Jan', score: 76 },
  { month: 'Feb', score: 78 },
  { month: 'Mar', score: 80 },
  { month: 'Apr', score: 81 },
  { month: 'May', score: 84 },
]

export default function InvestmentOpportunity() {
  const [overallScore, setOverallScore] = useState(DEFAULT_OVERALL)
  const [scoreCards, setScoreCards] = useState(DEFAULT_SCORE_CARDS)
  const [sectors, setSectors] = useState(DEFAULT_SECTORS)
  const [riskFactors, setRiskFactors] = useState(DEFAULT_RISK_FACTORS)
  const [scoreHistory, setScoreHistory] = useState(DEFAULT_HISTORY)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchOpportunity()
      .then((data) => {
        if (!data) return
        if (data.overallScore) setOverallScore((prev) => ({ ...prev, ...data.overallScore }))
        if (data.scoreCards?.length) setScoreCards(data.scoreCards)
        if (data.sectors?.length) setSectors(data.sectors)
        if (data.riskFactors?.length) setRiskFactors(data.riskFactors)
        if (data.scoreHistory?.length) setScoreHistory(data.scoreHistory)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const gaugeData = [{ value: overallScore.score, fill: 'url(#gaugeGrad)' }]

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center text-white">
            <Zap size={18} />
          </div>
          <h1 className="text-2xl font-bold text-white">Investment Opportunity Dashboard</h1>
          {loading && <span className="text-violet-400 text-sm animate-pulse ml-2">Loading live data…</span>}
        </div>
        <p className="text-slate-400 text-sm mt-1">Real-time scoring of market conditions, risk exposure, and sectoral momentum.</p>
      </div>

      {/* Overall score */}
      <Card>
        <p className="text-center text-xs tracking-widest text-slate-500 font-semibold mb-2">OVERALL SCORE</p>
        <div className="flex flex-col items-center">
          <div className="w-52 h-32 relative">
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart innerRadius="70%" outerRadius="100%" data={gaugeData} startAngle={180} endAngle={0}>
                <defs>
                  <linearGradient id="gaugeGrad" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#8b5cf6" />
                    <stop offset="50%" stopColor="#3b82f6" />
                    <stop offset="100%" stopColor="#22d3a7" />
                  </linearGradient>
                </defs>
                <RadialBar background={{ fill: '#1e293b' }} dataKey="value" cornerRadius={20} />
              </RadialBarChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center pt-4">
              <span className="text-5xl font-bold text-white">{overallScore.score}</span>
              <span className="text-slate-500 text-xs">/{overallScore.max}</span>
            </div>
          </div>
          <Badge tone="green">{overallScore.label?.toUpperCase()}</Badge>
          <div className="flex justify-between w-full max-w-sm text-[11px] text-slate-500 mt-3">
            <span>Caution</span><span>Fair</span><span>Good</span><span>Excellent</span>
          </div>
          <p className="text-slate-400 text-sm text-center mt-4 max-w-md">{overallScore.summary}</p>
        </div>
      </Card>

      {/* Score cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {scoreCards.map((c) => {
          const Icon = icons[c.key] || Zap
          return <ScoreStat key={c.key} icon={Icon} title={c.title} value={c.value} tag={c.tag} color={c.color} />
        })}
      </div>

      {/* Score history */}
      <Card>
        <SectionHeader
          title="Score History"
          subtitle="12-month opportunity score trend"
          right={<Badge tone="green"><TrendingUp size={11} className="inline -mt-0.5 mr-1" />{overallScore.changeSinceLastMonth}</Badge>}
        />
        <div className="h-56">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={scoreHistory}>
              <defs>
                <linearGradient id="scoreArea" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#8b5cf6" stopOpacity={0.4} />
                  <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="month" stroke="#475569" fontSize={11} tickLine={false} axisLine={false} />
              <YAxis stroke="#475569" fontSize={11} tickLine={false} axisLine={false} domain={[55, 100]} />
              <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8, color: '#e6edf3' }} />
              <Area type="monotone" dataKey="score" stroke="#8b5cf6" fill="url(#scoreArea)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Sector opportunity matrix */}
      <Card>
        <SectionHeader title="Sector Opportunity Matrix" subtitle="Ranked by opportunity score" right={<Zap size={16} className="text-amber-400" />} />
        <div className="space-y-4">
          {sectors.map((s) => (
            <div key={s.name} className="flex items-center gap-4">
              <span className="text-slate-500 text-sm w-4">{s.rank}</span>
              <div className="w-28 shrink-0">
                <p className="text-white text-sm font-medium">{s.name}</p>
                <p className="text-slate-500 text-xs">{s.status}</p>
              </div>
              <div className="flex-1"><ProgressBar value={s.score} color={s.color} /></div>
              <span className="text-sm font-semibold w-8 text-right" style={{ color: s.color }}>{s.score}</span>
              <span className={`text-xs font-semibold w-10 text-right ${s.change >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                {s.change >= 0 ? '+' : ''}{s.change}
              </span>
            </div>
          ))}
        </div>
      </Card>

      {/* Risk factors */}
      <Card>
        <SectionHeader title="Risk Factor Overview" subtitle="Current exposure across key dimensions" right={<ShieldCheck size={16} className="text-emerald-400" />} />
        <div className="space-y-4">
          {riskFactors.map((r) => (
            <div key={r.name} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {r.level === 'High' ? <AlertTriangle size={14} className="text-rose-400" /> :
                  r.level === 'Medium' ? <AlertTriangle size={14} className="text-amber-400" /> :
                  <CheckCircle2 size={14} className="text-emerald-400" />}
                <span className="text-slate-300 text-sm">{r.name}</span>
              </div>
              <Badge tone={levelTone(r.level)}>{r.level}</Badge>
            </div>
          ))}
        </div>
        <div className="flex items-center justify-between mt-6 pt-4 border-t border-slate-800">
          <span className="text-slate-500 text-xs">Overall Risk Posture</span>
          <span className="text-emerald-400 text-xs font-semibold">Managed</span>
        </div>
      </Card>
    </div>
  )
}
