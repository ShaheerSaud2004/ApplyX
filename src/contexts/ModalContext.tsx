'use client'

import React, { createContext, useContext, useState, ReactNode } from 'react'

interface ModalContextType {
  isLoginOpen: boolean
  isSignupOpen: boolean
  openLogin: () => void
  openSignup: () => void
  closeLogin: () => void
  closeSignup: () => void
  closeAll: () => void
}

const ModalContext = createContext<ModalContextType | undefined>(undefined)

export function ModalProvider({ children }: { children: ReactNode }) {
  const [isLoginOpen, setIsLoginOpen] = useState(false)
  const [isSignupOpen, setIsSignupOpen] = useState(false)

  const openLogin = () => {
    setIsSignupOpen(false)
    setIsLoginOpen(true)
  }

  const openSignup = () => {
    setIsLoginOpen(false)
    setIsSignupOpen(true)
  }

  const closeLogin = () => setIsLoginOpen(false)
  const closeSignup = () => setIsSignupOpen(false)

  const closeAll = () => {
    setIsLoginOpen(false)
    setIsSignupOpen(false)
  }

  return (
    <ModalContext.Provider
      value={{
        isLoginOpen,
        isSignupOpen,
        openLogin,
        openSignup,
        closeLogin,
        closeSignup,
        closeAll
      }}
    >
      {children}
    </ModalContext.Provider>
  )
}

export function useModal() {
  const context = useContext(ModalContext)
  if (context === undefined) {
    throw new Error('useModal must be used within a ModalProvider')
  }
  return context
} 