import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  Outlet,
  Link,
  createRootRouteWithContext,
  useRouter,
  HeadContent,
  Scripts,
} from "@tanstack/react-router";
import { useEffect, type ReactNode } from "react";

import appCss from "../styles.css?url";
import { reportLovableError } from "../lib/lovable-error-reporting";

function NotFoundComponent() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="max-w-md text-center">
        <h1 className="text-7xl font-bold text-foreground">404</h1>
        <h2 className="mt-4 text-xl font-semibold text-foreground">Page not found</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="mt-6">
          <Link
            to="/"
            className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
          >
            Go home
          </Link>
        </div>
      </div>
    </div>
  );
}

function ErrorComponent({ error, reset }: { error: Error; reset: () => void }) {
  console.error(error);
  const router = useRouter();
  useEffect(() => {
    reportLovableError(error, { boundary: "tanstack_root_error_component" });
  }, [error]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="max-w-md text-center">
        <h1 className="text-xl font-semibold tracking-tight text-foreground">
          This page didn't load
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Something went wrong on our end. You can try refreshing or head back home.
        </p>
        <div className="mt-6 flex flex-wrap justify-center gap-2">
          <button
            onClick={() => {
              router.invalidate();
              reset();
            }}
            className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
          >
            Try again
          </button>
          <a
            href="/"
            className="inline-flex items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-accent"
          >
            Go home
          </a>
        </div>
      </div>
    </div>
  );
}

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      // Primary SEO
      { title: 'Support Oluwamayowa "Logo" Adebola — Housing & UK Global Talent Visa' },
      { name: "description", content: "Help a dedicated Nigerian educator recover from a housing disaster and complete his UK Global Talent Visa medicals. Two urgent goals, fully transparent, every naira and dollar tracked publicly." },
      { name: "keywords", content: "Oluwamayowa Adebola, Logo Adebola, fundraiser Nigeria, housing fund, UK Global Talent Visa, donation campaign, Lagos educator, support Logo" },
      { name: "author", content: "Oluwamayowa Adebola" },
      { name: "robots", content: "index, follow" },
      { name: "theme-color", content: "#0e0e0c" },
      // Open Graph
      { property: "og:type", content: "website" },
      { property: "og:url", content: "https://support-logo.vercel.app/" },
      { property: "og:title", content: 'Support Oluwamayowa "Logo" Adebola — Housing & UK Talent Visa' },
      { property: "og:description", content: "Two urgent goals: housing disaster recovery (₦750k) and UK Talent Visa medicals ($1,000). Every donation tracked publicly. Help now." },
      { property: "og:image", content: "https://i.ibb.co/VXZ5Fy2/IMG-20231101-233922-794.jpg" },
      { property: "og:image:alt", content: "Oluwamayowa Logo Adebola smiling at a teaching event" },
      { property: "og:image:width", content: "1200" },
      { property: "og:image:height", content: "630" },
      { property: "og:locale", content: "en_GB" },
      { property: "og:site_name", content: "Support Logo Campaign" },
      // Twitter / X Card
      { name: "twitter:card", content: "summary_large_image" },
      { name: "twitter:site", content: "@LogoAdebola" },
      { name: "twitter:creator", content: "@LogoAdebola" },
      { name: "twitter:title", content: 'Support Oluwamayowa "Logo" Adebola' },
      { name: "twitter:description", content: "Housing fund + UK Talent Visa medicals. Fully transparent campaign. Every naira tracked." },
      { name: "twitter:image", content: "https://i.ibb.co/VXZ5Fy2/IMG-20231101-233922-794.jpg" },
      { name: "twitter:image:alt", content: "Oluwamayowa Logo Adebola at a teaching event" },
      // JSON-LD structured data injected via script tag below
    ],
    links: [
      { rel: "stylesheet", href: appCss },
      { rel: "icon", href: "/favicon.ico", type: "image/x-icon" },
      // Canonical URL — prevents duplicate content penalties
      { rel: "canonical", href: "https://support-logo.vercel.app/" },
      // Preconnect for faster image loads from ibb.co
      { rel: "preconnect", href: "https://i.ibb.co" },
      // Preload the hero image so it doesn't block LCP
      {
        rel: "preload",
        as: "image",
        href: "https://i.ibb.co/VXZ5Fy2/IMG-20231101-233922-794.jpg",
      },
    ],
    scripts: [
      {
        type: "application/ld+json",
        children: JSON.stringify({
          "@context": "https://schema.org",
          "@type": "DonateAction",
          "name": 'Support Oluwamayowa "Logo" Adebola — Housing & UK Talent Visa',
          "description": "Help a dedicated Nigerian educator recover from a housing disaster and complete UK Global Talent Visa medicals.",
          "url": "https://support-logo.vercel.app/",
          "image": "https://i.ibb.co/VXZ5Fy2/IMG-20231101-233922-794.jpg",
          "recipient": {
            "@type": "Person",
            "name": "Oluwamayowa Adebola",
            "alternateName": "Logo Adebola",
            "jobTitle": "Educator & Cybersecurity Tutor",
            "address": { "@type": "PostalAddress", "addressLocality": "Lagos", "addressCountry": "NG" }
          },
          "potentialAction": {
            "@type": "DonateAction",
            "target": "https://support-logo.vercel.app/#donate"
          }
        }),
      },
    ],
  }),
  shellComponent: RootShell,
  component: RootComponent,
  notFoundComponent: NotFoundComponent,
  errorComponent: ErrorComponent,
});

function RootShell({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head>
        <HeadContent />
      </head>
      <body>
        {children}
        <Scripts />
      </body>
    </html>
  );
}

function RootComponent() {
  const { queryClient } = Route.useRouteContext();

  return (
    <QueryClientProvider client={queryClient}>
      {/* Required: nested routes render here. Removing <Outlet /> breaks all child routes. */}
      <Outlet />
    </QueryClientProvider>
  );
}
