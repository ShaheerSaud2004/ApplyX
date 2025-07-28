'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/components/AuthProvider'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
// import { Textarea } from '@/components/ui/textarea'
// import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
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
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/applications`, {
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
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/applications/${editingApplication.id}`, {
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
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="px-4 lg:px-6 h-14 flex items-center border-b bg-white/80 backdrop-blur-sm">
        <div className="container flex items-center">
          <Link href="/" className="flex items-center space-x-2">
            <div className="relative">
              <div className="w-6 h-6 bg-gradient-to-br from-blue-600 to-purple-600 rounded flex items-center justify-center">
                <svg className="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                </svg>
              </div>
              <div className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-gradient-to-br from-orange-500 to-red-500 rounded-full"></div>
            </div>
            <div className="flex flex-col">
              <span className="font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                ApplyX
              </span>
              <span className="text-xs text-muted-foreground -mt-1">by Nebula.AI</span>
            </div>
          </Link>
          <nav className="ml-6 flex items-center space-x-4 lg:space-x-6">
            <Link href="/dashboard" className="text-sm font-medium text-muted-foreground">
              Dashboard
            </Link>
            <Link href="/applications" className="text-sm font-medium">
              Applications
            </Link>
            <Link href="/manual-apply" className="text-sm font-medium text-muted-foreground">
              Manual Apply Links
            </Link>
            <Link href="/profile" className="text-sm font-medium text-muted-foreground">
              Profile
            </Link>
            {user?.isAdmin && (
              <Link href="/admin" className="text-sm font-medium text-blue-600 hover:text-blue-800">
                Admin Panel
              </Link>
            )}
          </nav>
          <div className="ml-auto flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-sm">
              <User className="h-4 w-4" />
              <span className="font-medium">{user?.firstName} {user?.lastName}</span>
            </div>

            <Button variant="outline" size="sm" onClick={logout}>
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      <div className="flex-1 space-y-4 p-8 pt-6">
        <div className="flex items-center justify-between space-y-2">
          <h2 className="text-3xl font-bold tracking-tight">Applications</h2>
          <div className="flex items-center space-x-2">
            <Button variant="outline" onClick={loadApplications}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="grid gap-4 md:grid-cols-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending</CardTitle>
              <Clock className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">{stats.pending}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Viewed</CardTitle>
              <AlertCircle className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{stats.viewed}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Interviews</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.interview}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Rejected</CardTitle>
              <XCircle className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{stats.rejected}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Hired</CardTitle>
              <CheckCircle className="h-4 w-4 text-emerald-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-emerald-600">{stats.hired}</div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle>Filter & Search</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <input
                    placeholder="Search by job title, company, or location..."
                    className="pl-8 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
              </div>
              
              <select 
                className="rounded-md border border-input bg-background px-3 py-2 text-sm"
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

              <select 
                className="rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'date' | 'company' | 'status')}
              >
                <option value="date">Sort by Date</option>
                <option value="company">Sort by Company</option>
                <option value="status">Sort by Status</option>
              </select>
            </div>
          </CardContent>
        </Card>

        {/* Applications List */}
        <Card>
          <CardHeader>
            <CardTitle>Your Applications ({filteredApplications.length})</CardTitle>
            <CardDescription>
              Track and manage all your job applications in one place
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <Loader className="h-8 w-8 animate-spin" />
                <span className="ml-2">Loading applications...</span>
              </div>
            ) : filteredApplications.length === 0 ? (
              <div className="text-center py-8">
                <Building2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No applications found</h3>
                <p className="text-muted-foreground mb-4">
                  {searchTerm || statusFilter !== 'all' 
                    ? 'Try adjusting your filters or search terms'
                    : 'Start your job search with the LinkedIn bot to see applications here'
                  }
                </p>
                <Button asChild>
                  <Link href="/dashboard">Go to Dashboard</Link>
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredApplications.map((application) => {
                  // Safely get status config with fallback
                  const statusKey = application.status || 'pending'
                  const statusInfo = statusConfig[statusKey] || statusConfig['pending']
                  const StatusIcon = statusInfo.icon
                  
                  return (
                    <div key={application.id} className="border rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="text-lg font-semibold">{application.jobTitle}</h3>
                            <Badge className={statusInfo.color}>
                              <StatusIcon className="h-3 w-3 mr-1" />
                              {statusInfo.label}
                            </Badge>
                          </div>
                          
                          <div className="grid md:grid-cols-2 gap-4 text-sm text-muted-foreground">
                            <div className="flex items-center gap-2">
                              <Building2 className="h-4 w-4" />
                              <span>{application.company}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <MapPin className="h-4 w-4" />
                              <span>{application.location}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Calendar className="h-4 w-4" />
                              <span>Applied {new Date(application.appliedAt).toLocaleDateString()}</span>
                            </div>
                            {application.salary && (
                              <div className="flex items-center gap-2">
                                <DollarSign className="h-4 w-4" />
                                <span>{application.salary}</span>
                              </div>
                            )}
                          </div>

                          {application.notes && (
                            <p className="mt-3 text-sm text-muted-foreground">{application.notes}</p>
                          )}
                        </div>

                        <div className="flex items-center gap-2 ml-4">
                          {application.jobUrl && (
                            <Button variant="outline" size="sm" asChild>
                              <a href={application.jobUrl} target="_blank" rel="noopener noreferrer">
                                <ExternalLink className="h-4 w-4" />
                              </a>
                            </Button>
                          )}
                          <Button variant="outline" size="sm" onClick={() => openEditModal(application)}>
                            Edit
                          </Button>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Edit Application Modal */}
      <Dialog open={!!editingApplication} onOpenChange={(open) => !open && closeEditModal()}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Edit Application</DialogTitle>
          </DialogHeader>
          {editingApplication && (
            <div className="space-y-4">
              <div>
                <h4 className="font-medium">{editingApplication.jobTitle}</h4>
                <p className="text-sm text-muted-foreground">{editingApplication.company}</p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="status">Status</Label>
                <select 
                  value={editFormData.status} 
                  onChange={(e) => setEditFormData({...editFormData, status: e.target.value as any})}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <option value="pending">Pending</option>
                  <option value="viewed">Viewed</option>
                  <option value="interview">Interview</option>
                  <option value="rejected">Rejected</option>
                  <option value="hired">Hired</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="notes">Notes</Label>
                <textarea
                  id="notes"
                  placeholder="Add notes about this application..."
                  value={editFormData.notes}
                  onChange={(e) => setEditFormData({...editFormData, notes: e.target.value})}
                  rows={3}
                  className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={closeEditModal}>
              Cancel
            </Button>
            <Button onClick={updateApplication} disabled={updateLoading}>
              {updateLoading ? 'Updating...' : 'Save Changes'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
} 