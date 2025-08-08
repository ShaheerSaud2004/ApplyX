'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Activity, 
  RefreshCw, 
  Pause, 
  Play,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle,
  Info,
  Download,
  Eye,
  EyeOff
} from 'lucide-react'
import { useAuth } from './AuthProvider'
import { getApiUrl } from '@/lib/utils'

interface ActivityLog {
  id: number
  action: string
  details: string
  status: 'info' | 'success' | 'error' | 'warning'
  timestamp: string
  metadata?: any
}

interface LiveActivityLogProps {
  className?: string
  isRunning?: boolean
  autoScroll?: boolean
  maxHeight?: string
  onReset?: () => void
}

export const LiveActivityLog = React.forwardRef<{ reset: () => void }, LiveActivityLogProps>(({ 
  className, 
  isRunning = false, 
  autoScroll = true,
  maxHeight = "400px",
  onReset
}, ref) => {
  const { token } = useAuth()
  const [activities, setActivities] = useState<ActivityLog[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [isPaused, setIsPaused] = useState(false)
  const [isCollapsed, setIsCollapsed] = useState(false)
  const logEndRef = useRef<HTMLDivElement>(null)
  const scrollContainerRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new activities arrive (disabled to prevent dashboard scrolling)
  useEffect(() => {
    // Disabled auto-scroll to prevent unwanted dashboard scrolling behavior
    // if (autoScroll && !isPaused && logEndRef.current) {
    //   logEndRef.current.scrollIntoView({ behavior: 'smooth' })
    // }
  }, [activities, autoScroll, isPaused])

  // Fetch activity logs
  const fetchActivityLogs = async () => {
    if (!token || isPaused) return

    try {
      setIsLoading(true)
      const response = await fetch(getApiUrl('/api/bot/activity/log?limit=100'), {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        const data = await response.json()
        if (data.success && data.activities) {
          // Sort by timestamp descending for display (newest first in API, but we want newest last for chat-like experience)
          const sortedActivities = data.activities.reverse()
          setActivities(sortedActivities)
        }
        setError('')
      } else {
        console.warn('Failed to fetch activity logs')
      }
    } catch (err) {
      console.warn('Error fetching activity logs:', err)
    } finally {
      setIsLoading(false)
    }
  }

  // Real-time polling - continuous updates
  useEffect(() => {
    if (!token) return

    // Initial fetch
    fetchActivityLogs()

    let interval: NodeJS.Timeout | null = null

    if (!isPaused) {
      if (isRunning) {
        // Poll every 10 seconds when bot is running (reduced for better performance)
        interval = setInterval(fetchActivityLogs, 10000)
      } else {
        // Poll every 60 seconds when bot is stopped
        interval = setInterval(fetchActivityLogs, 60000)
      }
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [token, isRunning, isPaused])

  // Format timestamp for display
  const formatTime = (timestamp: string) => {
    try {
      const date = new Date(timestamp)
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    } catch {
      return timestamp
    }
  }

  // Get status icon and color
  const getStatusInfo = (status: string) => {
    switch (status) {
      case 'success':
        return { icon: CheckCircle, color: 'text-green-600', bgColor: 'bg-green-50', badge: 'default' }
      case 'error':
        return { icon: XCircle, color: 'text-red-600', bgColor: 'bg-red-50', badge: 'destructive' }
      case 'warning':
        return { icon: AlertCircle, color: 'text-yellow-600', bgColor: 'bg-yellow-50', badge: 'secondary' }
      default:
        return { icon: Info, color: 'text-blue-600', bgColor: 'bg-blue-50', badge: 'outline' }
    }
  }

  // Clear logs
  const clearLogs = async () => {
    try {
      // Clear logs from backend database
      const response = await fetch(getApiUrl('/api/activity/clear'), {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const result = await response.json()
        console.log(`✅ Cleared ${result.deleted_count} activity log entries from database`)
        
        // Clear local state after successful backend clear
        setActivities([])
        
        // Show success message if you have a toast system
        // toast.success(`Cleared ${result.deleted_count} log entries`)
      } else {
        console.error('Failed to clear logs from backend:', response.statusText)
        // Still clear local state as fallback
        setActivities([])
      }
    } catch (error) {
      console.error('Error clearing logs:', error)
      // Still clear local state as fallback
      setActivities([])
    }
  }

  // Reset function that can be called externally
  const resetActivityLog = async () => {
    console.log('🔄 Resetting live activity log...')
    setActivities([])
    setError('')
    setIsPaused(false)
    
    // Clear backend logs
    try {
      const response = await fetch(getApiUrl('/api/activity/clear'), {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const result = await response.json()
        console.log(`✅ Reset complete: Cleared ${result.deleted_count} activity log entries`)
      } else {
        console.warn('Failed to clear backend logs during reset')
      }
    } catch (error) {
      console.warn('Error clearing backend logs during reset:', error)
    }
    
    // Call external reset callback if provided
    if (onReset) {
      onReset()
    }
  }

  // Expose reset function to parent component
  React.useImperativeHandle(ref, () => ({
    reset: resetActivityLog
  }))

  // Export logs as text
  const exportLogs = () => {
    const logText = activities.map(activity => 
      `[${formatTime(activity.timestamp)}] ${activity.action}: ${activity.details}`
    ).join('\n')
    
    const blob = new Blob([logText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `bot-activity-log-${new Date().toISOString().split('T')[0]}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  if (isCollapsed) {
    return (
      <Card className={className}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4" />
            <CardTitle className="text-sm font-medium">Live Activity Log</CardTitle>
            {!isPaused && (
              <div className="flex items-center gap-1">
                <div className={`w-2 h-2 rounded-full animate-pulse ${
                  isRunning ? 'bg-green-500' : 'bg-blue-500'
                }`}></div>
                <span className={`text-xs ${
                  isRunning ? 'text-green-600' : 'text-blue-600'
                }`}>
                  {isRunning ? 'LIVE' : 'AUTO'}
                </span>
              </div>
            )}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsCollapsed(false)}
          >
            <Eye className="h-4 w-4" />
          </Button>
        </CardHeader>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4" />
          <CardTitle className="text-sm font-medium">Live Activity Log</CardTitle>
          {!isPaused && (
            <div className="flex items-center gap-1" title={
              isRunning ? "Real-time updates every 2 seconds" : "Auto-updates every 5 seconds"
            }>
              <div className={`w-2 h-2 rounded-full animate-pulse ${
                isRunning ? 'bg-green-500' : 'bg-blue-500'
              }`}></div>
              <span className={`text-xs ${
                isRunning ? 'text-green-600' : 'text-blue-600'
              }`}>
                {isRunning ? 'LIVE' : 'AUTO'}
              </span>
            </div>
          )}
        </div>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsPaused(!isPaused)}
            title={isPaused ? "Resume updates" : "Pause updates"}
          >
            {isPaused ? <Play className="h-4 w-4" /> : <Pause className="h-4 w-4" />}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={fetchActivityLogs}
            disabled={isLoading}
            title="Refresh logs"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={exportLogs}
            disabled={activities.length === 0}
            title="Export logs"
          >
            <Download className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsCollapsed(true)}
            title="Minimize"
          >
            <EyeOff className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <CardDescription className="mb-3">
          {isRunning 
            ? "Real-time activity from your LinkedIn Easy Apply bot (2s updates)" 
            : "Auto-refreshing activity log (5s updates)"
          }
          {activities.length > 0 && (
            <span className="ml-2">• {activities.length} entries</span>
          )}
        </CardDescription>
        
        <div 
          ref={scrollContainerRef}
          className="border rounded-md p-3 bg-gray-50 overflow-y-auto font-mono text-sm"
          style={{ height: maxHeight }}
        >
          {activities.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-500">
              <Activity className="h-8 w-8 mb-2 opacity-50" />
              <p className="text-sm text-center">
                {isRunning 
                  ? 'Waiting for bot activity...' 
                  : 'No recent activity. The log auto-refreshes every 5 seconds.'
                }
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {activities.map((activity) => {
                const statusInfo = getStatusInfo(activity.status)
                const StatusIcon = statusInfo.icon
                
                return (
                  <div 
                    key={activity.id} 
                    className={`flex items-start gap-3 p-2 rounded-md ${statusInfo.bgColor} border-l-2 ${
                      activity.status === 'error' ? 'border-l-red-500' :
                      activity.status === 'success' ? 'border-l-green-500' :
                      activity.status === 'warning' ? 'border-l-yellow-500' :
                      'border-l-blue-500'
                    }`}
                  >
                    <StatusIcon className={`h-4 w-4 mt-0.5 ${statusInfo.color} flex-shrink-0`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-gray-900">{activity.action}</span>
                        <Badge variant={statusInfo.badge as any} className="text-xs">
                          {activity.status}
                        </Badge>
                        <span className="text-xs text-gray-500 ml-auto">
                          {formatTime(activity.timestamp)}
                        </span>
                      </div>
                      <p className="text-gray-700 break-words">{activity.details}</p>
                      {activity.metadata && Object.keys(activity.metadata).length > 0 && (
                        <div className="mt-1 text-xs text-gray-600">
                          {Object.entries(activity.metadata).map(([key, value]) => (
                            <span key={key} className="mr-3">
                              {key}: {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
              <div ref={logEndRef} />
            </div>
          )}
        </div>
        
        {isPaused && (
          <div className="mt-2 flex items-center gap-2 text-sm text-yellow-600">
            <Pause className="h-4 w-4" />
            Updates paused - Click play to resume
          </div>
        )}
        
        {activities.length > 20 && (
          <div className="mt-2 flex justify-between items-center text-xs text-gray-500">
            <span>Showing latest {activities.length} entries</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={clearLogs}
              className="text-xs"
            >
              Clear logs
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
})

LiveActivityLog.displayName = 'LiveActivityLog' 