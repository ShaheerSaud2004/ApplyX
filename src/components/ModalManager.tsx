'use client'

import { useModal } from '@/contexts/ModalContext'
import { AuthModals } from './AuthModals'

export function ModalManager() {
  const { isLoginOpen, isSignupOpen, closeLogin, closeSignup, openLogin, openSignup } = useModal()

  return (
    <AuthModals 
      isLoginOpen={isLoginOpen}
      isSignupOpen={isSignupOpen}
      onLoginClose={closeLogin}
      onSignupClose={closeSignup}
      onLoginOpen={openLogin}
      onSignupOpen={openSignup}
    />
  )
} 