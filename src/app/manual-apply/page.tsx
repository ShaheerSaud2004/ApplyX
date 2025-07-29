'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  ExternalLink, 
  Search, 
  Filter, 
  Building2, 
  Code, 
  Shield, 
  Users, 
  LogOut,
  User,
  Globe,
  MapPin,
  DollarSign,
  Clock,
  RefreshCw,
  TrendingUp,
  BarChart3,
  Server,
  Lightbulb,
  Edit3,
  Check,
  X,
  Palette,
  Heart,
  Settings,
  Scale,
  GraduationCap,
  MessageSquare,
  Cog,
  Rocket,
  MoreHorizontal,
  ChevronDown,
  Star,
  Calendar,
  Target,
  Zap,
  Eye,
  SortAsc,
  SortDesc
} from 'lucide-react'
import Link from 'next/link'
import { useAuth } from '@/components/AuthProvider'

interface JobListing {
  id: string
  title: string
  company: string
  location: string
  salary?: string
  posted_date: string
  url: string
  category: string
  description?: string
  is_remote: boolean
  experience_level: string
  source: string
  tags: string[]
}

interface JobCategory {
  label: string
  icon: string
  color: string
  description: string
  count: number
}

interface JobStats {
  total_jobs: number
  jobs_today: number
  jobs_this_week: number
  experience_levels: { [key: string]: number }
  remote_stats: { remote: number; on_site: number }
  top_companies: { company: string; count: number }[]
  sources: { [key: string]: number }
}

interface TrendingData {
  trending_titles: { title: string; count: number }[]
  trending_companies: { company: string; count: number }[]
  trending_locations: { location: string; count: number }[]
}

const iconMap: { [key: string]: any } = {
  Code, BarChart3, Shield, Server, Lightbulb, Palette, TrendingUp, Users,
  DollarSign, Heart, Settings, Scale, Building2, GraduationCap, MessageSquare,
  Cog, Rocket, MoreHorizontal, Globe
}

export default function ManualApplyPage() {
  const { user, token, logout } = useAuth()
  const [jobs, setJobs] = useState<JobListing[]>([])
  const [categories, setCategories] = useState<{ [key: string]: JobCategory }>({})
  const [stats, setStats] = useState<JobStats | null>(null)
  const [trending, setTrending] = useState<TrendingData | null>(null)
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)
  
  // Filters
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [experienceLevel, setExperienceLevel] = useState('all')
  const [remoteFilter, setRemoteFilter] = useState('all')
  const [sortBy, setSortBy] = useState('posted_date')
  const [sortOrder, setSortOrder] = useState('DESC')
  const [currentPage, setCurrentPage] = useState(1)
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false)
  
  // Edit functionality
  const [editingJob, setEditingJob] = useState<string | null>(null)
  const [editingCategory, setEditingCategory] = useState<string>('')
  const [isUpdatingJob, setIsUpdatingJob] = useState(false)

  useEffect(() => {
    if (user) {
      loadInitialData()
    }
  }, [user])

  useEffect(() => {
    if (user) {
      loadJobs()
    }
  }, [user, selectedCategory, searchTerm, experienceLevel, remoteFilter, sortBy, sortOrder, currentPage])

  const loadInitialData = async () => {
    try {
      setLoading(true)
      
      // Load categories, stats, and trending data in parallel
      const [categoriesRes, statsRes, trendingRes] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/jobs/categories`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/jobs/stats`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/jobs/trending`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ])

      const categoriesData = await categoriesRes.json()
      const statsData = await statsRes.json()
      const trendingData = await trendingRes.json()

      setCategories(categoriesData.categories)
      setStats(statsData)
      setTrending(trendingData)
      
    } catch (error) {
      console.error('Error loading initial data:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadJobs = async () => {
    try {
      const params = new URLSearchParams({
        category: selectedCategory,
        search: searchTerm,
        experience_level: experienceLevel,
        is_remote: remoteFilter,
        sort_by: sortBy,
        sort_order: sortOrder,
        page: currentPage.toString(),
        limit: '20'
      })

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/jobs?${params}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await response.json()
      
      if (currentPage === 1) {
        setJobs(data.jobs)
      } else {
        setJobs(prev => [...prev, ...data.jobs])
      }
      
    } catch (error) {
      console.error('Error loading jobs:', error)
    }
  }

  const triggerJobUpdate = async () => {
    try {
      setUpdating(true)
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/jobs/update`, { 
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const data = await response.json()
      
      if (response.ok) {
        // Reload all data after update
        await loadInitialData()
        setCurrentPage(1)
      } else {
        console.error('Update failed:', data.error)
      }
    } catch (error) {
      console.error('Error updating jobs:', error)
    } finally {
      setUpdating(false)
    }
  }

  const resetFilters = () => {
    setSelectedCategory('all')
    setSearchTerm('')
    setExperienceLevel('all')
    setRemoteFilter('all')
    setSortBy('posted_date')
    setSortOrder('DESC')
    setCurrentPage(1)
  }

  const loadMoreJobs = () => {
    setCurrentPage(prev => prev + 1)
  }

  const startEditingJob = (jobId: string, currentCategory: string) => {
    setEditingJob(jobId)
    setEditingCategory(currentCategory)
  }

  const cancelEditing = () => {
    setEditingJob(null)
    setEditingCategory('')
  }

  const updateJobCategory = async (jobId: string, newCategory: string) => {
    try {
      setIsUpdatingJob(true)
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/jobs/${jobId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          category: newCategory
        })
      })

      if (response.ok) {
        // Update the local state
        setJobs(prevJobs => 
          prevJobs.map(job => 
            job.id === jobId 
              ? { ...job, category: newCategory }
              : job
          )
        )
        
        // Refresh categories to update counts
        await loadInitialData()
        
        setEditingJob(null)
        setEditingCategory('')
      } else {
        console.error('Failed to update job category')
      }
    } catch (error) {
      console.error('Error updating job category:', error)
    } finally {
      setIsUpdatingJob(false)
    }
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card>
          <CardContent className="p-6">
            <p className="text-center">Please log in to view manual apply links.</p>
            <Button asChild className="w-full mt-4">
              <Link href="/auth/login">Login</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-100">
      {/* Header */}
      <header className="px-4 lg:px-6 h-16 flex items-center border-b bg-white/80 backdrop-blur-md sticky top-0 z-50 shadow-sm">
        <div className="flex h-16 items-center px-4">
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
              <span className="text-xs text-muted-foreground -mt-1">by Nebula.AI</span>
            </div>
          </Link>
          <nav className="ml-8 flex items-center space-x-6">
            <Link href="/dashboard" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
              Dashboard
            </Link>
            <Link href="/applications" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
              Applications
            </Link>
            <Link href="/manual-apply" className="text-sm font-medium text-purple-600 border-b-2 border-purple-600 pb-1">
              Manual Apply Links
            </Link>
            <Link href="/profile" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
              Profile
            </Link>
            {user?.isAdmin && (
              <Link href="/admin" className="text-sm font-medium text-purple-600 hover:text-purple-800 transition-colors">
                Admin Panel
              </Link>
            )}
          </nav>
          <div className="ml-auto flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-sm bg-white/50 rounded-full px-3 py-1 backdrop-blur-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="font-medium">{user?.firstName} {user?.lastName}</span>
            </div>
            <Button variant="outline" size="sm" onClick={logout} className="bg-white/50 backdrop-blur-sm hover:bg-white/80">
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      <div className="flex-1 space-y-8 p-8 pt-8">
        {/* Hero Section */}
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600 p-8 text-white shadow-2xl">
          <div className="absolute inset-0 bg-black/10"></div>
          <div className="relative z-10">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-4xl font-bold mb-2">Manual Apply Links</h1>
                <p className="text-purple-100 text-lg">Comprehensive job opportunities from top sources, updated daily</p>
              </div>
              <div className="flex items-center space-x-3">
                <Button 
                  variant="secondary" 
                  onClick={triggerJobUpdate}
                  disabled={updating}
                  className="bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white/30"
                >
                  <RefreshCw className={`h-4 w-4 mr-2 ${updating ? 'animate-spin' : ''}`} />
                  {updating ? 'Updating...' : 'Update Jobs'}
                </Button>
                <Button variant="secondary" onClick={resetFilters} className="bg-white/20 backdrop-blur-sm border-white/30 text-white hover:bg-white/30">
                  Reset Filters
                </Button>
              </div>
            </div>
          </div>
          <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-16 translate-x-16"></div>
          <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full translate-y-12 -translate-x-12"></div>
        </div>

        {/* Stats Overview */}
        {stats && (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <div className="bg-white/70 backdrop-blur-md rounded-2xl p-6 border border-white/50 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 shadow-lg">
                  <Target className="h-6 w-6 text-white" />
                </div>
                <span className="text-sm font-medium text-muted-foreground">Total Jobs</span>
              </div>
              <div className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                {stats?.total_jobs?.toLocaleString() || '0'}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                From {stats?.sources ? Object.keys(stats.sources).length : 0} sources
              </p>
            </div>

            <div className="bg-white/70 backdrop-blur-md rounded-2xl p-6 border border-white/50 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 rounded-xl bg-gradient-to-br from-yellow-500 to-orange-500 shadow-lg">
                  <Zap className="h-6 w-6 text-white" />
                </div>
                <span className="text-sm font-medium text-muted-foreground">Added Today</span>
              </div>
              <div className="text-3xl font-bold bg-gradient-to-r from-yellow-600 to-orange-600 bg-clip-text text-transparent">
                {stats?.jobs_today || 0}
              </div>
              <p className="text-sm text-muted-foreground mt-1">Fresh opportunities</p>
            </div>

            <div className="bg-white/70 backdrop-blur-md rounded-2xl p-6 border border-white/50 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 shadow-lg">
                  <Calendar className="h-6 w-6 text-white" />
                </div>
                <span className="text-sm font-medium text-muted-foreground">This Week</span>
              </div>
              <div className="text-3xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                {stats?.jobs_this_week || 0}
              </div>
              <p className="text-sm text-muted-foreground mt-1">New listings</p>
            </div>

            <div className="bg-white/70 backdrop-blur-md rounded-2xl p-6 border border-white/50 shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 shadow-lg">
                  <Globe className="h-6 w-6 text-white" />
                </div>
                <span className="text-sm font-medium text-muted-foreground">Remote Jobs</span>
              </div>
              <div className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                {stats?.remote_stats?.remote || 0}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                {stats?.remote_stats?.remote && stats?.total_jobs ? Math.round((stats.remote_stats.remote / stats.total_jobs) * 100) : 0}% of total
              </p>
            </div>
          </div>
        )}

        {/* Search and Advanced Filters */}
        <div className="bg-white/70 backdrop-blur-md rounded-3xl p-8 border border-white/50 shadow-xl">
          <div className="flex items-center mb-6">
            <div className="p-3 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 shadow-lg mr-4">
              <Search className="h-6 w-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-bold">Search & Filter Jobs</h3>
              <p className="text-muted-foreground">Find your perfect opportunity</p>
            </div>
          </div>

          <div className="flex flex-col space-y-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-4 top-4 h-5 w-5 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Search jobs, companies, or locations..."
                  className="w-full pl-12 pr-4 py-4 border border-white/50 rounded-xl bg-white/50 backdrop-blur-sm text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <Button
                variant="outline"
                onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                className="bg-white/50 hover:bg-white/80 rounded-xl px-6 py-4"
              >
                <Filter className="h-4 w-4 mr-2" />
                Advanced Filters
                <ChevronDown className={`h-4 w-4 ml-2 transition-transform ${showAdvancedFilters ? 'rotate-180' : ''}`} />
              </Button>
            </div>

            {showAdvancedFilters && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 pt-6 border-t border-white/30">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Experience Level</label>
                  <select
                    className="w-full p-3 border border-white/50 rounded-xl bg-white/50 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                    value={experienceLevel}
                    onChange={(e) => setExperienceLevel(e.target.value)}
                  >
                    <option value="all">All Levels</option>
                    <option value="entry">Entry Level</option>
                    <option value="mid">Mid Level</option>
                    <option value="senior">Senior Level</option>
                    <option value="executive">Executive</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Work Type</label>
                  <select
                    className="w-full p-3 border border-white/50 rounded-xl bg-white/50 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                    value={remoteFilter}
                    onChange={(e) => setRemoteFilter(e.target.value)}
                  >
                    <option value="all">All Types</option>
                    <option value="true">Remote Only</option>
                    <option value="false">On-site Only</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Sort By</label>
                  <select
                    className="w-full p-3 border border-white/50 rounded-xl bg-white/50 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                  >
                    <option value="posted_date">Date Posted</option>
                    <option value="company">Company</option>
                    <option value="title">Job Title</option>
                    <option value="location">Location</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Order</label>
                  <Button
                    variant="outline"
                    className="w-full justify-start bg-white/50 hover:bg-white/80 rounded-xl"
                    onClick={() => setSortOrder(sortOrder === 'ASC' ? 'DESC' : 'ASC')}
                  >
                    {sortOrder === 'ASC' ? <SortAsc className="h-4 w-4 mr-2" /> : <SortDesc className="h-4 w-4 mr-2" />}
                    {sortOrder === 'ASC' ? 'Ascending' : 'Descending'}
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Categories Filter */}
        {Object.keys(categories).length > 0 && (
          <div className="bg-white/70 backdrop-blur-md rounded-3xl p-8 border border-white/50 shadow-xl">
            <div className="flex items-center mb-6">
              <div className="p-3 rounded-xl bg-gradient-to-br from-teal-500 to-cyan-500 shadow-lg mr-4">
                <Building2 className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold">Job Categories</h3>
                <p className="text-muted-foreground">Browse by industry and specialization</p>
              </div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
              <button
                onClick={() => setSelectedCategory('all')}
                className={`relative p-4 rounded-2xl text-left transition-all duration-300 hover:scale-105 ${
                  selectedCategory === 'all' 
                    ? 'bg-gradient-to-br from-purple-500 to-pink-500 text-white shadow-lg' 
                    : 'bg-white/50 hover:bg-white/80 backdrop-blur-sm border border-white/50'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${selectedCategory === 'all' ? 'bg-white/20' : 'bg-purple-100'}`}>
                    <Globe className={`h-5 w-5 ${selectedCategory === 'all' ? 'text-white' : 'text-purple-600'}`} />
                  </div>
                  <div>
                    <div className="font-medium">All Jobs</div>
                    <div className={`text-sm ${selectedCategory === 'all' ? 'text-purple-100' : 'text-muted-foreground'}`}>
                      {jobs.length}
                    </div>
                  </div>
                </div>
              </button>
              {Object.entries(categories).map(([key, category]) => {
                const IconComponent = iconMap[category.icon] || Building2
                const isSelected = selectedCategory === key
                return (
                  <button
                    key={key}
                    onClick={() => setSelectedCategory(key)}
                    className={`relative p-4 rounded-2xl text-left transition-all duration-300 hover:scale-105 ${
                      isSelected 
                        ? 'bg-gradient-to-br from-purple-500 to-pink-500 text-white shadow-lg' 
                        : 'bg-white/50 hover:bg-white/80 backdrop-blur-sm border border-white/50'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${isSelected ? 'bg-white/20' : 'bg-purple-100'}`}>
                        <IconComponent className={`h-5 w-5 ${isSelected ? 'text-white' : 'text-purple-600'}`} />
                      </div>
                      <div>
                        <div className="font-medium">{category.label}</div>
                        <div className={`text-sm ${isSelected ? 'text-purple-100' : 'text-muted-foreground'}`}>
                          {category.count}
                        </div>
                      </div>
                    </div>
                  </button>
                )
              })}
            </div>
          </div>
        )}

        {/* Job Listings */}
        <div className="bg-white/70 backdrop-blur-md rounded-3xl p-8 border border-white/50 shadow-xl">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center">
              <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-500 to-green-500 shadow-lg mr-4">
                <Rocket className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold">
                  Job Listings ({jobs.length} showing)
                  {selectedCategory !== 'all' && categories[selectedCategory] && (
                    <span className="ml-3 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
                      {categories[selectedCategory].label}
                    </span>
                  )}
                </h3>
                <p className="text-muted-foreground">Click on any job to apply directly on the company's website</p>
              </div>
            </div>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="relative">
                <div className="w-12 h-12 rounded-full border-4 border-purple-200 border-t-purple-600 animate-spin"></div>
              </div>
              <span className="ml-4 text-lg font-medium">Loading jobs...</span>
            </div>
          ) : jobs.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
                <Building2 className="h-12 w-12 text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-2">No jobs found</h3>
              <p className="text-muted-foreground mb-6 text-lg">
                Try adjusting your search terms or filters
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {jobs.map((job) => {
                const categoryInfo = categories[job.category]
                
                return (
                  <div key={job.id} className="group bg-white/70 backdrop-blur-sm border border-white/60 rounded-lg p-3 hover:shadow-md hover:bg-white/80 transition-all duration-200 hover:scale-[1.01]">
                    <div className="flex items-center justify-between gap-4">
                      {/* Essential Job Info */}
                      <div className="flex items-center gap-4 flex-1 min-w-0">
                        {/* Job Title & Company */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold text-base truncate text-gray-800">{job.title}</h3>
                            {job.is_remote && (
                              <Badge variant="secondary" className="text-xs bg-green-100 text-green-700">Remote</Badge>
                            )}
                            {editingJob === job.id ? (
                              <div className="flex items-center space-x-1">
                                <Select 
                                  value={editingCategory} 
                                  onValueChange={setEditingCategory}
                                  disabled={isUpdatingJob}
                                >
                                  <SelectTrigger className="w-32 h-6 text-xs">
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent>
                                    {Object.entries(categories).map(([key, category]) => (
                                      <SelectItem key={key} value={key}>
                                        {category.label}
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                                <Button 
                                  size="sm" 
                                  variant="ghost" 
                                  className="h-6 w-6 p-0 bg-green-100 hover:bg-green-200"
                                  onClick={() => updateJobCategory(job.id, editingCategory)}
                                  disabled={isUpdatingJob}
                                >
                                  <Check className="h-3 w-3 text-green-600" />
                                </Button>
                                <Button 
                                  size="sm" 
                                  variant="ghost" 
                                  className="h-6 w-6 p-0 bg-red-100 hover:bg-red-200"
                                  onClick={cancelEditing}
                                  disabled={isUpdatingJob}
                                >
                                  <X className="h-3 w-3 text-red-600" />
                                </Button>
                              </div>
                            ) : (
                              <Button 
                                size="sm" 
                                variant="ghost" 
                                className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                                onClick={() => startEditingJob(job.id, job.category)}
                              >
                                <Edit3 className="h-3 w-3 text-gray-500" />
                              </Button>
                            )}
                          </div>
                          <div className="flex items-center gap-3 text-sm text-gray-600">
                            <span className="flex items-center gap-1">
                              <Building2 className="h-3 w-3" />
                              {job.company}
                            </span>
                            <span className="flex items-center gap-1">
                              <MapPin className="h-3 w-3" />
                              {job.location}
                            </span>
                            {job.salary && (
                              <span className="flex items-center gap-1 font-medium text-green-600">
                                <DollarSign className="h-3 w-3" />
                                {job.salary}
                              </span>
                            )}
                          </div>
                        </div>
                        
                        {/* Category & Date */}
                        <div className="hidden md:flex items-center gap-2 text-xs text-gray-500">
                          <Badge variant="outline" className="text-xs">
                            {categoryInfo?.label || job.category}
                          </Badge>
                          <span>{new Date(job.posted_date).toLocaleDateString()}</span>
                        </div>
                      </div>
                      
                      {/* Apply Button */}
                      <Button asChild size="sm" className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white border-none rounded-lg h-8 px-4">
                        <a href={job.url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-xs">
                          <ExternalLink className="h-3 w-3" />
                          Apply
                        </a>
                      </Button>
                    </div>
                  </div>
                )
              })}
              
              {/* Load More Button */}
              <div className="text-center pt-6">
                <Button 
                  variant="outline" 
                  onClick={loadMoreJobs}
                  className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white border-none rounded-xl px-8 py-3 shadow-lg"
                >
                  Load More Jobs
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
} 