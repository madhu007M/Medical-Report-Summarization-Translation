'use client'
import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Stethoscope, Bell, MapPin, User, Calendar, Send, RefreshCw,
  AlertCircle, CheckCircle2, Loader2, Filter, ChevronDown, Plus
} from 'lucide-react'
import Navbar from '@/components/Navbar'
import { getDoctorAlerts, postDoctorAlert } from '@/lib/api'

const MOCK_ALERTS = [
  { id: 1, doctor: 'Dr. Aisha Sharma', title: 'Dengue Advisory', message: 'Avoid stagnant water. Use mosquito repellents. Vector control in progress at Andheri West.', region: 'Mumbai', created_at: '2025-03-04T10:23:00Z', priority: 'high' },
  { id: 2, doctor: 'Dr. Rajan Mehta', title: 'H3N2 Flu Warning', message: 'Influenza cases rising. Wear masks in crowded areas. Vaccination available at BM Hospital.', region: 'Bengaluru', created_at: '2025-03-03T08:11:00Z', priority: 'moderate' },
  { id: 3, doctor: 'Dr. Priya Nair', title: 'Heat Stroke Prevention', message: 'Stay hydrated. Avoid direct sun 12–4 PM. Elderly and children at higher risk this week.', region: 'Chennai', created_at: '2025-03-02T15:44:00Z', priority: 'low' },
]

type Alert = typeof MOCK_ALERTS[0]

const PRIORITY_CFG = {
  high:     { color: 'text-rose-400',    bg: 'bg-rose-500/10 border-rose-500/25',    dot: 'bg-rose-400',    label: 'High' },
  moderate: { color: 'text-amber-400',   bg: 'bg-amber-500/10 border-amber-500/25',  dot: 'bg-amber-400',   label: 'Moderate' },
  low:      { color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/25', dot: 'bg-emerald-400', label: 'Low' },
}

function AlertCard({ a, delay }: { a: Alert; delay: number }) {
  const cfg = PRIORITY_CFG[a.priority as keyof typeof PRIORITY_CFG] ?? PRIORITY_CFG.low
  const date = new Date(a.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay, duration: 0.4 }}
      whileHover={{ x: 4, boxShadow: '0 4px 20px rgba(0,0,0,0.3)' }}
      className={`glass border ${cfg.bg} rounded-2xl p-5 transition-all`}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <motion.div
            animate={{ scale: [1, 1.3, 1] }}
            transition={{ repeat: Infinity, duration: 2, delay }}
            className={`w-2 h-2 rounded-full ${cfg.dot}`}
          />
          <span className="font-bold text-white">{a.title}</span>
        </div>
        <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-lg border ${cfg.bg} ${cfg.color}`}>
          {cfg.label}
        </span>
      </div>
      <p className="text-slate-400 text-sm leading-relaxed mb-3">{a.message}</p>
      <div className="flex items-center gap-4 text-xs text-slate-600">
        <span className="flex items-center gap-1"><User className="w-3 h-3" />{a.doctor}</span>
        <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{a.region}</span>
        <span className="flex items-center gap-1 ml-auto"><Calendar className="w-3 h-3" />{date}</span>
      </div>
    </motion.div>
  )
}

export default function DoctorPage() {
  const [alerts, setAlerts] = useState<Alert[]>(MOCK_ALERTS)
  const [loading, setLoading] = useState(false)
  const [posting, setPosting] = useState(false)
  const [success, setSuccess] = useState(false)
  const [filterRegion, setFilterRegion] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ doctor_name: '', region: '', title: '', message: '', priority: 'moderate' })

  const loadAlerts = async (region = '') => {
    setLoading(true)
    try {
      const data = await getDoctorAlerts(region)
      if (data?.alerts?.length) setAlerts(data.alerts)
      else setAlerts(MOCK_ALERTS)
    } catch {
      setAlerts(MOCK_ALERTS)
    } finally { setLoading(false) }
  }

  const postAlert = async () => {
    if (!form.doctor_name || !form.region || !form.title || !form.message) return
    setPosting(true)
    try {
      await postDoctorAlert({ doctor_name: form.doctor_name, region: form.region, title: form.title, message: form.message })
      setSuccess(true)
      setForm({ doctor_name: '', region: '', title: '', message: '', priority: 'moderate' })
      setShowForm(false)
      await loadAlerts()
      setTimeout(() => setSuccess(false), 3000)
    } catch (e) {
      console.error(e)
    } finally { setPosting(false) }
  }

  const filtered = filterRegion.trim()
    ? alerts.filter(a => a.region.toLowerCase().includes(filterRegion.toLowerCase()))
    : alerts

  return (
    <div className="min-h-screen bg-[#020817] grid-bg">
      <div className="absolute inset-0 bg-hero-gradient pointer-events-none" />
      <Navbar />

      <main className="relative max-w-6xl mx-auto px-4 pt-24 pb-16">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center">
              <Stethoscope className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight">
              Doctor <span className="gradient-text">Dashboard</span>
            </h1>
          </div>
          <p className="text-slate-400 ml-[52px]">Broadcast health alerts and monitor community wellness</p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Alerts list */}
          <div className="lg:col-span-2 space-y-5">
            {/* Controls */}
            <div className="flex flex-wrap gap-3 items-center">
              <div className="relative flex-1 min-w-[180px]">
                <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                <input
                  value={filterRegion}
                  onChange={e => setFilterRegion(e.target.value)}
                  placeholder="Filter by region…"
                  className="w-full pl-9 pr-4 py-2.5 glass border border-white/10 rounded-xl text-sm text-slate-200 bg-transparent placeholder-slate-600 focus:outline-none focus:border-teal-500/50"
                />
              </div>
              <motion.button
                whileHover={{ scale: 1.04 }}
                whileTap={{ scale: 0.96 }}
                onClick={() => loadAlerts(filterRegion)}
                disabled={loading}
                className="glass border border-white/10 px-4 py-2.5 rounded-xl text-sm text-slate-300 hover:text-white flex items-center gap-1.5 transition-colors"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-teal-400' : ''}`} />
                Refresh
              </motion.button>
            </div>

            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-slate-500 uppercase tracking-widest">
                {filtered.length} Active Alert{filtered.length !== 1 ? 's' : ''}
              </h2>
              {success && (
                <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="flex items-center gap-1.5 text-sm text-emerald-400">
                  <CheckCircle2 className="w-4 h-4" /> Alert posted
                </motion.div>
              )}
            </div>

            {/* Cards */}
            <div className="space-y-3">
              {filtered.length === 0 ? (
                <div className="text-center py-12 text-slate-600">
                  <Bell className="w-10 h-10 mx-auto mb-3 opacity-30" />
                  <p>No alerts in this region</p>
                </div>
              ) : (
                filtered.map((a, i) => <AlertCard key={a.id} a={a as any} delay={i * 0.08} />)
              )}
            </div>
          </div>

          {/* Post alert panel */}
          <div className="space-y-4">
            {/* Post new alert */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="glass border border-white/8 rounded-2xl overflow-hidden"
            >
              <button
                onClick={() => setShowForm(f => !f)}
                className="w-full flex items-center justify-between px-5 py-4 hover:bg-white/3 transition-colors"
              >
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-indigo-500/15 border border-indigo-500/20 flex items-center justify-center">
                    <Plus className="w-4 h-4 text-indigo-400" />
                  </div>
                  <span className="font-semibold text-white">Post New Alert</span>
                </div>
                <motion.div animate={{ rotate: showForm ? 180 : 0 }}>
                  <ChevronDown className="w-4 h-4 text-slate-500" />
                </motion.div>
              </button>

              <AnimatePresence>
                {showForm && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden border-t border-white/8"
                  >
                    <div className="p-5 space-y-3">
                      {[
                        { key: 'doctor_name', label: 'Doctor Name',  placeholder: 'Dr. Sharma' },
                        { key: 'region',      label: 'Region',        placeholder: 'Mumbai' },
                        { key: 'title',       label: 'Alert Title',   placeholder: 'Dengue Warning' },
                      ].map(({ key, label, placeholder }) => (
                        <div key={key}>
                          <label className="text-xs text-slate-500 font-medium mb-1 block">{label}</label>
                          <input
                            value={form[key as keyof typeof form]}
                            onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
                            placeholder={placeholder}
                            className="w-full glass border border-white/10 rounded-xl px-3 py-2 text-sm text-slate-200 bg-transparent placeholder-slate-600 focus:outline-none focus:border-indigo-500/50"
                          />
                        </div>
                      ))}
                      <div>
                        <label className="text-xs text-slate-500 font-medium mb-1 block">Message</label>
                        <textarea
                          value={form.message}
                          onChange={e => setForm(f => ({ ...f, message: e.target.value }))}
                          placeholder="Describe the health alert…"
                          rows={3}
                          className="w-full glass border border-white/10 rounded-xl px-3 py-2 text-sm text-slate-200 bg-transparent placeholder-slate-600 focus:outline-none focus:border-indigo-500/50 resize-none"
                        />
                      </div>
                      <div>
                        <label className="text-xs text-slate-500 font-medium mb-1 block">Priority</label>
                        <select
                          value={form.priority}
                          onChange={e => setForm(f => ({ ...f, priority: e.target.value }))}
                          className="w-full glass border border-white/10 rounded-xl px-3 py-2 text-sm text-slate-200 bg-slate-900 focus:outline-none focus:border-indigo-500/50"
                        >
                          <option value="low">Low</option>
                          <option value="moderate">Moderate</option>
                          <option value="high">High</option>
                        </select>
                      </div>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={postAlert}
                        disabled={posting}
                        className="w-full btn-teal py-3 rounded-xl text-white font-semibold text-sm flex items-center justify-center gap-2 disabled:opacity-60"
                      >
                        {posting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                        {posting ? 'Posting…' : 'Broadcast Alert'}
                      </motion.button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>

            {/* Quick stats */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="glass border border-white/8 rounded-2xl p-5 space-y-3"
            >
              <h3 className="font-semibold text-white text-sm">Alert Summary</h3>
              {(['high', 'moderate', 'low'] as const).map(p => {
                const count = alerts.filter(a => a.priority === p || (!a.priority && p === 'low')).length
                const cfg = PRIORITY_CFG[p]
                return (
                  <div key={p} className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${cfg.dot}`} />
                    <span className="text-slate-400 text-sm flex-1 capitalize">{cfg.label} Priority</span>
                    <span className={`text-sm font-bold ${cfg.color}`}>{count}</span>
                  </div>
                )
              })}
              <div className="pt-2 border-t border-white/8">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-500">Total Alerts</span>
                  <span className="text-white font-bold">{alerts.length}</span>
                </div>
              </div>
            </motion.div>

            {/* Disclaimer */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="p-4 glass border border-amber-500/15 rounded-xl flex items-start gap-3"
            >
              <AlertCircle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
              <p className="text-slate-500 text-xs leading-relaxed">
                Alerts are broadcast to patients in the specified region. Only verified healthcare professionals should post alerts. False alerts may be removed.
              </p>
            </motion.div>
          </div>
        </div>
      </main>
    </div>
  )
}
