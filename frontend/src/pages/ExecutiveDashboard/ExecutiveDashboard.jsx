import { useEffect, useState } from 'react'
import { fetchOverview, fetchFundingTrends, fetchStartups } from '../../services/api'
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'

const SECTOR_COLORS = {
  Fintech: '#3b82f6', HealthTech: '#10b981', CleanTech: '#059669',
  EdTech: '#eab308', AI: '#8b5cf6', 'E-commerce': '#f97316',
  Cybersecurity: '#ec4899', DeepTech: '#6366f1',
}
const cardCls = 'bg-bg-panel border border-border rounded-[10px] p-5'
const cardTitleCls = 'text-base font-bold text-text-primary mb-4'
const mutedCls = 'text-xs text-text-muted'
const tooltipStyle = { backgroundColor: '#21262d', border: '1px solid #30363d', borderRadius: 8, color: '#e6edf3', fontSize: 12 }

const unicornWatch = [
  { name: 'PayNova',     sector: 'Fintech', stage: 'Series C', valuation: '$820M', target: '$1B target', raised: '$180M', percentRaised: 82 },
  { name: 'Cognivia AI', sector: 'AI',      stage: 'Series B', valuation: '$690M', target: '$1B target', raised: '$142M', percentRaised: 69 },
  { name: 'CureLoop',    sector: 'HealthTech', stage: 'Series B', valuation: '$610M', target: '$1B target', raised: '$132M', percentRaised: 61 },
  { name: 'ShopStack',   sector: 'E-commerce', stage: 'Series C', valuation: '$640M', target: '$1B target', raised: '$121M', percentRaised: 64 },
]

export default function ExecutiveDashboard() {
  const [stats, setStats] = useState({ totalFunding: 0, totalStartups: 0, activeInvestors: 0, fundingRounds: 0 })
  const [fundingGrowth, setFundingGrowth] = useState([])
  const [sectorFunding, setSectorFunding] = useState([])
  const [fundingStages, setFundingStages] = useState([])
  const [topStartups, setTopStartups] = useState([])
  const [dealSize, setDealSize] = useState({ minDeal: '$0M', avgDeal: '$0M', maxDeal: '$0M', maxDealCompany: '-', totalDeals: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.allSettled([
      fetchOverview(),
      fetchFundingTrends(),
      fetchStartups({ limit: 10 }),
    ]).then(([overviewRes, trendsRes, startupsRes]) => {
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
        const t = trendsRes.value
        if (t.fundingGrowth?.length) setFundingGrowth(t.fundingGrowth)
        if (t.sectorFunding?.length) setSectorFunding(t.sectorFunding)
        if (t.fundingStages?.length) setFundingStages(t.fundingStages)
        if (t.dealSize) setDealSize(t.dealSize)
      }
      if (startupsRes.status === 'fulfilled' && startupsRes.value?.data?.length) {
        setTopStartups(startupsRes.value.data.slice(0, 10).map((s, i) => ({ ...s, rank: i + 1 })))
      }
    }).finally(() => setLoading(false))
  }, [])

  return (
    <div className="flex flex-col gap-5">
      {/* Stats Cards */}
      <div className="grid gap-4" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
        {[
          { label: 'Total Funding', value: `$${stats.totalFunding}B`, sub: '+18.3% YoY', icon: '💰', color: '#8b5cf6' },
          { label: 'Total Startups', value: stats.totalStartups?.toLocaleString(), sub: '+142 new this year', icon: '🚀', color: '#3b82f6' },
          { label: 'Active Investors', value: stats.activeInvestors, sub: '+54 new this quarter', icon: '👥', color: '#06b6d4' },
          { label: 'Funding Rounds', value: `${((stats.fundingRounds || 0) / 1000).toFixed(1)}K`, sub: '+8.2% vs last year', icon: '📈', color: '#10b981' },
        ].map(({ label, value, sub, icon, color }) => (
          <div key={label} className={cardCls}>
            <div className="flex justify-between items-start mb-3">
              <div className="w-9 h-9 rounded-lg flex items-center justify-center text-base" style={{ background: color + '20' }}>{icon}</div>
              <span className="text-[11px] text-accent-green font-semibold">↑</span>
            </div>
            <div className="text-[20px] font-bold text-text-primary mb-1 leading-none">{loading ? '...' : value}</div>
            <div className="text-[13px] text-text-muted">{label}</div>
            <div className="text-[11px] text-accent-green mt-1.5">{sub}</div>
          </div>
        ))}
      </div>

      {/* Unicorn Watch */}
      <div className={cardCls}>
        <div className="flex items-center justify-between mb-2 flex-wrap gap-2">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 bg-accent-green/10 px-2.5 py-1 rounded-full">
              <div className="w-[7px] h-[7px] rounded-full bg-accent-green pulse-dot" />
              <span className="text-[10px] font-bold text-accent-green tracking-wider uppercase">Live</span>
            </div>
            <span className={cardTitleCls + ' mb-0'}>Unicorn Watch</span>
          </div>
          <span className={mutedCls}>{unicornWatch.length} candidates tracked</span>
        </div>
        <p className={mutedCls + ' mb-4'}>Startups approaching $1B valuation threshold</p>
        <div className="grid gap-3" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
          {unicornWatch.map((s) => (
            <div key={s.name} className="bg-bg-sunken border border-border rounded-lg p-3.5">
              <div className="font-semibold text-text-primary mb-1">{s.name}</div>
              <div className="flex gap-1.5 mb-2.5">
                <span className="text-[11px] px-2 py-0.5 rounded" style={{ background: (SECTOR_COLORS[s.sector] || '#8b5cf6') + '20', color: SECTOR_COLORS[s.sector] || '#8b5cf6' }}>{s.sector}</span>
                <span className="text-[11px] text-text-muted">{s.stage}</span>
              </div>
              <div className="text-[11px] text-text-muted mb-0.5">Valuation</div>
              <div className="text-xl font-bold text-brand-purple mb-2">{s.valuation}</div>
              <div className="h-1.5 bg-bg-field rounded-[3px] mb-1">
                <div className="h-full rounded-[3px] bg-brand-gradient-h" style={{ width: `${s.percentRaised}%` }} />
              </div>
              <div className="flex justify-between text-[11px] text-text-muted">
                <span>{s.target}</span>
                <span className="font-semibold">{s.percentRaised}%</span>
              </div>
              <div className="mt-2 pt-2 border-t border-border text-[11px] text-text-muted">
                Raised: <span className="text-text-primary font-semibold">{s.raised}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid gap-5" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))' }}>
        <div className={cardCls}>
          <div className={cardTitleCls}>Funding Growth (YoY)</div>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={fundingGrowth}>
              <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
              <XAxis dataKey="year" stroke="#8b949e" tick={{ fontSize: 12 }} />
              <YAxis stroke="#8b949e" tick={{ fontSize: 12 }} tickFormatter={(v) => `$${v}B`} />
              <Tooltip contentStyle={tooltipStyle} formatter={(v) => [`$${v}B`, 'Funding']} />
              <Line type="monotone" dataKey="amount" stroke="#8b5cf6" strokeWidth={3} dot={{ fill: '#8b5cf6', r: 5 }} activeDot={{ r: 7 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className={cardCls}>
          <div className={cardTitleCls}>Sector-wise Funding</div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={sectorFunding} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
              <XAxis type="number" stroke="#8b949e" tick={{ fontSize: 12 }} tickFormatter={(v) => `$${v}B`} />
              <YAxis dataKey="sector" type="category" stroke="#8b949e" tick={{ fontSize: 12 }} width={90} />
              <Tooltip contentStyle={tooltipStyle} formatter={(v) => [`$${v}B`, 'Funding']} cursor={{ fill: 'transparent' }} />
              <defs><linearGradient id="barGrad" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stopColor="#8b5cf6" /><stop offset="100%" stopColor="#3b82f6" /></linearGradient></defs>
              <Bar dataKey="amount" fill="url(#barGrad)" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Startups Table */}
      <div className={cardCls}>
        <div className="flex justify-between items-center mb-4">
          <div className={cardTitleCls + ' mb-0'}>Top 10 Funded Startups</div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse min-w-[520px]">
            <thead>
              <tr>
                {['Rank', 'Startup Name', 'Sector', 'Total Funding', 'Stage'].map((h) => (
                  <th key={h} className="text-left text-[13px] font-semibold text-white uppercase tracking-wider pb-2.5 border-b border-border">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {topStartups.map((s) => (
                <tr key={s.rank || s.id} className="border-b border-bg-field">
                  <td className="py-3"><div className="w-[30px] h-[30px] rounded-full flex items-center justify-center font-medium text-[13px] bg-transparent text-text-primary">{s.rank}</div></td>
                  <td className="py-3 px-2 font-semibold text-text-primary">{s.name}</td>
                  <td className="py-3 px-2"><span className="text-[11px] px-2 py-[3px] rounded" style={{ background: (SECTOR_COLORS[s.sector] || '#8b5cf6') + '20', color: SECTOR_COLORS[s.sector] || '#8b5cf6' }}>{s.sector}</span></td>
                  <td className="py-3 px-2 text-brand-purple font-semibold font-mono">{s.totalFunding}</td>
                  <td className="py-3 px-2 text-text-muted text-[13px]">{s.stage}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid gap-5" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))' }}>
        <div className={cardCls}>
          <div className={cardTitleCls}>Funding Stage Distribution</div>
          <div className="flex flex-wrap gap-4 items-center">
            <ResponsiveContainer width={200} height={200}>
              <PieChart>
                <Pie data={fundingStages} cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={2} dataKey="percentage">
                  {fundingStages.map((e, i) => <Cell key={i} fill={e.color || '#6b7280'} />)}
                </Pie>
                <Tooltip contentStyle={tooltipStyle} />
              </PieChart>
            </ResponsiveContainer>
            <div className="flex-1 min-w-[140px]">
              {fundingStages.map((s) => (
                <div key={s.stage} className="flex justify-between items-center mb-2.5">
                  <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-sm" style={{ background: s.color || '#6b7280' }} />
                    <span className="text-[13px] text-text-primary">{s.stage}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-[13px] font-semibold text-text-primary">{s.deals}</div>
                    <div className="text-[11px] text-text-muted">{s.percentage}%</div>
                  </div>
                </div>
              ))}
              <div className="mt-3 pt-3 border-t border-border text-xs text-text-muted">
                Total deals tracked: <span className="text-text-primary font-semibold">{dealSize.totalDeals?.toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
        <div className={cardCls}>
          <div className={cardTitleCls}>Deal Size Analysis</div>
          <p className={mutedCls + ' mb-4'}>Funding range across all active deals</p>
          <div className="grid grid-cols-3 gap-2.5 mb-5">
            {[
              { label: 'Min Deal', value: dealSize.minDeal, sub: 'Seed stage floor', color: '#3b82f6' },
              { label: 'Avg Deal', value: dealSize.avgDeal, sub: `${dealSize.totalDeals} deals`, color: '#f59e0b' },
              { label: 'Max Deal', value: dealSize.maxDeal, sub: dealSize.maxDealCompany, color: '#8b5cf6' },
            ].map(({ label, value, sub, color }) => (
              <div key={label} className="bg-bg-sunken border border-border rounded-lg p-3">
                <div className="w-7 h-7 rounded-md flex items-center justify-center text-sm mb-2" style={{ background: color + '20' }}>💲</div>
                <div className="text-[11px] text-text-muted mb-0.5">{label}</div>
                <div className="text-base font-bold text-text-primary mb-0.5">{loading ? '...' : value}</div>
                <div className="text-[11px] text-text-muted truncate" title={sub}>{sub}</div>
              </div>
            ))}
          </div>
          <div className="h-2.5 rounded-[5px] bg-deal-gradient mb-2" />
          <div className="flex justify-between text-[11px] text-text-muted">
            <span>Seed<br />{dealSize.minDeal}</span>
            <span>Series A</span>
            <span>Series B</span>
            <span className="text-right">Series C+<br />{dealSize.maxDeal}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

