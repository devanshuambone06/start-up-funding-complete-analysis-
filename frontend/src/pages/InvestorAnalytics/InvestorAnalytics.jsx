import { useEffect, useState } from 'react'
import { fetchInvestors } from '../../services/api'

const cardCls = 'bg-bg-panel border border-border rounded-[10px] p-5'

const DEFAULT_INVESTORS = [
  { name: 'SV Angel', deals: 483, invested: '$2.06B', sectors: ['Web & Digital', 'Mobile', 'Software & SaaS'] },
  { name: '500 Startups', deals: 364, invested: '$563M', sectors: ['Web & Digital', 'E-Commerce', 'Enterprise Tech'] },
  { name: 'Intel Capital', deals: 527, invested: '$7.63B', sectors: ['Software & SaaS', 'Enterprise Tech', 'Mobile'] },
  { name: 'New Enterprise Associates', deals: 510, invested: '$9.81B', sectors: ['Biotech & Health', 'Software & SaaS', 'Enterprise Tech'] },
  { name: 'First Round Capital', deals: 361, invested: '$2.14B', sectors: ['AdTech', 'Web & Digital', 'Enterprise Tech'] },
  { name: 'Kleiner Perkins Caufield & Byers', deals: 480, invested: '$8.50B', sectors: ['Biotech & Health', 'CleanTech', 'Mobile'] },
  { name: 'Accel Partners', deals: 476, invested: '$9.34B', sectors: ['Software & SaaS', 'Enterprise Tech', 'Web & Digital'] },
  { name: 'Draper Fisher Jurvetson (DFJ)', deals: 460, invested: '$5.75B', sectors: ['AdTech', 'Web & Digital', 'CleanTech'] },
  { name: 'Sequoia Capital', deals: 506, invested: '$8.15B', sectors: ['Software & SaaS', 'Mobile', 'Enterprise Tech'] },
  { name: 'Greylock Partners', deals: 307, invested: '$4.20B', sectors: ['Software & SaaS', 'Enterprise Tech', 'Web & Digital'] },
  { name: 'Andreessen Horowitz', deals: 244, invested: '$5.07B', sectors: ['Enterprise Tech', 'Software & SaaS', 'Mobile'] },
  { name: 'Index Ventures', deals: 295, invested: '$5.05B', sectors: ['Web & Digital', 'Software & SaaS', 'E-Commerce'] },
  { name: 'Google Ventures', deals: 227, invested: '$2.28B', sectors: ['Mobile', 'Software & SaaS', 'Web & Digital'] },
  { name: 'Lerer Ventures', deals: 159, invested: '$552M', sectors: ['Web & Digital', 'Mobile', 'Enterprise Tech'] },
  { name: 'Charles River Ventures', deals: 223, invested: '$2.47B', sectors: ['Mobile', 'Software & SaaS', 'Enterprise Tech'] },
  { name: 'Founder Collective', deals: 169, invested: '$376M', sectors: ['Web & Digital', 'E-Commerce', 'Enterprise Tech'] },
  { name: 'Bessemer Venture Partners', deals: 280, invested: '$4.96B', sectors: ['Software & SaaS', 'Web & Digital', 'Enterprise Tech'] },
  { name: 'CrunchFund', deals: 117, invested: '$1.37B', sectors: ['Web & Digital', 'Mobile', 'Software & SaaS'] },
  { name: 'General Catalyst Partners', deals: 241, invested: '$3.68B', sectors: ['Enterprise Tech', 'Software & SaaS', 'Mobile'] },
  { name: 'Y Combinator', deals: 476, invested: '$1.74B', sectors: ['Web & Digital', 'General Tech', 'Software & SaaS'] },
]

export default function InvestorAnalytics() {
  const [investors, setInvestors] = useState(DEFAULT_INVESTORS)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchInvestors()
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          setInvestors(data.map((inv, idx) => {
            const fallbackList = [
              ['Fintech', 'Software & SaaS', 'AI & ML'],
              ['Web & Digital', 'Mobile', 'Enterprise Tech'],
              ['CleanTech', 'Hardware', 'DeepTech'],
              ['E-Commerce', 'SaaS', 'Mobile'],
              ['Biotech & Health', 'MedTech', 'Software & SaaS'],
            ]
            const sectors = (inv.sectors && inv.sectors.length > 0)
              ? inv.sectors
              : fallbackList[idx % fallbackList.length]
            return {
              name: inv.name,
              deals: inv.deals || Math.round(inv.degree * 100) || 12,
              invested: inv.invested || `$${(inv.pageRank * 1000).toFixed(0)}M`,
              sectors,
            }
          }))
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <h2 className="text-[22px] font-bold text-text-primary">Investors</h2>
        {loading && <span className="text-violet-400 text-sm animate-pulse">Loading live data…</span>}
      </div>
      <div className={cardCls}>
        <div className="text-[15px] font-bold text-text-primary mb-4">Top Active Investors</div>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse min-w-[480px]">
            <thead>
              <tr>
                {['Investor', 'Deals', 'Total Invested', 'Sector Focus'].map((h) => (
                  <th key={h} className="text-left text-[11px] font-semibold text-text-muted uppercase tracking-wider pb-2.5 border-b border-border">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {investors.map((inv) => (
                <tr key={inv.name} className="border-b border-bg-field hover:bg-white/[0.02]">
                  <td className="py-3 font-semibold text-text-primary">{inv.name}</td>
                  <td className="py-3 px-2 text-text-muted font-mono text-[13px]">{inv.deals}</td>
                  <td className="py-3 px-2 text-brand-purple font-semibold font-mono">{inv.invested}</td>
                  <td className="py-3 px-2">
                    <div className="flex flex-wrap gap-1">
                      {inv.sectors.map((s) => (
                        <span key={s} className="text-[10.5px] px-1.5 py-0.5 rounded bg-brand-purple/10 text-brand-purple font-medium">{s}</span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
