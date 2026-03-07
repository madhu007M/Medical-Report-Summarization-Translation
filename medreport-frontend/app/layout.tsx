import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'MedReport AI — AI Medical Report Interpreter',
  description: 'AI-powered medical report interpretation, community health intelligence, and multilingual support.',
  keywords: 'medical AI, report analysis, health assistant, symptom checker',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="bg-[#020817] text-slate-100 antialiased min-h-screen">
        {children}
      </body>
    </html>
  )
}
