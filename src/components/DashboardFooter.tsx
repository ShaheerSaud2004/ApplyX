"use client"

import Link from 'next/link'

export default function DashboardFooter() {
  const year = new Date().getFullYear()
  return (
    <footer className="w-full border-t bg-white/80 backdrop-blur-sm">
      <div className="mx-auto max-w-7xl px-4 md:px-6 py-3 flex items-center justify-between">
        <p className="text-[11px] text-gray-500 whitespace-nowrap overflow-hidden text-ellipsis">
          © {year} ApplyX • Nebula.AI • All rights reserved.
        </p>
        <nav className="hidden sm:flex gap-4 sm:gap-6">
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