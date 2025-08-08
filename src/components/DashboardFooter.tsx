"use client"

import Link from 'next/link'

export default function DashboardFooter() {
  const year = new Date().getFullYear()
  return (
    <footer className="w-full border-t bg-white/80 backdrop-blur-sm">
      <div className="mx-auto max-w-7xl px-4 md:px-6 py-4 flex flex-col items-center gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-col items-center text-center sm:flex-row sm:items-center sm:text-left">
          <p className="text-xs text-gray-500">
            © {year} ApplyX
          </p>
          <span aria-hidden className="hidden sm:inline mx-3 h-1 w-1 rounded-full bg-gray-300" />
          <p className="text-xs text-gray-500">A product of Nebula.AI</p>
          <span aria-hidden className="hidden sm:inline mx-3 h-1 w-1 rounded-full bg-gray-300" />
          <p className="text-xs text-gray-500">All rights reserved.</p>
        </div>
        <nav className="flex flex-wrap justify-center gap-x-6 gap-y-2">
          <Link className="text-xs hover:underline underline-offset-4 text-gray-500 hover:text-blue-600" href="/terms">
            Terms of Service
          </Link>
          <Link className="text-xs hover:underline underline-offset-4 text-gray-500 hover:text-blue-600" href="/privacy">
            Privacy Policy
          </Link>
        </nav>
      </div>
    </footer>
  )
} 