'use client'

import React, { useState, useEffect } from 'react'
import { useAuth } from './AuthProvider'
import { PersistentBotIndicator } from './PersistentBotIndicator'

export function GlobalBotIndicator() {
  const { token, isAuthenticated } = useAuth()
  const [botStatus, setBotStatus] = useState<any>(null)
  const [isRunning, setIsRunning] = useState(false)

  useEffect(() => {
    if (!token || !isAuthenticated) {
      setBotStatus(null)
      setIsRunning(false)
      return
    }

    // Check bot status
    const checkBotStatus = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/bot/status`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })

        if (response.ok) {
          const status = await response.json()
          setBotStatus(status)

          // Check for persistent running status
          const running = status.status === 'running' ||
            (status.persistent_session && status.persistent_session.is_active)

          setIsRunning(running)
        }
      } catch (error) {
        console.error('Error checking bot status:', error)
      }
    }

    // Initial check
    checkBotStatus()

    // Poll every 30 seconds for status updates (less frequent than dashboard)
    const interval = setInterval(checkBotStatus, 30000)

    return () => clearInterval(interval)
  }, [token, isAuthenticated])

  // Only show if authenticated and bot is running
  if (!isAuthenticated || !isRunning) {
    return null
  }

  return (
    <PersistentBotIndicator
      isRunning={isRunning}
      persistent={botStatus?.persistent_session?.survives_refresh || false}
      applicationsCount={botStatus?.applicationsSubmitted || 0}
    />
  )
} 