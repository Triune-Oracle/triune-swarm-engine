/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // Support for both static export and server-side rendering
  trailingSlash: false,
  images: {
    unoptimized: true
  },
  // Ensure compatibility with Vercel
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  // Handle existing files in root
  async rewrites() {
    return [
      {
        source: '/dashboard.html',
        destination: '/dashboard'
      }
    ];
  }
}

module.exports = nextConfig