import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '@/components/AuthProvider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'EasyApply Platform - AI-Powered Job Application Assistant',
  description: 'Automate your job applications with AI-powered resume tailoring and ChatGPT Agent Mode',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-background">
          <AuthProvider>
            {children}
          </AuthProvider>
        </div>
      </body>
    </html>
  )
} 