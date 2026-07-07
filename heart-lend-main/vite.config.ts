// @lovable.dev/vite-tanstack-config already includes the following — do NOT add them manually
// or the app will break with duplicate plugins:
//   - tanstackStart, viteReact, tailwindcss, tsConfigPaths, nitro (build-only using cloudflare as a default target),
//     componentTagger (dev-only), VITE_* env injection, @ path alias, React/TanStack dedupe,
//     error logger plugins, and sandbox detection (port/host/strictPort).
import { defineConfig } from "@lovable.dev/vite-tanstack-config";

// Allow NITRO_PRESET env var to override the default cloudflare target.
// When deploying to Vercel, set NITRO_PRESET=vercel in the Vercel dashboard
// (Project Settings → Environment Variables) or via vercel.json build.env.
const nitroPreset = process.env.NITRO_PRESET as
  | "vercel"
  | "cloudflare-module"
  | undefined;

export default defineConfig({
  tanstackStart: {
    server: { entry: "server" },
  },
  ...(nitroPreset
    ? {
        nitro: {
          preset: nitroPreset,
        },
      }
    : {}),
});
