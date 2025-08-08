import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '@/components/AuthProvider'
import { WelcomeScreen } from '@/components/WelcomeScreen'
import { GlobalBotIndicator } from '@/components/GlobalBotIndicator'
import { ModalManager } from '@/components/ModalManager'

import { ModalProvider } from '@/contexts/ModalContext'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
  title: 'ApplyX by Nebula.AI - AI-Powered Job Application Engine',
  description: 'Land your dream job faster with ApplyX. Our AI agent finds jobs, tailors resumes, and applies 24/7 while you sleep. Start free trial today.',
  icons: {
    icon: [
      { url: '/favicon.ico', sizes: '16x16', type: 'image/x-icon' },
      { url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' }
    ],
    apple: [
      { url: '/favicon.svg', sizes: 'any', type: 'image/svg+xml' }
    ]
  },
  manifest: '/site.webmanifest',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'your-google-verification-code',
    yandex: 'your-yandex-verification-code',
  },
  openGraph: {
    title: 'ApplyX by Nebula.AI - AI-Powered Job Application Engine',
    description: 'Land your dream job faster with ApplyX. Our AI agent finds jobs, tailors resumes, and applies 24/7 while you sleep.',
    url: '/',
    siteName: 'ApplyX',
    locale: 'en_US',
    type: 'website',
    images: [
      {
        url: '/favicon.svg',
        width: 1200,
        height: 630,
        alt: 'ApplyX - AI-Powered Job Application Engine',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ApplyX by Nebula.AI - AI-Powered Job Application Engine',
    description: 'Land your dream job faster with ApplyX. Our AI agent finds jobs, tailors resumes, and applies 24/7 while you sleep.',
    images: ['/favicon.svg'],
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
}



export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.className} suppressHydrationWarning>
      <body>
        <AuthProvider>
          <ModalProvider>
            <WelcomeScreen />
            <GlobalBotIndicator />
            {children}
            <ModalManager />

          </ModalProvider>
        </AuthProvider>
      </body>
    </html>
  )
} 