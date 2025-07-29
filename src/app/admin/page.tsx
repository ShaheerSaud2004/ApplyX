'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/components/AuthProvider'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  Users, 
  UserCheck, 
  UserX, 
  TrendingUp, 
  Calendar,
  Search,
  Filter,
  Edit,
  Trash2,
  Mail,
  Phone,
  ExternalLink,
  CheckCircle,
  XCircle,
  Clock,
  Shield,
  BarChart3,
  Activity,
  Database,
  Download,
  Eye,
  Server,
  AlertTriangle,
  FileText,
  Zap,
  LogOut
} from 'lucide-react'

interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  phone?: string
  linkedin?: string
  website?: string
  subscription_plan: string
  daily_quota: number
  daily_usage: number
  subscription_status?: string
  isAdmin: boolean
  status: 'pending' | 'approved' | 'rejected'
  created_at: string
  stripe_customer_id?: string
  current_period_end?: string
}

interface AdminStats {
  total_users: number
  pending_users: number
  users_by_plan: { plan: string; count: number }[]
  total_applications: number
  applications_this_month: number
  monthly_revenue: number
}

interface Analytics {
  top_companies: { company: string; count: number }[]
  top_job_titles: { title: string; count: number }[]
  applications_by_status: { status: string; count: number }[]
  daily_trends: { date: string; count: number }[]
  user_success_rates: { email: string; name: string; total_applications: number; successful_applications: number; success_rate: number }[]
  most_active_users: { email: string; name: string; applications: number }[]
}

interface SystemHealth {
  database: {
    total_users: number
    total_applications: number
    size_mb: number
  }
  activity: {
    recent_activity_1h: number
    active_users_24h: number
    recent_errors_24h: number
  }
  bots: {
    active_sessions: number
  }
  timestamp: string
}

interface UserApplications {
  user: { email: string; name: string }
  applications: Array<{
    id: string
    job_title: string
    company: string
    location: string
    job_url: string
    status: string
    applied_at: string
    notes: string
  }>
  total_count: number
}

interface Activity {
  action: string
  details: string
  status: string
  timestamp: string
  metadata: string
  user?: { email: string; name: string }
}

export default function AdminDashboard() {
  const { user, token, isAuthenticated, logout } = useAuth()
  const router = useRouter()
  
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'analytics' | 'activity' | 'health'>('overview')
  const [users, setUsers] = useState<User[]>([])
  const [pendingUsers, setPendingUsers] = useState<User[]>([])
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [analytics, setAnalytics] = useState<Analytics | null>(null)
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null)
  const [recentActivity, setRecentActivity] = useState<Activity[]>([])
  const [selectedUser, setSelectedUser] = useState<User | null>(null)
  const [userApplications, setUserApplications] = useState<UserApplications | null>(null)
  const [userActivity, setUserActivity] = useState<Activity[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'approved' | 'rejected'>('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState('')
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [isTriggeringDailyApps, setIsTriggeringDailyApps] = useState(false)

  const fetchAdminData = async () => {
    try {
      const [usersRes, pendingRes, statsRes] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/users`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/users/pending`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/stats`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ])

      if (usersRes.ok) {
        const usersData = await usersRes.json()
        setUsers(usersData)
      }

      if (pendingRes.ok) {
        const pendingData = await pendingRes.json()
        setPendingUsers(pendingData)
      }

      if (statsRes.ok) {
        const statsData = await statsRes.json()
        setStats(statsData)
      }

      setLastUpdated(new Date())
      setLoading(false)
    } catch (err) {
      setError('Failed to load admin data')
      setLoading(false)
    }
  }

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/analytics`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setAnalytics(data)
      }
    } catch (err) {
      console.error('Failed to fetch analytics:', err)
    }
  }

  const fetchSystemHealth = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/system-health`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setSystemHealth(data)
      }
    } catch (err) {
      console.error('Failed to fetch system health:', err)
    }
  }

  const fetchRecentActivity = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/recent-activity?limit=20`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (response.ok) {
        const data = await response.json()
        setRecentActivity(data.activities)
      }
    } catch (err) {
      console.error('Failed to fetch recent activity:', err)
    }
  }

  const fetchUserDetails = async (userId: string) => {
    try {
      const [appsRes, activityRes] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/users/${userId}/applications`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/users/${userId}/activity?limit=20`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ])

      if (appsRes.ok) {
        const appsData = await appsRes.json()
        setUserApplications(appsData)
      }

      if (activityRes.ok) {
        const activityData = await activityRes.json()
        setUserActivity(activityData.activities)
      }
    } catch (err) {
      console.error('Failed to fetch user details:', err)
    }
  }

  const exportUsers = async () => {
    try {
      setActionLoading('export')
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/export/users`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'users_export.csv'
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        setSuccessMessage('Users data exported successfully!')
        setTimeout(() => setSuccessMessage(''), 3000)
      }
    } catch (err) {
      setError('Failed to export users data')
    } finally {
      setActionLoading(null)
    }
  }

  const triggerDailyApplications = async () => {
    setIsTriggeringDailyApps(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/trigger-daily-applications`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      const data = await response.json()

      if (response.ok) {
        setSuccessMessage(`✅ ${data.message}`)
        setTimeout(() => setSuccessMessage(''), 5000)
      } else {
        setError(data.message || 'Failed to trigger daily applications')
      }
    } catch (error) {
      console.error('Error triggering daily applications:', error)
      setError('Failed to trigger daily applications')
    } finally {
      setIsTriggeringDailyApps(false)
    }
  }

  useEffect(() => {
    if (!isAuthenticated || !user?.isAdmin) {
      router.push('/dashboard')
      return
    }
    
    fetchAdminData()
    
    // Auto-refresh every 30 seconds to keep data current
    const refreshInterval = setInterval(() => {
      fetchAdminData()
      if (activeTab === 'analytics') fetchAnalytics()
      if (activeTab === 'health') fetchSystemHealth()
      if (activeTab === 'activity') fetchRecentActivity()
    }, 30000)
    
    return () => clearInterval(refreshInterval)
  }, [isAuthenticated, user, router, activeTab])

  useEffect(() => {
    // Fetch data when tab changes
    if (activeTab === 'analytics' && !analytics) {
      fetchAnalytics()
    }
    if (activeTab === 'health' && !systemHealth) {
      fetchSystemHealth()
    }
    if (activeTab === 'activity' && recentActivity.length === 0) {
      fetchRecentActivity()
    }
  }, [activeTab])

  const manualRefresh = () => {
    setLoading(true)
    fetchAdminData()
  }

  const approveUser = async (userId: string) => {
    setActionLoading(`approve-${userId}`)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/users/${userId}/approve`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        setSuccessMessage('User approved successfully!')
        setTimeout(() => setSuccessMessage(''), 3000)
        setError('') // Clear any previous errors
        fetchAdminData() // Refresh data
      } else {
        const error = await response.json()
        setError(error.error || 'Failed to approve user')
      }
    } catch (err) {
      setError('Failed to approve user')
    } finally {
      setActionLoading(null)
    }
  }

  const rejectUser = async (userId: string, reason: string = '') => {
    setActionLoading(`reject-${userId}`)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/users/${userId}/reject`, {
        method: 'POST',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ reason })
      })

      if (response.ok) {
        setSuccessMessage('User rejected successfully!')
        setTimeout(() => setSuccessMessage(''), 3000)
        setError('') // Clear any previous errors
        fetchAdminData() // Refresh data
      } else {
        const error = await response.json()
        setError(error.error || 'Failed to reject user')
      }
    } catch (err) {
      setError('Failed to reject user')
    } finally {
      setActionLoading(null)
    }
  }

  const deleteUser = async (userId: string) => {
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      return
    }

    setActionLoading(`delete-${userId}`)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/users/${userId}/delete`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        setSelectedUser(null) // Close modal if open
        setSuccessMessage('User deleted successfully!')
        setTimeout(() => setSuccessMessage(''), 3000)
        setError('') // Clear any previous errors
        fetchAdminData() // Refresh data
      } else {
        const error = await response.json()
        setError(error.error || 'Failed to delete user')
      }
    } catch (err) {
      setError('Failed to delete user')
    } finally {
      setActionLoading(null)
    }
  }

  const updateUser = async (userId: string, userData: Partial<User>) => {
    setActionLoading('update-user')
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/admin/users/${userId}`, {
        method: 'PUT',
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      })

      if (response.ok) {
        setSelectedUser(null) // Close modal
        setSuccessMessage('User updated successfully!')
        setTimeout(() => setSuccessMessage(''), 3000)
        fetchAdminData() // Refresh data immediately
        setError('') // Clear any previous errors
      } else {
        const error = await response.json()
        setError(error.error || 'Failed to update user')
      }
    } catch (err) {
      setError('Failed to update user')
    } finally {
      setActionLoading(null)
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved':
        return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800"><CheckCircle className="w-3 h-3 mr-1" />Approved</span>
      case 'pending':
        return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-yellow-100 text-yellow-800"><Clock className="w-3 h-3 mr-1" />Pending</span>
      case 'rejected':
        return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-red-100 text-red-800"><XCircle className="w-3 h-3 mr-1" />Rejected</span>
      default:
        return <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-800">Unknown</span>
    }
  }

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         `${user.first_name} ${user.last_name}`.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesFilter = statusFilter === 'all' || user.status === statusFilter
    return matchesSearch && matchesFilter
  })

  if (!isAuthenticated || !user?.isAdmin) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Shield className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Admin Access Required</h2>
          <p className="text-gray-600">You need admin privileges to access this page.</p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading admin dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="px-4 py-8 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-gray-600 mt-2">Manage users, approvals, and platform analytics</p>
            {lastUpdated && (
              <p className="text-sm text-gray-500 mt-1">
                Last updated: {lastUpdated.toLocaleTimeString()}
              </p>
            )}
            </div>
          <div className="flex items-center space-x-3">
            <Button
              onClick={manualRefresh}
              disabled={loading}
              variant="outline"
              className="flex items-center space-x-2"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Refreshing...</span>
                </>
              ) : (
                <>
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>Refresh</span>
                </>
              )}
            </Button>
            <Button
              onClick={logout}
              variant="outline"
              className="flex items-center space-x-2 text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200"
            >
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </Button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-600">{error}</p>
            <button 
              onClick={() => setError('')}
              className="text-red-500 hover:text-red-700 ml-2"
            >
              ×
            </button>
          </div>
        )}

        {/* Success Message */}
        {successMessage && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-md">
            <p className="text-green-600">{successMessage}</p>
            <button 
              onClick={() => setSuccessMessage('')}
              className="text-green-500 hover:text-green-700 ml-2"
            >
              ×
            </button>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              {[
                { id: 'overview', label: 'Overview', icon: Users },
                { id: 'users', label: 'User Management', icon: UserCheck },
                { id: 'analytics', label: 'Analytics', icon: BarChart3 },
                { id: 'activity', label: 'Activity Feed', icon: Activity },
                { id: 'health', label: 'System Health', icon: Server }
              ].map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`flex items-center space-x-2 py-2 px-1 border-b-2 font-medium text-sm ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{tab.label}</span>
                  </button>
                )
              })}
            </nav>
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
        {/* Stats Cards */}
        {stats && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total_users}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Pending Approval</CardTitle>
                    <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                    <div className="text-2xl font-bold">{stats.pending_users || 0}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Applications</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total_applications}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">This Month</CardTitle>
                <Calendar className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.applications_this_month}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Monthly Revenue</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">${stats.monthly_revenue.toFixed(2)}</div>
              </CardContent>
            </Card>
          </div>
        )}

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Download className="h-5 w-5" />
                    <span>Export Data</span>
                  </CardTitle>
                  <CardDescription>Download user data and analytics</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button 
                    onClick={exportUsers}
                    disabled={actionLoading === 'export'}
                    className="w-full"
                  >
                    {actionLoading === 'export' ? 'Exporting...' : 'Export Users CSV'}
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <UserCheck className="h-5 w-5" />
                    <span>Pending Users</span>
                  </CardTitle>
                  <CardDescription>Users awaiting approval</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold mb-2">{pendingUsers.length}</div>
                  <Button 
                    onClick={() => setActiveTab('users')}
                    variant="outline"
                    className="w-full"
                  >
                    Review Pending
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Activity className="h-5 w-5" />
                    <span>Recent Activity</span>
                  </CardTitle>
                  <CardDescription>Platform activity overview</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button 
                    onClick={() => setActiveTab('activity')}
                    variant="outline"
                    className="w-full"
                  >
                    View Activity Feed
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="space-y-8">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Platform Analytics</h2>
              <Button onClick={fetchAnalytics} variant="outline">
                <BarChart3 className="h-4 w-4 mr-2" />
                Refresh Analytics
              </Button>
            </div>

            {analytics && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Top Companies */}
                <Card>
                  <CardHeader>
                    <CardTitle>Top Companies</CardTitle>
                    <CardDescription>Most applied to companies</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {analytics.top_companies.slice(0, 5).map((company, index) => (
                        <div key={index} className="flex justify-between items-center">
                          <span className="font-medium">{company.company}</span>
                          <span className="text-blue-600 font-bold">{company.count}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Top Job Titles */}
                <Card>
                  <CardHeader>
                    <CardTitle>Popular Job Titles</CardTitle>
                    <CardDescription>Most sought after positions</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {analytics.top_job_titles.slice(0, 5).map((job, index) => (
                        <div key={index} className="flex justify-between items-center">
                          <span className="font-medium">{job.title}</span>
                          <span className="text-green-600 font-bold">{job.count}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Application Status */}
                <Card>
                  <CardHeader>
                    <CardTitle>Application Status</CardTitle>
                    <CardDescription>Breakdown by application status</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {analytics.applications_by_status.map((status, index) => (
                        <div key={index} className="flex justify-between items-center">
                          <span className="font-medium capitalize">{status.status}</span>
                          <span className="text-purple-600 font-bold">{status.count}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Most Active Users */}
                <Card>
                  <CardHeader>
                    <CardTitle>Most Active Users</CardTitle>
                    <CardDescription>Users with most applications</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {analytics.most_active_users.slice(0, 5).map((user, index) => (
                        <div key={index} className="flex justify-between items-center">
                          <div>
                            <p className="font-medium">{user.name}</p>
                            <p className="text-sm text-gray-500">{user.email}</p>
                          </div>
                          <span className="text-orange-600 font-bold">{user.applications}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* User Success Rates */}
                <Card className="lg:col-span-2">
                  <CardHeader>
                    <CardTitle>User Success Rates</CardTitle>
                    <CardDescription>Users with highest interview/offer rates (5+ applications)</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {analytics.user_success_rates.slice(0, 10).map((user, index) => (
                        <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                          <div>
                            <p className="font-medium">{user.name}</p>
                            <p className="text-sm text-gray-500">{user.email}</p>
                          </div>
                          <div className="text-right">
                            <p className="font-bold text-green-600">{user.success_rate}%</p>
                            <p className="text-sm text-gray-500">
                              {user.successful_applications}/{user.total_applications} successful
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
          </div>
        )}

        {/* System Health Tab */}
        {activeTab === 'health' && (
          <div className="space-y-8">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">System Health</h2>
              <Button onClick={fetchSystemHealth} variant="outline">
                <Server className="h-4 w-4 mr-2" />
                Refresh Health
              </Button>
            </div>

            {systemHealth && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Database className="h-5 w-5" />
                      <span>Database</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="flex justify-between">
                      <span>Size:</span>
                      <span className="font-bold">{systemHealth.database.size_mb} MB</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Users:</span>
                      <span className="font-bold">{systemHealth.database.total_users}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Applications:</span>
                      <span className="font-bold">{systemHealth.database.total_applications}</span>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Activity className="h-5 w-5" />
                      <span>Activity</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <div className="flex justify-between">
                      <span>Last Hour:</span>
                      <span className="font-bold">{systemHealth.activity.recent_activity_1h}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Active Users (24h):</span>
                      <span className="font-bold">{systemHealth.activity.active_users_24h}</span>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <AlertTriangle className="h-5 w-5" />
                      <span>Errors</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex justify-between">
                      <span>Last 24h:</span>
                      <span className={`font-bold ${systemHealth.activity.recent_errors_24h > 0 ? 'text-red-600' : 'text-green-600'}`}>
                        {systemHealth.activity.recent_errors_24h}
                      </span>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Zap className="h-5 w-5" />
                      <span>Bots</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex justify-between">
                      <span>Active Sessions:</span>
                      <span className="font-bold">{systemHealth.bots.active_sessions}</span>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            <Card>
              <CardHeader>
                <CardTitle>System Status</CardTitle>
                <CardDescription>
                  Last updated: {systemHealth ? new Date(systemHealth.timestamp).toLocaleString() : 'Never'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span>Database: Online</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span>API: Operational</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className={`w-3 h-3 rounded-full ${systemHealth?.activity.recent_errors_24h === 0 ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
                    <span>Errors: {systemHealth?.activity.recent_errors_24h === 0 ? 'None' : 'Some'}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Activity Tab */}
        {activeTab === 'activity' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Recent Activity</h2>
              <Button onClick={fetchRecentActivity} variant="outline">
                <Activity className="h-4 w-4 mr-2" />
                Refresh Activity
              </Button>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Platform Activity Feed</CardTitle>
                <CardDescription>Recent actions across the platform</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {recentActivity.map((activity, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                      <div className={`w-2 h-2 rounded-full mt-2 ${
                        activity.status === 'error' ? 'bg-red-500' : 
                        activity.status === 'success' ? 'bg-green-500' : 'bg-blue-500'
                      }`}></div>
                      <div className="flex-1">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-medium">{activity.action}</p>
                            <p className="text-sm text-gray-600">{activity.details}</p>
                            {activity.user && (
                              <p className="text-xs text-gray-500 mt-1">
                                User: {activity.user.name} ({activity.user.email})
                              </p>
                            )}
                          </div>
                          <span className="text-xs text-gray-500">
                            {new Date(activity.timestamp).toLocaleString()}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                  {recentActivity.length === 0 && (
                    <p className="text-center text-gray-500 py-8">No recent activity</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Users Tab - Existing User Management */}
        {activeTab === 'users' && (
          <div className="space-y-6">
            {/* User Management Section */}
            {/* Search and Filter */}
            <div className="flex items-center space-x-4 mb-6">
              <div className="relative flex-1">
                <Search className="h-4 w-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <Input
                  placeholder="Search by name or email..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <div className="flex items-center space-x-2">
                <Filter className="h-4 w-4 text-gray-500" />
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value as any)}
                  className="border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="all">All Users</option>
                  <option value="pending">Pending</option>
                  <option value="approved">Approved</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>
              <Button 
                onClick={exportUsers}
                disabled={actionLoading === 'export'}
                variant="outline"
              >
                <Download className="h-4 w-4 mr-2" />
                Export CSV
              </Button>
              
              <Button 
                onClick={triggerDailyApplications}
                disabled={isTriggeringDailyApps}
                variant="outline"
                className="bg-blue-50 hover:bg-blue-100 border-blue-200 text-blue-700"
              >
                <Zap className="h-4 w-4 mr-2" />
                {isTriggeringDailyApps ? 'Triggering...' : 'Trigger Daily Apps'}
              </Button>
            </div>

            {/* Pending Approvals Section */}
        {pendingUsers.length > 0 && (
              <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center">
                <UserCheck className="h-5 w-5 mr-2" />
                Pending Approvals ({pendingUsers.length})
              </CardTitle>
              <CardDescription>
                Users waiting for admin approval to access the platform
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {pendingUsers.map(user => (
                  <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div>
                        <p className="font-medium">{user.first_name} {user.last_name}</p>
                        <p className="text-sm text-gray-600">{user.email}</p>
                        <p className="text-xs text-gray-500">
                          Registered: {new Date(user.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button 
                        size="sm" 
                        onClick={() => approveUser(user.id)}
                        className="bg-green-600 hover:bg-green-700"
                            disabled={actionLoading === `approve-${user.id}`}
                          >
                            {actionLoading === `approve-${user.id}` ? (
                              <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                            ) : (
                              <>
                        <CheckCircle className="h-4 w-4 mr-1" />
                        Approve
                              </>
                            )}
                      </Button>
                      <Button 
                        size="sm" 
                        variant="destructive"
                        onClick={() => rejectUser(user.id, 'Account rejected by admin')}
                            disabled={actionLoading === `reject-${user.id}`}
                          >
                            {actionLoading === `reject-${user.id}` ? (
                              <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                            ) : (
                              <>
                        <XCircle className="h-4 w-4 mr-1" />
                        Reject
                              </>
                            )}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

            {/* All Users Table */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Users className="h-5 w-5 mr-2" />
                  All Users ({filteredUsers.length})
            </CardTitle>
            <CardDescription>
              Manage all platform users and their permissions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b">
                        <th className="text-left p-4 font-medium">User</th>
                        <th className="text-left p-4 font-medium">Status</th>
                        <th className="text-left p-4 font-medium">Plan</th>
                        <th className="text-left p-4 font-medium">Usage</th>
                        <th className="text-left p-4 font-medium">Joined</th>
                        <th className="text-left p-4 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredUsers.map(user => (
                    <tr key={user.id} className="border-b hover:bg-gray-50">
                          <td className="p-4">
                        <div className="flex items-center space-x-3">
                          <div>
                            <p className="font-medium flex items-center">
                              {user.first_name} {user.last_name}
                                  {user.isAdmin && <Shield className="h-4 w-4 ml-2 text-blue-600" />}
                            </p>
                                <p className="text-sm text-gray-500">{user.email}</p>
                          </div>
                        </div>
                      </td>
                          <td className="p-4">
                        {getStatusBadge(user.status)}
                      </td>
                          <td className="p-4">
                        <span className="capitalize">{user.subscription_plan}</span>
                      </td>
                          <td className="p-4">
                            <span>{user.daily_usage}/{user.daily_quota}</span>
                      </td>
                          <td className="p-4">
                            <span>{new Date(user.created_at).toLocaleDateString()}</span>
                      </td>
                          <td className="p-4">
                        <div className="flex items-center space-x-2">
                              {/* View Details Button */}
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => {
                                  setSelectedUser(user)
                                  fetchUserDetails(user.id)
                                }}
                                disabled={actionLoading === `view-${user.id}`}
                              >
                                <Eye className="h-4 w-4" />
                              </Button>
                              
                              {/* Edit Button */}
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setSelectedUser(user)}
                                disabled={actionLoading === `update-user`}
                              >
                                {actionLoading === `update-user` ? (
                                  <svg className="animate-spin h-4 w-4 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                  </svg>
                                ) : (
                            <Edit className="h-4 w-4" />
                                )}
                          </Button>
                              
                          {user.status === 'pending' && (
                            <>
                              <Button
                                size="sm"
                                onClick={() => approveUser(user.id)}
                                className="bg-green-600 hover:bg-green-700"
                                    disabled={actionLoading === `approve-${user.id}`}
                                  >
                                    {actionLoading === `approve-${user.id}` ? (
                                      <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                      </svg>
                                    ) : (
                                <CheckCircle className="h-4 w-4" />
                                    )}
                              </Button>
                              <Button
                                size="sm"
                                variant="destructive"
                                onClick={() => rejectUser(user.id)}
                                    disabled={actionLoading === `reject-${user.id}`}
                                  >
                                    {actionLoading === `reject-${user.id}` ? (
                                      <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                      </svg>
                                    ) : (
                                <XCircle className="h-4 w-4" />
                                    )}
                              </Button>
                            </>
                          )}
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => deleteUser(user.id)}
                                disabled={actionLoading === `delete-${user.id}`}
                              >
                                {actionLoading === `delete-${user.id}` ? (
                                  <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                  </svg>
                                ) : (
                            <Trash2 className="h-4 w-4" />
                                )}
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

            {filteredUsers.length === 0 && (
              <div className="text-center py-8">
                <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No users found matching your criteria.</p>
              </div>
            )}
                </div>
          </CardContent>
        </Card>
          </div>
        )}

        {/* User Details Modal */}
        {selectedUser && userApplications && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b">
                <div className="flex justify-between items-center">
                  <h2 className="text-2xl font-bold">User Details: {userApplications.user.name}</h2>
                  <Button variant="outline" onClick={() => {
                    setSelectedUser(null)
                    setUserApplications(null)
                    setUserActivity([])
                  }}>
                    ×
                  </Button>
                </div>
                <p className="text-gray-600">{userApplications.user.email}</p>
              </div>

              <div className="p-6 space-y-6">
                {/* User Info Summary */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card>
                    <CardContent className="p-4">
                      <div className="text-center">
                        <p className="text-2xl font-bold text-blue-600">{userApplications.total_count}</p>
                        <p className="text-sm text-gray-600">Total Applications</p>
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4">
                      <div className="text-center">
                        <p className="text-2xl font-bold text-green-600">{selectedUser.daily_usage}</p>
                        <p className="text-sm text-gray-600">Daily Usage</p>
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4">
                      <div className="text-center">
                        <p className="text-2xl font-bold text-purple-600">{selectedUser.subscription_plan}</p>
                        <p className="text-sm text-gray-600">Plan</p>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Applications Tab */}
                <div>
                  <h3 className="text-xl font-bold mb-4">Recent Applications</h3>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {userApplications.applications.slice(0, 10).map((app, index) => (
                      <div key={index} className="p-4 border rounded-lg">
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-medium">{app.job_title}</h4>
                            <p className="text-sm text-gray-600">{app.company}</p>
                            <p className="text-xs text-gray-500">{app.location}</p>
                          </div>
                          <div className="text-right">
                            <span className={`px-2 py-1 rounded text-xs ${
                              app.status === 'applied' ? 'bg-blue-100 text-blue-800' :
                              app.status === 'interview' ? 'bg-green-100 text-green-800' :
                              app.status === 'rejected' ? 'bg-red-100 text-red-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {app.status}
                            </span>
                            <p className="text-xs text-gray-500 mt-1">
                              {new Date(app.applied_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        {app.job_url && (
                          <a href={app.job_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 text-xs mt-2 inline-flex items-center">
                            <ExternalLink className="h-3 w-3 mr-1" />
                            View Job
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Activity Log */}
                <div>
                  <h3 className="text-xl font-bold mb-4">Recent Activity</h3>
                  <div className="space-y-3 max-h-64 overflow-y-auto">
                    {userActivity.map((activity, index) => (
                      <div key={index} className="p-3 bg-gray-50 rounded-lg">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-medium text-sm">{activity.action}</p>
                            <p className="text-xs text-gray-600">{activity.details}</p>
                          </div>
                          <span className="text-xs text-gray-500">
                            {new Date(activity.timestamp).toLocaleString()}
                          </span>
                        </div>
                      </div>
                    ))}
                    {userActivity.length === 0 && (
                      <p className="text-center text-gray-500 py-4">No recent activity</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* User Edit Modal (separate from details modal) */}
        {selectedUser && !userApplications && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-bold mb-4">Edit User: {selectedUser.first_name} {selectedUser.last_name}</h3>
              <div className="space-y-4">
                <div>
                  <Label>Email</Label>
                  <Input 
                    value={selectedUser.email} 
                    onChange={(e) => setSelectedUser({...selectedUser, email: e.target.value})}
                  />
                </div>
                <div>
                  <Label>First Name</Label>
                  <Input 
                    value={selectedUser.first_name} 
                    onChange={(e) => setSelectedUser({...selectedUser, first_name: e.target.value})}
                  />
                </div>
                <div>
                  <Label>Last Name</Label>
                  <Input 
                    value={selectedUser.last_name} 
                    onChange={(e) => setSelectedUser({...selectedUser, last_name: e.target.value})}
                  />
                </div>
                <div>
                  <Label>Status</Label>
                  <select 
                    value={selectedUser.status}
                    onChange={(e) => setSelectedUser({...selectedUser, status: e.target.value as any})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="pending">Pending</option>
                    <option value="approved">Approved</option>
                    <option value="rejected">Rejected</option>
                  </select>
                </div>
                <div>
                  <Label>Subscription Plan</Label>
                  <select 
                    value={selectedUser.subscription_plan}
                    onChange={(e) => setSelectedUser({...selectedUser, subscription_plan: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="free">Free</option>
                    <option value="basic">Basic</option>
                    <option value="pro">Pro</option>
                  </select>
                </div>
                <div>
                  <Label>Daily Quota</Label>
                  <Input 
                    type="number"
                    value={selectedUser.daily_quota} 
                    onChange={(e) => setSelectedUser({...selectedUser, daily_quota: parseInt(e.target.value)})}
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    id="isAdmin" 
                    checked={selectedUser.isAdmin}
                    onChange={(e) => setSelectedUser({...selectedUser, isAdmin: e.target.checked})}
                    className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                  />
                  <Label htmlFor="isAdmin">Admin Privileges</Label>
                </div>
              </div>
              <div className="flex justify-end space-x-2 mt-6">
                <Button variant="outline" onClick={() => setSelectedUser(null)}>
                  Cancel
                </Button>
                <Button onClick={() => {
                  if (selectedUser) {
                    updateUser(selectedUser.id, {
                      first_name: selectedUser.first_name,
                      last_name: selectedUser.last_name,
                      email: selectedUser.email,
                      subscription_plan: selectedUser.subscription_plan,
                      daily_quota: selectedUser.daily_quota,
                      isAdmin: selectedUser.isAdmin,
                      status: selectedUser.status
                    })
                  }
                }}
                disabled={actionLoading === 'update-user'}
                >
                  {actionLoading === 'update-user' ? (
                    <>
                      <svg className="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 714 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Saving...
                    </>
                  ) : (
                    'Save Changes'
                  )}
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
} 