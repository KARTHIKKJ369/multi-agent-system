import type { NextConfig } from "next";

const backendUrl =
  process.env.BACKEND_INTERNAL_URL ||
  process.env.API_URL ||
  "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: "/api/py/:path*",
        destination: `${backendUrl}/api/v1/:path*`,
      },
      {
        source: "/api/health",
        destination: `${backendUrl}/health`,
      },
    ];
  },
};

export default nextConfig;

