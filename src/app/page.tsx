'use client'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowRight, Bot, FileText, Target, TrendingUp, Users, Zap } from 'lucide-react'
import Link from 'next/link'
import { useAuth } from '@/components/AuthProvider'

function AuthenticatedNav() {
  const { isAuthenticated, user, logout } = useAuth()

  if (isAuthenticated) {
    return (
      <>
        <Link className="text-sm font-medium hover:underline underline-offset-4" href="/dashboard">
          Dashboard
        </Link>
        <Link className="text-sm font-medium hover:underline underline-offset-4" href="/profile">
          Profile
        </Link>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">
            Welcome, {user?.first_name}
          </span>
          <button
            onClick={logout}
            className="text-sm font-medium hover:underline underline-offset-4 text-red-600"
          >
            Logout
          </button>
        </div>
      </>
    )
  }

  return (
    <>
      <Link className="text-sm font-medium hover:underline underline-offset-4" href="/auth/login">
        Sign In
      </Link>
      <Link className="text-sm font-medium hover:underline underline-offset-4" href="/auth/signup">
        Sign Up
      </Link>
    </>
  )
}

function CTAButtons() {
  const { isAuthenticated } = useAuth()

  if (isAuthenticated) {
    return (
      <>
        <Button asChild size="lg">
          <Link href="/dashboard">
            Go to Dashboard <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
        <Button variant="outline" size="lg" asChild>
          <Link href="/profile">Setup Profile</Link>
        </Button>
      </>
    )
  }

  return (
    <>
      <Button asChild size="lg">
        <Link href="/auth/signup">
          Get Started Free <ArrowRight className="ml-2 h-4 w-4" />
        </Link>
      </Button>
      <Button variant="outline" size="lg" asChild>
        <Link href="/pricing">Upgrade Plan</Link>
      </Button>
    </>
  )
}

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Header */}
      <header className="px-4 lg:px-6 h-14 flex items-center border-b">
        <Link className="flex items-center justify-center" href="/">
          <Zap className="h-6 w-6 text-primary" />
          <span className="ml-2 text-lg font-semibold">EasyApply Platform</span>
        </Link>
        <nav className="ml-auto flex gap-4 sm:gap-6">
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="#features">
            Features
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="/pricing">
            Pricing
          </Link>
          <AuthenticatedNav />
        </nav>
      </header>

      {/* Hero Section */}
      <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col items-center space-y-4 text-center">
            <div className="space-y-2">
              <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl/none">
                Apply to 30+ jobs per day. Automatically. While you sleep.
              </h1>
              <p className="mx-auto max-w-[700px] text-gray-500 md:text-xl dark:text-gray-400">
                Teemo AI finds jobs, tailors your resume, applies, and tracks everything. Start free.
              </p>
            </div>
            <div className="space-x-4">
              <CTAButtons />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="w-full py-12 md:py-24 lg:py-32 bg-gray-50 dark:bg-gray-800">
        <div className="container px-4 md:px-6">
          <div className="text-center space-y-4 mb-12">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
              Why Choose Teemo AI?
            </h2>
            <p className="max-w-[900px] mx-auto text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed dark:text-gray-400">
              Everything you need to automate your job search and land your dream job
            </p>
          </div>
          <div className="grid gap-6 lg:grid-cols-3 md:grid-cols-2">
            <Card>
              <CardHeader>
                <Bot className="h-8 w-8 text-primary" />
                <CardTitle>✅ Automated job search</CardTitle>
                <CardDescription>
                  AI agent automatically finds and applies to relevant jobs while you sleep
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-1">
                  <li>• Intelligent job matching</li>
                  <li>• 24/7 automated applications</li>
                  <li>• LinkedIn Easy Apply integration</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <FileText className="h-8 w-8 text-primary" />
                <CardTitle>✅ AI-tailored resume + cover letters</CardTitle>
                <CardDescription>
                  Personalize your resume and generate unique cover letters for each application
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-1">
                  <li>• Keyword optimization</li>
                  <li>• Custom cover letters</li>
                  <li>• ATS-friendly formatting</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Target className="h-8 w-8 text-primary" />
                <CardTitle>✅ Easy Apply integration</CardTitle>
                <CardDescription>
                  Seamlessly integrates with LinkedIn and other job platforms
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-1">
                  <li>• LinkedIn Easy Apply</li>
                  <li>• Indeed Quick Apply</li>
                  <li>• Custom job boards</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <TrendingUp className="h-8 w-8 text-primary" />
                <CardTitle>✅ Dashboard + tracking</CardTitle>
                <CardDescription>
                  Track all your applications with detailed analytics and insights
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-1">
                  <li>• Application tracking</li>
                  <li>• Success metrics</li>
                  <li>• Response analytics</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Users className="h-8 w-8 text-primary" />
                <CardTitle>✅ Free & paid plans</CardTitle>
                <CardDescription>
                  Start free with 5 applications per day, upgrade for more
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-1">
                  <li>• Free: 5 applications/day</li>
                  <li>• Basic: 30 applications/day</li>
                  <li>• Pro: 50 applications/day</li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Zap className="h-8 w-8 text-primary" />
                <CardTitle>✅ Premium Features</CardTitle>
                <CardDescription>
                  Advanced features for power users and job seekers
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="text-sm space-y-1">
                  <li>• Daily email summaries</li>
                  <li>• Google Sheets export</li>
                  <li>• Referral bonuses</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="w-full py-12 md:py-24 lg:py-32">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col items-center space-y-4 text-center">
            <div className="space-y-2">
              <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
                Ready to Transform Your Job Search?
              </h2>
              <p className="mx-auto max-w-[700px] text-gray-500 md:text-xl dark:text-gray-400">
                Join thousands of professionals who have automated their job applications with AI
              </p>
            </div>
            <div className="space-x-4">
              <CTAButtons />
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="flex flex-col gap-2 sm:flex-row py-6 w-full shrink-0 items-center px-4 md:px-6 border-t">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          © 2024 EasyApply Platform. All rights reserved.
        </p>
        <nav className="sm:ml-auto flex gap-4 sm:gap-6">
          <Link className="text-xs hover:underline underline-offset-4" href="#">
            Terms of Service
          </Link>
          <Link className="text-xs hover:underline underline-offset-4" href="#">
            Privacy
          </Link>
        </nav>
      </footer>
    </div>
  )
} 