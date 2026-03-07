'use client'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Brain, Globe, Languages, Download, ChevronDown,
  Zap, AlertCircle, CheckCircle2, RotateCcw, Loader2
} from 'lucide-react'
import Navbar from '@/components/Navbar'
import ReportUpload from '@/components/dashboard/ReportUpload'
import RiskIndicator from '@/components/dashboard/RiskIndicator'
import SummaryCard from '@/components/dashboard/SummaryCard'
import VoicePlayer from '@/components/dashboard/VoicePlayer'
import { apiAbsoluteUrl, exportPDF, processReport, translateText } from '@/lib/api'

const LANGUAGES = [
  { code: 'en', name: 'English' },
  { code: 'hi', name: 'Hindi (हिन्दी)' },
  { code: 'kn', name: 'Kannada (ಕನ್ನಡ)' },
  { code: 'ta', name: 'Tamil (தமிழ்)' },
  { code: 'te', name: 'Telugu (తెలుగు)' },
  { code: 'mr', name: 'Marathi (मराठी)' },
  { code: 'bn', name: 'Bengali (বাংলা)' },
]

type Step = 'upload' | 'analyzing' | 'results'

export default function DashboardPage() {
  const [step, setStep] = useState<Step>('upload')
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<any>(null)
  const [language, setLanguage] = useState('en')
  const [location, setLocation] = useState('')
  const [phone, setPhone] = useState('')
  const [symptoms, setSymptoms] = useState('')
  const [translatedSummary, setTranslatedSummary] = useState('')
  const [translating, setTranslating] = useState(false)
  const [transLang, setTransLang] = useState('en')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showLangMenu, setShowLangMenu] = useState(false)

  const handleAnalyze = async () => {
    if (!file) return
    setStep('analyzing')
    setError('')
    try {
      const data = await processReport(file, { language, phone, location, symptoms })
      setResult(data)
      setStep('results')
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || 'Analysis failed')
      setStep('upload')
    }
  }

  const handleTranslate = async () => {
    if (!result?.summary) return
    setTranslating(true)
    try {
      const data = await translateText(result.summary, transLang)
      setTranslatedSummary(data.translated_text)
    } catch (e) {
      console.error(e)
    } finally {
      setTranslating(false)
    }
  }

  const reset = () => {
    setStep('upload'); setFile(null); setResult(null)
    setTranslatedSummary(''); setError('')
  }

  const risk     = result?.risk ?? {}
  const summary  = translatedSummary || result?.summary || ''
  const audioUrl = result?.report_id
    ? apiAbsoluteUrl(`/audio/explanation?text=${encodeURIComponent(summary)}&language=${transLang || language}`)
    : undefined

  return (
    <div className="min-h-screen bg-[#020817] grid-bg">
      <div className="absolute inset-0 bg-hero-gradient pointer-events-none" />
      <Navbar />

      <main className="relative max-w-6xl mx-auto px-4 pt-24 pb-16">
        {/* Page header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-teal-500 to-cyan-500 flex items-center justify-center shadow-teal-sm">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight">
              Report <span className="gradient-text">Analysis</span>
            </h1>
            {step === 'results' && (
              <motion.button
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                onClick={reset}
                className="ml-auto flex items-center gap-1.5 px-3 py-1.5 rounded-xl glass border border-white/10 text-slate-400 hover:text-white text-sm font-medium transition-colors"
              >
                <RotateCcw className="w-4 h-4" />
                New Report
              </motion.button>
            )}
          </div>
          <p className="text-slate-400 ml-[52px]">
            Upload a medical report and receive an AI-powered, multilingual health summary
          </p>
        </motion.div>

        <AnimatePresence mode="wait">

          {/* ── UPLOAD STEP ─────────────────────────────────────── */}
          {(step === 'upload' || step === 'analyzing') && (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -24 }}
              className="grid grid-cols-1 lg:grid-cols-3 gap-6"
            >
              {/* Upload area */}
              <div className="lg:col-span-2 space-y-4">
                <ReportUpload onFile={setFile} loading={step === 'analyzing'} />
                {error && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex items-center gap-2 px-4 py-3 rounded-xl risk-bg-high text-rose-300 text-sm"
                  >
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    {error}
                  </motion.div>
                )}
              </div>

              {/* Options panel */}
              <div className="space-y-4">
                {/* Language */}
                <div className="glass border border-white/8 rounded-2xl p-5">
                  <div className="flex items-center gap-2 mb-4">
                    <Globe className="w-4 h-4 text-teal-400" />
                    <span className="text-sm font-semibold text-white">Settings</span>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <label className="text-xs text-slate-500 font-medium mb-1 block">Output Language</label>
                      <select
                        value={language}
                        onChange={e => setLanguage(e.target.value)}
                        className="w-full glass border border-white/10 rounded-xl px-3 py-2 text-sm text-slate-200 bg-transparent focus:outline-none focus:border-teal-500/50"
                      >
                        {LANGUAGES.map(l => <option key={l.code} value={l.code} className="bg-slate-900">{l.name}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="text-xs text-slate-500 font-medium mb-1 block">City / PIN Code</label>
                      <input
                        value={location} onChange={e => setLocation(e.target.value)}
                        placeholder="Mumbai, 400001"
                        className="w-full glass border border-white/10 rounded-xl px-3 py-2 text-sm text-slate-200 bg-transparent placeholder-slate-600 focus:outline-none focus:border-teal-500/50"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-slate-500 font-medium mb-1 block">Phone (SMS Alerts)</label>
                      <input
                        value={phone} onChange={e => setPhone(e.target.value)}
                        placeholder="+91XXXXXXXXXX"
                        className="w-full glass border border-white/10 rounded-xl px-3 py-2 text-sm text-slate-200 bg-transparent placeholder-slate-600 focus:outline-none focus:border-teal-500/50"
                      />
                    </div>
                    <div>
                      <label className="text-xs text-slate-500 font-medium mb-1 block">Known Symptoms</label>
                      <input
                        value={symptoms} onChange={e => setSymptoms(e.target.value)}
                        placeholder="fever, cough, headache…"
                        className="w-full glass border border-white/10 rounded-xl px-3 py-2 text-sm text-slate-200 bg-transparent placeholder-slate-600 focus:outline-none focus:border-teal-500/50"
                      />
                    </div>
                  </div>
                </div>

                {/* Analyze button */}
                <motion.button
                  whileHover={file ? { scale: 1.02, boxShadow: '0 0 30px rgba(20,184,166,0.4)' } : {}}
                  whileTap={file ? { scale: 0.98 } : {}}
                  onClick={handleAnalyze}
                  disabled={!file || step === 'analyzing'}
                  className="w-full btn-teal py-4 rounded-2xl text-white font-bold text-base flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed shadow-teal-sm"
                >
                  {step === 'analyzing' ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Analyzing with AI…
                    </>
                  ) : (
                    <>
                      <Zap className="w-5 h-5" />
                      Analyze Report
                    </>
                  )}
                </motion.button>

                {/* Analyzing overlay */}
                <AnimatePresence>
                  {step === 'analyzing' && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="glass border border-teal-500/20 rounded-2xl p-5 space-y-3"
                    >
                      {['Extracting text with OCR…', 'Running AI summarization…', 'Calculating risk score…', 'Preparing report…'].map((s, i) => (
                        <motion.div
                          key={s}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: i * 0.7 }}
                          className="flex items-center gap-2 text-sm text-slate-400"
                        >
                          <motion.div
                            animate={{ scale: [1, 1.3, 1] }}
                            transition={{ repeat: Infinity, duration: 1.5, delay: i * 0.7 }}
                            className="w-2 h-2 rounded-full bg-teal-500"
                          />
                          {s}
                        </motion.div>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          )}

          {/* ── RESULTS STEP ────────────────────────────────────── */}
          {step === 'results' && result && (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="space-y-6"
            >
              {/* Top grid: Risk + Summary */}
              <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">
                <div className="lg:col-span-2">
                  <RiskIndicator
                    level={risk.risk_level ?? 'Unknown'}
                    score={risk.risk_score ?? 0}
                    recommendation={risk.recommendation}
                    alerts={risk.alerts}
                  />
                </div>
                <div className="lg:col-span-3 space-y-4">
                  <SummaryCard
                    summary={summary}
                    language={transLang || language}
                    onDownloadPDF={result?.report_id ? async () => {
                      const blob = await exportPDF(String(result.report_id))
                      const url = URL.createObjectURL(blob)
                      const a = document.createElement('a'); a.href = url; a.download = `report_${result.report_id}.pdf`; a.click()
                    } : undefined}
                  />
                  <VoicePlayer audioUrl={audioUrl} text={summary} language={transLang || language} />
                </div>
              </div>

              {/* Translate */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="glass border border-white/8 rounded-2xl p-5"
              >
                <div className="flex items-center gap-2 mb-4">
                  <Languages className="w-4 h-4 text-cyan-400" />
                  <span className="font-semibold text-white">Translate Summary</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {LANGUAGES.map(l => (
                    <motion.button
                      key={l.code}
                      whileHover={{ scale: 1.04 }}
                      whileTap={{ scale: 0.96 }}
                      onClick={() => { setTransLang(l.code); }}
                      className={`px-3 py-1.5 rounded-xl text-sm font-medium transition-all ${
                        transLang === l.code
                          ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
                          : 'glass border border-white/8 text-slate-400 hover:text-white hover:border-white/20'
                      }`}
                    >
                      {l.name}
                    </motion.button>
                  ))}
                  <motion.button
                    whileHover={{ scale: 1.04 }}
                    whileTap={{ scale: 0.96 }}
                    onClick={handleTranslate}
                    disabled={translating}
                    className="ml-auto px-4 py-1.5 rounded-xl btn-teal text-white text-sm font-semibold flex items-center gap-1.5 disabled:opacity-60"
                  >
                    {translating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Globe className="w-4 h-4" />}
                    {translating ? 'Translating…' : 'Translate'}
                  </motion.button>
                </div>
                {translatedSummary && (
                  <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-4 p-4 glass rounded-xl"
                  >
                    <p className="text-slate-300 text-sm leading-relaxed">{translatedSummary}</p>
                  </motion.div>
                )}
              </motion.div>

              {/* Report meta */}
              {result.report_id && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.3 }}
                  className="flex items-center gap-2 text-xs text-slate-600"
                >
                  <CheckCircle2 className="w-3.5 h-3.5 text-teal-500" />
                  Report ID: <span className="font-mono">{result.report_id}</span>
                  {phone && <span>· SMS sent to {phone}</span>}
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}
