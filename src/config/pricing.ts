import { PlanDetails, SubscriptionPlan } from '@/types'

export const PRICING_PLANS: Record<SubscriptionPlan, PlanDetails> = {
  [SubscriptionPlan.FREE]: {
    id: SubscriptionPlan.FREE,
    name: 'Free',
    price: 0,
    dailyApplications: 10,
    features: [
      '10 applications per day',
      'Basic resume tailoring',
      'Application tracking',
      'Email support'
    ]
  },
  [SubscriptionPlan.BASIC]: {
    id: SubscriptionPlan.BASIC,
    name: 'Basic',
    price: 4.99,
    dailyApplications: 60,
    stripePriceId: process.env.NEXT_PUBLIC_STRIPE_BASIC_PRICE_ID,
    features: [
      '60 applications per day',
      'Advanced AI resume tailoring',
      'Custom cover letters',
      'Application tracking',
      'Daily email summaries',
      'Priority support'
    ]
  },
  [SubscriptionPlan.PRO]: {
    id: SubscriptionPlan.PRO,
    name: 'Pro',
    price: 9.99,
    dailyApplications: 100,
    stripePriceId: process.env.NEXT_PUBLIC_STRIPE_PRO_PRICE_ID,
    features: [
      '100+ applications per day',
      'Premium AI resume tailoring',
      'Custom cover letters',
      'Application tracking',
      'Daily email summaries',
      'Google Sheets export',
      'Notion integration',
      'Resume preview & download',
      'Priority support',
      'Referral bonuses'
    ]
  }
}

export const getPlanByName = (planName: string): PlanDetails | null => {
  return PRICING_PLANS[planName as SubscriptionPlan] || null
}

export const getQuotaForPlan = (plan: SubscriptionPlan): number => {
  return PRICING_PLANS[plan].dailyApplications
} 