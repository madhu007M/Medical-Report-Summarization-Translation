'use client'
import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Play, Pause, Volume2, VolumeX, SkipForward } from 'lucide-react'

interface Props {
  audioUrl?: string
  text?: string
  language?: string
}

const NUM_BARS = 28

function WaveformBar({ i, playing }: { i: number; playing: boolean }) {
  const maxH = 20 + Math.sin(i * 0.8) * 14
  return (
    <motion.div
      style={{ height: '100%', display: 'flex', alignItems: 'center' }}
      initial={false}
      animate={playing ? {
        scaleY: [0.3, 1 + Math.sin(i * 0.6) * 0.6, 0.3],
        opacity: [0.5, 1, 0.5],
      } : { scaleY: 0.3, opacity: 0.3 }}
      transition={{
        repeat: playing ? Infinity : 0,
        duration: 0.8 + (i % 5) * 0.12,
        ease: 'easeInOut',
        delay: i * 0.04,
      }}
    >
      <div
        className="rounded-full"
        style={{
          width: 3,
          height: maxH,
          background: playing
            ? `linear-gradient(180deg, #14B8A6, #06B6D4)`
            : 'rgba(255,255,255,0.15)',
        }}
      />
    </motion.div>
  )
}

export default function VoicePlayer({ audioUrl, text, language = 'en' }: Props) {
  const [playing, setPlaying] = useState(false)
  const [muted, setMuted] = useState(false)
  const [progress, setProgress] = useState(0)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  const toggle = () => {
    if (!audioRef.current) {
      if (audioUrl) {
        audioRef.current = new Audio(audioUrl)
        audioRef.current.addEventListener('timeupdate', () => {
          const d = audioRef.current!.duration
          if (d) setProgress((audioRef.current!.currentTime / d) * 100)
        })
        audioRef.current.addEventListener('ended', () => { setPlaying(false); setProgress(0) })
      } else return
    }
    if (playing) {
      audioRef.current.pause()
    } else {
      audioRef.current.muted = muted
      audioRef.current.play()
    }
    setPlaying(p => !p)
  }

  const toggleMute = () => {
    setMuted(m => {
      if (audioRef.current) audioRef.current.muted = !m
      return !m
    })
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass border border-white/8 rounded-2xl p-5"
    >
      <div className="flex items-center gap-2 mb-4">
        <div className="w-8 h-8 rounded-lg bg-blue-500/15 border border-blue-500/20 flex items-center justify-center">
          <Volume2 className="w-4 h-4 text-blue-400" />
        </div>
        <span className="font-semibold text-white">Voice Explanation</span>
        <span className="px-2 py-0.5 rounded-md glass border border-white/10 text-xs text-slate-400 font-mono ml-auto">
          {language.toUpperCase()}
        </span>
      </div>

      {/* Waveform */}
      <div
        className="flex items-center gap-0.5 h-14 px-2 rounded-xl bg-black/20 mb-4 relative overflow-hidden cursor-pointer"
        onClick={toggle}
      >
        {Array.from({ length: NUM_BARS }).map((_, i) => (
          <WaveformBar key={i} i={i} playing={playing} />
        ))}
        {/* Progress overlay */}
        <div className="absolute inset-0 flex items-center pointer-events-none">
          <div className="h-full bg-transparent" style={{ width: `${progress}%` }} />
        </div>
        {!audioUrl && (
          <div className="absolute inset-0 flex items-center justify-center">
            <p className="text-slate-500 text-xs">No audio available</p>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="flex items-center gap-3">
        <motion.button
          whileHover={{ scale: 1.08 }}
          whileTap={{ scale: 0.92 }}
          onClick={toggle}
          disabled={!audioUrl}
          className="w-12 h-12 rounded-full btn-teal flex items-center justify-center text-white shadow-teal-sm disabled:opacity-40"
        >
          <AnimatePresence mode="wait">
            {playing ? (
              <motion.div key="pause" initial={{ scale: 0 }} animate={{ scale: 1 }} exit={{ scale: 0 }}>
                <Pause className="w-5 h-5" fill="white" />
              </motion.div>
            ) : (
              <motion.div key="play" initial={{ scale: 0 }} animate={{ scale: 1 }} exit={{ scale: 0 }}>
                <Play className="w-5 h-5 ml-0.5" fill="white" />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.button>

        {/* Progress bar */}
        <div className="flex-1 h-2 rounded-full bg-white/8 overflow-hidden">
          <motion.div
            className="h-full rounded-full bg-gradient-to-r from-teal-500 to-cyan-400"
            style={{ width: `${progress}%` }}
          />
        </div>

        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={toggleMute}
          className="w-9 h-9 rounded-lg hover:bg-white/5 flex items-center justify-center text-slate-400 hover:text-white transition-colors"
        >
          {muted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
        </motion.button>
      </div>

      {text && (
        <p className="text-xs text-slate-600 mt-3 line-clamp-2 leading-relaxed">{text}</p>
      )}
    </motion.div>
  )
}
