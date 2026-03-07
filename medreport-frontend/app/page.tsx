'use client'
import { useRef, useEffect, useState } from 'react'
import Link from 'next/link'
import { motion, useInView, useMotionValue, useTransform, animate } from 'framer-motion'
import {
  Heart, Activity, Brain, Shield, Zap, Globe, Users, FileText,
  ArrowRight, Stethoscope, Pill, Microscope, AudioLines, ChevronRight,
  MessageSquare, MapPin, Bell, TrendingUp, CheckCircle2
} from 'lucide-react'
import Navbar from '@/components/Navbar'

/* ── Animated counter ──────────────────────────────────── */
function Counter({ to, suffix = '' }: { to: number; suffix?: string }) {
  const ref = useRef<HTMLSpanElement>(null)
  const count = useMotionValue(0)
  const inView = useInView(ref, { once: true })
  useEffect(() => {
    if (inView) {
      const controls = animate(count, to, { duration: 2, ease: 'easeOut' })
      count.on('change', v => { if (ref.current) ref.current.textContent = `${Math.round(v).toLocaleString()}${suffix}` })
      return controls.stop
    }
  }, [inView, to, count, suffix])
  return <span ref={ref}>0{suffix}</span>
}

/* ── Floating icon ─────────────────────────────────────── */
function FloatingIcon({ icon, delay, x, y, size = 'md', color }: {
  icon: React.ReactNode; delay: number; x: string; y: string; size?: string; color: string
}) {
  const s = size === 'lg' ? 'w-16 h-16' : size === 'sm' ? 'w-10 h-10' : 'w-12 h-12'
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0 }}
      animate={{ opacity: [0, 0.8, 0.6], scale: 1, y: [0, -16, -8, 0] }}
      transition={{ delay, duration: 2, y: { repeat: Infinity, duration: 4 + delay, ease: 'easeInOut' } }}
      style={{ position: 'absolute', left: x, top: y }}
      className={`${s} rounded-2xl glass border border-white/10 flex items-center justify-center shadow-glass`}
    >
      <div className={color}>{icon}</div>
    </motion.div>
  )
}

const features = [
  {
    icon: <FileText className="w-6 h-6" />, color: 'text-teal-400',
    bg: 'from-teal-500/20 to-teal-600/5',
    title: 'AI Report Analysis', desc: 'Upload medical reports in PDF, image, or text and receive instant AI-powered simplified explanations.',
  },
  {
    icon: <Brain className="w-6 h-6" />, color: 'text-purple-400',
    bg: 'from-purple-500/20 to-purple-600/5',
    title: 'Intelligent Summarization', desc: 'BART-based NLP model converts complex medical jargon into clear, understandable language.',
  },
  {
    icon: <Globe className="w-6 h-6" />, color: 'text-cyan-400',
    bg: 'from-cyan-500/20 to-cyan-600/5',
    title: 'Multilingual Support', desc: 'Full support for English, Hindi, Kannada, Tamil, Telugu, Marathi, and Bengali.',
  },
  {
    icon: <AudioLines className="w-6 h-6" />, color: 'text-blue-400',
    bg: 'from-blue-500/20 to-blue-600/5',
    title: 'Voice Explanation', desc: 'Text-to-speech engine reads your report summary aloud — sentence by sentence or as a full audio.',
  },
  {
    icon: <MessageSquare className="w-6 h-6" />, color: 'text-emerald-400',
    bg: 'from-emerald-500/20 to-emerald-600/5',
    title: 'Symptom Chatbot', desc: 'Conversational AI asks targeted questions about your symptoms and provides evidence-based guidance.',
  },
  {
    icon: <MapPin className="w-6 h-6" />, color: 'text-rose-400',
    bg: 'from-rose-500/20 to-rose-600/5',
    title: 'Outbreak Detection', desc: 'Location-based disease cluster detection alerts your community and doctors before outbreaks spread.',
  },
  {
    icon: <Bell className="w-6 h-6" />, color: 'text-amber-400',
    bg: 'from-amber-500/20 to-amber-600/5',
    title: 'Doctor Alerts', desc: 'Verified physicians can broadcast health alerts directly to patients in their region.',
  },
  {
    icon: <Shield className="w-6 h-6" />, color: 'text-indigo-400',
    bg: 'from-indigo-500/20 to-indigo-600/5',
    title: 'Risk Assessment', desc: 'Automated Risk Engine scores reports as Low / Moderate / High with detailed actionable recommendations.',
  },
]

const stats = [
  { val: 50000, suffix: '+', label: 'Reports Analyzed',     icon: <FileText className="w-5 h-5 text-teal-400" /> },
  { val: 7,     suffix: '',  label: 'Languages Supported',  icon: <Globe className="w-5 h-5 text-cyan-400" /> },
  { val: 98,    suffix: '%', label: 'AI Accuracy',          icon: <TrendingUp className="w-5 h-5 text-blue-400" /> },
  { val: 12000, suffix: '+', label: 'Community Users',      icon: <Users className="w-5 h-5 text-purple-400" /> },
]

const steps = [
  { icon: <FileText className="w-7 h-7 text-teal-400" />, step: '01', title: 'Upload Report', desc: 'Drag & drop your medical report — PDF, image or plain text.' },
  { icon: <Brain className="w-7 h-7 text-purple-400" />,  step: '02', title: 'AI Analyzes',   desc: 'Our BART model reads and simplifies the medical content.' },
  { icon: <Shield className="w-7 h-7 text-blue-400" />,   step: '03', title: 'Get Risk Score', desc: 'Receive a color-coded risk level with specific health alerts.' },
  { icon: <AudioLines className="w-7 h-7 text-cyan-400" />, step: '04', title: 'Listen & Share', desc: 'Hear the summary read aloud and share via SMS or WhatsApp.' },
]

const container = { hidden: {}, visible: { transition: { staggerChildren: 0.1 } } }
const item = { hidden: { opacity: 0, y: 24 }, visible: { opacity: 1, y: 0, transition: { duration: 0.6 } } }

export default function LandingPage() {
  return (
    <main className="relative overflow-x-hidden">
      <Navbar />

      {/* ── Hero ──────────────────────────────────────────────── */}
      <section className="relative min-h-screen flex items-center justify-center pt-16 overflow-hidden">
        {/* Background */}
        <div className="absolute inset-0 grid-bg" />
        <div className="absolute inset-0 bg-hero-gradient" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[900px] bg-teal-glow opacity-30 rounded-full blur-3xl pointer-events-none" />

        {/* Floating icons */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          <FloatingIcon icon={<Heart className="w-7 h-7" fill="currentColor" />} color="text-rose-400"    delay={0.2} x="8%"  y="20%" size="lg" />
          <FloatingIcon icon={<Activity className="w-6 h-6" />}                 color="text-teal-400"    delay={0.5} x="85%" y="18%" />
          <FloatingIcon icon={<Brain className="w-6 h-6" />}                    color="text-purple-400"  delay={0.8} x="12%" y="65%" />
          <FloatingIcon icon={<Stethoscope className="w-6 h-6" />}              color="text-cyan-400"    delay={0.3} x="80%" y="60%" />
          <FloatingIcon icon={<Pill className="w-5 h-5" />}                     color="text-emerald-400" delay={1.0} x="72%" y="30%" size="sm" />
          <FloatingIcon icon={<Microscope className="w-5 h-5" />}               color="text-blue-400"    delay={0.7} x="20%" y="35%" size="sm" />
          <FloatingIcon icon={<Shield className="w-5 h-5" />}                   color="text-indigo-400"  delay={1.2} x="55%" y="80%" size="sm" />
          <FloatingIcon icon={<Globe className="w-5 h-5" />}                    color="text-amber-400"   delay={0.9} x="38%" y="12%" size="sm" />
        </div>

        <div className="relative max-w-5xl mx-auto px-4 text-center">
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center gap-2 glass border border-teal-500/30 rounded-full px-4 py-1.5 mb-8"
          >
            <span className="w-2 h-2 rounded-full bg-teal-400 animate-pulse-slow" />
            <span className="text-sm text-teal-300 font-medium">AI-Powered Healthcare Platform</span>
          </motion.div>

          {/* Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.1 }}
            className="text-5xl sm:text-6xl md:text-7xl font-black tracking-tight leading-tight mb-6"
          >
            <span className="text-white">Understand Your</span>
            <br />
            <span className="gradient-text">Medical Reports</span>
            <br />
            <span className="text-white">with AI</span>
          </motion.h1>

          {/* Subheadline */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="text-slate-400 text-lg sm:text-xl max-w-2xl mx-auto mb-10 leading-relaxed"
          >
            Upload any medical report and instantly receive a simplified AI explanation,
            multilingual translation, voice readout, risk assessment, and personalized health guidance.
          </motion.p>

          {/* CTA buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-4 justify-center items-center"
          >
            <Link href="/dashboard">
              <motion.button
                whileHover={{ scale: 1.05, boxShadow: '0 0 40px rgba(20,184,166,0.4)' }}
                whileTap={{ scale: 0.97 }}
                className="btn-teal px-8 py-4 rounded-2xl text-white font-bold text-lg flex items-center gap-2 shadow-teal"
              >
                <Zap className="w-5 h-5" />
                Start Analysis
                <ArrowRight className="w-5 h-5" />
              </motion.button>
            </Link>
            <Link href="/chat">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.97 }}
                className="glass border border-white/15 px-8 py-4 rounded-2xl text-white font-semibold text-lg flex items-center gap-2 hover:border-teal-500/40 transition-colors"
              >
                <MessageSquare className="w-5 h-5 text-teal-400" />
                Talk to Health AI
              </motion.button>
            </Link>
          </motion.div>

          {/* Trust badges */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="flex flex-wrap justify-center gap-6 mt-14 text-sm text-slate-500"
          >
            {['7 languages', '50K+ reports', 'AI-powered', 'Free to use'].map(b => (
              <span key={b} className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-teal-500" />
                {b}
              </span>
            ))}
          </motion.div>
        </div>

        {/* Scroll indicator */}
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ repeat: Infinity, duration: 2 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2 w-6 h-10 rounded-full border-2 border-white/20 flex justify-center pt-2"
        >
          <div className="w-1 h-2 rounded-full bg-teal-400" />
        </motion.div>
      </section>

      {/* ── Stats ─────────────────────────────────────────────── */}
      <section className="py-20 px-4 relative">
        <div className="absolute inset-0 bg-gradient-to-b from-[#020817] via-[#0A1628] to-[#020817]" />
        <div className="max-w-5xl mx-auto relative">
          <motion.div
            variants={container}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid grid-cols-2 md:grid-cols-4 gap-4"
          >
            {stats.map(({ val, suffix, label, icon }) => (
              <motion.div
                key={label}
                variants={item}
                whileHover={{ scale: 1.04 }}
                className="glass border border-white/8 rounded-2xl p-6 text-center card-hover border-teal-glow"
              >
                <div className="flex justify-center mb-3">{icon}</div>
                <div className="text-3xl md:text-4xl font-black gradient-text mb-1">
                  <Counter to={val} suffix={suffix} />
                </div>
                <div className="text-slate-500 text-sm font-medium">{label}</div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── How it works ──────────────────────────────────────── */}
      <section className="py-24 px-4">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <p className="text-teal-400 font-semibold text-sm uppercase tracking-widest mb-3">How It Works</p>
            <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
              From Report to <span className="gradient-text">Understanding</span>
            </h2>
            <p className="text-slate-400 text-lg max-w-lg mx-auto">
              Four steps to transform complex medical documents into clear, actionable health insights.
            </p>
          </motion.div>

          <div className="relative grid grid-cols-1 md:grid-cols-4 gap-6">
            {/* Connector line */}
            <div className="hidden md:block absolute top-12 left-[12.5%] right-[12.5%] h-px bg-gradient-to-r from-transparent via-teal-500/30 to-transparent" />

            {steps.map(({ icon, step, title, desc }, i) => (
              <motion.div
                key={step}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15 }}
                whileHover={{ y: -6 }}
                className="glass border border-white/8 rounded-2xl p-6 text-center card-hover relative"
              >
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-teal-500/20 to-transparent border border-teal-500/20 flex items-center justify-center mx-auto mb-4">
                  {icon}
                </div>
                <div className="text-6xl font-black text-white/5 absolute top-3 right-4 select-none">{step}</div>
                <h3 className="font-bold text-white mb-2">{title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features grid ─────────────────────────────────────── */}
      <section className="py-24 px-4 relative">
        <div className="absolute inset-0 grid-bg opacity-50" />
        <div className="max-w-6xl mx-auto relative">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <p className="text-teal-400 font-semibold text-sm uppercase tracking-widest mb-3">Platform Features</p>
            <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
              Everything for Your <span className="gradient-text">Health</span>
            </h2>
          </motion.div>

          <motion.div
            variants={container}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
          >
            {features.map(({ icon, color, bg, title, desc }) => (
              <motion.div
                key={title}
                variants={item}
                whileHover={{ scale: 1.03, y: -4 }}
                className="glass border border-white/8 rounded-2xl p-5 card-hover group cursor-default"
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${bg} flex items-center justify-center mb-4`}>
                  <span className={color}>{icon}</span>
                </div>
                <h3 className="font-bold text-white mb-2 group-hover:text-teal-300 transition-colors">{title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{desc}</p>
                <div className="mt-4 flex items-center gap-1 text-xs text-teal-500 opacity-0 group-hover:opacity-100 transition-opacity">
                  Learn more <ChevronRight className="w-3 h-3" />
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── CTA ───────────────────────────────────────────────── */}
      <section className="py-32 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="glass-strong border border-teal-500/20 rounded-3xl p-12 relative overflow-hidden"
          >
            <div className="absolute inset-0 bg-teal-glow opacity-30" />
            <div className="relative">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-teal-500 to-cyan-500 flex items-center justify-center mx-auto mb-6 shadow-teal">
                <Heart className="w-8 h-8 text-white" fill="white" />
              </div>
              <h2 className="text-4xl font-black text-white mb-4">
                Ready to understand your health?
              </h2>
              <p className="text-slate-400 text-lg mb-8">
                Upload your first report for free. No account needed.
              </p>
              <Link href="/dashboard">
                <motion.button
                  whileHover={{ scale: 1.06, boxShadow: '0 0 50px rgba(20,184,166,0.5)' }}
                  whileTap={{ scale: 0.97 }}
                  className="btn-teal px-10 py-4 rounded-2xl text-white font-bold text-lg inline-flex items-center gap-2 shadow-teal"
                >
                  <Zap className="w-5 h-5" />
                  Get Started — It&apos;s Free
                  <ArrowRight className="w-5 h-5" />
                </motion.button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-10 px-4 text-center text-slate-600 text-sm">
        <p>© 2025 MedReport AI • Built with Next.js, Framer Motion & FastAPI</p>
        <p className="mt-1 text-xs text-slate-700">For informational purposes only. Not a substitute for professional medical advice.</p>
      </footer>
    </main>
  )
}
