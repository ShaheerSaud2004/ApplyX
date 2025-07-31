'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/components/AuthProvider'
import { getApiUrl } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  Calendar, 
  Building2, 
  MapPin, 
  DollarSign, 
  Clock, 
  CheckCircle,
  XCircle,
  AlertCircle,
  Loader,
  ExternalLink,
  Filter,
  Search,
  Download,
  RefreshCw,
  User,
  LogOut
} from 'lucide-react'
import Link from 'next/link'

interface Application {
  id: string
  jobTitle: string
  company: string
  location: string
  salary?: string
  appliedAt: string
  status: 'pending' | 'viewed' | 'interview' | 'rejected' | 'hired'
  jobUrl?: string
  notes?: string
  responseTime?: number
}

interface EditApplicationData {
  status: 'pending' | 'viewed' | 'interview' | 'rejected' | 'hired'
  notes: string
}

const statusConfig = {
  pending: { 
    icon: Clock, 
    color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    label: 'Pending'
  },
  viewed: { 
    icon: AlertCircle, 
    color: 'bg-blue-100 text-blue-800 border-blue-200',
    label: 'Viewed'
  },
  interview: { 
    icon: CheckCircle, 
    color: 'bg-green-100 text-green-800 border-green-200',
    label: 'Interview'
  },
  rejected: { 
    icon: XCircle, 
    color: 'bg-red-100 text-red-800 border-red-200',
    label: 'Rejected'
  },
  hired: { 
    icon: CheckCircle, 
    color: 'bg-emerald-100 text-emerald-800 border-emerald-200',
    label: 'Hired'
  }
}

export default function ApplicationsPage() {
  const { user, token, logout } = useAuth()
  const [applications, setApplications] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [sortBy, setSortBy] = useState<'date' | 'company' | 'status'>('date')
  const [editingApplication, setEditingApplication] = useState<Application | null>(null)
  const [editFormData, setEditFormData] = useState<EditApplicationData>({ status: 'pending', notes: '' })
  const [updateLoading, setUpdateLoading] = useState(false)

  useEffect(() => {
    if (token) {
      loadApplications()
      
      // Set up auto-refresh every 15 seconds to catch new applications
      const refreshInterval = setInterval(() => {
        console.log('🔄 Auto-refreshing applications to check for new jobs...')
        loadApplications()
      }, 15000) // 15 seconds - frequent refresh to catch new applications
      
      return () => clearInterval(refreshInterval)
    }
  }, [token])

  const loadApplications = async () => {
    try {
      setLoading(true)
      const currentCount = applications.length
      
              const response = await fetch(getApiUrl('/api/applications'), {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        const data = await response.json()
        const newApplications = data.applications || []
        
        // Check if new applications were added
        if (newApplications.length > currentCount) {
          const newCount = newApplications.length - currentCount
          console.log(`🎉 ${newCount} new application(s) detected!`)
          
          // You could add a toast notification here if you have a toast component
          // toast.success(`${newCount} new application(s) found!`)
        }
        
        setApplications(newApplications)
      } else {
        console.error('Failed to load applications')
      }
    } catch (error) {
      console.error('Error loading applications:', error)
    } finally {
      setLoading(false)
    }
  }

  const openEditModal = (application: Application) => {
    setEditingApplication(application)
    setEditFormData({
      status: application.status,
      notes: application.notes || ''
    })
  }

  const closeEditModal = () => {
    setEditingApplication(null)
    setEditFormData({ status: 'pending', notes: '' })
  }

  const updateApplication = async () => {
    if (!editingApplication) return

    setUpdateLoading(true)
    try {
      const response = await fetch(getApiUrl(`/api/applications/${editingApplication.id}`), {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(editFormData)
      })

      if (response.ok) {
        // Update the application in the local state
        setApplications(prev => prev.map(app => 
          app.id === editingApplication.id 
            ? { ...app, status: editFormData.status, notes: editFormData.notes }
            : app
        ))
        closeEditModal()
        console.log('✅ Application updated successfully')
      } else {
        console.error('Failed to update application')
      }
    } catch (error) {
      console.error('Error updating application:', error)
    } finally {
      setUpdateLoading(false)
    }
  }

  const filteredApplications = applications.filter(app => {
    const matchesSearch = app.jobTitle.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         app.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         app.location.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesStatus = statusFilter === 'all' || app.status === statusFilter
    
    return matchesSearch && matchesStatus
  }).sort((a, b) => {
    switch (sortBy) {
      case 'date':
        return new Date(b.appliedAt).getTime() - new Date(a.appliedAt).getTime()
      case 'company':
        return a.company.localeCompare(b.company)
      case 'status':
        return a.status.localeCompare(b.status)
      default:
        return 0
    }
  })

  const getStatusStats = () => {
    const stats = applications.reduce((acc, app) => {
      acc[app.status] = (acc[app.status] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return {
      total: applications.length,
      pending: stats.pending || 0,
      viewed: stats.viewed || 0,
      interview: stats.interview || 0,
      rejected: stats.rejected || 0,
      hired: stats.hired || 0
    }
  }

  const stats = getStatusStats()

  if (!user) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card>
          <CardContent className="p-6">
            <p className="text-center">Please log in to view your applications.</p>
            <Button asChild className="w-full mt-4">
              <Link href="/auth/login">Login</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <header className="px-4 lg:px-6 h-16 flex items-center border-b bg-white/80 backdrop-blur-md sticky top-0 z-50 shadow-sm">
        <div className="container flex items-center">
          <Link href="/" className="flex items-center space-x-2">
            <div className="relative">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center shadow-lg">
                <svg className="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                </svg>
              </div>
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-gradient-to-br from-orange-500 to-red-500 rounded-full animate-pulse"></div>
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-lg bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                ApplyX
              </span>
              <span className="text-xs text-muted-foreground -mt-1 hidden sm:block">by Nebula.AI</span>
            </div>
          </Link>
          
          {/* Desktop Navigation */}
          <nav className="ml-8 hidden md:flex items-center space-x-6">
            <Link href="/dashboard" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
              Dashboard
            </Link>
            <Link href="/applications" className="text-sm font-medium text-blue-600 border-b-2 border-blue-600 pb-1">
              Applications
            </Link>
            <Link href="/manual-apply" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
              Manual Apply
            </Link>
            <Link href="/profile" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
              Profile
            </Link>
            {user?.isAdmin && (
              <Link href="/admin" className="text-sm font-medium text-purple-600 hover:text-purple-800 transition-colors">
                Admin
              </Link>
            )}
          </nav>
          
          <div className="ml-auto flex items-center space-x-2 md:space-x-4">
            {/* User info - hidden on mobile */}
            <div className="hidden sm:flex items-center space-x-2 text-sm bg-white/50 rounded-full px-3 py-1 backdrop-blur-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="font-medium">{user?.firstName} {user?.lastName}</span>
            </div>

            <Button variant="outline" size="sm" onClick={logout} className="bg-white/50 backdrop-blur-sm hover:bg-white/80">
              <LogOut className="h-4 w-4 md:mr-2" />
              <span className="hidden md:inline">Logout</span>
            </Button>
          </div>
        </div>
      </header>

      <div className="flex-1 space-y-6 md:space-y-8 p-4 md:p-8 pt-8">
        {/* Hero Section */}
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 p-6 md:p-8 text-white shadow-2xl">
          <div className="absolute inset-0 bg-black/10"></div>
          <div className="relative z-10">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
              <div>
                <h1 className="text-2xl md:text-4xl font-bold mb-2">Job Applications</h1>
                <p className="text-blue-100 text-base md:text-lg">Track your career journey with beautiful insights</p>
              </div>
              <div className="flex items-center space-x-3">
                <Button variant="secondary" onClick={loadApplications} className="bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white/30">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
                <Button variant="secondary" className="bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white/30">
                  <Download className="h-4 w-4 mr-2" />
                  Export
                </Button>
              </div>
            </div>
          </div>
          <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-16 translate-x-16"></div>
          <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full translate-y-12 -translate-x-12"></div>
        </div>

        {/* Statistics Cards */}
        <div className="grid gap-6 md:grid-cols-6">
          <div className="bg-white/70 backdrop-blur-md rounded-2xl p-6 border border-white/50 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 shadow-lg">
                <Building2 className="h-6 w-6 text-white" />
              </div>
              <span className="text-sm font-medium text-muted-foreground">Total</span>
            </div>
            <div className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              {stats.total}
            </div>
            <p className="text-sm text-muted-foreground mt-1">Applications submitted</p>
          </div>
          
          <div className="bg-white/70 backdrop-blur-md rounded-2xl p-6 border border-white/50 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-xl bg-gradient-to-br from-yellow-500 to-orange-500 shadow-lg">
                <Clock className="h-6 w-6 text-white" />
              </div>
              <span className="text-sm font-medium text-muted-foreground">Pending</span>
            </div>
            <div className="text-3xl font-bold bg-gradient-to-r from-yellow-600 to-orange-600 bg-clip-text text-transparent">
              {stats.pending}
            </div>
            <p className="text-sm text-muted-foreground mt-1">Awaiting response</p>
          </div>

          <div className="bg-white/70 backdrop-blur-md rounded-2xl p-6 border border-white/50 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 shadow-lg">
                <AlertCircle className="h-6 w-6 text-white" />
              </div>
              <span className="text-sm font-medium text-muted-foreground">Viewed</span>
            </div>
            <div className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
              {stats.viewed}
            </div>
            <p className="text-sm text-muted-foreground mt-1">Profile reviewed</p>
          </div>

          <div className="bg-white/70 backdrop-blur-md rounded-2xl p-6 border border-white/50 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 shadow-lg">
                <CheckCircle className="h-6 w-6 text-white" />
              </div>
              <span className="text-sm font-medium text-muted-foreground">Interviews</span>
            </div>
            <div className="text-3xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
              {stats.interview}
            </div>
            <p className="text-sm text-muted-foreground mt-1">Interview scheduled</p>
          </div>

          <div className="bg-white/70 backdrop-blur-md rounded-2xl p-6 border border-white/50 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-xl bg-gradient-to-br from-red-500 to-pink-500 shadow-lg">
                <XCircle className="h-6 w-6 text-white" />
              </div>
              <span className="text-sm font-medium text-muted-foreground">Rejected</span>
            </div>
            <div className="text-3xl font-bold bg-gradient-to-r from-red-600 to-pink-600 bg-clip-text text-transparent">
              {stats.rejected}
            </div>
            <p className="text-sm text-muted-foreground mt-1">Not selected</p>
          </div>

          <div className="bg-white/70 backdrop-blur-md rounded-2xl p-6 border border-white/50 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-500 to-green-600 shadow-lg">
                <CheckCircle className="h-6 w-6 text-white" />
              </div>
              <span className="text-sm font-medium text-muted-foreground">Hired</span>
            </div>
            <div className="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-green-600 bg-clip-text text-transparent">
              {stats.hired}
            </div>
            <p className="text-sm text-muted-foreground mt-1">Job offers received</p>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid gap-8 lg:grid-cols-2">
          {/* Application Status Chart */}
          <div className="bg-white/70 backdrop-blur-md rounded-3xl p-8 border border-white/50 shadow-xl">
            <div className="flex items-center mb-6">
              <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 shadow-lg mr-4">
                <Calendar className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold">Application Status Overview</h3>
                <p className="text-muted-foreground">Distribution of your applications by status</p>
              </div>
            </div>
            <div className="space-y-4">
              {[
                { label: 'Pending', value: stats.pending, color: 'from-yellow-400 to-orange-500', bgColor: 'bg-yellow-100', total: stats.total },
                { label: 'Viewed', value: stats.viewed, color: 'from-blue-400 to-cyan-500', bgColor: 'bg-blue-100', total: stats.total },
                { label: 'Interviews', value: stats.interview, color: 'from-green-400 to-emerald-500', bgColor: 'bg-green-100', total: stats.total },
                { label: 'Rejected', value: stats.rejected, color: 'from-red-400 to-pink-500', bgColor: 'bg-red-100', total: stats.total },
                { label: 'Hired', value: stats.hired, color: 'from-emerald-400 to-green-500', bgColor: 'bg-emerald-100', total: stats.total }
              ].map((item) => {
                const percentage = stats.total > 0 ? (item.value / stats.total) * 100 : 0
                return (
                  <div key={item.label} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center space-x-3">
                        <div className={`w-4 h-4 rounded-full ${item.bgColor}`}></div>
                        <span className="font-medium">{item.label}</span>
                      </div>
                      <span className="font-semibold">{item.value} ({percentage.toFixed(1)}%)</span>
                    </div>
                    <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className={`h-full bg-gradient-to-r ${item.color} transition-all duration-700 ease-out rounded-full`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Key Metrics */}
          <div className="bg-white/70 backdrop-blur-md rounded-3xl p-8 border border-white/50 shadow-xl">
            <div className="flex items-center mb-6">
              <div className="p-3 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 shadow-lg mr-4">
                <CheckCircle className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold">Success Metrics</h3>
                <p className="text-muted-foreground">Track your application performance</p>
              </div>
            </div>
            <div className="space-y-6">
              {/* Response Rate */}
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="font-medium">Response Rate</span>
                  <span className="font-semibold text-blue-600">
                    {stats.total > 0 ? (((stats.viewed + stats.interview + stats.hired) / stats.total) * 100).toFixed(1) : 0}%
                  </span>
                </div>
                <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-blue-400 to-purple-500 transition-all duration-700 ease-out rounded-full"
                    style={{ width: `${stats.total > 0 ? ((stats.viewed + stats.interview + stats.hired) / stats.total) * 100 : 0}%` }}
                  />
                </div>
                <p className="text-sm text-muted-foreground">
                  {stats.viewed + stats.interview + stats.hired} responses from {stats.total} applications
                </p>
              </div>

              {/* Interview Rate */}
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="font-medium">Interview Rate</span>
                  <span className="font-semibold text-purple-600">
                    {stats.total > 0 ? ((stats.interview / stats.total) * 100).toFixed(1) : 0}%
                  </span>
                </div>
                <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-purple-400 to-pink-500 transition-all duration-700 ease-out rounded-full"
                    style={{ width: `${stats.total > 0 ? (stats.interview / stats.total) * 100 : 0}%` }}
                  />
                </div>
                <p className="text-sm text-muted-foreground">
                  {stats.interview} interviews from {stats.total} applications
                </p>
              </div>

              {/* Success Rate */}
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="font-medium">Success Rate</span>
                  <span className="font-semibold text-emerald-600">
                    {stats.total > 0 ? ((stats.hired / stats.total) * 100).toFixed(1) : 0}%
                  </span>
                </div>
                <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-emerald-400 to-green-500 transition-all duration-700 ease-out rounded-full"
                    style={{ width: `${stats.total > 0 ? (stats.hired / stats.total) * 100 : 0}%` }}
                  />
                </div>
                <p className="text-sm text-muted-foreground">
                  {stats.hired} offers from {stats.total} applications
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white/70 backdrop-blur-md rounded-3xl p-8 border border-white/50 shadow-xl">
          <div className="flex items-center mb-6">
            <div className="p-3 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 shadow-lg mr-4">
              <Filter className="h-6 w-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold">Filter & Search</h3>
              <p className="text-muted-foreground">Find specific applications quickly</p>
            </div>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-medium">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
                <input
                  placeholder="Search by job title, company, or location..."
                  className="pl-10 w-full rounded-xl border border-white/50 bg-white/50 backdrop-blur-sm px-4 py-3 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Status Filter</label>
              <select 
                className="w-full rounded-xl border border-white/50 bg-white/50 backdrop-blur-sm px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="all">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="viewed">Viewed</option>
                <option value="interview">Interview</option>
                <option value="rejected">Rejected</option>
                <option value="hired">Hired</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Sort By</label>
              <select 
                className="w-full rounded-xl border border-white/50 bg-white/50 backdrop-blur-sm px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'date' | 'company' | 'status')}
              >
                <option value="date">Sort by Date</option>
                <option value="company">Sort by Company</option>
                <option value="status">Sort by Status</option>
              </select>
            </div>
          </div>
        </div>

        {/* Applications List */}
        <div className="bg-white/70 backdrop-blur-md rounded-3xl p-8 border border-white/50 shadow-xl">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center">
              <div className="p-3 rounded-xl bg-gradient-to-br from-green-500 to-teal-500 shadow-lg mr-4">
                <Building2 className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold">Your Applications ({filteredApplications.length})</h3>
                <p className="text-muted-foreground">Track and manage all your job applications in one place</p>
              </div>
            </div>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="relative">
                <div className="w-12 h-12 rounded-full border-4 border-blue-200 border-t-blue-600 animate-spin"></div>
              </div>
              <span className="ml-4 text-lg font-medium">Loading applications...</span>
            </div>
          ) : filteredApplications.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <Building2 className="h-12 w-12 text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-2">No applications found</h3>
              <p className="text-muted-foreground mb-6 text-lg">
                {searchTerm || statusFilter !== 'all' 
                  ? 'Try adjusting your filters or search terms'
                  : 'Start your job search with the LinkedIn bot to see applications here'
                }
              </p>
              <Button asChild className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 rounded-xl shadow-lg">
                <Link href="/dashboard">Go to Dashboard</Link>
              </Button>
            </div>
          ) : (
            <div className="space-y-6">
              {filteredApplications.map((application) => {
                // Safely get status config with fallback
                const statusKey = application.status || 'pending'
                const statusInfo = statusConfig[statusKey] || statusConfig['pending']
                const StatusIcon = statusInfo.icon
                
                return (
                  <div key={application.id} className="bg-white/50 backdrop-blur-sm border border-white/50 rounded-2xl p-6 hover:shadow-xl hover:bg-white/70 transition-all duration-300 hover:scale-[1.02]">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-4 mb-4">
                          <h3 className="text-xl font-bold">{application.jobTitle}</h3>
                          <div className={`flex items-center px-3 py-1 rounded-full text-sm font-medium border ${statusInfo.color}`}>
                            <StatusIcon className="h-4 w-4 mr-2" />
                            {statusInfo.label}
                          </div>
                        </div>
                        
                        <div className="grid md:grid-cols-2 gap-4 text-sm">
                          <div className="flex items-center gap-3 p-3 rounded-xl bg-white/50">
                            <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500">
                              <Building2 className="h-4 w-4 text-white" />
                            </div>
                            <span className="font-medium">{application.company}</span>
                          </div>
                          <div className="flex items-center gap-3 p-3 rounded-xl bg-white/50">
                            <div className="p-2 rounded-lg bg-gradient-to-br from-green-500 to-teal-500">
                              <MapPin className="h-4 w-4 text-white" />
                            </div>
                            <span className="font-medium">{application.location}</span>
                          </div>
                          <div className="flex items-center gap-3 p-3 rounded-xl bg-white/50">
                            <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500">
                              <Calendar className="h-4 w-4 text-white" />
                            </div>
                            <span className="font-medium">Applied {new Date(application.appliedAt).toLocaleDateString()} at {new Date(application.appliedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                          </div>
                          {application.salary && (
                            <div className="flex items-center gap-3 p-3 rounded-xl bg-white/50">
                              <div className="p-2 rounded-lg bg-gradient-to-br from-yellow-500 to-orange-500">
                                <DollarSign className="h-4 w-4 text-white" />
                              </div>
                              <span className="font-medium">{application.salary}</span>
                            </div>
                          )}
                        </div>

                        {application.notes && (
                          <div className="mt-4 p-4 rounded-xl bg-white/50 border border-white/50">
                            <p className="text-sm font-medium text-muted-foreground">{application.notes}</p>
                          </div>
                        )}
                      </div>

                      <div className="flex items-center gap-3 ml-6">
                        {application.jobUrl && (
                          <Button variant="outline" size="sm" asChild className="bg-white/50 hover:bg-white/80 rounded-xl">
                            <a href={application.jobUrl} target="_blank" rel="noopener noreferrer">
                              <ExternalLink className="h-4 w-4" />
                            </a>
                          </Button>
                        )}
                        <Button variant="outline" size="sm" onClick={() => openEditModal(application)} className="bg-white/50 hover:bg-white/80 rounded-xl">
                          Edit
                        </Button>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>

      {/* Edit Application Modal */}
      <Dialog open={!!editingApplication} onOpenChange={(open) => !open && closeEditModal()}>
        <DialogContent className="sm:max-w-[500px] bg-white/90 backdrop-blur-md border border-white/50 rounded-2xl">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold">Edit Application</DialogTitle>
          </DialogHeader>
          {editingApplication && (
            <div className="space-y-6">
              <div className="p-4 rounded-xl bg-gradient-to-r from-blue-50 to-purple-50 border border-white/50">
                <h4 className="font-bold text-lg">{editingApplication.jobTitle}</h4>
                <p className="text-muted-foreground">{editingApplication.company}</p>
              </div>
              
              <div className="space-y-3">
                <Label htmlFor="status" className="text-sm font-medium">Status</Label>
                <select 
                  value={editFormData.status} 
                  onChange={(e) => setEditFormData({...editFormData, status: e.target.value as any})}
                  className="w-full rounded-xl border border-white/50 bg-white/50 backdrop-blur-sm px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                >
                  <option value="pending">Pending</option>
                  <option value="viewed">Viewed</option>
                  <option value="interview">Interview</option>
                  <option value="rejected">Rejected</option>
                  <option value="hired">Hired</option>
                </select>
              </div>

              <div className="space-y-3">
                <Label htmlFor="notes" className="text-sm font-medium">Notes</Label>
                <textarea
                  id="notes"
                  placeholder="Add notes about this application..."
                  value={editFormData.notes}
                  onChange={(e) => setEditFormData({...editFormData, notes: e.target.value})}
                  rows={4}
                  className="w-full rounded-xl border border-white/50 bg-white/50 backdrop-blur-sm px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all placeholder:text-muted-foreground resize-none"
                />
              </div>
            </div>
          )}
          <DialogFooter className="space-x-3">
            <Button variant="outline" onClick={closeEditModal} className="rounded-xl">
              Cancel
            </Button>
            <Button onClick={updateApplication} disabled={updateLoading} className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-xl">
              {updateLoading ? 'Updating...' : 'Save Changes'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
} 