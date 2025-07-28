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
  Settings, 
  Target, 
  TrendingUp, 
  Users,
  Pause,
  RefreshCw,
  Upload,
  CheckCircle,
  Clock,
  AlertCircle
} from 'lucide-react'
import Link from 'next/link'
import { useState, useEffect } from 'react'
import { useAuth } from '@/components/AuthProvider'

// Mock data - will be replaced with real API calls
const mockStats = {
  totalApplications: 147,
  applicationsThisWeek: 23,
  applicationsThisMonth: 89,
  successRate: 12.5,
  averageResponseTime: 5.2,
  topCompanies: [
    { company: 'Microsoft', count: 8 },
    { company: 'Google', count: 6 },
    { company: 'Apple', count: 5 },
    { company: 'Amazon', count: 4 }
  ],
  applicationsByStatus: [
    { status: 'applied', count: 89 },
    { status: 'interview', count: 12 },
    { status: 'rejected', count: 35 },
    { status: 'offer', count: 3 }
  ]
}

const mockUserPlan = {
  plan: 'free',
  dailyQuota: 5,
  dailyUsage: 3,
  subscriptionStatus: 'active'
}

const mockApplications = [
  {
    id: '1',
    jobTitle: 'Senior Software Engineer',
    company: 'Microsoft',
    location: 'Seattle, WA',
    appliedAt: new Date('2024-01-15'),
    status: 'interview',
    aiGenerated: true
  },
  {
    id: '2',
    jobTitle: 'AI Engineer',
    company: 'OpenAI',
    location: 'San Francisco, CA',
    appliedAt: new Date('2024-01-14'),
    status: 'applied',
    aiGenerated: true
  },
  {
    id: '3',
    jobTitle: 'Cybersecurity Analyst',
    company: 'Google',
    location: 'Mountain View, CA',
    appliedAt: new Date('2024-01-13'),
    status: 'rejected',
    aiGenerated: false
  }
]

const mockAgentStatus = {
  isRunning: false,
  currentTask: 'Resume tailoring for Software Engineer positions',
  progress: 75,
  tasksCompleted: 12,
  applicationsSubmitted: 8,
  lastRun: new Date('2024-01-15T10:30:00')
}

export default function DashboardPage() {
  const { user, token } = useAuth()
  const [agentRunning, setAgentRunning] = useState(mockAgentStatus.isRunning)

  const toggleAgent = () => {
    setAgentRunning(!agentRunning)
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

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="flex h-16 items-center px-4">
          <Link href="/" className="flex items-center space-x-2">
            <Bot className="h-6 w-6" />
            <span className="font-bold">EasyApply Platform</span>
          </Link>
          <nav className="ml-6 flex items-center space-x-4 lg:space-x-6">
            <Link href="/dashboard" className="text-sm font-medium">
              Dashboard
            </Link>
            <Link href="/applications" className="text-sm font-medium text-muted-foreground">
              Applications
            </Link>
            <Link href="/profile" className="text-sm font-medium text-muted-foreground">
              Profile
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
          <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
          <div className="flex items-center space-x-2">
            <Button variant="outline">
              <Upload className="h-4 w-4 mr-2" />
              Upload Resume
            </Button>
            <Button>
              <BrainCircuit className="h-4 w-4 mr-2" />
              Configure Agent
            </Button>
          </div>
        </div>

        {/* Quota Status Card */}
        <Card className="col-span-4">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5" />
                  Daily Quota Status
                </CardTitle>
                <CardDescription>
                  {mockUserPlan.dailyUsage}/{mockUserPlan.dailyQuota} applications used today
                </CardDescription>
              </div>
              <div className="text-right">
                <div className="text-sm text-muted-foreground">Current Plan</div>
                <div className="font-semibold capitalize">{mockUserPlan.plan}</div>
                {mockUserPlan.plan === 'free' && (
                  <Button variant="outline" size="sm" asChild className="mt-2">
                    <Link href="/pricing">Upgrade Plan</Link>
                  </Button>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Applications Used Today</span>
                  <span>{mockUserPlan.dailyUsage}/{mockUserPlan.dailyQuota}</span>
                </div>
                <Progress value={(mockUserPlan.dailyUsage / mockUserPlan.dailyQuota) * 100} />
              </div>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Remaining Today</p>
                  <p className="font-semibold">{mockUserPlan.dailyQuota - mockUserPlan.dailyUsage}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Quota Resets</p>
                  <p className="font-semibold">Midnight</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Plan Status</p>
                  <p className="font-semibold text-green-600">Active</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Agent Status Card */}
        <Card className="col-span-4">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Bot className="h-5 w-5" />
                  AI Agent Status
                </CardTitle>
                <CardDescription>
                  {agentRunning ? 'Agent is actively applying to jobs' : 'Agent is currently stopped'}
                </CardDescription>
              </div>
              <Button 
                onClick={toggleAgent}
                variant={agentRunning ? "destructive" : "default"}
                size="sm"
                disabled={mockUserPlan.dailyUsage >= mockUserPlan.dailyQuota}
              >
                {mockUserPlan.dailyUsage >= mockUserPlan.dailyQuota ? (
                  'Quota Exceeded'
                ) : agentRunning ? (
                  <>
                    <Pause className="h-4 w-4 mr-2" />
                    Stop Agent
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4 mr-2" />
                    Start Agent
                  </>
                )}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>{mockAgentStatus.currentTask}</span>
                  <span>{mockAgentStatus.progress}%</span>
                </div>
                <Progress value={mockAgentStatus.progress} />
              </div>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Tasks Completed</p>
                  <p className="font-semibold">{mockAgentStatus.tasksCompleted}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Applications Submitted</p>
                  <p className="font-semibold">{mockAgentStatus.applicationsSubmitted}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Last Run</p>
                  <p className="font-semibold">{mockAgentStatus.lastRun.toLocaleDateString()}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Stats Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Applications</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{mockStats.totalApplications}</div>
              <p className="text-xs text-muted-foreground">
                +{mockStats.applicationsThisWeek} from last week
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">This Month</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{mockStats.applicationsThisMonth}</div>
              <p className="text-xs text-muted-foreground">
                +12% from last month
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{mockStats.successRate}%</div>
              <p className="text-xs text-muted-foreground">
                +2.5% from last month
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{mockStats.averageResponseTime} days</div>
              <p className="text-xs text-muted-foreground">
                -1.2 days from last month
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
          {/* Recent Applications */}
          <Card className="col-span-4">
            <CardHeader>
              <CardTitle>Recent Applications</CardTitle>
              <CardDescription>
                Your latest job applications powered by AI
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockApplications.map((app) => (
                  <div key={app.id} className="flex items-center space-x-4">
                    <div className="flex-1 space-y-1">
                      <p className="text-sm font-medium leading-none">{app.jobTitle}</p>
                      <p className="text-sm text-muted-foreground">{app.company} • {app.location}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      {app.aiGenerated && (
                        <Bot className="h-4 w-4 text-primary" title="AI Generated" />
                      )}
                      <div className={`flex items-center space-x-1 ${getStatusColor(app.status)}`}>
                        {getStatusIcon(app.status)}
                        <span className="text-sm capitalize">{app.status}</span>
                      </div>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {app.appliedAt.toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Top Companies */}
          <Card className="col-span-3">
            <CardHeader>
              <CardTitle>Top Companies</CardTitle>
              <CardDescription>
                Companies you've applied to most
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {mockStats.topCompanies.map((company, index) => (
                <div key={company.company} className="flex items-center">
                  <div className="flex-1">
                    <p className="text-sm font-medium">{company.company}</p>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {company.count} applications
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common tasks and configurations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <Button className="h-20 flex-col" variant="outline">
                <Upload className="h-6 w-6 mb-2" />
                Upload New Resume
              </Button>
              <Button className="h-20 flex-col" variant="outline">
                <Settings className="h-6 w-6 mb-2" />
                Update Preferences
              </Button>
              <Button className="h-20 flex-col" variant="outline">
                <RefreshCw className="h-6 w-6 mb-2" />
                Refresh Jobs
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
} 