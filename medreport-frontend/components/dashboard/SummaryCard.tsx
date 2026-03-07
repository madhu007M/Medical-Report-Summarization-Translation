'use client'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { FileText, Volume2, Download, Copy, CheckCheck } from 'lucide-react'

interface Props {
  summary: string
  language?: string
  onDownloadPDF?: () => void
  onSpeak?: () => void
}

export default function SummaryCard({ summary, language = 'EN', onDownloadPDF, onSpeak }: Props) {
  const [copied, setCopied] = useState(false)

  const copy = () => {
    navigator.clipboard.writeText(summary)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="glass border border-white/8 rounded-2xl overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-white/8">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-teal-500/15 border border-teal-500/20 flex items-center justify-center">
            <FileText className="w-4 h-4 text-teal-400" />
          </div>
          <span className="font-semibold text-white">AI Summary</span>
          <span className="px-2 py-0.5 rounded-md glass border border-white/10 text-xs text-slate-400 font-mono">
            {language.toUpperCase()}
          </span>
        </div>
        <div className="flex items-center gap-1">
          {onSpeak && (
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={onSpeak}
              className="w-8 h-8 rounded-lg hover:bg-teal-500/15 flex items-center justify-center text-slate-400 hover:text-teal-400 transition-colors"
            >
              <Volume2 className="w-4 h-4" />
            </motion.button>
          )}
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={copy}
            className="w-8 h-8 rounded-lg hover:bg-white/5 flex items-center justify-center text-slate-400 hover:text-white transition-colors"
          >
            {copied ? <CheckCheck className="w-4 h-4 text-teal-400" /> : <Copy className="w-4 h-4" />}
          </motion.button>
          {onDownloadPDF && (
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={onDownloadPDF}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-teal-500/10 hover:bg-teal-500/20 border border-teal-500/20 text-teal-400 text-xs font-medium transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              PDF
            </motion.button>
          )}
        </div>
      </div>

      {/* Summary text */}
      <div className="p-5">
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-slate-300 leading-relaxed text-sm"
        >
          {summary}
        </motion.p>
      </div>
    </motion.div>
  )
}
