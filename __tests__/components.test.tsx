import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
    }
  },
  usePathname() {
    return '/'
  },
}))

// Mock API calls
global.fetch = jest.fn()

describe('UI Components', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear()
  })

  test('Button renders correctly', () => {
    render(<Button>Test Button</Button>)
    expect(screen.getByRole('button', { name: 'Test Button' })).toBeInTheDocument()
  })

  test('Button handles click events', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click Me</Button>)
    
    fireEvent.click(screen.getByRole('button', { name: 'Click Me' }))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  test('Card component renders with content', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Test Card</CardTitle>
          <CardDescription>Test Description</CardDescription>
        </CardHeader>
        <CardContent>
          <p>Test Content</p>
        </CardContent>
      </Card>
    )

    expect(screen.getByText('Test Card')).toBeInTheDocument()
    expect(screen.getByText('Test Description')).toBeInTheDocument()
    expect(screen.getByText('Test Content')).toBeInTheDocument()
  })

  test('Input component works correctly', () => {
    const handleChange = jest.fn()
    render(
      <div>
        <Label htmlFor="test-input">Test Input</Label>
        <Input id="test-input" onChange={handleChange} />
      </div>
    )

    const input = screen.getByLabelText('Test Input')
    fireEvent.change(input, { target: { value: 'test value' } })
    
    expect(handleChange).toHaveBeenCalled()
    expect(input).toHaveValue('test value')
  })

  test('Progress component displays correct value', () => {
    render(<Progress value={50} />)
    
    const progressBar = screen.getByRole('progressbar')
    expect(progressBar).toHaveAttribute('aria-valuenow', '50')
  })
})

describe('Authentication Flow', () => {
  test('Login form submission', async () => {
    const mockResponse = {
      ok: true,
      json: async () => ({
        token: 'mock-token',
        user: { id: '1', email: 'test@example.com' }
      })
    }

    ;(fetch as jest.Mock).mockResolvedValueOnce(mockResponse)

    const LoginForm = () => {
      const [email, setEmail] = React.useState('')
      const [password, setPassword] = React.useState('')

      const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        })

        if (response.ok) {
          const data = await response.json()
          localStorage.setItem('token', data.token)
        }
      }

      return (
        <form onSubmit={handleSubmit}>
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          
          <Button type="submit">Login</Button>
        </form>
      )
    }

    render(<LoginForm />)

    fireEvent.change(screen.getByLabelText('Email'), { 
      target: { value: 'test@example.com' } 
    })
    fireEvent.change(screen.getByLabelText('Password'), { 
      target: { value: 'password123' } 
    })
    
    fireEvent.click(screen.getByRole('button', { name: 'Login' }))

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          email: 'test@example.com', 
          password: 'password123' 
        })
      })
    })
  })

  test('Registration form validation', () => {
    const RegistrationForm = () => {
      const [email, setEmail] = React.useState('')
      const [password, setPassword] = React.useState('')
      const [errors, setErrors] = React.useState<string[]>([])

      const validateForm = () => {
        const newErrors: string[] = []
        
        if (!email.includes('@')) {
          newErrors.push('Valid email is required')
        }
        
        if (password.length < 8) {
          newErrors.push('Password must be at least 8 characters')
        }
        
        setErrors(newErrors)
        return newErrors.length === 0
      }

      const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        validateForm()
      }

      return (
        <form onSubmit={handleSubmit}>
          <Input
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          
          <Input
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          
          <Button type="submit">Register</Button>
          
          {errors.map((error, index) => (
            <div key={index} role="alert">{error}</div>
          ))}
        </form>
      )
    }

    render(<RegistrationForm />)

    fireEvent.change(screen.getByPlaceholderText('Email'), { 
      target: { value: 'invalid-email' } 
    })
    fireEvent.change(screen.getByPlaceholderText('Password'), { 
      target: { value: '123' } 
    })
    
    fireEvent.click(screen.getByRole('button', { name: 'Register' }))

    expect(screen.getByText('Valid email is required')).toBeInTheDocument()
    expect(screen.getByText('Password must be at least 8 characters')).toBeInTheDocument()
  })
})

describe('Dashboard Components', () => {
  test('Agent status display', () => {
    const AgentStatus = ({ 
      isRunning, 
      progress, 
      applicationsSubmitted 
    }: {
      isRunning: boolean
      progress: number
      applicationsSubmitted: number
    }) => (
      <Card>
        <CardHeader>
          <CardTitle>
            Agent Status: {isRunning ? 'Running' : 'Stopped'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Progress value={progress} />
          <p>Applications submitted: {applicationsSubmitted}</p>
        </CardContent>
      </Card>
    )

    render(
      <AgentStatus 
        isRunning={true}
        progress={75}
        applicationsSubmitted={15}
      />
    )

    expect(screen.getByText('Agent Status: Running')).toBeInTheDocument()
    expect(screen.getByText('Applications submitted: 15')).toBeInTheDocument()
    
    const progressBar = screen.getByRole('progressbar')
    expect(progressBar).toHaveAttribute('aria-valuenow', '75')
  })

  test('Quota display component', () => {
    const QuotaDisplay = ({ 
      used, 
      total, 
      plan 
    }: {
      used: number
      total: number
      plan: string
    }) => {
      const percentage = (used / total) * 100
      
      return (
        <Card>
          <CardHeader>
            <CardTitle>Daily Quota</CardTitle>
            <CardDescription>{used}/{total} applications used</CardDescription>
          </CardHeader>
          <CardContent>
            <Progress value={percentage} />
            <p>Current plan: {plan}</p>
            {used >= total && (
              <p role="alert">Quota exceeded! Upgrade to continue.</p>
            )}
          </CardContent>
        </Card>
      )
    }

    render(<QuotaDisplay used={5} total={5} plan="free" />)

    expect(screen.getByText('5/5 applications used')).toBeInTheDocument()
    expect(screen.getByText('Current plan: free')).toBeInTheDocument()
    expect(screen.getByText('Quota exceeded! Upgrade to continue.')).toBeInTheDocument()
  })
})

describe('Pricing Components', () => {
  test('Pricing card displays correctly', () => {
    const PricingCard = ({ 
      plan, 
      price, 
      features 
    }: {
      plan: string
      price: number
      features: string[]
    }) => (
      <Card>
        <CardHeader>
          <CardTitle>{plan}</CardTitle>
          <CardDescription>${price}/month</CardDescription>
        </CardHeader>
        <CardContent>
          <ul>
            {features.map((feature, index) => (
              <li key={index}>✅ {feature}</li>
            ))}
          </ul>
          <Button>Choose {plan}</Button>
        </CardContent>
      </Card>
    )

    const features = [
              '50 applications per day',
      'AI resume tailoring',
      'Email support'
    ]

    render(<PricingCard plan="Basic" price={10} features={features} />)

    expect(screen.getByText('Basic')).toBeInTheDocument()
    expect(screen.getByText('$10/month')).toBeInTheDocument()
    expect(screen.getByText('✅ 50 applications per day')).toBeInTheDocument()
    expect(screen.getByText('✅ AI resume tailoring')).toBeInTheDocument()
    expect(screen.getByText('✅ Email support')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Choose Basic' })).toBeInTheDocument()
  })
})

describe('File Upload Components', () => {
  test('Resume upload component', async () => {
    const mockResponse = {
      ok: true,
      json: async () => ({ message: 'Resume uploaded successfully' })
    }

    ;(fetch as jest.Mock).mockResolvedValueOnce(mockResponse)

    const ResumeUpload = () => {
      const [file, setFile] = React.useState<File | null>(null)
      const [message, setMessage] = React.useState('')

      const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        
        if (!file) return

        const formData = new FormData()
        formData.append('resume', file)

        const response = await fetch('/api/upload/resume', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: formData
        })

        const data = await response.json()
        setMessage(data.message)
      }

      return (
        <form onSubmit={handleSubmit}>
          <Input
            type="file"
            accept=".pdf,.doc,.docx"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          <Button type="submit" disabled={!file}>
            Upload Resume
          </Button>
          {message && <p>{message}</p>}
        </form>
      )
    }

    render(<ResumeUpload />)

    const fileInput = screen.getByDisplayValue('')
    const uploadButton = screen.getByRole('button', { name: 'Upload Resume' })

    expect(uploadButton).toBeDisabled()

    // Simulate file selection
    const file = new File(['dummy content'], 'resume.pdf', { type: 'application/pdf' })
    Object.defineProperty(fileInput, 'files', {
      value: [file],
      writable: false,
    })

    fireEvent.change(fileInput)
    
    await waitFor(() => {
      expect(uploadButton).not.toBeDisabled()
    })

    fireEvent.click(uploadButton)

    await waitFor(() => {
      expect(screen.getByText('Resume uploaded successfully')).toBeInTheDocument()
    })
  })
})

describe('Error Handling', () => {
  test('API error handling', async () => {
    const mockResponse = {
      ok: false,
      status: 400,
      json: async () => ({ error: 'Invalid request' })
    }

    ;(fetch as jest.Mock).mockResolvedValueOnce(mockResponse)

    const ApiComponent = () => {
      const [error, setError] = React.useState('')

      const makeRequest = async () => {
        try {
          const response = await fetch('/api/test')
          
          if (!response.ok) {
            const data = await response.json()
            setError(data.error || 'An error occurred')
          }
        } catch (err) {
          setError('Network error')
        }
      }

      return (
        <div>
          <Button onClick={makeRequest}>Make Request</Button>
          {error && <div role="alert">{error}</div>}
        </div>
      )
    }

    render(<ApiComponent />)

    fireEvent.click(screen.getByRole('button', { name: 'Make Request' }))

    await waitFor(() => {
      expect(screen.getByText('Invalid request')).toBeInTheDocument()
    })
  })
}) 