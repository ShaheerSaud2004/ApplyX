'use client'

import { useState, useEffect } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { X, FileText } from 'lucide-react'

interface TermsOfServiceModalProps {
  isOpen: boolean
  onClose: () => void
}

export function TermsOfServiceModal({ isOpen, onClose }: TermsOfServiceModalProps) {
  const [showCat, setShowCat] = useState(false)
  const [timeLeft, setTimeLeft] = useState(5)

  useEffect(() => {
    if (isOpen) {
      setShowCat(true)
      setTimeLeft(5)
      
      const timer = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            setShowCat(false)
            clearInterval(timer)
            return 0
          }
          return prev - 1
        })
      }, 1000)

      return () => clearInterval(timer)
    }
  }, [isOpen])

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="fixed left-[50%] top-[50%] z-[99999] grid w-[92vw] max-w-md sm:max-w-xl md:max-w-2xl translate-x-[-50%] translate-y-[-50%] gap-4 border bg-white p-4 sm:p-6 shadow-2xl duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] rounded-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader className="relative">
          <DialogTitle className="text-xl sm:text-2xl font-bold text-center flex items-center justify-center gap-2">
            <FileText className="h-6 w-6 text-blue-600" />
            Terms of Service
            <FileText className="h-6 w-6 text-blue-600" />
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Cat Animation Section */}
          {showCat && (
            <div className="text-center p-8 bg-gradient-to-r from-orange-50 to-yellow-50 rounded-lg border-2 border-dashed border-orange-200">
              <div className="mb-4">
                <div className="text-8xl animate-bounce">🐱</div>
              </div>
              <p className="text-lg font-medium text-gray-700 mb-2">
                Meow! Here's your cat! 🎵
              </p>
              <p className="text-sm text-gray-600">
                Disappearing in {timeLeft} seconds...
              </p>
            </div>
          )}

          {/* Terms of Service Content */}
          {!showCat && (
            <div className="space-y-6 text-sm">
              <section>
                <h3 className="text-lg font-semibold mb-3">1. Acceptance of Terms</h3>
                <p className="text-gray-600 leading-relaxed">
                  By accessing and using ApplyX, you accept and agree to be bound by the terms and provision of this agreement.
                </p>
              </section>

              <section>
                <h3 className="text-lg font-semibold mb-3">2. Use License</h3>
                <p className="text-gray-600 leading-relaxed">
                  Permission is granted to temporarily use ApplyX for personal, non-commercial transitory viewing only.
                </p>
              </section>

              <section>
                <h3 className="text-lg font-semibold mb-3">3. Disclaimer</h3>
                <p className="text-gray-600 leading-relaxed">
                  The materials on ApplyX are provided on an 'as is' basis. ApplyX makes no warranties, expressed or implied.
                </p>
              </section>

              <section>
                <h3 className="text-lg font-semibold mb-3">4. Limitations</h3>
                <p className="text-gray-600 leading-relaxed">
                  In no event shall ApplyX or its suppliers be liable for any damages arising out of the use or inability to use the materials.
                </p>
              </section>

              <section>
                <h3 className="text-lg font-semibold mb-3">5. Revisions and Errata</h3>
                <p className="text-gray-600 leading-relaxed">
                  The materials appearing on ApplyX could include technical, typographical, or photographic errors.
                </p>
              </section>

              <section>
                <h3 className="text-lg font-semibold mb-3">6. Links</h3>
                <p className="text-gray-600 leading-relaxed">
                  ApplyX has not reviewed all of the sites linked to its website and is not responsible for the contents of any such linked site.
                </p>
              </section>

              <section>
                <h3 className="text-lg font-semibold mb-3">7. Site Terms of Use Modifications</h3>
                <p className="text-gray-600 leading-relaxed">
                  ApplyX may revise these terms of use for its website at any time without notice.
                </p>
              </section>

              <section>
                <h3 className="text-lg font-semibold mb-3">8. Governing Law</h3>
                <p className="text-gray-600 leading-relaxed">
                  These terms and conditions are governed by and construed in accordance with the laws.
                </p>
              </section>

              <div className="mt-8 pt-6 border-t border-gray-200">
                <p className="text-xs text-gray-500 text-center">
                  Last updated: {new Date().toLocaleDateString()}
                </p>
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
} 