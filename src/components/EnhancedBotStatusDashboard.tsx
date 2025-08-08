'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import {
  Bot,
  Play,
  Pause,
  RefreshCw,
  CheckCircle,
  Clock,
  AlertCircle,
  Zap,
  Target,
  FileText,
  Users,
  Search,
  Send,
  Coffee,
  Eye
} from 'lucide-react'
import { useAuth } from './AuthProvider'
import { getApiUrl } from '@/lib/utils'

interface BotStatus {
  status: 'running' | 'stopped' | 'error' | 'paused'
  currentTask: string
  progress: number
  tasksCompleted: number
  applicationsSubmitted: number
  lastRun: string | null
  sessionStartTime?: string
  estimatedTimeRemaining?: number
  currentJobTitle?: string
  currentCompany?: string
  persistent_session?: {
    survives_refresh: boolean
    session_id?: string
    duration_seconds: number
    restart_count: number
  }
  detailedSteps?: {
    step: string
    status: 'completed' | 'current' | 'pending'
    timestamp?: string
  }[]
}

interface UserPlan {
  plan: string
  dailyQuota: number
  dailyUsage: number
  subscriptionStatus: string
}

interface EnhancedBotStatusProps {
  className?: string
  onStartAgent?: () => void  // Callback to handle agent start with LinkedIn credential check
  onStopAgent?: () => void   // Callback to handle agent stop
  hasLinkedInCredentials?: boolean
  botStatus?: BotStatus | null  // Real-time bot status from parent
  isRunning?: boolean       // Real-time running state from parent
  realTimeEnabled?: boolean // Whether real-time updates are enabled
  isStartingBot?: boolean   // Loading state when starting bot
  isStoppingBot?: boolean   // Loading state when stopping bot
  actionMessage?: string    // Current action message
  userPlan?: UserPlan | null // User's quota information
  timeUntilReset?: string   // Countdown timer for quota reset
}

export function EnhancedBotStatusDashboard({
  className,
  onStartAgent,
  onStopAgent,
  hasLinkedInCredentials,
  botStatus: propBotStatus,
  isRunning: propIsRunning,
  realTimeEnabled,
  isStartingBot = false,
  isStoppingBot = false,
  actionMessage,
  userPlan,
  timeUntilReset
}: EnhancedBotStatusProps) {
  const { token } = useAuth()
  const [localBotStatus, setLocalBotStatus] = useState<BotStatus | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [clearingStatus, setClearingStatus] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<string>('')

  // Use props if available (real-time), otherwise use local state with polling
  const botStatus = propBotStatus || localBotStatus
  const isRunning = propIsRunning ?? (botStatus?.status === 'running')

  // Determine if any loading action is happening
  const isAnyLoading = isStartingBot || isStoppingBot || isLoading

  // Update last updated timestamp when bot status changes
  useEffect(() => {
    if (botStatus) {
      setLastUpdated(new Date().toLocaleTimeString())
    }
  }, [botStatus])

  // Fallback polling for when real-time is not enabled
  useEffect(() => {
    if (!token || realTimeEnabled) return

    fetchBotStatus()

    const interval = setInterval(() => {
      if (botStatus?.status === 'running') {
        fetchBotStatus()
      }
    }, 60000)

    return () => clearInterval(interval)
  }, [token, botStatus?.status, realTimeEnabled])

  const fetchBotStatus = async () => {
    try {
      const response = await fetch(getApiUrl('/api/bot/status'), {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        const data = await response.json()
        setLocalBotStatus(data)
      } else {
        // Default status if endpoint doesn't exist
        setLocalBotStatus({
          status: 'stopped',
          currentTask: 'Ready to start job search',
          progress: 0,
          tasksCompleted: 0,
          applicationsSubmitted: 0,
          lastRun: null
        })
      }
    } catch (err) {
      console.error('Error fetching bot status:', err)
      setLocalBotStatus({
        status: 'stopped',
        currentTask: 'Ready to start job search',
        progress: 0,
        tasksCompleted: 0,
        applicationsSubmitted: 0,
        lastRun: null
      })
    }
  }

  const toggleBot = async () => {
    if (!botStatus) return

    // If trying to start the agent, use the parent's start handler (which includes LinkedIn credential check)
    if (botStatus.status === 'stopped' && onStartAgent) {
      onStartAgent()
      return
    }

    // For stopping the agent, use parent's stop handler if available
    if (onStopAgent) {
      onStopAgent()
      return
    }

    // Fallback: handle stopping directly if no parent handler
    setIsLoading(true)
    setError('')

    try {
      const response = await fetch(getApiUrl('/api/bot/stop'), {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        // Update local status since parent doesn't handle it
        setLocalBotStatus(prev => prev ? {
          ...prev,
          status: 'stopped',
          currentTask: 'Stopped by user'
        } : null)
      } else {
        const errorData = await response.json()
        setError(errorData.error || 'Failed to stop bot')
      }
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const clearBotStatus = async () => {
    setClearingStatus(true)
    setError('')

    try {
      const response = await fetch(getApiUrl('/api/bot/clear-status'), {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to clear status')
      }

      const result = await response.json()
      console.log('Clear status result:', result)

      // Immediately fetch updated status
      fetchBotStatus()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to clear status')
    } finally {
      setClearingStatus(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'bg-green-500'
      case 'stopped': return 'bg-gray-500'
      case 'error': return 'bg-red-500'
      case 'paused': return 'bg-yellow-500'
      default: return 'bg-gray-500'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <Zap className="h-4 w-4 text-green-600" />
      case 'stopped': return <Pause className="h-4 w-4 text-gray-600" />
      case 'error': return <AlertCircle className="h-4 w-4 text-red-600" />
      case 'paused': return <Clock className="h-4 w-4 text-yellow-600" />
      default: return <Bot className="h-4 w-4 text-gray-600" />
    }
  }

  const getStepIcon = (step: string) => {
    if (step.toLowerCase().includes('search')) return <Search className="h-4 w-4" />
    if (step.toLowerCase().includes('apply')) return <Send className="h-4 w-4" />
    if (step.toLowerCase().includes('resume')) return <FileText className="h-4 w-4" />
    if (step.toLowerCase().includes('profile')) return <Users className="h-4 w-4" />
    if (step.toLowerCase().includes('review')) return <Eye className="h-4 w-4" />
    return <CheckCircle className="h-4 w-4" />
  }

  const formatTimeRemaining = (seconds: number): string => {
    if (seconds < 60) return `${seconds}s`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`
  }

  if (!botStatus) {
    return (
      <Card className={className}>
        <CardContent className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${getStatusColor(botStatus.status)} animate-pulse`}></div>
            <div>
              <CardTitle className="flex items-center gap-2">
                {getStatusIcon(botStatus.status)}
                AI Agent Status
                {realTimeEnabled && isRunning && (
                  <div className="flex items-center gap-1 text-xs text-green-600 font-normal" title="Real-time updates every 2 seconds">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    LIVE
                  </div>
                )}
                {botStatus?.persistent_session?.survives_refresh && (
                  <div className="flex items-center gap-1 text-xs text-blue-600 font-normal" title="Session persists across page refreshes">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    PERSISTENT
                  </div>
                )}
              </CardTitle>
              <CardDescription className="flex items-center gap-2">
                {botStatus.currentTask}
                {lastUpdated && (
                  <span className="text-xs text-muted-foreground">
                    • Updated {lastUpdated}
                  </span>
                )}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant={botStatus.status === 'running' ? 'default' : 'secondary'}>
              {botStatus.status.toUpperCase()}
            </Badge>
            <Button
              onClick={toggleBot}
              variant={botStatus.status === 'running' ? "destructive" : "default"}
              size="sm"
              disabled={isAnyLoading || (botStatus.status === 'stopped' && !hasLinkedInCredentials) || (!!userPlan && userPlan.dailyUsage >= userPlan.dailyQuota)}
            >
              {isAnyLoading ? (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              ) : botStatus.status === 'running' ? (
                <Pause className="h-4 w-4 mr-2" />
              ) : (
                <Play className="h-4 w-4 mr-2" />
              )}
              {isStartingBot ? 'Starting Bot...' :
                isStoppingBot ? 'Stopping Bot...' :
                  isLoading ? 'Loading...' :
                    botStatus.status === 'running' ? 'Stop Agent' :
                      !hasLinkedInCredentials ? 'Add LinkedIn Credentials' :
                        !!userPlan && userPlan.dailyUsage >= userPlan.dailyQuota ? 'Quota Reached' : 'Start Agent'}
            </Button>

            {/* Debug button - only show if there's potential status confusion */}
            {(botStatus.status === 'stopped' && process.env.NODE_ENV === 'development') && (
              <Button
                onClick={clearBotStatus}
                variant="ghost"
                size="sm"
                disabled={clearingStatus}
                className="text-xs opacity-50 hover:opacity-100"
              >
                {clearingStatus ? (
                  <RefreshCw className="h-3 w-3 animate-spin" />
                ) : (
                  'Clear Status'
                )}
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md">
            <AlertCircle className="h-4 w-4 text-red-500" />
            <span className="text-sm text-red-600">{error}</span>
          </div>
        )}

        {!hasLinkedInCredentials && (
          <div className="flex items-center gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
            <AlertCircle className="h-4 w-4 text-yellow-500" />
            <span className="text-sm text-yellow-700">LinkedIn credentials required to start agent</span>
          </div>
        )}

        {actionMessage && (
          <div className="flex items-center gap-2 p-3 bg-blue-50 border border-blue-200 rounded-md">
            <Bot className="h-4 w-4 text-blue-500" />
            <span className="text-sm text-blue-700">{actionMessage}</span>
          </div>
        )}

        {/* Quota Exceeded Message */}
        {userPlan && userPlan.dailyUsage >= userPlan.dailyQuota && !isRunning && (
          <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md">
            <AlertCircle className="h-4 w-4 text-red-500" />
            <div className="flex-1">
              <span className="text-sm text-red-700 font-medium">
                🚫 Daily quota reached ({userPlan.dailyUsage}/{userPlan.dailyQuota})
              </span>
              {timeUntilReset && (
                <p className="text-xs text-red-600 mt-1">
                  Auto-restart in {timeUntilReset} • Quota resets at midnight
                </p>
              )}
            </div>
          </div>
        )}

        {/* Current Progress */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Overall Progress</span>
            <span>{botStatus.progress}%</span>
          </div>
          <Progress value={botStatus.progress} className="w-full" />
          {botStatus.estimatedTimeRemaining && botStatus.status === 'running' && (
            <p className="text-xs text-muted-foreground">
              Estimated time remaining: {formatTimeRemaining(botStatus.estimatedTimeRemaining)}
            </p>
          )}
        </div>

        {/* Persistent Session Info */}
        {botStatus.persistent_session && (
          <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
            <h4 className="font-medium text-blue-900 mb-2 flex items-center gap-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              Persistent Session Active
            </h4>
            <div className="space-y-1 text-sm text-blue-700">
              <p><span className="font-medium">Session ID:</span> {botStatus.persistent_session.session_id?.slice(-8)}</p>
              <p><span className="font-medium">Survives refresh:</span> ✅ Yes</p>
              <p><span className="font-medium">Running time:</span> {Math.floor(botStatus.persistent_session.duration_seconds / 60)}m</p>
              {botStatus.persistent_session.restart_count > 0 && (
                <p><span className="font-medium">Auto-restarts:</span> {botStatus.persistent_session.restart_count}</p>
              )}
              <p className="text-xs text-blue-600 mt-2">
                💡 Your bot will continue running even if you refresh the page or close this tab
              </p>
            </div>
          </div>
        )}

        {/* Current Job Details */}
        {botStatus.status === 'running' && (botStatus.currentJobTitle || botStatus.currentCompany) && (
          <div className="bg-green-50 border border-green-200 rounded-md p-4">
            <h4 className="font-medium text-green-900 mb-2">Currently Processing</h4>
            <div className="space-y-1 text-sm text-green-700">
              {botStatus.currentJobTitle && (
                <p><span className="font-medium">Position:</span> {botStatus.currentJobTitle}</p>
              )}
              {botStatus.currentCompany && (
                <p><span className="font-medium">Company:</span> {botStatus.currentCompany}</p>
              )}
            </div>
          </div>
        )}

        {/* Detailed Steps */}
        {botStatus.detailedSteps && botStatus.detailedSteps.length > 0 && (
          <div className="space-y-3">
            <h4 className="font-medium text-sm">Current Process</h4>
            <div className="space-y-2">
              {botStatus.detailedSteps.map((step, index) => (
                <div
                  key={index}
                  className={`flex items-center gap-3 p-3 rounded-md ${step.status === 'completed' ? 'bg-green-50 border border-green-200' :
                      step.status === 'current' ? 'bg-blue-50 border border-blue-200' :
                        'bg-gray-50 border border-gray-200'
                    }`}
                >
                  <div className={`flex-shrink-0 ${step.status === 'completed' ? 'text-green-600' :
                      step.status === 'current' ? 'text-blue-600' :
                        'text-gray-400'
                    }`}>
                    {step.status === 'completed' ? (
                      <CheckCircle className="h-4 w-4" />
                    ) : step.status === 'current' ? (
                      <div className="animate-spin">
                        <RefreshCw className="h-4 w-4" />
                      </div>
                    ) : (
                      getStepIcon(step.step)
                    )}
                  </div>
                  <div className="flex-1">
                    <p className={`text-sm ${step.status === 'completed' ? 'text-green-700' :
                        step.status === 'current' ? 'text-blue-700' :
                          'text-gray-600'
                      }`}>
                      {step.step}
                    </p>
                    {step.timestamp && (
                      <p className="text-xs text-muted-foreground">
                        {new Date(step.timestamp).toLocaleTimeString()}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Statistics */}
        <div className="grid grid-cols-3 gap-4 text-center">
          <div className="space-y-1">
            <p className="text-2xl font-bold text-green-600">{botStatus.tasksCompleted}</p>
            <p className="text-xs text-muted-foreground">Tasks Completed</p>
          </div>
          <div className="space-y-1">
            <p className="text-2xl font-bold text-blue-600">{botStatus.applicationsSubmitted}</p>
            <p className="text-xs text-muted-foreground">Applications Sent</p>
          </div>
          <div className="space-y-1">
            <p className="text-2xl font-bold text-purple-600">
              {botStatus.sessionStartTime ?
                Math.floor((Date.now() - new Date(botStatus.sessionStartTime).getTime()) / (1000 * 60)) :
                0
              }m
            </p>
            <p className="text-xs text-muted-foreground">Runtime</p>
          </div>
        </div>

        {/* Last Run Info */}
        {botStatus.lastRun && (
          <div className="text-center text-sm text-muted-foreground">
            Last run: {new Date(botStatus.lastRun).toLocaleString()}
          </div>
        )}

        {/* Idle State */}
        {botStatus.status === 'stopped' && (
          <div className="text-center py-4">
            <Coffee className="h-8 w-8 mx-auto mb-2 text-gray-400" />
            <p className="text-sm text-muted-foreground">
              Agent is idle. Click "Start Agent" to begin applying to jobs.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
} 