/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: { center: true, padding: '2rem', screens: { '2xl': '1400px' } },
    extend: {
      colors: {
        teal: {
          50:  '#f0fdfa', 100: '#ccfbf1', 200: '#99f6e4', 300: '#5eead4',
          400: '#2dd4bf', 500: '#14b8a6', 600: '#0d9488', 700: '#0f766e',
          800: '#115e59', 900: '#134e4a', 950: '#042f2e',
        },
        cyber: { DEFAULT: '#00F5FF', dim: '#00B8C4' },
        glass: {
          white: 'rgba(255,255,255,0.06)',
          border: 'rgba(255,255,255,0.1)',
        },
      },
      backgroundImage: {
        'grid-pattern': "url(\"data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32' width='32' height='32' fill='none' stroke='rgb(148 163 184 / 0.05)'%3e%3cpath d='M0 .5H31.5V32'/%3e%3c/svg%3e\")",
        'hero-gradient': 'radial-gradient(ellipse 80% 80% at 50% -20%,rgba(20,184,166,0.2),rgba(2,8,23,0))',
        'card-gradient': 'linear-gradient(135deg, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0.02) 100%)',
        'teal-glow':    'radial-gradient(ellipse at center, rgba(20,184,166,0.35) 0%, transparent 70%)',
      },
      animation: {
        'float':         'float 6s ease-in-out infinite',
        'float-slow':    'float 9s ease-in-out infinite',
        'float-fast':    'float 4s ease-in-out infinite',
        'pulse-slow':    'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'gradient-x':    'gradientX 6s ease infinite',
        'shimmer':       'shimmer 2s linear infinite',
        'spin-slow':     'spin 8s linear infinite',
        'bounce-slow':   'bounce 3s infinite',
        'waveform':      'waveform 1s ease-in-out infinite',
        'scanline':      'scanline 3s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px) rotate(0deg)' },
          '33%':       { transform: 'translateY(-16px) rotate(3deg)' },
          '66%':       { transform: 'translateY(-8px) rotate(-2deg)' },
        },
        gradientX: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%':       { backgroundPosition: '100% 50%' },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition:  '200% 0' },
        },
        waveform: {
          '0%, 100%': { scaleY: 0.4 },
          '50%':       { scaleY: 1.4 },
        },
        scanline: {
          '0%':   { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
      },
      fontFamily: {
        sans:  ['var(--font-inter)'],
        mono:  ['var(--font-mono)'],
      },
      boxShadow: {
        'teal': '0 0 40px rgba(20,184,166,0.3)',
        'teal-sm': '0 0 16px rgba(20,184,166,0.2)',
        'glow': '0 0 60px rgba(20,184,166,0.15), 0 25px 50px rgba(0,0,0,0.5)',
        'glass': '0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1)',
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
