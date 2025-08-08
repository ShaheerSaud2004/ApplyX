'use client'

import { useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { X, Shield, Eye, Lock, Users, Globe, FileText } from 'lucide-react'

interface PrivacyPolicyModalProps {
  isOpen: boolean
  onClose: () => void
}

export function PrivacyPolicyModal({ isOpen, onClose }: PrivacyPolicyModalProps) {
  const [isSpinning, setIsSpinning] = useState(false)

  const handleCatClick = () => {
    setIsSpinning(true)
    setTimeout(() => setIsSpinning(false), 2000) // Stop spinning after 2 seconds
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="fixed left-[50%] top-[50%] z-[99999] grid w-[92vw] max-w-md sm:max-w-2xl md:max-w-3xl translate-x-[-50%] translate-y-[-50%] gap-4 border bg-white p-4 sm:p-6 shadow-2xl duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] rounded-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader className="relative">
          <DialogTitle className="text-xl sm:text-2xl font-bold text-center flex items-center justify-center gap-2">
            <Shield className="h-6 w-6 text-blue-600" />
            Privacy Policy
            <Shield className="h-6 w-6 text-blue-600" />
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Spinning Cat Section */}
          <div className="text-center p-6 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border-2 border-dashed border-purple-200">
            <div className="mb-4">
              <button
                onClick={handleCatClick}
                className={`inline-block transition-transform duration-1000 ${
                  isSpinning ? 'animate-spin' : 'hover:scale-110'
                }`}
                disabled={isSpinning}
              >
                <div className="text-6xl">🐱</div>
              </button>
            </div>
            <p className="text-sm text-gray-600">
              {isSpinning 
                ? "🎵 Cat is spinning to the music! 🎵" 
                : "Click the cat to make it spin! 🎵"
              }
            </p>
          </div>

          {/* Privacy Policy Content */}
          <div className="space-y-6 text-sm">
            <section>
              <h3 className="text-lg font-semibold flex items-center gap-2 mb-3">
                <Eye className="h-5 w-5 text-blue-600" />
                1. Information We Collect
              </h3>
              <p className="text-gray-600 leading-relaxed">
                We collect information you provide directly to us, such as when you create an account, 
                submit job applications, or contact us for support. This may include your name, email address, 
                resume, and LinkedIn credentials.
              </p>
            </section>

            <section>
              <h3 className="text-lg font-semibold flex items-center gap-2 mb-3">
                <Lock className="h-5 w-5 text-green-600" />
                2. How We Use Your Information
              </h3>
              <p className="text-gray-600 leading-relaxed">
                We use the information we collect to provide, maintain, and improve our services, 
                process your job applications, communicate with you, and ensure the security of our platform.
              </p>
            </section>

            <section>
              <h3 className="text-lg font-semibold flex items-center gap-2 mb-3">
                <Users className="h-5 w-5 text-purple-600" />
                3. Information Sharing
              </h3>
              <p className="text-gray-600 leading-relaxed">
                We do not sell, trade, or otherwise transfer your personal information to third parties 
                without your consent, except as described in this policy or as required by law.
              </p>
            </section>

            <section>
              <h3 className="text-lg font-semibold flex items-center gap-2 mb-3">
                <Shield className="h-5 w-5 text-red-600" />
                4. Data Security
              </h3>
              <p className="text-gray-600 leading-relaxed">
                We implement appropriate security measures to protect your personal information against 
                unauthorized access, alteration, disclosure, or destruction.
              </p>
            </section>

            <section>
              <h3 className="text-lg font-semibold flex items-center gap-2 mb-3">
                <Globe className="h-5 w-5 text-orange-600" />
                5. Cookies and Tracking
              </h3>
              <p className="text-gray-600 leading-relaxed">
                We use cookies and similar tracking technologies to enhance your experience on our platform 
                and analyze usage patterns.
              </p>
            </section>

            <section>
              <h3 className="text-lg font-semibold flex items-center gap-2 mb-3">
                <FileText className="h-5 w-5 text-indigo-600" />
                6. Third-Party Services
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Our service may integrate with third-party platforms like LinkedIn. These services have 
                their own privacy policies, and we encourage you to review them.
              </p>
            </section>

            <section>
              <h3 className="text-lg font-semibold flex items-center gap-2 mb-3">
                <Users className="h-5 w-5 text-teal-600" />
                7. Your Rights
              </h3>
              <p className="text-gray-600 leading-relaxed">
                You have the right to access, update, or delete your personal information. You may also 
                opt out of certain communications from us.
              </p>
            </section>

            <section>
              <h3 className="text-lg font-semibold flex items-center gap-2 mb-3">
                <Shield className="h-5 w-5 text-pink-600" />
                8. Children's Privacy
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Our service is not intended for children under 13 years of age. We do not knowingly 
                collect personal information from children under 13.
              </p>
            </section>

            <section>
              <h3 className="text-lg font-semibold flex items-center gap-2 mb-3">
                <FileText className="h-5 w-5 text-cyan-600" />
                9. Changes to This Policy
              </h3>
              <p className="text-gray-600 leading-relaxed">
                We may update this privacy policy from time to time. We will notify you of any changes 
                by posting the new policy on this page.
              </p>
            </section>

            <section>
              <h3 className="text-lg font-semibold flex items-center gap-2 mb-3">
                <Globe className="h-5 w-5 text-blue-600" />
                10. Contact Us
              </h3>
              <p className="text-gray-600 leading-relaxed">
                If you have any questions about this Privacy Policy, please contact us at 
                <a href="mailto:privacy@applyx.com" className="text-blue-600 hover:underline ml-1">
                  privacy@applyx.com
                </a>
              </p>
            </section>

            <div className="mt-8 pt-6 border-t border-gray-200">
              <p className="text-xs text-gray-500 text-center">
                Last updated: {new Date().toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
} 