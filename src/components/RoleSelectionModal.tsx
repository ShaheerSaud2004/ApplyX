'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { useRouter } from 'next/navigation'
import { Shield, User, Settings, BarChart3, Users, Briefcase, X } from 'lucide-react'

interface RoleSelectionModalProps {
  isOpen: boolean
  onClose: () => void
  user: {
    id: string
    email: string
    firstName: string
    lastName: string
    isAdmin: boolean
  }
}

export function RoleSelectionModal({ isOpen, onClose, user }: RoleSelectionModalProps) {
  const router = useRouter()
  const [selectedRole, setSelectedRole] = useState<'admin' | 'user' | null>(null)

  // Debug logging
  console.log('RoleSelectionModal:', { isOpen, user: user?.firstName })

  const handleRoleSelect = (role: 'admin' | 'user') => {
    console.log('Role selected:', role)
    setSelectedRole(role)
    
    // Add a small delay to ensure modal state is properly managed
    setTimeout(() => {
      console.log('Navigating to:', role === 'admin' ? '/admin' : '/dashboard')
      // Navigate to the selected dashboard
      if (role === 'admin') {
        router.push('/admin')
      } else {
        router.push('/dashboard')
      }
      
      onClose()
    }, 100)
  }

  const handleClose = () => {
    // Don't automatically redirect - just close the modal
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="fixed left-[50%] top-[50%] z-[99999] grid w-[95vw] max-w-2xl translate-x-[-50%] translate-y-[-50%] gap-6 border bg-white p-8 shadow-2xl duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] rounded-lg">
        {/* Close Button */}
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-100 transition-colors"
        >
          <X className="h-5 w-5" />
        </button>

        <DialogHeader className="space-y-4">
          <div className="flex justify-center">
            <div className="relative">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-600 to-blue-600 rounded-full flex items-center justify-center">
                <Shield className="h-8 w-8 text-white" />
              </div>
              <div className="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center">
                <User className="h-3 w-3 text-white" />
              </div>
            </div>
          </div>
          
          <div className="text-center space-y-2">
            <DialogTitle className="text-2xl font-bold text-gray-900">
              Welcome back, {user.firstName}! 👋
            </DialogTitle>
            <DialogDescription className="text-gray-600">
              You have admin privileges. Choose which dashboard you'd like to access:
            </DialogDescription>
          </div>
        </DialogHeader>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Admin Dashboard Option */}
          <div 
            className={`relative p-6 border-2 rounded-lg cursor-pointer transition-all duration-200 hover:shadow-lg ${
              selectedRole === 'admin' 
                ? 'border-purple-500 bg-purple-50' 
                : 'border-gray-200 hover:border-purple-300 bg-white'
            }`}
            onClick={() => handleRoleSelect('admin')}
          >
            <div className="flex items-center justify-center mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-600 to-blue-600 rounded-full flex items-center justify-center">
                <Shield className="h-6 w-6 text-white" />
              </div>
            </div>
            
            <h3 className="text-lg font-semibold text-gray-900 text-center mb-2">
              Admin Dashboard
            </h3>
            
            <p className="text-sm text-gray-600 text-center mb-4">
              Manage users, monitor system, and oversee operations
            </p>
            
            <div className="space-y-2">
              <div className="flex items-center text-xs text-gray-500">
                <Users className="h-3 w-3 mr-2" />
                User Management
              </div>
              <div className="flex items-center text-xs text-gray-500">
                <BarChart3 className="h-3 w-3 mr-2" />
                Analytics & Reports
              </div>
              <div className="flex items-center text-xs text-gray-500">
                <Settings className="h-3 w-3 mr-2" />
                System Settings
              </div>
            </div>
            
            {selectedRole === 'admin' && (
              <div className="absolute top-2 right-2">
                <div className="w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
                  <svg className="h-2 w-2 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            )}
          </div>

          {/* User Dashboard Option */}
          <div 
            className={`relative p-6 border-2 rounded-lg cursor-pointer transition-all duration-200 hover:shadow-lg ${
              selectedRole === 'user' 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-200 hover:border-blue-300 bg-white'
            }`}
            onClick={() => handleRoleSelect('user')}
          >
            <div className="flex items-center justify-center mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-cyan-600 rounded-full flex items-center justify-center">
                <Briefcase className="h-6 w-6 text-white" />
              </div>
            </div>
            
            <h3 className="text-lg font-semibold text-gray-900 text-center mb-2">
              User Dashboard
            </h3>
            
            <p className="text-sm text-gray-600 text-center mb-4">
              Apply to jobs, track applications, and manage your profile
            </p>
            
            <div className="space-y-2">
              <div className="flex items-center text-xs text-gray-500">
                <Briefcase className="h-3 w-3 mr-2" />
                Job Applications
              </div>
              <div className="flex items-center text-xs text-gray-500">
                <BarChart3 className="h-3 w-3 mr-2" />
                Application Tracking
              </div>
              <div className="flex items-center text-xs text-gray-500">
                <User className="h-3 w-3 mr-2" />
                Profile Management
              </div>
            </div>
            
            {selectedRole === 'user' && (
              <div className="absolute top-2 right-2">
                <div className="w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
                  <svg className="h-2 w-2 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="text-center">
          <p className="text-xs text-gray-500 mb-4">
            You can switch between dashboards anytime from the navigation menu
          </p>
          
          <div className="flex justify-center gap-3">
            <Button 
              onClick={() => handleRoleSelect('admin')}
              className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white"
            >
              Go to Admin Dashboard
            </Button>
            <Button 
              onClick={() => handleRoleSelect('user')}
              variant="outline"
              className="border-blue-200 text-blue-600 hover:bg-blue-50"
            >
              Go to User Dashboard
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
} 