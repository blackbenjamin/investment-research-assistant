/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // This allows the app to work both directly and when proxied from /IRA-app
  // When deployed to Vercel directly, basePath will be empty
  // When proxied from projects.benjaminblack.consulting/IRA-app, assets will work
  assetPrefix: process.env.NEXT_PUBLIC_BASE_PATH || '',
  basePath: process.env.NEXT_PUBLIC_BASE_PATH || '',
}

module.exports = nextConfig
