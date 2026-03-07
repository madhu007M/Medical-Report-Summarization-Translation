'use client'
import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  MapPin, AlertTriangle, TrendingUp, Users, Search,
  RefreshCw, Activity, Zap, ShieldAlert, BadgeAlert, CheckCircle2, Loader2,
  Bell, User, Calendar, Stethoscope
} from 'lucide-react'
import Navbar from '@/components/Navbar'
import { getOutbreaks, getDoctorAlerts } from '@/lib/api'

const MOCK_CLUSTERS = [
  { location: 'Mumbai, Maharashtra', suspected_cause: 'H3N2 Influenza', cases: 42, risk_score: 0.76, trend: 'rising' },
  { location: 'Bengaluru, Karnataka', suspected_cause: 'Dengue Fever', cases: 28, risk_score: 0.55, trend: 'stable' },
  { location: 'Delhi NCR', suspected_cause: 'COVID-19 Subvariant', cases: 61, risk_score: 0.82, trend: 'rising' },
  { location: 'Chennai, Tamil Nadu', suspected_cause: 'Chikungunya', cases: 14, risk_score: 0.33, trend: 'declining' },
  { location: 'Hyderabad, Telangana', suspected_cause: 'Cholera (suspected)', cases: 9, risk_score: 0.48, trend: 'stable' },
]

const STATS = [
  { label: 'Active Alerts',    val: '5',   icon: <BadgeAlert className="w-5 h-5 text-rose-400" />,    color: 'text-rose-400' },
  { label: 'Regions Monitored', val: '28',  icon: <MapPin className="w-5 h-5 text-teal-400" />,         color: 'text-teal-400' },
  { label: 'Cases Tracked',    val: '154',  icon: <Users className="w-5 h-5 text-cyan-400" />,           color: 'text-cyan-400' },
  { label: 'Risk Score Avg',   val: '0.59', icon: <TrendingUp className="w-5 h-5 text-amber-400" />,   color: 'text-amber-400' },
]

type Cluster = typeof MOCK_CLUSTERS[0]

function RiskBar({ pct, color }: { pct: number; color: string }) {
  return (
    <div className="h-2 w-full rounded-full bg-black/30 overflow-hidden">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${pct}%` }}
        transition={{ duration: 1.2, ease: 'easeOut' }}
        className="h-full rounded-full"
        style={{ background: `linear-gradient(90deg, ${color}88, ${color})` }}
      />
    </div>
  )
}

function OutbreakCard({ c, delay }: { c: Cluster; delay: number }) {
  const pct = Math.round(c.risk_score * 100)
  const color = pct >= 70 ? '#EF4444' : pct >= 40 ? '#F59E0B' : '#22C55E'
  const lvl   = pct >= 70 ? 'High' : pct >= 40 ? 'Moderate' : 'Low'
  const TrendIcon = c.trend === 'rising' ? TrendingUp : c.trend === 'declining' ? Activity : Activity

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.4 }}
      whileHover={{ y: -3, boxShadow: '0 12px 30px rgba(0,0,0,0.3)' }}
      className="glass border border-white/8 rounded-2xl p-5 card-hover"
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center gap-1.5 mb-1">
            <MapPin className="w-3.5 h-3.5 text-slate-500 flex-shrink-0" />
            <span className="font-semibold text-white text-sm">{c.location}</span>
          </div>
          <p className="text-slate-500 text-xs">Cause: <span className="text-slate-300">{c.suspected_cause}</span></p>
        </div>
        <div className="flex flex-col items-end gap-1">
          <span className="text-xs font-bold px-2 py-0.5 rounded-lg" style={{ background: `${color}22`, color }}>
            {lvl}
          </span>
          <span className="text-[10px] text-slate-600 flex items-center gap-1">
            <TrendIcon className="w-3 h-3" />
            {c.trend}
          </span>
        </div>
      </div>

      <RiskBar pct={pct} color={color} />

      <div className="flex items-center justify-between mt-3">
        <div className="flex items-center gap-1.5 text-xs text-slate-500">
          <Users className="w-3.5 h-3.5" />
          <span><span className="text-white font-semibold">{c.cases}</span> reported cases</span>
        </div>
        <span className="text-sm font-bold" style={{ color }}>{pct}%</span>
      </div>
    </motion.div>
  )
}

const PRIORITY_CFG = {
  high:     { color: 'text-rose-400',    bg: 'bg-rose-500/10 border-rose-500/30',     dot: 'bg-rose-500',    label: 'High',     leftColor: '#EF4444' },
  moderate: { color: 'text-amber-400',   bg: 'bg-amber-500/10 border-amber-500/30',   dot: 'bg-amber-500',   label: 'Moderate', leftColor: '#F59E0B' },
  low:      { color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/30', dot: 'bg-emerald-500', label: 'Low',      leftColor: '#22C55E' },
}

type DoctorAlert = { id?: number; doctor: string; title: string; message: string; region: string; created_at: string; priority?: string }

function timeAgo(dateStr: string): string {
  try {
    const diff = Date.now() - new Date(dateStr).getTime()
    const mins = Math.floor(diff / 60000)
    if (mins < 1) return 'Just now'
    if (mins < 60) return `${mins}m ago`
    const hours = Math.floor(mins / 60)
    if (hours < 24) return `${hours}h ago`
    return `${Math.floor(hours / 24)}d ago`
  } catch { return dateStr }
}

function DoctorAlertCard({ a, delay }: { a: DoctorAlert; delay: number }) {
  const priorityKey = (a.priority ?? 'moderate') as keyof typeof PRIORITY_CFG
  const cfg = PRIORITY_CFG[priorityKey] ?? PRIORITY_CFG.moderate
  const when = timeAgo(a.created_at)
  return (
    <motion.div
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay, duration: 0.35 }}
      className={`relative rounded-xl border p-4 bg-slate-800/80 overflow-hidden ${cfg.bg}`}
      style={{ borderLeftColor: cfg.leftColor, borderLeftWidth: '3px' }}
    >
      <div className="flex items-start justify-between gap-2 mb-1.5">
        <div className="flex items-center gap-2">
          <motion.div
            animate={{ scale: [1, 1.4, 1] }}
            transition={{ repeat: Infinity, duration: 2, delay }}
            className={`w-2 h-2 rounded-full flex-shrink-0 ${cfg.dot}`}
          />
          <span className="font-bold text-white text-sm leading-tight">{a.title}</span>
        </div>
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-lg border flex-shrink-0 ${cfg.bg} ${cfg.color}`}>
          {cfg.label}
        </span>
      </div>
      <p className="text-slate-300 text-sm leading-relaxed ml-4 mb-2">{a.message}</p>
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs ml-4">
        <span className="flex items-center gap-1 text-slate-400"><Stethoscope className="w-3 h-3 text-teal-400" />{a.doctor}</span>
        <span className="flex items-center gap-1 text-slate-400"><MapPin className="w-3 h-3 text-rose-400" />{a.region}</span>
        <span className="flex items-center gap-1 ml-auto text-slate-500"><Calendar className="w-3 h-3" />{when}</span>
      </div>
    </motion.div>
  )
}

export default function CommunityPage() {
  const [region, setRegion] = useState('')
  const [clusters, setClusters] = useState<Cluster[]>(MOCK_CLUSTERS)
  const [loading, setLoading] = useState(false)
  const [scanned, setScanned] = useState(false)
  const [doctorAlerts, setDoctorAlerts] = useState<DoctorAlert[]>([])
  const [alertsLoading, setAlertsLoading] = useState(false)
  const [toast, setToast] = useState<{ title: string; region: string } | null>(null)
  const prevCountRef = React.useRef(0)

  const loadDoctorAlerts = async (rgn = '', showToast = false) => {
    setAlertsLoading(true)
    try {
      const data = await getDoctorAlerts(rgn)
      const incoming: DoctorAlert[] = data?.alerts ?? []
      if (showToast && incoming.length > prevCountRef.current && incoming.length > 0) {
        const newest = incoming[0]
        setToast({ title: newest.title, region: newest.region })
        setTimeout(() => setToast(null), 4000)
      }
      prevCountRef.current = incoming.length
      setDoctorAlerts(incoming)
    } catch {
      setDoctorAlerts([])
    } finally {
      setAlertsLoading(false)
    }
  }

  useEffect(() => {
    loadDoctorAlerts()
    const interval = setInterval(() => loadDoctorAlerts('', true), 15000)
    return () => clearInterval(interval)
  }, [])

  const scan = async () => {
    setLoading(true)
    try {
      const data = await getOutbreaks(region)
      if (data?.clusters?.length) setClusters(data.clusters)
      else setClusters(MOCK_CLUSTERS)
    } catch {
      setClusters(MOCK_CLUSTERS)
    } finally {
      setLoading(false)
      setScanned(true)
    }
    await loadDoctorAlerts(region)
  }

  const filtered = region.trim()
    ? clusters.filter(c => c.location.toLowerCase().includes(region.toLowerCase()))
    : clusters

  return (
    <div className="min-h-screen bg-[#020817] grid-bg">
      <div className="absolute inset-0 bg-hero-gradient pointer-events-none" />
      <Navbar />

      {/* Alert toast popup */}
      <AnimatePresence>
        {toast && (
          <motion.div
            key="toast"
            initial={{ opacity: 0, y: -60, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -40, scale: 0.9 }}
            transition={{ type: 'spring', stiffness: 300, damping: 24 }}
            className="fixed top-20 right-5 z-50 flex items-start gap-3 bg-indigo-600/95 backdrop-blur-sm border border-indigo-400/40 text-white rounded-2xl shadow-2xl px-5 py-4 max-w-sm"
          >
            <div className="w-9 h-9 rounded-xl bg-white/15 flex items-center justify-center flex-shrink-0">
              <Bell className="w-4.5 h-4.5 text-white" />
            </div>
            <div>
              <p className="font-bold text-sm">New Doctor Alert</p>
              <p className="text-indigo-200 text-xs mt-0.5">{toast.title} — {toast.region}</p>
            </div>
            <button onClick={() => setToast(null)} className="ml-auto text-indigo-300 hover:text-white text-lg leading-none">×</button>
          </motion.div>
        )}
      </AnimatePresence>

      <main className="relative max-w-6xl mx-auto px-4 pt-24 pb-16">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-rose-500 to-orange-500 flex items-center justify-center">
              <ShieldAlert className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight">
              Community <span className="gradient-text">Health Monitor</span>
            </h1>
          </div>
          <p className="text-slate-400 ml-[52px]">Real-time disease cluster detection and regional outbreak intelligence</p>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8"
        >
          {STATS.map(({ label, val, icon, color }, i) => (
            <motion.div
              key={label}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.08 }}
              whileHover={{ scale: 1.04 }}
              className="glass border border-white/8 rounded-2xl p-4 text-center"
            >
              <div className="flex justify-center mb-2">{icon}</div>
              <div className={`text-2xl font-black ${color} mb-0.5`}>{val}</div>
              <div className="text-slate-500 text-xs">{label}</div>
            </motion.div>
          ))}
        </motion.div>

        {/* Doctor Alerts Feed — LIVE */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-rose-500 to-orange-500 flex items-center justify-center shadow-lg">
                <Bell className="w-4 h-4 text-white" />
              </div>
              <h2 className="text-xl font-bold text-white">Doctor Alerts</h2>
              <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-rose-500/15 border border-rose-500/30">
                <motion.div
                  animate={{ opacity: [1, 0.3, 1] }}
                  transition={{ repeat: Infinity, duration: 1.4 }}
                  className="w-1.5 h-1.5 rounded-full bg-rose-400"
                />
                <span className="text-xs font-bold text-rose-400">LIVE</span>
              </div>
              {doctorAlerts.length > 0 && (
                <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30">
                  {doctorAlerts.length}
                </span>
              )}
            </div>
            <motion.button
              whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}
              onClick={() => loadDoctorAlerts(region)}
              disabled={alertsLoading}
              className="glass border border-white/10 px-3 py-1.5 rounded-xl text-xs text-slate-400 hover:text-white flex items-center gap-1.5 transition-colors"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${alertsLoading ? 'animate-spin text-teal-400' : ''}`} />
              Refresh
            </motion.button>
          </div>

          {alertsLoading && doctorAlerts.length === 0 ? (
            <div className="flex items-center gap-2 text-slate-500 text-sm py-6 px-2">
              <Loader2 className="w-4 h-4 animate-spin" /> Loading alerts…
            </div>
          ) : doctorAlerts.length === 0 ? (
            <div className="border border-white/8 rounded-2xl p-8 text-center bg-slate-900/50">
              <Bell className="w-10 h-10 mx-auto mb-3 text-slate-700" />
              <p className="text-slate-400 text-sm font-medium">No doctor alerts yet</p>
              <p className="text-slate-600 text-xs mt-1">Alerts posted from the Doctor Dashboard will appear here automatically.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {doctorAlerts.map((a, i) => (
                <DoctorAlertCard key={a.id ?? `${a.created_at}-${i}`} a={a} delay={i * 0.05} />
              ))}
            </div>
          )}
        </motion.div>

        {/* Search + Scan */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="glass border border-white/8 rounded-2xl p-5 mb-6 flex flex-col sm:flex-row gap-3"
        >
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              value={region}
              onChange={e => setRegion(e.target.value)}
              placeholder="Filter by city or region (e.g. Mumbai, Delhi…)"
              className="w-full pl-9 pr-4 py-2.5 glass border border-white/10 rounded-xl text-sm text-slate-200 bg-transparent placeholder-slate-600 focus:outline-none focus:border-teal-500/50"
            />
          </div>
          <motion.button
            whileHover={{ scale: 1.03 }}
            whileTap={{ scale: 0.97 }}
            onClick={scan}
            disabled={loading}
            className="btn-teal px-5 py-2.5 rounded-xl text-white font-semibold text-sm flex items-center gap-2 shadow-teal-sm disabled:opacity-60 whitespace-nowrap"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
            {loading ? 'Scanning…' : 'Scan Outbreaks'}
          </motion.button>
        </motion.div>

        {/* Clusters grid */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-widest">
              {filtered.length} cluster{filtered.length !== 1 ? 's' : ''} detected
            </h2>
            {scanned && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center gap-1.5 text-xs text-teal-400"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                Updated just now
              </motion.div>
            )}
          </div>

          <AnimatePresence>
            {filtered.length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-center py-16 text-slate-600"
              >
                <CheckCircle2 className="w-12 h-12 mx-auto mb-3 text-emerald-500/50" />
                <p className="text-lg font-semibold text-slate-400">No outbreaks detected in this region</p>
              </motion.div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filtered.map((c, i) => (
                  <OutbreakCard key={c.location} c={c as any} delay={i * 0.07} />
                ))}
              </div>
            )}
          </AnimatePresence>
        </div>

        {/* Disclaimer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-8 p-4 glass border border-amber-500/15 rounded-2xl flex items-start gap-3"
        >
          <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
          <p className="text-slate-500 text-xs leading-relaxed">
            Outbreak data is generated by AI pattern detection across symptom reports. This is an early-warning tool and should be verified with official health authority data before taking action.
          </p>
        </motion.div>
      </main>
    </div>
  )
}
