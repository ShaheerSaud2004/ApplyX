'use client'

import React, { useState, useRef, useCallback, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle,
  DialogDescription 
} from '@/components/ui/dialog'
import { 
  Upload, 
  File, 
  CheckCircle, 
  AlertCircle, 
  X,
  FileText,
  Download,
  Trash2
} from 'lucide-react'
import { useAuth } from './AuthProvider'

interface ResumeUploadModalProps {
  isOpen: boolean
  onOpenChange: (open: boolean) => void
  onUploadSuccess?: (filename: string) => void
}

interface UploadedResume {
  filename: string
  originalName: string
  uploadedAt: string
  size: number
}

export function ResumeUploadModal({ isOpen, onOpenChange, onUploadSuccess }: ResumeUploadModalProps) {
  const { token } = useAuth()
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadedResumes, setUploadedResumes] = useState<UploadedResume[]>([])
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loadingResumes, setLoadingResumes] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Load existing resumes when modal opens
  useEffect(() => {
    if (isOpen && token) {
      loadExistingResumes()
    }
  }, [isOpen, token])

  const loadExistingResumes = async () => {
    if (!token) return
    
    setLoadingResumes(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/resumes`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        const data = await response.json()
        setUploadedResumes(data.resumes || [])
      }
    } catch (error) {
      console.error('Error loading resumes:', error)
    } finally {
      setLoadingResumes(false)
    }
  }

  const MAX_FILE_SIZE = 16 * 1024 * 1024 // 16MB
  const ALLOWED_TYPES = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']

  const validateFile = (file: File): string | null => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      return 'Only PDF, DOC, and DOCX files are allowed'
    }
    if (file.size > MAX_FILE_SIZE) {
      return 'File size must be less than 16MB'
    }
    return null
  }

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      handleFileSelection(files[0])
    }
  }, [])

  const handleFileSelection = (file: File) => {
    setError('')
    setSuccess('')
    
    const validationError = validateFile(file)
    if (validationError) {
      setError(validationError)
      return
    }
    
    setSelectedFile(file)
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      handleFileSelection(files[0])
    }
  }

  const uploadFile = async () => {
    if (!selectedFile || !token) return

    setUploading(true)
    setUploadProgress(0)
    setError('')
    setSuccess('')

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const xhr = new XMLHttpRequest()
      
      // Track upload progress
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const progress = Math.round((e.loaded / e.total) * 100)
          setUploadProgress(progress)
        }
      })

      // Handle completion
      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText)
          setSuccess('Resume uploaded successfully!')
          setSelectedFile(null)
          setUploadProgress(100)
          
          // Refresh the resumes list from server
          loadExistingResumes()
          
          if (onUploadSuccess) {
            onUploadSuccess(response.filename)
          }
          
          // Reset after 2 seconds
          setTimeout(() => {
            setUploadProgress(0)
            setSuccess('')
          }, 2000)
        } else {
          const errorResponse = JSON.parse(xhr.responseText)
          setError(errorResponse.error || 'Upload failed')
        }
        setUploading(false)
      })

      xhr.addEventListener('error', () => {
        setError('Upload failed. Please try again.')
        setUploading(false)
      })

      xhr.open('POST', `${process.env.NEXT_PUBLIC_API_URL}/api/upload/resume`)
      xhr.setRequestHeader('Authorization', `Bearer ${token}`)
      xhr.send(formData)

    } catch (error) {
      console.error('Upload error:', error)
      setError('Upload failed. Please try again.')
      setUploading(false)
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const removeSelectedFile = () => {
    setSelectedFile(null)
    setError('')
    setSuccess('')
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Upload Resume
          </DialogTitle>
          <DialogDescription>
            Upload your resume in PDF, DOC, or DOCX format (max 16MB)
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Upload Area */}
          <Card 
            className={`border-2 border-dashed transition-all duration-300 ${
              isDragging 
                ? 'border-blue-500 bg-blue-50' 
                : selectedFile 
                ? 'border-green-500 bg-green-50' 
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <CardContent 
              className="p-8 text-center cursor-pointer"
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              {selectedFile ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-center w-16 h-16 mx-auto bg-green-100 rounded-full">
                    <FileText className="h-8 w-8 text-green-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-green-800">{selectedFile.name}</h3>
                    <p className="text-sm text-green-600">{formatFileSize(selectedFile.size)}</p>
                  </div>
                  <div className="flex justify-center gap-2">
                    <Button onClick={uploadFile} disabled={uploading} size="sm">
                      {uploading ? 'Uploading...' : 'Upload File'}
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={(e) => {
                        e.stopPropagation()
                        removeSelectedFile()
                      }}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center justify-center w-16 h-16 mx-auto bg-gray-100 rounded-full">
                    <Upload className="h-8 w-8 text-gray-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-800">
                      {isDragging ? 'Drop your resume here' : 'Click to upload or drag and drop'}
                    </h3>
                    <p className="text-sm text-gray-600">PDF, DOC, DOCX up to 16MB</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Hidden File Input */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.doc,.docx"
            onChange={handleFileInputChange}
            className="hidden"
          />

          {/* Upload Progress */}
          {uploading && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Uploading...</span>
                <span>{uploadProgress}%</span>
              </div>
              <Progress value={uploadProgress} className="w-full" />
            </div>
          )}

          {/* Error/Success Messages */}
          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-md">
              <AlertCircle className="h-4 w-4 text-red-500" />
              <span className="text-sm text-red-600">{error}</span>
            </div>
          )}

          {success && (
            <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-md">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span className="text-sm text-green-600">{success}</span>
            </div>
          )}

          {/* Recently Uploaded Files */}
          {uploadedResumes.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Recently Uploaded</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {uploadedResumes.slice(0, 3).map((resume, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                    <div className="flex items-center gap-3">
                      <FileText className="h-4 w-4 text-blue-600" />
                      <div>
                        <p className="text-sm font-medium">{resume.originalName}</p>
                        <p className="text-xs text-gray-500">
                          {formatFileSize(resume.size)} • {new Date(resume.uploadedAt).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-1">
                      <Button variant="ghost" size="sm">
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Close
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
} 