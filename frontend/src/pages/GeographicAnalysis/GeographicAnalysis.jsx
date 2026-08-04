import React, { useState, useMemo, useEffect } from 'react'
import { MapPin, DollarSign, Building2, Users, TrendingUp, Filter } from 'lucide-react'
import { Card, SectionHeader, Badge } from '../../components/ui'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, PieChart, Pie, Cell, Legend } from 'recharts'
import { fetchGeographic } from '../../services/api'

const views = ['Funding', 'Startups', 'Growth']
const SORT_KEY = { Funding: 'funding', Startups: 'startups', Growth: 'growth' }

function parseRegion(region = '') {
  const parts = region.split(',').map((p) => p.trim())
  const country = parts[parts.length - 1] || ''
  const state = parts.slice(0, -1).join(', ') || ''
  return { state, country }
}

function uniqueSorted(arr) {
  return [...new Set(arr)].filter(Boolean).sort()
}

const DEFAULT_HUBS = [
  { region: 'Silicon Valley, California, USA', city: 'San Francisco', state: 'California', country: 'USA', funding: 345000000000, startups: 8420, growth: 24.5 },
  { region: 'New York City, New York, USA', city: 'New York', state: 'New York', country: 'USA', funding: 185000000000, startups: 4910, growth: 19.2 },
  { region: 'London, Greater London, GBR', city: 'London', state: 'Greater London', country: 'GBR', funding: 92000000000, startups: 3120, growth: 16.8 },
  { region: 'Bengaluru, Karnataka, IND', city: 'Bengaluru', state: 'Karnataka', country: 'IND', funding: 68000000000, startups: 2840, growth: 31.4 },
  { region: 'Berlin, Berlin, DEU', city: 'Berlin', state: 'Berlin', country: 'DEU', funding: 42000000000, startups: 1650, growth: 14.1 },
  { region: 'Singapore, Central Region, SGP', city: 'Singapore', state: 'Central Region', country: 'SGP', funding: 39000000000, startups: 1480, growth: 22.7 },
]
const DEFAULT_SECTOR_MIX = [
  { name: 'Fintech', value: 35 },
  { name: 'AI & Data', value: 28 },
  { name: 'HealthTech', value: 18 },
  { name: 'Enterprise', value: 12 },
  { name: 'Other', value: 7 },
]

export default function GeographicAnalysis() {
  const [view, setView] = useState('Growth')
  const [country, setCountry] = useState('All Countries')
  const [state, setState] = useState('All States')
  const [city, setCity] = useState('All Cities')
  const [hubs, setHubs] = useState(DEFAULT_HUBS)
  const [sectorMix, setSectorMix] = useState(DEFAULT_SECTOR_MIX)
  const [globalInvestors, setGlobalInvestors] = useState(13786)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchGeographic()
      .then((data) => {
        if (!data) return
        if (data.hubs?.length) {
          const mapped = data.hubs.map((h) => ({ ...h, ...parseRegion(h.region) }))
          setHubs(mapped)
        }
        if (data.sectorMix?.length) setSectorMix(data.sectorMix)
        if (data.summary?.investors) setGlobalInvestors(data.summary.investors)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const hubsWithLocation = useMemo(() => hubs.map((h) => ({ ...h, ...parseRegion(h.region) })), [hubs])

  const countryOptions = useMemo(() => ['All Countries', ...uniqueSorted(hubsWithLocation.map((h) => h.country))], [hubsWithLocation])
  const stateOptions = useMemo(() => {
    const pool = country === 'All Countries' ? hubsWithLocation : hubsWithLocation.filter((h) => h.country === country)
    return ['All States', ...uniqueSorted(pool.map((h) => h.state))]
  }, [country, hubsWithLocation])
  const cityOptions = useMemo(() => {
    let pool = hubsWithLocation
    if (country !== 'All Countries') pool = pool.filter((h) => h.country === country)
    if (state !== 'All States') pool = pool.filter((h) => h.state === state)
    return ['All Cities', ...uniqueSorted(pool.map((h) => h.city))]
  }, [country, state, hubsWithLocation])

  function handleCountryChange(value) { setCountry(value); setState('All States'); setCity('All Cities') }
  function handleStateChange(value) { setState(value); setCity('All Cities') }

  const filteredSorted = useMemo(() => {
    let rows = hubsWithLocation
    if (country !== 'All Countries') rows = rows.filter((h) => h.country === country)
    if (state !== 'All States') rows = rows.filter((h) => h.state === state)
    if (city !== 'All Cities') rows = rows.filter((h) => h.city === city)
    const key = SORT_KEY[view]
    return [...rows].sort((a, b) => (b[key] || 0) - (a[key] || 0))
  }, [country, state, city, view, hubsWithLocation])

  const stats = useMemo(() => {
    const totalFunding = filteredSorted.reduce((sum, h) => sum + (h.funding || h.fundingB || 0), 0)
    const totalStartups = filteredSorted.reduce((sum, h) => sum + (h.startups || 0), 0)
    const avgGrowth = filteredSorted.length ? filteredSorted.reduce((sum, h) => sum + (h.growth || 0), 0) / filteredSorted.length : 0
    return { totalfunding: totalFunding, hubs: filteredSorted.length, startups: totalStartups, avgYoyGrowth: avgGrowth, investors: globalInvestors }
  }, [filteredSorted, globalInvestors])

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <MapPin size={20} className="text-violet-400" /> Geographic Analysis
            {loading && <span className="text-violet-400 text-sm font-normal animate-pulse ml-2">Loading live data…</span>}
          </h1>
          <p className="text-slate-400 text-sm mt-1">Investment distribution across global startup hubs</p>
        </div>
        <div className="flex bg-slate-900 border border-slate-800 rounded-full p-1">
          {views.map((v) => (
            <button key={v} onClick={() => setView(v)} className={`px-4 py-1.5 rounded-full text-sm font-medium transition ${view === v ? 'bg-violet-600 text-white' : 'text-slate-400 hover:text-slate-200'}`}>{v}</button>
          ))}
        </div>
      </div>

      <Card>
        <div className="flex items-center gap-2 text-slate-400 text-sm mb-4"><Filter size={14} /> Filters</div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <FilterSelect label="Country" value={country} options={countryOptions} onChange={handleCountryChange} />
          <FilterSelect label="State / Region" value={state} options={stateOptions} onChange={handleStateChange} />
          <FilterSelect label="City" value={city} options={cityOptions} onChange={setCity} />
        </div>
      </Card>

      <div className="grid grid-cols-2 gap-4">
        <StatCard icon={DollarSign} label="Total Funding" value={`$${stats.totalfunding.toFixed(1)}B`} sub={`Across ${stats.hubs} hubs`} color="#8b5cf6" />
        <StatCard icon={Building2} label="Startups" value={stats.startups.toLocaleString()} sub="Active companies" color="#3b82f6" />
        <StatCard icon={Users} label="Investors" value={stats.investors.toLocaleString()} sub="Unique investors" color="#22d3a7" />
        <StatCard icon={TrendingUp} label="Avg YoY Growth" value={`+${stats.avgYoyGrowth.toFixed(1)}%`} sub="Year-over-year" color="#f5a623" />
      </div>

      <Card>
        <SectionHeader title="Top Investment Hubs" subtitle={`Sorted by ${view.toLowerCase()}`} />
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={filteredSorted.slice(0, 10)}>
              <XAxis dataKey="city" stroke="#475569" fontSize={10} tickLine angle={-20} textAnchor="end" height={50} />
              <YAxis stroke="#475569" fontSize={11} unit={view === 'Growth' ? '%' : ''} />
              <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8, color: '#e6edf3' }} cursor={{ fill: 'transparent' }} />
              <Bar dataKey={SORT_KEY[view]} radius={[6, 6, 0, 0]} fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card>
        <SectionHeader title="Sector Mix" subtitle="Funding distribution by sector" />
        <div className="h-64 flex items-center justify-center">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={sectorMix} dataKey="value" nameKey="name" innerRadius={60} outerRadius={90} paddingAngle={2}>
                {sectorMix.map((s) => <Cell key={s.name} fill={s.color} />)}
              </Pie>
              <Legend verticalAlign="bottom" formatter={(value) => <span className="text-slate-400 text-xs">{value}</span>} />
              <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </Card>

      <Card>
        <SectionHeader title="Hub Detail" subtitle={`Top 8 hubs — sorted by ${view.toLowerCase()}, filtered view`} />
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500 text-xs uppercase tracking-wide border-b border-slate-800">
                <th className="pb-3 font-medium">#</th>
                <th className="pb-3 font-medium">City</th>
                <th className="pb-3 font-medium">Funding</th>
                <th className="pb-3 font-medium">Startups</th>
                <th className="pb-3 font-medium text-right">Growth</th>
              </tr>
            </thead>
            <tbody>
              {filteredSorted.slice(0, 8).map((h, i) => (
                <tr key={h.city} className="border-b border-slate-800/60 last:border-0">
                  <td className="py-3"><span className="w-6 h-6 rounded-full bg-violet-500/15 text-violet-300 text-xs flex items-center justify-center">{i + 1}</span></td>
                  <td className="py-3"><p className="text-slate-200 font-medium">{h.city}</p><p className="text-slate-500 text-xs">{h.region}</p></td>
                  <td className="py-3 text-violet-300 font-mono">${(h.funding || h.fundingB || 0).toFixed(1)}B</td>
                  <td className="py-3 text-slate-300">{h.startups}</td>
                  <td className="py-3 text-right"><Badge tone="green">+{h.growth}%</Badge></td>
                </tr>
              ))}
              {filteredSorted.length === 0 && (
                <tr><td colSpan={5} className="py-6 text-center text-slate-500 text-sm">No hubs match the selected filters.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}

function FilterSelect({ label, value, options, onChange }) {
  return (
    <div>
      <label className="text-slate-500 text-xs mb-1.5 block">{label}</label>
      <select className="input" value={value} onChange={(e) => onChange(e.target.value)}>
        {options.map((o) => <option key={o}>{o}</option>)}
      </select>
    </div>
  )
}

function StatCard({ icon: Icon, label, value, sub, color }) {
  return (
    <Card className="!p-5">
      <div className="flex items-center justify-between mb-3">
        <span className="text-slate-500 text-xs uppercase tracking-wide">{label}</span>
        <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${color}22`, color }}><Icon size={14} /></div>
      </div>
      <p className="text-2xl font-bold" style={{ color }}>{value}</p>
      <p className="text-slate-500 text-xs mt-1">{sub}</p>
    </Card>
  )
}
