'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'

interface User {
  id: string
  email: string
  first_name: string
  last_name: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (token: string, user: User) => void
  logout: () => void
  loading: boolean
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    // Check for existing auth on mount
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')

    if (savedToken && savedUser) {
      try {
        const parsedUser = JSON.parse(savedUser)
        setToken(savedToken)
        setUser(parsedUser)
      } catch (error) {
        console.error('Error parsing saved user:', error)
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    }
    setLoading(false)
  }, [])

  useEffect(() => {
    // Redirect logic based on auth state
    if (!loading) {
      const isAuthPage = pathname?.startsWith('/auth/')
      const isPublicPage = ['/', '/pricing'].includes(pathname || '')
      const isProtectedPage = ['/dashboard', '/profile', '/admin'].some(path => 
        pathname?.startsWith(path)
      )

      if (user && isAuthPage) {
        // Logged in user trying to access auth pages -> redirect to dashboard
        router.push('/dashboard')
      } else if (!user && isProtectedPage) {
        // Non-logged in user trying to access protected pages -> redirect to login
        router.push('/auth/login')
      }
    }
  }, [user, pathname, loading, router])

  const login = (newToken: string, newUser: User) => {
    setToken(newToken)
    setUser(newUser)
    localStorage.setItem('token', newToken)
    localStorage.setItem('user', JSON.stringify(newUser))
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/')
  }

  const value = {
    user,
    token,
    login,
    logout,
    loading,
    isAuthenticated: !!user
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
} 