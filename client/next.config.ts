import { execSync } from "node:child_process";
import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

function readGitValue(command: string, fallback = "unknown"): string {
  try {
    return execSync(command, { encoding: "utf8" }).trim() || fallback;
  } catch {
    return fallback;
  }
}

const gitBranch =
  process.env.VERCEL_GIT_COMMIT_REF ??
  process.env.GIT_BRANCH ??
  readGitValue("git rev-parse --abbrev-ref HEAD");

const gitCommit =
  process.env.VERCEL_GIT_COMMIT_SHA ??
  process.env.GIT_COMMIT ??
  readGitValue("git rev-parse HEAD");

const nextConfig: NextConfig = {
  output: "standalone",
  env: {
    NEXT_PUBLIC_APP_GIT_BRANCH: gitBranch,
    NEXT_PUBLIC_APP_GIT_COMMIT: gitCommit,
  },
};

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

export default withNextIntl(nextConfig);
