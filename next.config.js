/** @type {import('next').NextConfig} */
const nextConfig = {
  // Use standalone output for better Amplify compatibility
  output: 'standalone',
  trailingSlash: true,
  skipTrailingSlashRedirect: true,
  images: {
    unoptimized: true
  },
  experimental: {
    esmExternals: 'loose'
  },
  webpack: (config) => {
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      net: false,
      tls: false,
    };
    return config;
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_REGION: process.env.NEXT_PUBLIC_REGION,
    NEXT_PUBLIC_ENVIRONMENT: process.env.NEXT_PUBLIC_ENVIRONMENT,
  }
}

module.exports = nextConfig
