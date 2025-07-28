'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  Users, 
  DollarSign, 
  Activity, 
  TrendingUp,
  Shield,
  Settings,
  Search,
  Filter,
  MoreVertical
} from 'lucide-react'
import Link from 'next/link'

// Mock data - will be replaced with real API calls
const mockAdminStats = {
  total_users: 1247,
  users_by_plan: [
    { plan: 'free', count: 890 },
    { plan: 'basic', count: 267 },
    { plan: 'pro', count: 90 }
  ],
  total_applications: 45678,
  applications_this_month: 12453,
  monthly_revenue: 4670
}

const mockUsers = [
  {
    id: '1',
    email: 'john.doe@example.com',
    first_name: 'John',
    last_name: 'Doe',
    subscription_plan: 'basic',
    daily_quota: 30,
    daily_usage: 15,
    subscription_status: 'active',
    created_at: '2024-01-15T10:30:00Z'
  },
  {
    id: '2',
    email: 'jane.smith@example.com',
    first_name: 'Jane',
    last_name: 'Smith',
    subscription_plan: 'pro',
    daily_quota: 50,
    daily_usage: 42,
    subscription_status: 'active',
    created_at: '2024-01-10T08:15:00Z'
  },
  {
    id: '3',
    email: 'user@example.com',
    first_name: 'Free',
    last_name: 'User',
    subscription_plan: 'free',
    daily_quota: 5,
    daily_usage: 5,
    subscription_status: 'active',
    created_at: '2024-01-20T14:22:00Z'
  }
]

export default function AdminDashboard() {
  const [stats, setStats] = useState(mockAdminStats)
  const [users, setUsers] = useState(mockUsers)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedPlan, setSelectedPlan] = useState('all')

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         `${user.first_name} ${user.last_name}`.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesPlan = selectedPlan === 'all' || user.subscription_plan === selectedPlan
    return matchesSearch && matchesPlan
  })

  const getPlanColor = (plan: string) => {
    switch (plan) {
      case 'free': return 'text-gray-600 bg-gray-100'
      case 'basic': return 'text-blue-600 bg-blue-100'
      case 'pro': return 'text-purple-600 bg-purple-100'
      default: return 'text-gray-600 bg-gray-100'
    }
  }

  const getUsageColor = (usage: number, quota: number) => {
    const percentage = (usage / quota) * 100
    if (percentage >= 100) return 'text-red-600'
    if (percentage >= 80) return 'text-orange-600'
    return 'text-green-600'
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="flex h-16 items-center px-4">
          <Link href="/" className="flex items-center space-x-2">
            <Shield className="h-6 w-6" />
            <span className="font-bold">Teemo AI Admin</span>
          </Link>
          <nav className="ml-6 flex items-center space-x-4 lg:space-x-6">
            <Link href="/admin" className="text-sm font-medium">
              Dashboard
            </Link>
            <Link href="/dashboard" className="text-sm font-medium text-muted-foreground">
              User Dashboard
            </Link>
          </nav>
          <div className="ml-auto flex items-center space-x-4">
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Button>
          </div>
        </div>
      </header>

      <div className="flex-1 space-y-4 p-8 pt-6">
        <div className="flex items-center justify-between space-y-2">
          <h2 className="text-3xl font-bold tracking-tight">Admin Dashboard</h2>
          <div className="flex items-center space-x-2">
            <Button variant="outline">
              <Filter className="h-4 w-4 mr-2" />
              Export Data
            </Button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_users.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                +12% from last month
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Monthly Revenue</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${stats.monthly_revenue.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                +8% from last month
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Applications</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_applications.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                +15% from last month
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">This Month</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.applications_this_month.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">
                applications submitted
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Users by Plan */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {stats.users_by_plan.map((planData) => (
            <Card key={planData.plan}>
              <CardHeader className="pb-2">
                <CardTitle className="text-base font-medium capitalize">
                  {planData.plan} Plan Users
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{planData.count.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">
                  {((planData.count / stats.total_users) * 100).toFixed(1)}% of total
                </p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* User Management */}
        <Card>
          <CardHeader>
            <CardTitle>User Management</CardTitle>
            <CardDescription>
              View and manage all user accounts
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Filters */}
            <div className="flex items-center space-x-4 mb-6">
              <div className="flex-1 max-w-sm">
                <Label htmlFor="search">Search Users</Label>
                <div className="relative">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="search"
                    placeholder="Search by email or name..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-8"
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="plan-filter">Filter by Plan</Label>
                <select
                  id="plan-filter"
                  value={selectedPlan}
                  onChange={(e) => setSelectedPlan(e.target.value)}
                  className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
                >
                  <option value="all">All Plans</option>
                  <option value="free">Free</option>
                  <option value="basic">Basic</option>
                  <option value="pro">Pro</option>
                </select>
              </div>
            </div>

            {/* Users Table */}
            <div className="rounded-md border">
              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="border-b p-4 text-left">User</th>
                      <th className="border-b p-4 text-left">Plan</th>
                      <th className="border-b p-4 text-left">Usage</th>
                      <th className="border-b p-4 text-left">Status</th>
                      <th className="border-b p-4 text-left">Joined</th>
                      <th className="border-b p-4 text-left">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUsers.map((user) => (
                      <tr key={user.id} className="border-b">
                        <td className="p-4">
                          <div>
                            <div className="font-medium">{user.first_name} {user.last_name}</div>
                            <div className="text-sm text-muted-foreground">{user.email}</div>
                          </div>
                        </td>
                        <td className="p-4">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${getPlanColor(user.subscription_plan)}`}>
                            {user.subscription_plan}
                          </span>
                        </td>
                        <td className="p-4">
                          <div className={`text-sm font-medium ${getUsageColor(user.daily_usage, user.daily_quota)}`}>
                            {user.daily_usage}/{user.daily_quota}
                          </div>
                          <div className="text-xs text-muted-foreground">today</div>
                        </td>
                        <td className="p-4">
                          <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-600">
                            Active
                          </span>
                        </td>
                        <td className="p-4">
                          <div className="text-sm">
                            {new Date(user.created_at).toLocaleDateString()}
                          </div>
                        </td>
                        <td className="p-4">
                          <Button variant="ghost" size="sm">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-muted-foreground">
                Showing {filteredUsers.length} of {users.length} users
              </div>
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="sm">Previous</Button>
                <Button variant="outline" size="sm">Next</Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
} 