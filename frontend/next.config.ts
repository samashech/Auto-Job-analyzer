import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  devIndicators: false,
  // @ts-ignore
  turbopack: {
    root: __dirname,
  },
};

export default nextConfig;
