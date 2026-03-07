'use client'
import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  MessageSquare, Send, RotateCcw, Bot, User,
  Stethoscope, AlertCircle, ChevronRight, Loader2
} from 'lucide-react'
import Navbar from '@/components/Navbar'
import { chat } from '@/lib/api'

const QUICK_SYMPTOMS = [
  'Fever', 'Cough', 'Headache', 'Chest pain',
  'Fatigue', 'Nausea', 'Shortness of breath', 'Body ache',
]

interface Message {
  role: 'user' | 'assistant' | 'system'
  text: string
  time: string
}

function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -4 }}
      className="flex items-end gap-2"
    >
      <div className="w-8 h-8 rounded-xl bg-teal-500/15 border border-teal-500/20 flex items-center justify-center flex-shrink-0">
        <Bot className="w-4 h-4 text-teal-400" />
      </div>
      <div className="chat-bot px-4 py-3 rounded-2xl rounded-bl-sm flex items-center gap-1.5">
        {[0, 1, 2].map(i => (
          <motion.div
            key={i}
            animate={{ y: [0, -6, 0], opacity: [0.4, 1, 0.4] }}
            transition={{ repeat: Infinity, duration: 1, delay: i * 0.18 }}
            className="w-2 h-2 rounded-full bg-teal-400"
          />
        ))}
      </div>
    </motion.div>
  )
}

function ChatBubble({ msg }: { msg: Message }) {
  const isUser = msg.role === 'user'
  return (
    <motion.div
      initial={{ opacity: 0, x: isUser ? 20 : -20, y: 10 }}
      animate={{ opacity: 1, x: 0, y: 0 }}
      transition={{ duration: 0.35 }}
      className={`flex items-end gap-2 ${isUser ? 'flex-row-reverse' : ''}`}
    >
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 ${
        isUser ? 'bg-blue-500/15 border border-blue-500/20' : 'bg-teal-500/15 border border-teal-500/20'
      }`}>
        {isUser ? <User className="w-4 h-4 text-blue-400" /> : <Bot className="w-4 h-4 text-teal-400" />}
      </div>

      {/* Bubble */}
      <div className={`max-w-[72%] ${isUser ? 'chat-user' : 'chat-bot'} px-4 py-3`}>
        <p className="text-sm text-white leading-relaxed whitespace-pre-wrap">{msg.text}</p>
        <p className="text-[10px] text-white/30 mt-1 text-right">{msg.time}</p>
      </div>
    </motion.div>
  )
}

const WELCOME: Message = {
  role: 'assistant',
  text: 'Hello! I\'m your AI Health Assistant.\n\nI can help you understand symptoms, assess health risks, and provide evidence-based guidance. Please describe what you\'re experiencing, or select a symptom below.\n\n⚠️ This is not a substitute for professional medical advice.',
  time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([WELCOME])
  const [input, setInput] = useState('')
  const [chips, setChips] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [sessionId] = useState(() => Math.random().toString(36).slice(2))
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const addChip = (sym: string) => {
    setChips(c => c.includes(sym) ? c.filter(x => x !== sym) : [...c, sym])
  }

  const sendMessage = async (text?: string) => {
    const msg = (text ?? input).trim()
    if (!msg) return
    setInput('')
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    setMessages(m => [...m, { role: 'user', text: msg, time }])
    setLoading(true)
    try {
      const data = await chat(sessionId, msg, chips)
      let reply = data.response ?? ''
      if (data.prompts?.length) {
        reply += '\n\n**Suggested questions:**\n' + data.prompts.map((q: string) => `• ${q}`).join('\n')
      }
      setMessages(m => [...m, { role: 'assistant', text: reply, time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }])
    } catch (e: any) {
      setMessages(m => [...m, { role: 'assistant', text: 'Sorry, I\'m having trouble connecting. Please check that the backend is running.', time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }])
    } finally {
      setLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([WELCOME]); setChips([]); setInput('')
  }

  return (
    <div className="min-h-screen bg-[#020817] grid-bg flex flex-col">
      <div className="absolute inset-0 bg-hero-gradient pointer-events-none" />
      <Navbar />

      <main className="relative flex flex-col flex-1 max-w-3xl w-full mx-auto px-4 pt-20 pb-0">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass border border-teal-500/20 rounded-2xl p-5 mb-4 mt-4 flex items-center gap-4"
          style={{ background: 'linear-gradient(135deg, rgba(20,184,166,0.12), rgba(6,182,212,0.06))' }}
        >
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-teal-500 to-cyan-500 flex items-center justify-center shadow-teal-sm flex-shrink-0">
            <Stethoscope className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <h1 className="text-lg font-bold text-white">AI Health Assistant</h1>
            <p className="text-slate-400 text-sm">Evidence-based symptom guidance · Always consult a doctor for diagnosis</p>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-teal-400 animate-pulse" />
            <span className="text-xs text-teal-400 font-medium">Active</span>
          </div>
          <motion.button
            whileHover={{ scale: 1.08 }}
            whileTap={{ scale: 0.92 }}
            onClick={clearChat}
            className="w-9 h-9 rounded-xl hover:bg-white/8 flex items-center justify-center text-slate-500 hover:text-white transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
          </motion.button>
        </motion.div>

        {/* Quick symptom chips */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="flex flex-wrap gap-1.5 mb-4"
        >
          {QUICK_SYMPTOMS.map(s => (
            <motion.button
              key={s}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => addChip(s)}
              className={`px-3 py-1 rounded-full text-xs font-medium border transition-all ${
                chips.includes(s)
                  ? 'bg-teal-500/20 text-teal-300 border-teal-500/40'
                  : 'glass border-white/10 text-slate-400 hover:text-white hover:border-white/20'
              }`}
            >
              {s}
            </motion.button>
          ))}
          {chips.length > 0 && (
            <button
              onClick={() => setChips([])}
              className="px-3 py-1 rounded-full text-xs text-rose-500 border border-rose-500/20 hover:bg-rose-500/10 transition-colors"
            >
              Clear
            </button>
          )}
        </motion.div>

        {/* Chat messages */}
        <div className="flex-1 overflow-y-auto space-y-4 pb-4 pr-1 min-h-[340px] max-h-[52vh]">
          {messages.map((m, i) => <ChatBubble key={i} msg={m} />)}
          <AnimatePresence>{loading && <TypingIndicator />}</AnimatePresence>
          <div ref={bottomRef} />
        </div>

        {/* Input area */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="sticky bottom-0 py-4"
        >
          <div className="glass border border-white/10 rounded-2xl flex items-end gap-2 p-2 focus-within:border-teal-500/40 transition-colors">
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() } }}
              placeholder="Describe your symptoms or ask a health question…"
              rows={1}
              className="flex-1 bg-transparent text-slate-200 placeholder-slate-600 text-sm resize-none focus:outline-none px-2 py-1 max-h-32"
              style={{ lineHeight: '1.5' }}
            />
            <motion.button
              whileHover={{ scale: 1.08 }}
              whileTap={{ scale: 0.92 }}
              onClick={() => sendMessage()}
              disabled={!input.trim() || loading}
              className="w-10 h-10 rounded-xl btn-teal flex items-center justify-center text-white shadow-teal-sm disabled:opacity-40 flex-shrink-0"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </motion.button>
          </div>
          <p className="text-center text-[11px] text-slate-700 mt-2">
            AI responses are informational only. Always consult a qualified medical professional.
          </p>
        </motion.div>
      </main>
    </div>
  )
}
