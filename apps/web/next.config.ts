import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // If an external backend URL is specified, proxy API requests to it.
  // Otherwise, native Next.js API routes in app/api/* serve all endpoints.
  ...(process.env.BACKEND_URL
    ? {
        async rewrites() {
          return [
            {
              source: "/api/:path*",
              destination: `${process.env.BACKEND_URL}/api/:path*`,
            },
          ];
        },
      }
    : {}),
};

export default nextConfig;
