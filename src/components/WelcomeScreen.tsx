'use client'

import { useEffect, useState } from 'react'
import { useAuth } from './AuthProvider'
import { CheckCircle, Sparkles } from 'lucide-react'

export function WelcomeScreen() {
  const { user } = useAuth()
  const [isVisible, setIsVisible] = useState(false)
  const [showWelcome, setShowWelcome] = useState(false)

  useEffect(() => {
    if (user) {
      setShowWelcome(true)
      setIsVisible(true)
      // Hide welcome screen after 3 seconds
      const timer = setTimeout(() => {
        setIsVisible(false)
        setTimeout(() => setShowWelcome(false), 500)
      }, 3000)
      return () => clearTimeout(timer)
    }
  }, [user])

  if (!showWelcome || !user) return null

  return (
    <div className={`fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center transition-all duration-500 ${isVisible ? 'opacity-100' : 'opacity-0'}`}>
      <div className={`bg-white rounded-2xl shadow-2xl p-8 max-w-md mx-4 text-center transform transition-all duration-500 ${isVisible ? 'scale-100 translate-y-0' : 'scale-95 translate-y-4'}`}>
        <div className="relative mb-6">
          <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-blue-600 rounded-full flex items-center justify-center mx-auto">
            <CheckCircle className="h-8 w-8 text-white" />
          </div>
          <div className="absolute -top-2 -right-2">
            <Sparkles className="h-6 w-6 text-yellow-500 animate-pulse" />
          </div>
        </div>

        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Welcome back, {user.firstName}! 🎉
        </h2>

        <p className="text-gray-600 mb-4">
          You're successfully logged in. Taking you to your dashboard...
        </p>

        <div className="flex items-center justify-center space-x-2">
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
      </div>
    </div>
  )
} 