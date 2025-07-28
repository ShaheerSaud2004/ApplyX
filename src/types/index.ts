export interface User {
  id: string
  email: string
  firstName: string
  lastName: string
  phone?: string
  linkedin?: string
  website?: string
  subscriptionPlan: SubscriptionPlan
  stripeCustomerId?: string
  subscriptionId?: string
  subscriptionStatus?: string
  currentPeriodEnd?: Date
  dailyQuota: number
  dailyUsage: number
  lastUsageReset: Date
  createdAt: Date
  updatedAt: Date
}

export enum SubscriptionPlan {
  FREE = 'free',
  BASIC = 'basic',
  PRO = 'pro'
}

export interface PlanDetails {
  id: SubscriptionPlan
  name: string
  price: number
  dailyApplications: number
  features: string[]
  stripePriceId?: string
}

export interface JobApplication {
  id: string
  userId: string
  jobTitle: string
  company: string
  location: string
  jobUrl: string
  status: ApplicationStatus
  appliedAt: Date
  resumeUsed?: string
  coverLetterUsed?: string
  notes?: string
  aiGenerated: boolean
}

export enum ApplicationStatus {
  PENDING = 'pending',
  APPLIED = 'applied',
  REJECTED = 'rejected',
  INTERVIEW = 'interview',
  OFFER = 'offer',
  ACCEPTED = 'accepted',
  DECLINED = 'declined'
}

export interface JobPreferences {
  id: string
  userId: string
  positions: string[]
  locations: string[]
  remote: boolean
  experienceLevel: ExperienceLevel[]
  jobTypes: JobType[]
  salaryMinimum?: number
  preferredIndustries?: string[]
  skillsRequired: string[]
}

export enum ExperienceLevel {
  INTERNSHIP = 'internship',
  ENTRY = 'entry',
  ASSOCIATE = 'associate',
  MID_SENIOR = 'mid-senior level',
  DIRECTOR = 'director',
  EXECUTIVE = 'executive'
}

export enum JobType {
  FULL_TIME = 'full-time',
  PART_TIME = 'part-time',
  CONTRACT = 'contract',
  TEMPORARY = 'temporary',
  INTERNSHIP = 'internship',
  VOLUNTEER = 'volunteer'
}

export interface Resume {
  id: string
  userId: string
  fileName: string
  filePath: string
  isDefault: boolean
  uploadedAt: Date
  aiOptimized: boolean
}

export interface AgentTask {
  id: string
  userId: string
  type: AgentTaskType
  status: TaskStatus
  progress: number
  parameters: Record<string, any>
  results?: Record<string, any>
  createdAt: Date
  completedAt?: Date
  error?: string
}

export enum AgentTaskType {
  JOB_SEARCH = 'job_search',
  RESUME_TAILOR = 'resume_tailor',
  COVER_LETTER_GENERATE = 'cover_letter_generate',
  APPLICATION_SUBMIT = 'application_submit',
  BULK_APPLY = 'bulk_apply'
}

export enum TaskStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

export interface DashboardStats {
  totalApplications: number
  applicationsThisWeek: number
  applicationsThisMonth: number
  successRate: number
  averageResponseTime: number
  topCompanies: Array<{ company: string; count: number }>
  applicationsByStatus: Array<{ status: ApplicationStatus; count: number }>
} 