import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Sidebar from '@/components/layout/Sidebar'
import AuthGate from '@/components/layout/AuthGate'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'PILOT-AI Demo',
  description: 'AI-Powered Planning Decision Support',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} flex h-screen bg-brand-light overflow-hidden`}>
        <AuthGate>
          <Sidebar />
          <main className="flex-1 flex flex-col h-screen overflow-y-auto">
            {children}
          </main>
        </AuthGate>
      </body>
    </html>
  )
}
