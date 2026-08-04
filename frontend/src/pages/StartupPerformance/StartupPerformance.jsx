import React, { useMemo, useState, useRef, useEffect } from 'react'
import { Search, Filter, Download, ChevronDown, ArrowUpDown } from 'lucide-react'
import { fetchStartups, getExportUrl, addStartup } from '../../services/api'

const sectorColors = {
  Fintech: '#3b82f6', HealthTech: '#22d3a7', 'AI & ML': '#8b5cf6',
  AI: '#8b5cf6', CleanTech: '#06b6d4', EdTech: '#ec4899', 'E-commerce': '#f5a623',
}
const stages = ['All Stages', 'Seed', 'Series A', 'Series B', 'Series C+']
function sectorStyle(sector) {
  const c = sectorColors[sector] || '#64748b'
  return { color: c, backgroundColor: c + '22', borderColor: c + '55' }
}

const DEFAULT_DB_STARTUPS = [
  { name: 'Stripe', sector: 'Fintech', stage: 'Series I', country: 'USA', totalFundingUSD: 8700000000, fundingRaised: '$8.7B', rounds: 19, isSuccessful: true },
  { name: 'Databricks', sector: 'AI & ML', stage: 'Series H', country: 'USA', totalFundingUSD: 4200000000, fundingRaised: '$4.2B', rounds: 11, isSuccessful: true },
  { name: 'SpaceX', sector: 'DeepTech', stage: 'Series C+', country: 'USA', totalFundingUSD: 9870000000, fundingRaised: '$9.87B', rounds: 24, isSuccessful: true },
  { name: 'Revolut', sector: 'Fintech', stage: 'Series E', country: 'GBR', totalFundingUSD: 1700000000, fundingRaised: '$1.7B', rounds: 8, isSuccessful: true },
  { name: 'Scale AI', sector: 'AI & ML', stage: 'Series F', country: 'USA', totalFundingUSD: 1600000000, fundingRaised: '$1.6B', rounds: 7, isSuccessful: true },
  { name: 'Canva', sector: 'E-commerce', stage: 'Series C+', country: 'AUS', totalFundingUSD: 560000000, fundingRaised: '$560M', rounds: 5, isSuccessful: true },
  { name: 'Razorpay', sector: 'Fintech', stage: 'Series F', country: 'IND', totalFundingUSD: 741000000, fundingRaised: '$741M', rounds: 9, isSuccessful: true },
  { name: 'BioNTech', sector: 'HealthTech', stage: 'Series B', country: 'DEU', totalFundingUSD: 1500000000, fundingRaised: '$1.5B', rounds: 6, isSuccessful: true },
  { name: 'Figma', sector: 'AI & ML', stage: 'Series E', country: 'USA', totalFundingUSD: 330000000, fundingRaised: '$330M', rounds: 5, isSuccessful: true },
  { name: 'Wiz', sector: 'AI & ML', stage: 'Series D', country: 'USA', totalFundingUSD: 900000000, fundingRaised: '$900M', rounds: 4, isSuccessful: true },
  { name: 'Notion', sector: 'AI & ML', stage: 'Series C', country: 'USA', totalFundingUSD: 343000000, fundingRaised: '$343M', rounds: 4, isSuccessful: true },
  { name: 'Zerodha', sector: 'Fintech', stage: 'Seed', country: 'IND', totalFundingUSD: 0, fundingRaised: '$0 (Bootstrapped)', rounds: 0, isSuccessful: true },
  { name: 'Meesho', sector: 'E-commerce', stage: 'Series F', country: 'IND', totalFundingUSD: 1100000000, fundingRaised: '$1.1B', rounds: 8, isSuccessful: true },
  { name: 'N26', sector: 'Fintech', stage: 'Series E', country: 'DEU', totalFundingUSD: 1100000000, fundingRaised: '$1.1B', rounds: 7, isSuccessful: false },
  { name: 'Ola Electric', sector: 'CleanTech', stage: 'Series C+', country: 'IND', totalFundingUSD: 920000000, fundingRaised: '$920M', rounds: 6, isSuccessful: true },
]

export default function StartupPerformance() {
  const [query, setQuery] = useState('')
  const [stage, setStage] = useState('All Stages')
  const [open, setOpen] = useState(false)
  const [sortDesc, setSortDesc] = useState(true)
  const [allStartups, setAllStartups] = useState(DEFAULT_DB_STARTUPS)
  const [loading, setLoading] = useState(false)
  const [showAddModal, setShowAddModal] = useState(false)
  const [addForm, setAddForm] = useState({
    name: '',
    sector: 'AI',
    country: 'USA',
    fundingRaised: '',
    rounds: '1',
    isSuccessful: false
  })
  const [addError, setAddError] = useState('')
  const [adding, setAdding] = useState(false)
  const dropdownRef = useRef(null)

  useEffect(() => {
    function onClick(e) { if (dropdownRef.current && !dropdownRef.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', onClick)
    return () => document.removeEventListener('mousedown', onClick)
  }, [])

  useEffect(() => {
    fetchStartups({ limit: 200 })
      .then((res) => { if (res?.data?.length) setAllStartups(res.data) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    let rows = allStartups.filter((s) => {
      const matchesQuery = !q || s.name?.toLowerCase().includes(q) || s.sector?.toLowerCase().includes(q)
      const matchesStage = stage === 'All Stages' || s.stage === stage
      return matchesQuery && matchesStage
    })
    rows = [...rows].sort((a, b) => sortDesc ? (b.totalFundingUSD || 0) - (a.totalFundingUSD || 0) : (a.totalFundingUSD || 0) - (b.totalFundingUSD || 0))
    return rows
  }, [query, stage, sortDesc, allStartups])

  const handleExport = () => { window.open(getExportUrl(), '_blank') }

  const handleAddSubmit = async (e) => {
    e.preventDefault()
    setAddError('')
    if (!addForm.name.trim()) {
      setAddError('Startup Name is required')
      return
    }
    const val = parseFloat(addForm.fundingRaised)
    if (isNaN(val) || val < 0) {
      setAddError('Please enter a valid funding amount')
      return
    }
    
    setAdding(true)
    try {
      const res = await addStartup({
        name: addForm.name,
        sector: addForm.sector,
        country: addForm.country,
        fundingRaised: val,
        rounds: parseInt(addForm.rounds, 10),
        isSuccessful: addForm.isSuccessful
      })
      if (res?.status === 'success' && res.data) {
        setAllStartups((prev) => [res.data, ...prev])
        setShowAddModal(false)
        setAddForm({
          name: '',
          sector: 'AI',
          country: 'USA',
          fundingRaised: '',
          rounds: '1',
          isSuccessful: false
        })
      } else {
        setAddError('Failed to add startup record')
      }
    } catch (err) {
      setAddError(err?.message || 'Error communicating with server')
    } finally {
      setAdding(false)
    }
  }

  return (
    <div style={{ background: '#050715', minHeight: '100vh', fontFamily: 'Inter, system-ui, sans-serif' }} className="p-6">
      <div style={{ background: '#0d1220', border: '1px solid #1c2333' }} className="rounded-2xl p-6 max-w-5xl mx-auto">
        <div className="flex justify-between items-center mb-5">
          <h2 className="text-white text-2xl font-semibold">Startup Database</h2>
          {loading && <span className="text-violet-400 text-sm animate-pulse">Loading live data…</span>}
        </div>
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 mb-6">
          <div className="relative flex-1 min-w-[200px]">
            <Search size={18} style={{ color: '#5b6478' }} className="absolute left-3 top-1/2 -translate-y-1/2" />
            <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search by company or sector..." style={{ background: '#11172a', border: '1px solid #212940', color: '#fff' }} className="w-full pl-10 pr-3 py-2.5 rounded-xl text-sm placeholder:text-[#5b6478] outline-none focus:border-[#3b82f6] transition-colors" />
          </div>
          <div className="relative" ref={dropdownRef}>
            <button onClick={() => setOpen((o) => !o)} style={{ background: '#11172a', border: '1px solid #212940', color: '#fff' }} className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm whitespace-nowrap hover:border-[#3b82f6] transition-colors">
              <Filter size={16} style={{ color: '#5b6478' }} />{stage}
              <ChevronDown size={16} style={{ color: '#5b6478', transform: open ? 'rotate(180deg)' : 'none', transition: 'transform .15s' }} />
            </button>
            {open && (
              <div style={{ background: 'transparent', backdropFilter: 'blur(10px)', border: '1px solid #212940' }} className="absolute right-0 sm:left-0 mt-2 w-44 rounded-xl overflow-hidden z-20 shadow-2xl">
                {stages.map((s) => (
                  <button key={s} onClick={() => { setStage(s); setOpen(false) }} style={{ background: s === stage ? 'rgba(255,255,255,0.08)' : 'transparent', color: '#fff' }} className="w-full text-left px-4 py-2.5 text-sm hover:bg-white/10 transition-colors">{s}</button>
                ))}
              </div>
            )}
          </div>
          <button onClick={handleExport} className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-blue-500 border border-[#2b3760] text-white hover:bg-blue-700 transition-all duration-300 whitespace-nowrap">
            <Download size={16} /> Export CSV
          </button>
          <button onClick={() => setShowAddModal(true)} className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 text-white hover:from-violet-700 hover:to-indigo-700 transition-all duration-300 whitespace-nowrap">
            ➕ Add Startup
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr style={{ borderBottom: '1px solid #1c2333' }}>
                <th className="text-left py-3 font-medium" style={{ color: '#7c8497' }}>
                  <button onClick={() => setSortDesc((d) => !d)} className="flex items-center gap-1 hover:text-white transition-colors">COMPANY <ArrowUpDown size={12} /></button>
                </th>
                <th className="text-left py-3 font-medium" style={{ color: '#7c8497' }}>SECTOR</th>
                <th className="text-left py-3 font-medium" style={{ color: '#7c8497' }}>STAGE</th>
                <th className="text-right py-3 font-medium" style={{ color: '#7c8497' }}>TOTAL FUNDING</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr><td colSpan={4} className="text-center py-8" style={{ color: '#5b6478' }}>{loading ? 'Loading…' : 'No startups match your search.'}</td></tr>
              ) : (
                filtered.map((s) => (
                  <tr key={s.id || s.name} style={{ borderBottom: '1px solid #151b2b' }}>
                    <td className="py-3.5 text-white font-medium">{s.name}</td>
                    <td className="py-3.5"><span style={sectorStyle(s.sector)} className="inline-block px-2.5 py-1 rounded-md text-xs border">{s.sector}</span></td>
                    <td className="py-3.5" style={{ color: '#c3c8d4' }}>{s.stage}</td>
                    <td className="py-3.5 text-right text-white font-semibold">{s.totalFunding}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showAddModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div style={{ background: '#0d1220', border: '1px solid #1c2333' }} className="w-full max-w-md rounded-2xl p-6 shadow-2xl relative">
            <h3 className="text-white text-xl font-semibold mb-4">Add New Startup Record</h3>
            
            {addError && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3 text-red-400 text-xs mb-4">
                ⚠️ {addError}
              </div>
            )}
            
            <form onSubmit={handleAddSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Startup Name</label>
                <input
                  type="text"
                  required
                  value={addForm.name}
                  onChange={(e) => setAddForm(f => ({ ...f, name: e.target.value }))}
                  style={{ background: '#11172a', border: '1px solid #212940', color: '#fff' }}
                  className="w-full px-3.5 py-2.5 rounded-xl text-sm outline-none focus:border-[#3b82f6]"
                  placeholder="e.g. Acme Corp"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Sector</label>
                  <select
                    value={addForm.sector}
                    onChange={(e) => setAddForm(f => ({ ...f, sector: e.target.value }))}
                    style={{ background: '#11172a', border: '1px solid #212940', color: '#fff' }}
                    className="w-full px-3.5 py-2.5 rounded-xl text-sm outline-none focus:border-[#3b82f6]"
                  >
                    <option value="AI">AI</option>
                    <option value="Fintech">Fintech</option>
                    <option value="HealthTech">HealthTech</option>
                    <option value="CleanTech">CleanTech</option>
                    <option value="EdTech">EdTech</option>
                    <option value="E-commerce">E-commerce</option>
                    <option value="Cybersecurity">Cybersecurity</option>
                    <option value="DeepTech">DeepTech</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Country</label>
                  <input
                    type="text"
                    required
                    value={addForm.country}
                    onChange={(e) => setAddForm(f => ({ ...f, country: e.target.value.toUpperCase() }))}
                    style={{ background: '#11172a', border: '1px solid #212940', color: '#fff' }}
                    className="w-full px-3.5 py-2.5 rounded-xl text-sm outline-none focus:border-[#3b82f6]"
                    placeholder="e.g. USA"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Funding (USD)</label>
                  <input
                    type="number"
                    required
                    value={addForm.fundingRaised}
                    onChange={(e) => setAddForm(f => ({ ...f, fundingRaised: e.target.value }))}
                    style={{ background: '#11172a', border: '1px solid #212940', color: '#fff' }}
                    className="w-full px-3.5 py-2.5 rounded-xl text-sm outline-none focus:border-[#3b82f6]"
                    placeholder="e.g. 5000000"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Funding Rounds</label>
                  <input
                    type="number"
                    required
                    min="1"
                    value={addForm.rounds}
                    onChange={(e) => setAddForm(f => ({ ...f, rounds: e.target.value }))}
                    style={{ background: '#11172a', border: '1px solid #212940', color: '#fff' }}
                    className="w-full px-3.5 py-2.5 rounded-xl text-sm outline-none focus:border-[#3b82f6]"
                  />
                </div>
              </div>

              <div className="flex items-center gap-2 pt-2">
                <input
                  type="checkbox"
                  id="isSuccessful"
                  checked={addForm.isSuccessful}
                  onChange={(e) => setAddForm(f => ({ ...f, isSuccessful: e.target.checked }))}
                  className="rounded border-gray-700 bg-[#11172a] text-[#3b82f6] focus:ring-0"
                />
                <label htmlFor="isSuccessful" className="text-sm text-gray-300 cursor-pointer">Has exited successfully? (Acquired / IPO)</label>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-[#1c2333]">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  style={{ border: '1px solid #212940', color: '#94a3b8' }}
                  className="px-4 py-2 rounded-xl text-sm hover:bg-white/5 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={adding}
                  className="px-4 py-2 rounded-xl text-sm bg-gradient-to-r from-violet-600 to-indigo-600 text-white hover:from-violet-700 hover:to-indigo-700 transition-colors"
                >
                  {adding ? 'Saving...' : 'Save Startup'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}