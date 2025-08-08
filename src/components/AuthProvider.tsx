'use client'

import React, { createContext, useContext, useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { getApiUrl } from '@/lib/utils'
import { RoleSelectionModal } from './RoleSelectionModal'

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
  showRoleSelection: (user: User) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [showRoleModal, setShowRoleModal] = useState(false)
  const [roleSelectionUser, setRoleSelectionUser] = useState<User | null>(null)
  const router = useRouter()

  useEffect(() => {
    // Check for existing token on mount
    const existingToken = localStorage.getItem('token')
    const existingUser = localStorage.getItem('user')
    
    if (existingToken && existingUser) {
      try {
        const user = JSON.parse(existingUser)
        setToken(existingToken)
        setUser(user)
      } catch (error) {
        console.error('Error parsing stored user data:', error)
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    } else {
      // Optional dev auto-login only if explicitly enabled
      const devAutoLogin = process.env.NEXT_PUBLIC_DEV_AUTO_LOGIN === '1'
      const devUserJson = process.env.NEXT_PUBLIC_DEV_USER_JSON
      if (devAutoLogin && devUserJson) {
        try {
          const defaultUser = JSON.parse(devUserJson)
          setToken('development-token')
          setUser(defaultUser)
          localStorage.setItem('token', 'development-token')
          localStorage.setItem('user', JSON.stringify(defaultUser))
        } catch (err) {
          console.warn('Invalid NEXT_PUBLIC_DEV_USER_JSON; skipping dev auto-login')
        }
      }
    }
    
    setIsLoading(false)
  }, [])

  // Prevent automatic navigation when role selection modal is open
  useEffect(() => {
    if (showRoleModal && roleSelectionUser) {
      // Modal is open, don't allow automatic navigation
      return
    }
  }, [showRoleModal, roleSelectionUser])

  // Direct login with token and user data (for modals, forms)
  const login = (token: string, user: User) => {
    setToken(token)
    setUser(user)
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(user))

    // Show role selection for admin users
    if (user.isAdmin) {
      console.log('Admin user detected, showing role selection')
      setRoleSelectionUser(user)
      setShowRoleModal(true)
      // Don't redirect automatically - let the modal handle navigation
    } else {
      router.push('/dashboard')
    }
  }

  // Show role selection modal
  const showRoleSelection = (user: User) => {
    setRoleSelectionUser(user)
    setShowRoleModal(true)
  }

  // Login with email/password (for login pages)
  const loginWithCredentials = async (email: string, password: string) => {
    try {
      const response = await fetch(getApiUrl('/api/auth/login'), {
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
      const response = await fetch(getApiUrl('/api/auth/register'), {
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
      isAuthenticated: !!user && !!token,
      showRoleSelection
    }}>
      {children}
      
      {/* Role Selection Modal */}
      {roleSelectionUser && (
        <RoleSelectionModal
          isOpen={showRoleModal}
          onClose={() => {
            setShowRoleModal(false)
            setRoleSelectionUser(null)
          }}
          user={roleSelectionUser}
        />
      )}
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