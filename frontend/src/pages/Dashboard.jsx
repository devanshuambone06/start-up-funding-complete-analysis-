import { useState, lazy, Suspense } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { TrendingUp } from 'lucide-react'
import Footer from '../components/Footer/Footer'

// Lazy-load all tab pages for better initial load performance
const ExecutiveDashboard  = lazy(() => import('./ExecutiveDashboard/ExecutiveDashboard'))
const FundingTrends       = lazy(() => import('./FundingTrends/FundingTrends'))
const SectorAnalysis      = lazy(() => import('./SectorAnalysis/SectorAnalysis'))
const StartupPerformance  = lazy(() => import('./StartupPerformance/StartupPerformance'))
const InvestorAnalytics   = lazy(() => import('./InvestorAnalytics/InvestorAnalytics'))
const InvestmentOpportunity = lazy(() => import('./InvestmentOpportunity/InvestmentOpportunity'))
const PredictiveAnalytics = lazy(() => import('./PredictiveAnalytics/PredictiveAnalytics'))
const Reports             = lazy(() => import('./Reports/Reports'))
const GeographicAnalysis  = lazy(() => import('./GeographicAnalysis/GeographicAnalysis'))

const TABS = [
  'Dashboard', 'Trends', 'Sectors', 'Startups',
  'Investors', 'Opportunity', 'Predict', 'Reports', 'Geographic',
]

function TabSpinner() {
  return (
    <div className="flex items-center justify-center py-24">
      <div className="w-8 h-8 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
    </div>
  )
}

export default function Dashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('Dashboard')
  const [dropdown, setDropdown] = useState(false)

  const initial = user?.email?.split('@')[0]?.charAt(0)?.toUpperCase() || 'U'
  const name = user?.name || user?.email?.split('@')[0] || 'User'

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const tabComponents = {
    Dashboard:   <ExecutiveDashboard />,
    Trends:      <FundingTrends />,
    Sectors:     <SectorAnalysis />,
    Startups:    <StartupPerformance />,
    Investors:   <InvestorAnalytics />,
    Opportunity: <InvestmentOpportunity />,
    Predict:     <PredictiveAnalytics />,
    Reports:     <Reports />,
    Geographic:  <GeographicAnalysis />,
  }

  return (
    <div className="min-h-screen bg-bg-base">
      {/* Navbar */}
      <nav className="bg-bg-panel border-b border-border sticky top-0 z-50">
        <div className="px-4 sm:px-6 py-3 flex items-center gap-4">
          {/* Logo */}
          <div className="flex items-center gap-2 shrink-0">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-blue-500 shadow-lg shadow-violet-900/40">
              <TrendingUp className="h-5 w-5 text-white" />
            </div>
            <span className="text-sm font-bold tracking-wide text-violet-300 hidden sm:inline">
              STARTUP FUNDING ANALYTICS
            </span>
          </div>

          {/* User Dropdown */}
          <div className="relative ml-auto">
            <button
              onClick={() => setDropdown((d) => !d)}
              className="flex items-center gap-2 bg-transparent border-none cursor-pointer px-2 py-1.5 rounded-lg hover:bg-white/5 transition-colors"
            >
              {user?.photoURL ? (
                <img src={user.photoURL} alt={name} className="w-8 h-8 rounded-full object-cover" />
              ) : (
                <div className="w-8 h-8 rounded-full bg-brand-purple flex items-center justify-center font-bold text-white text-sm">
                  {initial}
                </div>
              )}
              <span className="hidden sm:inline text-[13px] text-text-primary font-medium">{name}</span>
              <span className="text-text-muted text-[11px]">▾</span>
            </button>

            {dropdown && (
              <div
                className="absolute right-0 top-[110%] w-[220px] bg-bg-panel border border-border rounded-lg overflow-hidden shadow-2xl"
                onClick={() => setDropdown(false)}
              >
                <div className="px-4 py-3 border-b border-border">
                  <div className="font-semibold text-sm text-text-primary">{name}</div>
                  <div className="text-xs text-text-muted mt-0.5">{user?.email || user?.provider}</div>
                </div>
                <button
                  onClick={handleLogout}
                  className="w-full text-left px-4 py-2.5 bg-transparent border-none text-accent-red text-[13px] cursor-pointer hover:bg-white/5 transition-colors"
                >
                  ↩ Sign Out
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Tab Bar */}
        <div className="px-4 sm:px-6 flex gap-1 overflow-x-auto scrollbar-thin">
          {TABS.map((tab) => (
            <button
              key={tab}
              onClick={() => { setActiveTab(tab); setDropdown(false) }}
              className={`px-3.5 py-2.5 bg-transparent border-none cursor-pointer text-[13px] font-medium whitespace-nowrap transition-colors ${
                activeTab === tab
                  ? 'text-text-primary border-b-2 bg-gradient-to-b from-purple-600/20 to-blue-600/20 rounded-t-lg border-b-[#8181de] shadow-sm'
                  : 'text-text-muted border-b-2 border-transparent hover:text-text-primary'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </nav>

      {/* Tab Content */}
      <div className="p-4 sm:p-6">
        <Suspense fallback={<TabSpinner />}>
          {tabComponents[activeTab]}
        </Suspense>
      </div>

      <Footer onNavigate={setActiveTab} />
    </div>
  )
}
