'use client'

import React from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Bot, ExternalLink, RefreshCw } from 'lucide-react'
import Link from 'next/link'

interface PersistentBotIndicatorProps {
  isRunning: boolean
  persistent?: boolean
  applicationsCount?: number
  className?: string
}

export function PersistentBotIndicator({ 
  isRunning, 
  persistent = false, 
  applicationsCount = 0,
  className = ""
}: PersistentBotIndicatorProps) {
  
  if (!isRunning) return null

  return (
    <div className={`fixed bottom-4 right-4 z-50 ${className}`}>
      <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-4 max-w-sm">
        <div className="flex items-center gap-3">
          <div className="relative">
            <Bot className="h-6 w-6 text-blue-600" />
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
          </div>
          
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="font-medium text-sm">AI Agent Running</span>
              {persistent && (
                <Badge variant="outline" className="text-xs bg-blue-50 text-blue-700 border-blue-200">
                  <RefreshCw className="h-3 w-3 mr-1" />
                  Persistent
                </Badge>
              )}
            </div>
            
            <div className="text-xs text-gray-600">
              {applicationsCount > 0 ? (
                <span>{applicationsCount} applications submitted</span>
              ) : (
                <span>Searching for jobs...</span>
              )}
            </div>
            
            {persistent && (
              <div className="text-xs text-blue-600 mt-1">
                ✅ Survives page refresh
              </div>
            )}
          </div>
          
          <Link href="/dashboard">
            <Button variant="ghost" size="sm" className="p-2">
              <ExternalLink className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
} 