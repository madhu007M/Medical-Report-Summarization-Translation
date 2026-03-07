'use client'
import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, FileText, Image, X, CheckCircle2, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface Props {
  onFile: (file: File) => void
  loading?: boolean
  accept?: Record<string, string[]>
}

export default function ReportUpload({ onFile, loading = false, accept }: Props) {
  const [preview, setPreview] = useState<{ name: string; size: string; type: string } | null>(null)

  const onDrop = useCallback((accepted: File[]) => {
    if (!accepted[0]) return
    const f = accepted[0]
    setPreview({ name: f.name, size: (f.size / 1024).toFixed(1) + ' KB', type: f.type })
    onFile(f)
  }, [onFile])

  const { getRootProps, getInputProps, isDragActive, isDragAccept, isDragReject } = useDropzone({
    onDrop,
    multiple: false,
    accept: accept ?? {
      'application/pdf': ['.pdf'],
      'image/*':         ['.png', '.jpg', '.jpeg'],
      'text/plain':      ['.txt'],
    },
  })

  const borderColor = isDragAccept
    ? 'border-teal-400 shadow-teal'
    : isDragReject
    ? 'border-rose-500'
    : isDragActive
    ? 'border-teal-500'
    : preview
    ? 'border-teal-500/40'
    : 'border-white/10 hover:border-teal-500/40'

  return (
    <div className="w-full">
      <motion.div
        {...(getRootProps() as any)}
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
        className={cn(
          'relative rounded-2xl border-2 border-dashed transition-all duration-300 cursor-pointer overflow-hidden',
          borderColor,
          isDragActive ? 'glass-strong' : 'glass'
        )}
      >
        <input {...(getInputProps() as any)} />

        {/* Animated grid on drag */}
        <AnimatePresence>
          {isDragActive && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 grid-bg"
            />
          )}
        </AnimatePresence>

        <div className="p-10 flex flex-col items-center text-center relative z-10">
          <AnimatePresence mode="wait">
            {loading ? (
              <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <div className="w-16 h-16 rounded-2xl bg-teal-500/15 border border-teal-500/30 flex items-center justify-center mb-4">
                  <Loader2 className="w-8 h-8 text-teal-400 animate-spin" />
                </div>
                <p className="text-white font-semibold text-lg">Extracting text…</p>
                <p className="text-slate-500 text-sm mt-1">AI is reading your document</p>
                {/* Skeleton bars */}
                <div className="mt-6 space-y-2 w-64">
                  {[80, 64, 72, 48].map((w, i) => (
                    <div key={i} className={`h-2.5 rounded-full skeleton`} style={{ width: `${w}%` }} />
                  ))}
                </div>
              </motion.div>
            ) : preview ? (
              <motion.div
                key="preview"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                className="w-full"
              >
                <div className="w-16 h-16 rounded-2xl bg-teal-500/15 border border-teal-500/30 flex items-center justify-center mx-auto mb-4">
                  {preview.type.startsWith('image') ? (
                    <Image className="w-8 h-8 text-teal-400" />
                  ) : (
                    <FileText className="w-8 h-8 text-teal-400" />
                  )}
                </div>
                <p className="text-white font-semibold text-lg truncate max-w-xs mx-auto">{preview.name}</p>
                <p className="text-slate-500 text-sm mt-1">{preview.type} · {preview.size}</p>
                <div className="mt-4 flex items-center justify-center gap-2 text-teal-400 text-sm font-medium">
                  <CheckCircle2 className="w-4 h-4" />
                  File ready — click Analyze below
                </div>
                <button
                  onClick={e => { e.stopPropagation(); setPreview(null) }}
                  className="mt-3 text-slate-600 hover:text-slate-400 text-xs flex items-center gap-1 mx-auto"
                >
                  <X className="w-3 h-3" /> Remove
                </button>
              </motion.div>
            ) : (
              <motion.div key="idle" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <motion.div
                  animate={{ y: isDragActive ? -8 : 0 }}
                  className="w-16 h-16 rounded-2xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center mx-auto mb-5"
                >
                  <Upload className="w-8 h-8 text-teal-400" />
                </motion.div>
                <p className="text-white font-semibold text-lg mb-1">
                  {isDragActive ? 'Drop your file here' : 'Drag & drop your report'}
                </p>
                <p className="text-slate-500 text-sm mb-4">or click to browse files</p>
                <div className="flex gap-2 justify-center flex-wrap">
                  {['PDF', 'PNG', 'JPG', 'TXT'].map(t => (
                    <span key={t} className="px-2.5 py-1 rounded-lg glass border border-white/10 text-xs text-slate-400 font-mono">{t}</span>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  )
}
