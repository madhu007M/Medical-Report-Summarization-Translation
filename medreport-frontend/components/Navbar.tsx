'use client'
import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Activity, Menu, X, Heart, Stethoscope, Users, LayoutDashboard, MessageSquare } from 'lucide-react'
import { cn } from '@/lib/utils'

const links = [
  { href: '/',          label: 'Home',          icon: <Activity className="w-4 h-4" /> },
  { href: '/dashboard', label: 'Dashboard',     icon: <LayoutDashboard className="w-4 h-4" /> },
  { href: '/chat',      label: 'Health AI',     icon: <MessageSquare className="w-4 h-4" /> },
  { href: '/community', label: 'Community',     icon: <Users className="w-4 h-4" /> },
  { href: '/doctor',    label: 'Doctor Portal', icon: <Stethoscope className="w-4 h-4" /> },
]

export default function Navbar() {
  const pathname = usePathname()
  const [scrolled, setScrolled] = useState(false)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <motion.header
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className={cn(
        'fixed top-0 inset-x-0 z-50 transition-all duration-300',
        scrolled
          ? 'glass border-b border-white/8 shadow-[0_8px_32px_rgba(0,0,0,0.4)]'
          : 'bg-transparent'
      )}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5 group">
            <motion.div
              whileHover={{ scale: 1.1, rotate: 5 }}
              className="w-9 h-9 rounded-xl bg-gradient-to-br from-teal-500 to-cyan-500 flex items-center justify-center shadow-teal-sm"
            >
              <Heart className="w-5 h-5 text-white" fill="white" />
            </motion.div>
            <span className="font-bold text-lg tracking-tight">
              <span className="gradient-text">MedReport</span>
              <span className="text-white"> AI</span>
            </span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-1">
            {links.map(({ href, label, icon }) => {
              const active = pathname === href
              return (
                <Link key={href} href={href}>
                  <motion.div
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.97 }}
                    className={cn(
                      'flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                      active
                        ? 'bg-teal-500/15 text-teal-400 border border-teal-500/30'
                        : 'text-slate-400 hover:text-white hover:bg-white/5'
                    )}
                  >
                    {icon}
                    {label}
                    {active && (
                      <motion.span
                        layoutId="active-dot"
                        className="w-1.5 h-1.5 rounded-full bg-teal-400 ml-0.5"
                      />
                    )}
                  </motion.div>
                </Link>
              )
            })}
          </nav>

          {/* CTA + Hamburger */}
          <div className="flex items-center gap-3">
            <Link href="/dashboard" className="hidden md:block">
              <motion.button
                whileHover={{ scale: 1.04 }}
                whileTap={{ scale: 0.96 }}
                className="btn-teal px-4 py-2 rounded-xl text-sm font-semibold text-white shadow-teal-sm transition-all"
              >
                Analyze Report
              </motion.button>
            </Link>
            <button
              onClick={() => setOpen(!open)}
              className="md:hidden p-2 rounded-lg hover:bg-white/5 text-slate-400 hover:text-white transition-colors"
            >
              {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden glass border-t border-white/8"
          >
            <div className="px-4 py-3 space-y-1">
              {links.map(({ href, label, icon }) => (
                <Link key={href} href={href} onClick={() => setOpen(false)}>
                  <div className={cn(
                    'flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                    pathname === href
                      ? 'bg-teal-500/15 text-teal-400'
                      : 'text-slate-400 hover:text-white hover:bg-white/5'
                  )}>
                    {icon}
                    {label}
                  </div>
                </Link>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  )
}
