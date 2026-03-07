'use client'
import { motion } from 'framer-motion'
import { AlertTriangle, CheckCircle, XCircle, TrendingUp } from 'lucide-react'

type Level = 'High' | 'Moderate' | 'Low' | 'Unknown'

interface Props {
  level: Level
  score: number
  recommendation?: string
  alerts?: string[]
}

const cfg = {
  High:     { color: 'text-rose-400',    bg: 'risk-bg-high',     bar: '#EF4444', icon: <XCircle className="w-8 h-8" />,        glow: 'shadow-[0_0_30px_rgba(239,68,68,0.25)]' },
  Moderate: { color: 'text-amber-400',   bg: 'risk-bg-moderate', bar: '#F59E0B', icon: <AlertTriangle className="w-8 h-8" />, glow: 'shadow-[0_0_30px_rgba(245,158,11,0.2)]' },
  Low:      { color: 'text-emerald-400', bg: 'risk-bg-low',      bar: '#22C55E', icon: <CheckCircle className="w-8 h-8" />,   glow: 'shadow-[0_0_30px_rgba(34,197,94,0.2)]' },
  Unknown:  { color: 'text-slate-400',   bg: 'glass',            bar: '#64748B', icon: <TrendingUp className="w-8 h-8" />,    glow: '' },
}

export default function RiskIndicator({ level, score, recommendation, alerts }: Props) {
  const { color, bg, bar, icon, glow } = cfg[level] ?? cfg.Unknown
  const pct = (score / 10) * 100

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className={`rounded-2xl p-6 ${bg} ${glow} relative overflow-hidden`}
    >
      {/* Animated glow blob */}
      <motion.div
        animate={{ scale: [1, 1.2, 1], opacity: [0.15, 0.3, 0.15] }}
        transition={{ duration: 4, repeat: Infinity }}
        className="absolute -top-8 -right-8 w-32 h-32 rounded-full"
        style={{ background: bar, filter: 'blur(30px)' }}
      />

      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-center gap-4 mb-5">
          <motion.div
            initial={{ rotate: -15, scale: 0 }}
            animate={{ rotate: 0, scale: 1 }}
            transition={{ type: 'spring', stiffness: 200, delay: 0.2 }}
            className={color}
          >
            {icon}
          </motion.div>
          <div>
            <p className="text-sm font-medium text-slate-400 uppercase tracking-widest">Risk Level</p>
            <motion.h3
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.1 }}
              className={`text-3xl font-black ${color}`}
            >
              {level}
            </motion.h3>
          </div>
          <div className="ml-auto text-right">
            <p className="text-slate-400 text-xs font-medium">Score</p>
            <motion.p
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', delay: 0.3 }}
              className={`text-4xl font-black ${color}`}
            >
              {score}<span className="text-xl text-slate-500">/10</span>
            </motion.p>
          </div>
        </div>

        {/* Progress bar */}
        <div className="h-3 rounded-full bg-black/30 overflow-hidden mb-5">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${pct}%` }}
            transition={{ duration: 1.2, ease: 'easeOut', delay: 0.4 }}
            className="h-full rounded-full relative"
            style={{ background: `linear-gradient(90deg, ${bar}88, ${bar})` }}
          >
            <div className="absolute inset-0 rounded-full animate-pulse opacity-40" style={{ background: bar }} />
          </motion.div>
        </div>

        {/* Recommendation */}
        {recommendation && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="glass rounded-xl p-3 mb-3"
          >
            <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider mb-1">Recommendation</p>
            <p className="text-slate-200 text-sm leading-relaxed">{recommendation}</p>
          </motion.div>
        )}

        {/* Alerts */}
        {alerts && alerts.length > 0 && (
          <div className="space-y-1.5 mt-3">
            {alerts.map((a, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 + i * 0.1 }}
                className="flex items-start gap-2 text-sm"
              >
                <AlertTriangle className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
                <span className="text-slate-300">{a}</span>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  )
}
