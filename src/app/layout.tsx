import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '@/components/AuthProvider'
import { WelcomeScreen } from '@/components/WelcomeScreen'
import { GlobalBotIndicator } from '@/components/GlobalBotIndicator'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ApplyX by Nebula.AI - AI-Powered Job Application Engine',
  description: 'Land your dream job faster with ApplyX. Our AI agent finds jobs, tailors resumes, and applies 24/7 while you sleep. Start free trial today.',
  icons: {
    icon: [
      { url: '/favicon.ico', sizes: '16x16', type: 'image/x-icon' },
      { url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
      { url: '/favicon.svg', type: 'image/svg+xml' }
    ],
    shortcut: '/favicon.ico',
    apple: '/favicon-32x32.png',
  },
  manifest: '/site.webmanifest',
  themeColor: '#2563eb',
  viewport: 'width=device-width, initial-scale=1',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/favicon-32x32.png" />
      </head>
      <body className={inter.className}>
        <div className="min-h-screen bg-background">
          <AuthProvider>
            {children}
            <WelcomeScreen />
            <GlobalBotIndicator />
          </AuthProvider>
        </div>
      </body>
    </html>
  )
} 