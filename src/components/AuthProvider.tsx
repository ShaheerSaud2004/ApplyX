'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

interface User {
  id: string
  email: string
  firstName: string
  lastName: string
  isAdmin: boolean
}

export interface AuthContextType {
  user: User | null
  token: string | null
  login: (token: string, user: User) => void
  loginWithCredentials: (email: string, password: string) => Promise<{ success: boolean; message: string; isAdmin?: boolean }>
  register: (userData: any) => Promise<{ success: boolean; message: string }>
  logout: () => void
  isLoading: boolean
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    // Check for stored auth data on mount
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      setToken(storedToken)
      setUser(JSON.parse(storedUser))
    }
    setIsLoading(false)
  }, [])

  // Direct login with token and user data (for modals, forms)
  const login = (token: string, user: User) => {
    setToken(token)
    setUser(user)
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))

    // Admin users should always go to admin panel, no profile checks
    if (user.isAdmin) {
      console.log('Admin user detected, redirecting to admin panel')
      router.push('/admin')
    } else {
      router.push('/dashboard')
    }
  }

  // Login with email/password (for login pages)
  const loginWithCredentials = async (email: string, password: string) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      const data = await response.json()

      if (response.ok) {
        login(data.token, data.user)
        return { success: true, message: 'Login successful', isAdmin: data.user.isAdmin }
      } else {
        return { success: false, message: data.error || 'Login failed' }
      }
    } catch (error) {
      return { success: false, message: 'Network error' }
    }
  }

  const register = async (userData: any) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      })

      const data = await response.json()

      if (response.ok) {
        return { success: true, message: 'Registration successful! Please wait for admin approval.' }
      } else {
        return { success: false, message: data.error || 'Registration failed' }
      }
    } catch (error) {
      return { success: false, message: 'Network error' }
    }
  }

  const logout = () => {
    // Clear all auth data
    setUser(null)
    setToken(null)
    localStorage.removeItem('token')
    localStorage.removeItem('user')

    // Clear any other stored data
    localStorage.removeItem('userPlan')
    localStorage.removeItem('dashboardData')

    // Redirect to home page - use replace to prevent back button issues
    router.replace('/')
  }

  return (
    <AuthContext.Provider value={{
      user,
      token,
      login,
      loginWithCredentials,
      register,
      logout,
      isLoading,
      isAuthenticated: !!user && !!token
    }}>
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