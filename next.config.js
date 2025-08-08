/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    domains: ['localhost'],
  },
  experimental: {
    serverComponentsExternalPackages: ['pg'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  // Ensure static assets are served correctly
  assetPrefix: process.env.NODE_ENV === 'production' ? undefined : '',
  // Disable static optimization for development
  staticPageGenerationTimeout: 120,
}

module.exports = nextConfig 