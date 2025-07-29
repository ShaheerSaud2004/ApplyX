import React, { useState } from 'react'
import { LoginModal } from './LoginModal'
import { SignupModal } from './SignupModal'

export interface AuthModalsProps {
  isLoginOpen: boolean
  isSignupOpen: boolean
  onLoginClose: () => void
  onSignupClose: () => void
  onLoginOpen?: () => void
  onSignupOpen?: () => void
  onLoginSuccess?: () => void
  onSignupSuccess?: () => void
}

export const AuthModals: React.FC<AuthModalsProps> = ({
  isLoginOpen,
  isSignupOpen,
  onLoginClose,
  onSignupClose,
  onLoginOpen,
  onSignupOpen,
  onLoginSuccess,
  onSignupSuccess
}) => {
  return (
    <>
      <LoginModal
        isOpen={isLoginOpen}
        onOpenChange={onLoginClose}
        onSwitchToSignup={() => {
          onLoginClose()
          onSignupOpen?.()
        }}
      />
      <SignupModal
        isOpen={isSignupOpen}
        onOpenChange={onSignupClose}
        onSwitchToLogin={() => {
          onSignupClose()
          onLoginOpen?.()
        }}
      />
    </>
  )
}

export const useAuthModals = () => {
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

  return {
    isLoginOpen,
    isSignupOpen,
    openLogin,
    openSignup,
    closeLogin,
    closeSignup,
    closeAll
  }
} 