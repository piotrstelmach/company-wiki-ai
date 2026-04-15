import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  env: {
    BASE_API_URL: process.env.BASE_API_URL || "http://localhost:8080",
  },
};

export default nextConfig;
