'use client'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { 
  Bot, 
  BrainCircuit, 
  Calendar, 
  FileText, 
  Play, 
  Target, 
  TrendingUp, 
  Users,
  Pause,
  RefreshCw,
  Upload,
  CheckCircle,
  Clock,
  AlertCircle,
  Coffee,
  Sparkles,
  LogOut,
  User,
  Shield,
  Trash2,
  Menu,
  X,
  Settings
} from 'lucide-react'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import { useAuth } from '@/components/AuthProvider'
import { WelcomeOnboarding } from '@/components/WelcomeOnboarding'
import { ResumeUploadModal } from '@/components/ResumeUploadModal'
import { LinkedInCredentialsModal } from '@/components/LinkedInCredentialsModal'
import { EnhancedBotStatusDashboard } from '@/components/EnhancedBotStatusDashboard'
import { LiveActivityLog } from '@/components/LiveActivityLog'
import { getApiUrl } from '@/lib/utils'
import DashboardFooter from '@/components/DashboardFooter'

// Version tracking - update this with each change
const APP_VERSION = "1.0.9"

interface UserStats {
  totalApplications: number
  applicationsThisWeek: number
  applicationsThisMonth: number
  successRate: number
  averageResponseTime: number
  topCompanies: Array<{ company: string; count: number }>
  applicationsByStatus: Array<{ status: string; count: number }>
}

interface UserPlan {
  plan: string
  dailyQuota: number
  dailyUsage: number
  subscriptionStatus: string
}

interface Application {
  id: string
  jobTitle: string
  company: string
  location: string
  appliedAt: Date
  status: string
  aiGenerated: boolean
}

interface AgentStatus {
  status: 'running' | 'stopped' | 'error' | 'paused'
  currentTask: string
  progress: number
  tasksCompleted: number
  applicationsSubmitted: number
  lastRun: string | null
  user_id?: string
  started_at?: string
  pid?: number
  sessionStartTime?: string
  estimatedTimeRemaining?: number
  currentJobTitle?: string
  currentCompany?: string
  detailedSteps?: {
    step: string
    status: 'completed' | 'current' | 'pending'
    timestamp?: string
  }[]
}

export default function DashboardPage() {
  const { user, token, logout } = useAuth()
  const [needsOnboarding, setNeedsOnboarding] = useState(true)
  const [checkingOnboarding, setCheckingOnboarding] = useState(true)
  const [stats, setStats] = useState<UserStats | null>(null)
  const [userPlan, setUserPlan] = useState<UserPlan | null>(null)
  const [recentApplications, setRecentApplications] = useState<Application[]>([])
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null)
  const [agentRunning, setAgentRunning] = useState(false)
  const [showResumeUpload, setShowResumeUpload] = useState(false)
  const [showLinkedInModal, setShowLinkedInModal] = useState(false)
  const [hasLinkedInCredentials, setHasLinkedInCredentials] = useState(false)
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null)
  const [isStartingBot, setIsStartingBot] = useState(false)
  const [isStoppingBot, setIsStoppingBot] = useState(false)
  const [botActionMessage, setBotActionMessage] = useState<string>('')
  const [isResettingAccount, setIsResettingAccount] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [timeUntilReset, setTimeUntilReset] = useState('')

  useEffect(() => {
    checkOnboardingStatus()
  }, [token])

  useEffect(() => {
    if (token && !needsOnboarding) {
      loadDashboardData()
    }
  }, [token, needsOnboarding])

  // Auto-clear bot action messages after 5 seconds
  useEffect(() => {
    if (botActionMessage) {
      const timer = setTimeout(() => {
        setBotActionMessage('')
      }, 5000)
      return () => clearTimeout(timer)
    }
  }, [botActionMessage])

  // Calculate countdown timer for quota reset
  useEffect(() => {
    const updateCountdown = () => {
      const now = new Date()
      const midnight = new Date(now)
      midnight.setHours(24, 0, 0, 0)
      const timeUntilMidnight = midnight.getTime() - now.getTime()
      
      const hours = Math.floor(timeUntilMidnight / (1000 * 60 * 60))
      const minutes = Math.floor((timeUntilMidnight % (1000 * 60 * 60)) / (1000 * 60))
      const seconds = Math.floor((timeUntilMidnight % (1000 * 60)) / 1000)
      
      setTimeUntilReset(`${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`)
    }

    // Update immediately
    updateCountdown()
    
    // Update every second
    const interval = setInterval(updateCountdown, 1000)
    
    return () => clearInterval(interval)
  }, [])

  // Real-time polling for bot status when running
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null

    if (agentRunning && token) {
      // Poll every 5 seconds when bot is running (reduced frequency)
      interval = setInterval(async () => {
        try {
          // Poll bot status
          const response = await fetch(getApiUrl('/api/bot/status'), {
            headers: { 'Authorization': `Bearer ${token}` }
          })
          
          if (response.ok) {
            const agentData = await response.json()
            setAgentStatus(agentData)
            
            // If bot stopped, update running state
            if (agentData.status === 'stopped' || agentData.status === 'completed' || agentData.status === 'error') {
              setAgentRunning(false)
              // Reload full dashboard data to get updated application counts
              loadDashboardData()
            }
          }
          
          // Also update quota status and stats in real-time
          const quotaResponse = await fetch(getApiUrl('/api/user/plan'), {
            headers: { 'Authorization': `Bearer ${token}` }
          })
          
          if (quotaResponse.ok) {
            const quotaData = await quotaResponse.json()
            setUserPlan(quotaData)
          }

          // Update application stats and recent applications in real-time
          const [statsResponse, appsResponse] = await Promise.all([
            fetch(getApiUrl('/api/applications/stats'), {
              headers: { 'Authorization': `Bearer ${token}` }
            }),
            fetch(getApiUrl('/api/applications?limit=5'), {
              headers: { 'Authorization': `Bearer ${token}` }
            })
          ])
          
          if (statsResponse.ok) {
            const statsData = await statsResponse.json()
            setStats(statsData)
          }

          if (appsResponse.ok) {
            const appsData = await appsResponse.json()
            setRecentApplications(appsData.applications || [])
          }
          
        } catch (error) {
          console.error('Error polling bot status:', error)
        }
      }, 5000) // Poll every 5 seconds for better performance
      
      setPollingInterval(interval)
    } else {
      // Even when bot is not running, poll less frequently for quota updates
      if (token) {
        interval = setInterval(async () => {
          try {
            // Update quota status periodically
            const quotaResponse = await fetch(getApiUrl('/api/user/plan'), {
              headers: { 'Authorization': `Bearer ${token}` }
            })
            
            if (quotaResponse.ok) {
              const quotaData = await quotaResponse.json()
              setUserPlan(quotaData)
            }

            // Update application stats and recent applications periodically
            const [statsResponse, appsResponse] = await Promise.all([
              fetch(getApiUrl('/api/applications/stats'), {
                headers: { 'Authorization': `Bearer ${token}` }
              }),
              fetch(getApiUrl('/api/applications?limit=5'), {
                headers: { 'Authorization': `Bearer ${token}` }
              })
            ])
            
            if (statsResponse.ok) {
              const statsData = await statsResponse.json()
              setStats(statsData)
            }

            if (appsResponse.ok) {
              const appsData = await appsResponse.json()
              setRecentApplications(appsData.applications || [])
            }
          } catch (error) {
            console.error('Error polling quota status:', error)
          }
        }, 30000) // Poll every 30 seconds when bot is not running
        
        setPollingInterval(interval)
      } else if (interval) {
        clearInterval(interval)
        setPollingInterval(null)
      }
    }

    // Cleanup on unmount or when dependencies change
    return () => {
      if (interval) {
        clearInterval(interval)
      }
    }
  }, [agentRunning, token])

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval)
      }
    }
  }, [])

  const checkOnboardingStatus = async () => {
    if (!token) return
    
    // Skip onboarding checks for admin users
    if (user?.isAdmin) {
      setNeedsOnboarding(false)
      setCheckingOnboarding(false)
      return
    }
    
    try {
      const response = await fetch(getApiUrl('/api/profile'), {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        // Check if user has completed basic profile setup
        const hasBasicInfo = data.user?.firstName && data.user?.lastName
        const hasJobPrefs = data.jobPreferences?.jobTitles || data.jobTitles
        const hasLinkedIn = data.linkedinCreds?.hasCredentials || (data.linkedinCreds?.email && data.linkedinCreds?.password)
        const onboardingCompleted = data.onboardingCompleted || data.user?.onboardingCompleted
        
        setHasLinkedInCredentials(hasLinkedIn)
        // User needs onboarding if they haven't completed it OR missing basic info/job prefs
        setNeedsOnboarding(!onboardingCompleted && !(hasBasicInfo && hasJobPrefs))
      }
    } catch (error) {
      console.error('Error checking onboarding status:', error)
    } finally {
      setCheckingOnboarding(false)
    }
  }

  const handleManualRefresh = async () => {
    setIsRefreshing(true)
    try {
      await loadDashboardData()
    } catch (error) {
      console.error('Error refreshing dashboard:', error)
    } finally {
      setIsRefreshing(false)
    }
  }

  const loadDashboardData = async () => {
    try {
      console.log('🔍 Loading dashboard data with token:', token ? 'Token exists' : 'No token')
      // Load user plan/quota info
      const planResponse = await fetch(getApiUrl('/api/user/plan'), {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (planResponse.ok) {
        const planData = await planResponse.json()
        setUserPlan({
          plan: planData.plan || 'free',
          dailyQuota: planData.dailyQuota || 10,
          dailyUsage: planData.dailyUsage || 0,
          subscriptionStatus: planData.status || 'active'
        })
      } else {
        // Default plan for new users
        setUserPlan({
          plan: 'free',
          dailyQuota: 10,
          dailyUsage: 0,
          subscriptionStatus: 'active'
        })
      }

      // Load applications stats
      const statsResponse = await fetch(getApiUrl('/api/applications/stats'), {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (statsResponse.ok) {
        const statsData = await statsResponse.json()
        setStats(statsData)
      }

      // Load recent applications
      console.log('🔍 Fetching applications from:', getApiUrl('/api/applications?limit=5'))
      const appsResponse = await fetch(getApiUrl('/api/applications?limit=5'), {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      console.log('🔍 Applications response status:', appsResponse.status)
      if (appsResponse.ok) {
        const appsData = await appsResponse.json()
        console.log('🔍 Applications data:', appsData)
        setRecentApplications(appsData.applications || [])
      } else {
        console.error('❌ Applications fetch failed:', appsResponse.status, await appsResponse.text())
      }

      // Load agent status
      const agentResponse = await fetch(getApiUrl('/api/bot/status'), {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (agentResponse.ok) {
        const agentData = await agentResponse.json()
        setAgentStatus(agentData)
        
        // Check for persistent running status
        const isRunning = agentData.status === 'running' || 
                         (agentData.persistent_session && agentData.persistent_session.is_active)
        
        setAgentRunning(isRunning)
        
        // Log persistence info for debugging
        if (agentData.persistent_session) {
          console.log('🔄 Found persistent session:', {
            survives_refresh: agentData.persistent_session.survives_refresh,
            restart_count: agentData.persistent_session.restart_count,
            session_id: agentData.persistent_session.session_id
          })
        }
      } else {
        // Default agent status for new users
        setAgentStatus({
          status: 'stopped',
          currentTask: 'Ready to start job search',
          progress: 0,
          tasksCompleted: 0,
          applicationsSubmitted: 0,
          lastRun: null
        })
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error)
      // Set default empty states
      setUserPlan({
        plan: 'free',
        dailyQuota: 5,
        dailyUsage: 0,
        subscriptionStatus: 'active'
      })
      setAgentStatus({
        status: 'stopped',
        currentTask: 'Ready to start job search',
        progress: 0,
        tasksCompleted: 0,
        applicationsSubmitted: 0,
        lastRun: null
      })
    }
  }

  const handleOnboardingComplete = () => {
    setNeedsOnboarding(false)
  }

  const handleOnboardingSkip = () => {
    setNeedsOnboarding(false)
  }

  const handleStartAgent = async () => {
    // Check if user has LinkedIn credentials first
    if (!hasLinkedInCredentials) {
      setShowLinkedInModal(true)
      return
    }

    // Start the agent (quota checking now done server-side)
    setIsStartingBot(true)
    setBotActionMessage('🚀 Starting LinkedIn job application bot...')
    
    try {
      const response = await fetch(getApiUrl('/api/bot/start'), {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        // Immediately show bot as running
        setAgentRunning(true)
        setBotActionMessage('✅ Bot started successfully! Opening LinkedIn and beginning job search...')
        
        // Set initial status while bot initializes
        setAgentStatus({
          status: 'running',
          currentTask: 'Initializing bot and LinkedIn session...',
          progress: 0,
          tasksCompleted: 0,
          applicationsSubmitted: 0,
          lastRun: new Date().toISOString(),
          detailedSteps: [
            {
              step: 'Initialize LinkedIn session',
              status: 'current',
              timestamp: new Date().toISOString()
            },
            {
              step: 'Search for matching jobs',
              status: 'pending'
            },
            {
              step: 'Apply to qualified positions',
              status: 'pending'
            },
            {
              step: 'Generate application reports',
              status: 'pending'
            }
          ],
          sessionStartTime: new Date().toISOString(),
          estimatedTimeRemaining: 3600 // 1 hour estimate
        })
        
        // Real-time polling will start automatically due to agentRunning state change
        console.log('✅ Bot started successfully - Real-time updates enabled')
      } else {
        const errorData = await response.json()
        
        // Handle different error types
        if (errorData.code === 'QUOTA_EXCEEDED') {
          // Calculate time until midnight
          const now = new Date()
          const midnight = new Date(now)
          midnight.setHours(24, 0, 0, 0)
          const timeUntilMidnight = midnight.getTime() - now.getTime()
          const hours = Math.floor(timeUntilMidnight / (1000 * 60 * 60))
          const minutes = Math.floor((timeUntilMidnight % (1000 * 60 * 60)) / (1000 * 60))
          
          setBotActionMessage(`🚫 Daily quota reached! (${errorData.quota_info?.daily_usage}/${errorData.quota_info?.daily_quota} applications used). Bot will automatically restart in ${hours}h ${minutes}m when quota resets at midnight. 🌙`)
        } else if (errorData.code === 'LINKEDIN_CREDENTIALS_MISSING') {
          setHasLinkedInCredentials(false)
          setShowLinkedInModal(true)
          setBotActionMessage('⚠️ LinkedIn credentials required to start the bot.')
        } else if (errorData.code === 'CREDENTIALS_MISSING') {
          setHasLinkedInCredentials(false)
          setShowLinkedInModal(true)
          setBotActionMessage('⚠️ LinkedIn credentials not configured. Please add them in your profile.')
        } else {
          setBotActionMessage(`❌ Failed to start bot: ${errorData.message || errorData.error || 'Unknown error'}`)
        }
      }
    } catch (error) {
      console.error('Error starting agent:', error)
      setBotActionMessage('❌ Network error. Please check your connection and try again.')
    } finally {
      setIsStartingBot(false)
    }
  }

  const handleLinkedInCredentialsSaved = () => {
    setHasLinkedInCredentials(true)
    setShowLinkedInModal(false)
    // Refresh the onboarding status to make sure we have the latest LinkedIn credentials
    checkOnboardingStatus()
    // Reload dashboard data to reflect the updated credentials
    loadDashboardData()
    // Show success message
    alert('LinkedIn credentials saved successfully! You can now start the agent.')
  }

  const handleStopAgent = async () => {
    setIsStoppingBot(true)
    setBotActionMessage('🛑 Stopping bot and cleaning up...')
    
    try {
      const response = await fetch(getApiUrl('/api/bot/stop'), {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        // Immediately update UI
        setAgentRunning(false)
        setAgentStatus(prev => ({
          status: 'stopped',
          currentTask: 'Bot stopped by user',
          progress: 0,
          tasksCompleted: prev?.tasksCompleted || 0,
          applicationsSubmitted: prev?.applicationsSubmitted || 0,
          lastRun: prev?.lastRun || new Date().toISOString(),
          user_id: prev?.user_id,
          started_at: prev?.started_at,
          pid: prev?.pid,
          sessionStartTime: prev?.sessionStartTime,
          estimatedTimeRemaining: prev?.estimatedTimeRemaining,
          currentJobTitle: prev?.currentJobTitle,
          currentCompany: prev?.currentCompany,
          detailedSteps: prev?.detailedSteps
        }))
        
        setBotActionMessage('✅ Bot stopped successfully! All processes have been terminated.')
        
        // Reload dashboard data to get final stats
        loadDashboardData()
        console.log('🛑 Bot stopped successfully')
      } else {
        const errorData = await response.json()
        setBotActionMessage(`❌ Failed to stop bot: ${errorData.message || errorData.error || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Error stopping agent:', error)
      setBotActionMessage('❌ Network error while stopping agent.')
    } finally {
      setIsStoppingBot(false)
    }
  }

  const handleResetAccount = async () => {
    if (!confirm('⚠️ WARNING: This will permanently delete ALL your application history, activity logs, and bot sessions. This action cannot be undone.\n\nAre you sure you want to reset your account?')) {
      return
    }

    setIsResettingAccount(true)
    try {
      const response = await fetch(getApiUrl('/api/user/reset-account'), {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      const data = await response.json()

      if (response.ok) {
        setBotActionMessage(`✅ ${data.message}`)
        // Reload dashboard data to reflect the reset
        await loadDashboardData()
      } else {
        setBotActionMessage(`❌ ${data.error || 'Failed to reset account'}`)
      }
    } catch (error) {
      console.error('Reset account error:', error)
      setBotActionMessage('❌ Failed to reset account. Please check your connection and try again.')
    } finally {
      setIsResettingAccount(false)
    }
  }

  const toggleAgent = async () => {
    if (!userPlan || userPlan.dailyUsage >= userPlan.dailyQuota) return
    
    if (agentRunning) {
      await handleStopAgent()
    } else {
      await handleStartAgent()
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'applied': return 'text-blue-600'
      case 'interview': return 'text-green-600'
      case 'rejected': return 'text-red-600'
      case 'offer': return 'text-purple-600'
      default: return 'text-gray-600'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'applied': return <Clock className="h-4 w-4" />
      case 'interview': return <Users className="h-4 w-4" />
      case 'rejected': return <AlertCircle className="h-4 w-4" />
      case 'offer': return <CheckCircle className="h-4 w-4" />
      default: return <Clock className="h-4 w-4" />
    }
  }

  // Show loading while checking onboarding status
  if (checkingOnboarding) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-8 h-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent mx-auto"></div>
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    )
  }

  // Show onboarding for new users
  if (needsOnboarding) {
    return <WelcomeOnboarding onComplete={handleOnboardingComplete} onSkip={handleOnboardingSkip} />
  }

  // Check if user has any application data
  const hasApplicationData = stats && stats.totalApplications > 0
  const hasAgentRun = agentStatus && agentStatus.lastRun

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
                    <header className="border-b bg-white/80 backdrop-blur-md sticky top-0 z-50">
                <div className="flex h-14 md:h-16 items-center px-3 md:px-4">
                  <Link href="/" className="flex items-center space-x-2">
                    <div className="relative">
                      <div className="w-5 h-5 md:w-6 md:h-6 bg-gradient-to-br from-blue-600 to-purple-600 rounded flex items-center justify-center shadow-lg">
                        <svg className="h-3 w-3 md:h-4 md:w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                        </svg>
                      </div>
                      <div className="absolute -top-0.5 -right-0.5 w-1.5 h-1.5 md:w-2 md:h-2 bg-gradient-to-br from-orange-500 to-red-500 rounded-full animate-pulse"></div>
                    </div>
                    <div className="flex flex-col">
                      <span className="font-bold text-sm md:text-base bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                        ApplyX
                      </span>
                      <span className="text-xs text-muted-foreground -mt-1 hidden sm:block">by Nebula.AI</span>
                    </div>
                  </Link>
                  
                  {/* Mobile Back Button */}
                  <Link href="/" className="ml-4 md:hidden">
                    <Button variant="ghost" size="sm" className="text-xs">
                      ← Home
                    </Button>
                  </Link>
          
          {/* Desktop Navigation */}
          <nav className="ml-4 md:ml-6 hidden md:flex items-center space-x-3 lg:space-x-6">
            <Link href="/dashboard" className="text-sm font-medium transition-colors hover:text-blue-600">
              Dashboard
            </Link>
            <Link href="/applications" className="text-sm font-medium text-muted-foreground transition-colors hover:text-blue-600">
              Applications
            </Link>
            <Link href="/manual-apply" className="text-sm font-medium text-muted-foreground transition-colors hover:text-blue-600">
              Manual Apply
            </Link>
            <Link href="/profile" className="text-sm font-medium text-muted-foreground transition-colors hover:text-blue-600">
              Profile
            </Link>
            {user?.isAdmin && (
              <Link href="/admin" className="text-sm font-medium text-blue-600 hover:text-blue-800 transition-colors">
                Admin
              </Link>
            )}
          </nav>
          
          <div className="ml-auto flex items-center space-x-2">
            {/* Version display */}
            <div className="hidden sm:flex items-center text-xs text-muted-foreground bg-gray-50 rounded-full px-2 py-1">
              <span className="font-mono">v{APP_VERSION}</span>
            </div>
            
            {/* User info - hidden on mobile */}
            <div className="hidden lg:flex items-center space-x-2 text-sm bg-white/60 rounded-full px-3 py-1.5">
              <div className="w-5 h-5 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                <User className="h-3 w-3 text-white" />
              </div>
              <span className="font-medium">{user?.firstName} {user?.lastName}</span>
            </div>

            {/* Mobile menu button */}
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2"
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>

            <Button variant="outline" size="sm" onClick={logout} className="hover:bg-red-50 hover:border-red-200 hover:text-red-600 transition-all text-xs md:text-sm">
              <LogOut className="h-4 w-4 md:mr-2" />
              <span className="hidden md:inline">Logout</span>
            </Button>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t bg-white/95 backdrop-blur-md">
            <nav className="flex flex-col space-y-1 p-4">
              <Link 
                href="/dashboard" 
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-900 rounded-md hover:bg-gray-100 transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                Dashboard
              </Link>
              <Link 
                href="/applications" 
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-600 rounded-md hover:bg-gray-100 transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                Applications
              </Link>
              <Link 
                href="/manual-apply" 
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-600 rounded-md hover:bg-gray-100 transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                Manual Apply
              </Link>
              <Link 
                href="/profile" 
                className="flex items-center px-3 py-2 text-sm font-medium text-gray-600 rounded-md hover:bg-gray-100 transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                Profile
              </Link>
              {user?.isAdmin && (
                <Link 
                  href="/admin" 
                  className="flex items-center px-3 py-2 text-sm font-medium text-blue-600 rounded-md hover:bg-blue-50 transition-colors"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Admin
                </Link>
              )}
              <div className="flex items-center px-3 py-2 text-xs text-gray-500">
                <span className="font-mono">v{APP_VERSION}</span>
              </div>
            </nav>
          </div>
        )}
      </header>

      <div className="flex-1 space-y-8 md:space-y-10 p-3 md:p-8 pt-4 md:pt-6">
        {/* Welcome Section */}
        <div className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 via-purple-600/10 to-indigo-600/10 rounded-2xl"></div>
          <div className="absolute top-0 right-0 w-32 h-32 md:w-64 md:h-64 opacity-10">
            <svg viewBox="0 0 200 200" className="w-full h-full">
              <defs>
                <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#3b82f6"/>
                  <stop offset="100%" stopColor="#8b5cf6"/>
                </linearGradient>
              </defs>
              <circle cx="100" cy="100" r="80" fill="url(#grad1)"/>
            </svg>
          </div>
          <div className="relative p-3 md:p-6 lg:p-8">
            <div className="flex flex-col space-y-4">
              <div className="space-y-2">
                <h1 className="text-xl md:text-2xl lg:text-4xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent">
                  Welcome back, {user?.firstName}! 👋
                </h1>
                <p className="text-sm md:text-base lg:text-lg text-gray-600">
                  Your AI-powered job application assistant is ready to help you land your dream job. 
                  Let's make today count!
                </p>
                {/* Version display in welcome section */}
                <div className="flex items-center space-x-3 pt-2">
                  <span className="text-xs text-blue-600 bg-blue-100 rounded-full px-2 py-1 font-medium">
                    Version {APP_VERSION}
                  </span>
                  <span className="text-xs text-gray-500">
                    Last updated: {new Date().toLocaleDateString()}
                  </span>
                </div>
              </div>
              <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
                <Button 
                  onClick={() => setShowResumeUpload(true)}
                  className="bg-white/80 backdrop-blur-sm border border-white/50 text-gray-700 hover:bg-white/90 transition-all duration-300 shadow-lg hover:shadow-xl"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Upload Resume
                </Button>
                <Button 
                  onClick={() => setShowLinkedInModal(true)}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white border-none shadow-lg hover:shadow-xl transition-all duration-300"
                >
                  <Settings className="h-4 w-4 mr-2" />
                  Configure Agent
                </Button>
                <Button 
                  onClick={handleManualRefresh}
                  disabled={isRefreshing}
                  variant="outline"
                  className="bg-white/80 backdrop-blur-sm border border-blue-200 text-blue-700 hover:bg-blue-50 transition-all duration-300 shadow-lg hover:shadow-xl"
                >
                  <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
                  {isRefreshing ? 'Refreshing...' : 'Refresh Data'}
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Enhanced Bot Status Dashboard */}
        <div className="transform transition-all duration-200 hover:scale-[1.01]">
          <EnhancedBotStatusDashboard 
            onStartAgent={handleStartAgent}
            onStopAgent={handleStopAgent}
            hasLinkedInCredentials={hasLinkedInCredentials}
            botStatus={agentStatus}
            isRunning={agentRunning}
            realTimeEnabled={true}
            isStartingBot={isStartingBot}
            isStoppingBot={isStoppingBot}
            actionMessage={botActionMessage}
            userPlan={userPlan}
            timeUntilReset={timeUntilReset}
          />
        </div>

        {/* Live Activity Log */}
        <div className="transform transition-all duration-200 hover:scale-[1.01]">
          <LiveActivityLog 
            isRunning={agentRunning}
            autoScroll={false}
            maxHeight="500px"
            className="mt-6"
          />
        </div>

        {/* Quota Status Card */}
        {userPlan && (
          <Card className={`overflow-hidden border-0 shadow-lg transform transition-all duration-200 hover:scale-[1.02] hover:shadow-xl ${
            userPlan.dailyUsage >= userPlan.dailyQuota 
              ? 'bg-gradient-to-br from-red-50 to-orange-50 border-red-200' 
              : 'bg-gradient-to-br from-white to-blue-50/50'
          }`}>
            <CardHeader className="pb-3">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
                <div>
                  <CardTitle className="flex items-center justify-between text-lg">
                    <div className="flex items-center gap-2">
                    <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg shadow-md">
                      <Target className="h-5 w-5 text-white" />
                    </div>
                    Daily Quota Status
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleManualRefresh}
                      disabled={isRefreshing}
                      className="h-8 w-8 p-0 hover:bg-blue-50"
                    >
                      <RefreshCw className={`h-4 w-4 text-blue-600 ${isRefreshing ? 'animate-spin' : ''}`} />
                    </Button>
                  </CardTitle>
                  <CardDescription className="text-base mt-1">
                    {userPlan.dailyUsage}/{userPlan.dailyQuota} applications used today
                    {userPlan.dailyUsage >= userPlan.dailyQuota && (
                      <span className="block text-red-600 font-semibold mt-1">
                        🚫 Quota reached! Auto-restart at midnight
                      </span>
                    )}
                  </CardDescription>
                </div>
                <div className="text-center md:text-right bg-white/60 rounded-xl p-4 border border-blue-100">
                  <div className="text-sm text-muted-foreground">Current Plan</div>
                  <div className="font-bold text-lg capitalize bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    {userPlan.plan}
                  </div>
                  {userPlan.plan === 'free' && (
                    <Button variant="outline" size="sm" asChild className="mt-2 bg-gradient-to-r from-orange-500 to-red-500 text-white border-0 hover:from-orange-600 hover:to-red-600">
                      <Link href="/pricing">✨ Upgrade Plan</Link>
                    </Button>
                  )}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <div className="flex justify-between text-sm mb-3">
                    <span className="font-medium">Applications Used Today</span>
                    <span className="font-bold text-blue-600">{userPlan.dailyUsage}/{userPlan.dailyQuota}</span>
                  </div>
                  <div className="relative">
                    <Progress 
                      value={(userPlan.dailyUsage / userPlan.dailyQuota) * 100} 
                      className={`h-3 ${
                        userPlan.dailyUsage >= userPlan.dailyQuota 
                          ? 'bg-red-50' 
                          : 'bg-blue-50'
                      }`}
                    />
                    <div className={`absolute inset-0 rounded-full opacity-80 ${
                      userPlan.dailyUsage >= userPlan.dailyQuota
                        ? 'bg-gradient-to-r from-red-500 to-orange-500'
                        : 'bg-gradient-to-r from-blue-500 to-purple-500'
                    }`} 
                         style={{width: `${(userPlan.dailyUsage / userPlan.dailyQuota) * 100}%`}}>
                    </div>
                  </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-white/80 rounded-xl border border-blue-100">
                    <p className="text-sm text-muted-foreground mb-1">Remaining Today</p>
                    {userPlan.dailyUsage >= userPlan.dailyQuota ? (
                      <div>
                        <p className="text-2xl font-bold text-red-600">0</p>
                        <p className="text-xs text-red-500">Quota reached</p>
                      </div>
                    ) : (
                    <p className="text-2xl font-bold text-green-600">{userPlan.dailyQuota - userPlan.dailyUsage}</p>
                    )}
                  </div>
                  <div className="text-center p-4 bg-white/80 rounded-xl border border-blue-100">
                    <p className="text-sm text-muted-foreground mb-1">Quota Resets</p>
                    {userPlan.dailyUsage >= userPlan.dailyQuota ? (
                      <div>
                        <p className="text-lg font-bold text-red-600">In {timeUntilReset}</p>
                        <p className="text-xs text-muted-foreground">Auto-restart</p>
                      </div>
                    ) : (
                    <p className="text-lg font-bold text-purple-600">Midnight</p>
                    )}
                  </div>
                  <div className="text-center p-4 bg-white/80 rounded-xl border border-blue-100">
                    <p className="text-sm text-muted-foreground mb-1">Plan Status</p>
                    {userPlan.dailyUsage >= userPlan.dailyQuota ? (
                      <div>
                        <p className="text-lg font-bold text-orange-600">⏸️ Paused</p>
                        <p className="text-xs text-muted-foreground">Until reset</p>
                      </div>
                    ) : (
                    <p className="text-lg font-bold text-green-600">✅ Active</p>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* LinkedIn Credentials Warning */}
        {!hasLinkedInCredentials && (
          <Card className="border-amber-200 bg-gradient-to-r from-amber-50 to-orange-50 shadow-lg transform transition-all duration-200 hover:scale-[1.01] hover:shadow-xl">
            <CardContent className="flex flex-col md:flex-row md:items-center md:justify-between p-6 space-y-4 md:space-y-0">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-gradient-to-br from-amber-500 to-orange-500 rounded-full shadow-md">
                  <AlertCircle className="h-6 w-6 text-white" />
                </div>
                <div>
                  <p className="font-semibold text-amber-800 text-lg">LinkedIn Credentials Required</p>
                  <p className="text-amber-700">Add your LinkedIn credentials to start applying to jobs automatically.</p>
                </div>
              </div>
              <Button 
                onClick={() => setShowLinkedInModal(true)} 
                className="bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 shadow-lg hover:shadow-xl transition-all text-white border-0 w-full md:w-auto"
              >
                🔗 Add LinkedIn Credentials
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Stats Grid - Only show if user has application data */}
        {hasApplicationData && stats ? (
          <div className="grid gap-4 sm:gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
            <Card className="overflow-hidden border-0 shadow-lg bg-gradient-to-br from-white to-blue-50/30 transform transition-all duration-200 hover:scale-105 hover:shadow-xl">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Total Applications</CardTitle>
                <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg shadow-md">
                  <FileText className="h-4 w-4 text-white" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  {stats.totalApplications}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  📈 +{stats.applicationsThisWeek} from last week
                </p>
              </CardContent>
            </Card>

            <Card className="overflow-hidden border-0 shadow-lg bg-gradient-to-br from-white to-green-50/30 transform transition-all duration-200 hover:scale-105 hover:shadow-xl">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">This Month</CardTitle>
                <div className="p-2 bg-gradient-to-br from-green-500 to-emerald-500 rounded-lg shadow-md">
                  <Calendar className="h-4 w-4 text-white" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                  {stats.applicationsThisMonth}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  🚀 Applications submitted
                </p>
              </CardContent>
            </Card>

            <Card className="overflow-hidden border-0 shadow-lg bg-gradient-to-br from-white to-purple-50/30 transform transition-all duration-200 hover:scale-105 hover:shadow-xl">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Success Rate</CardTitle>
                <div className="p-2 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg shadow-md">
                  <TrendingUp className="h-4 w-4 text-white" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                  {stats.successRate}%
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  🎯 Response rate
                </p>
              </CardContent>
            </Card>

            <Card className="overflow-hidden border-0 shadow-lg bg-gradient-to-br from-white to-orange-50/30 transform transition-all duration-200 hover:scale-105 hover:shadow-xl">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">Avg Response Time</CardTitle>
                <div className="p-2 bg-gradient-to-br from-orange-500 to-red-500 rounded-lg shadow-md">
                  <Target className="h-4 w-4 text-white" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                  {stats.averageResponseTime}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  ⏱️ days average
                </p>
              </CardContent>
            </Card>
          </div>
        ) : (
          // Enhanced empty state for stats
          <Card className="border-0 shadow-xl bg-gradient-to-br from-white via-blue-50/30 to-purple-50/30 overflow-hidden">
            <CardContent className="flex flex-col items-center justify-center py-16">
              <div className="relative mb-6">
                <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center shadow-2xl">
                  <Sparkles className="h-12 w-12 text-white" />
                </div>
                <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center shadow-lg animate-bounce">
                  <span className="text-white text-lg">✨</span>
                </div>
              </div>
              <h3 className="text-2xl font-bold mb-3 bg-gradient-to-r from-gray-900 to-blue-700 bg-clip-text text-transparent">
                Ready to Start Your Job Search Journey?
              </h3>
              <p className="text-gray-600 text-center mb-6 max-w-md text-lg leading-relaxed">
                🚀 Launch your AI agent to begin applying to jobs automatically and watch your stats grow here
              </p>
              <Button 
                onClick={handleStartAgent} 
                disabled={!userPlan || userPlan.dailyUsage >= userPlan.dailyQuota}
                className={`shadow-xl hover:shadow-2xl transition-all text-lg px-8 py-3 h-auto ${
                  userPlan && userPlan.dailyUsage >= userPlan.dailyQuota
                    ? 'bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600 cursor-not-allowed'
                    : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700'
                }`}
              >
                <Play className="h-5 w-5 mr-2" />
                {userPlan && userPlan.dailyUsage >= userPlan.dailyQuota 
                  ? '🚫 Quota Reached - Wait for Reset' 
                  : '🎯 Start Applying to Jobs'
                }
              </Button>
              {!hasLinkedInCredentials && (
                <p className="text-sm text-muted-foreground mt-3 bg-white/60 px-3 py-1 rounded-full">
                  💡 LinkedIn credentials will be requested when you start
                </p>
              )}
              {userPlan && userPlan.dailyUsage >= userPlan.dailyQuota && (
                <div className="mt-3 p-3 bg-gradient-to-r from-red-50 to-orange-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-700 font-medium text-center">
                    ⏰ Auto-restart in {timeUntilReset} • Quota resets at midnight
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
          {/* Recent Applications */}
          <Card className="col-span-4 border-0 shadow-lg bg-gradient-to-br from-white to-gray-50/50 transform transition-all duration-200 hover:shadow-xl">
            <CardHeader className="pb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg shadow-md">
                  <FileText className="h-5 w-5 text-white" />
                </div>
                <div>
                  <CardTitle className="text-xl">Recent Applications</CardTitle>
                  <CardDescription className="text-base">
                    🤖 Your latest job applications powered by AI
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {recentApplications.length > 0 ? (
                <div className="space-y-4">
                  {recentApplications.map((app) => (
                    <div key={app.id} className="flex items-center space-x-4 p-4 bg-white rounded-xl border border-gray-100 hover:border-blue-200 hover:shadow-md transition-all">
                      <div className="flex-1 space-y-1">
                        <p className="text-sm font-semibold leading-none text-gray-900">{app.jobTitle}</p>
                        <p className="text-sm text-gray-600">{app.company} • {app.location}</p>
                      </div>
                      <div className="flex items-center space-x-3">
                        {app.aiGenerated && (
                          <div className="p-1.5 bg-gradient-to-br from-blue-500 to-purple-500 rounded-md shadow-sm">
                            <Bot className="h-3 w-3 text-white" />
                          </div>
                        )}
                        <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(app.status)} bg-gray-50`}>
                          {getStatusIcon(app.status)}
                          <span className="capitalize">{app.status}</span>
                        </div>
                      </div>
                      <div className="text-xs text-gray-500 bg-gray-50 px-2 py-1 rounded-md">
                        {new Date(app.appliedAt).toLocaleDateString()} at {new Date(app.appliedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-12">
                  <div className="w-16 h-16 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center mb-4 shadow-inner">
                    <Coffee className="h-8 w-8 text-gray-400" />
                  </div>
                  <p className="text-gray-500 text-center text-lg">
                    ☕ No applications yet. Start your AI agent to begin applying!
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Top Companies */}
          <Card className="col-span-3 border-0 shadow-lg bg-gradient-to-br from-white to-indigo-50/50 transform transition-all duration-200 hover:shadow-xl">
            <CardHeader className="pb-4">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-lg shadow-md">
                  <Users className="h-5 w-5 text-white" />
                </div>
                <div>
                  <CardTitle className="text-xl">Top Companies</CardTitle>
                  <CardDescription className="text-base">
                    🏢 Companies you've applied to most
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {stats && stats.topCompanies && stats.topCompanies.length > 0 ? (
                stats.topCompanies.map((company, index) => (
                  <div key={company.company} className="flex items-center p-3 bg-white rounded-lg border border-gray-100 hover:border-indigo-200 hover:shadow-sm transition-all">
                    <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-lg flex items-center justify-center text-white font-bold text-sm mr-3 shadow-md">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <p className="font-semibold text-gray-900">{company.company}</p>
                    </div>
                    <div className="text-sm font-medium text-indigo-600 bg-indigo-50 px-2 py-1 rounded-full">
                      {company.count} apps
                    </div>
                  </div>
                ))
              ) : (
                <div className="flex flex-col items-center justify-center py-8">
                  <div className="w-16 h-16 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center mb-4 shadow-inner">
                    <Users className="h-8 w-8 text-gray-400" />
                  </div>
                  <p className="text-gray-500 text-center">
                    📊 Company insights will appear after you start applying
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Enhanced Quick Actions */}
        <Card className="border-0 shadow-lg bg-gradient-to-br from-white via-gray-50/30 to-blue-50/30 transform transition-all duration-200 hover:shadow-xl">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-green-500 to-emerald-500 rounded-lg shadow-md">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <div>
                <CardTitle className="text-xl">⚡ Quick Actions</CardTitle>
                <CardDescription className="text-base">
                  Common tasks and configurations to get you started
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-4">
              <Button 
                className="h-24 flex-col bg-gradient-to-br from-blue-50 to-blue-100 hover:from-blue-100 hover:to-blue-200 border-blue-200 text-blue-700 hover:text-blue-800 shadow-lg hover:shadow-xl transform transition-all hover:scale-105" 
                variant="outline" 
                onClick={() => setShowResumeUpload(true)}
              >
                <Upload className="h-6 w-6 mb-2" />
                📄 Upload New Resume
              </Button>

              <Button 
                className="h-24 flex-col bg-gradient-to-br from-green-50 to-green-100 hover:from-green-100 hover:to-green-200 border-green-200 text-green-700 hover:text-green-800 shadow-lg hover:shadow-xl transform transition-all hover:scale-105" 
                variant="outline" 
                onClick={() => setShowLinkedInModal(true)}
              >
                <Shield className="h-6 w-6 mb-2" />
                🔗 {hasLinkedInCredentials ? 'Update' : 'Add'} LinkedIn
              </Button>

              <Button 
                className="h-24 flex-col bg-gradient-to-br from-purple-50 to-purple-100 hover:from-purple-100 hover:to-purple-200 border-purple-200 text-purple-700 hover:text-purple-800 shadow-lg hover:shadow-xl transform transition-all hover:scale-105" 
                variant="outline" 
                onClick={loadDashboardData}
              >
                <RefreshCw className="h-6 w-6 mb-2" />
                🔄 Refresh Data
              </Button>

              <Button 
                className="h-24 flex-col bg-gradient-to-br from-red-50 to-red-100 hover:from-red-100 hover:to-red-200 border-red-200 text-red-700 hover:text-red-800 shadow-lg hover:shadow-xl transform transition-all hover:scale-105" 
                variant="outline" 
                onClick={handleResetAccount}
                disabled={isResettingAccount}
              >
                <Trash2 className="h-6 w-6 mb-2" />
                🗑️ {isResettingAccount ? 'Resetting...' : 'Reset Account'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Resume Upload Modal */}
      <ResumeUploadModal 
        isOpen={showResumeUpload}
        onOpenChange={setShowResumeUpload}
        onUploadSuccess={(filename) => {
          console.log('Resume uploaded:', filename)
          // Optionally refresh data or show notification
          loadDashboardData()
        }}
      />

      {/* LinkedIn Credentials Modal */}
        {/* LinkedIn Credentials Modal */}
        <LinkedInCredentialsModal
          isOpen={showLinkedInModal}
          onOpenChange={setShowLinkedInModal}
          onCredentialsSaved={handleLinkedInCredentialsSaved}
        />
      </div>

      {/* Footer (dashboard only) */}
      <div className="mt-8">
        <DashboardFooter />
      </div>
    </div>
  )
}
