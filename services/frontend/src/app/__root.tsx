import {
  HeadContent,
  Scripts,
  createRootRouteWithContext,
  useLocation,
} from "@tanstack/react-router";
import { useMemo } from "react";
import { TanStackRouterDevtoolsPanel } from "@tanstack/react-router-devtools";
import { TanStackDevtools } from "@tanstack/react-devtools";

import { setupI18n } from "@lingui/core";
import { I18nProvider } from "@lingui/react";
import { messages as enMessages } from "../locales/en/messages";
import { messages as frMessages } from "../locales/fr/messages";

import TanStackQueryDevtools from "../shared/providers/tanstack-query/devtools";

import appCss from "../styles.css?url";

import type { QueryClient } from "@tanstack/react-query";
import { i18nMiddleware } from "@/middlewares/i18n";
import { ToasterProvider } from "@/shared/providers/toaster-provider";
import { DEFAULT_LOCALE, getLocaleFromPath } from "@/lib/i18n-utils";
import { ThemeProvider } from "next-themes";

interface MyRouterContext {
  queryClient: QueryClient;
}

const ALL_MESSAGES = {
  en: enMessages,
  fr: frMessages,
};

const APP_URL = import.meta.env.VITE_APP_URL ?? "https://react-app-starter.com";
const APP_NAME = import.meta.env.VITE_APP_NAME ?? "React App Starter";

export const Route = createRootRouteWithContext<MyRouterContext>()({
  head: (): { meta: any[]; links: any[] } => ({
      meta: [
        { charSet: "utf-8" },
        {
          name: "viewport",
          content: "width=device-width, initial-scale=1, maximum-scale=5",
        },

        // Title & Description
        { title: `${APP_NAME} - Modern Full-stack Template` },
        {
          name: "description",
          content:
            "Un starter pack ultra-rapide avec TanStack Start, Bun et Tailwind CSS. Construit pour la performance, la sécurité et une DX optimale.",
        },
        {
          name: "keywords",
          content:
            "tanstack start, bun, tailwind css, react, typescript, starter template, full-stack, vite, shadcn, lingui, i18n",
        },

        // Robots
        {
          name: "robots",
          content:
            "index, follow, max-video-preview:-1, max-image-preview:large, max-snippet:-1",
        },
        {
          name: "googlebot",
          content:
            "index, follow, max-video-preview:-1, max-image-preview:large, max-snippet:-1",
        },
        { name: "bingbot", content: "index, follow" },

        // Author
        { name: "author", content: APP_NAME },
        { name: "publisher", content: APP_NAME },
        { name: "creator", content: APP_NAME },

        // Language
        { httpEquiv: "content-language", content: "fr-FR" },

        // Open Graph
        { property: "og:title", content: `${APP_NAME} - Modern Full-stack Template` },
        {
          property: "og:description",
          content:
            "Un starter pack ultra-rapide avec TanStack Start, Bun et Tailwind CSS. Construit pour la performance, la sécurité et une DX optimale.",
        },
        { property: "og:url", content: APP_URL },
        { property: "og:image", content: `${APP_URL}/logo512.png` },
        { property: "og:image:secure_url", content: `${APP_URL}/logo512.png` },
        { property: "og:image:width", content: "1200" },
        { property: "og:image:height", content: "630" },
        { property: "og:image:alt", content: `${APP_NAME} - Modern Full-stack Template` },
        { property: "og:image:type", content: "image/png" },
        { property: "og:type", content: "website" },
        { property: "og:site_name", content: APP_NAME },
        { property: "og:locale", content: "fr_FR" },
        { property: "og:locale:alternate", content: "en_US" },

        // Twitter Card
        { name: "twitter:card", content: "summary_large_image" },
        { name: "twitter:site", content: "@yourhandle" },
        { name: "twitter:creator", content: "@yourhandle" },
        { name: "twitter:title", content: `${APP_NAME} - Modern Full-stack Template` },
        {
          name: "twitter:description",
          content:
            "Un starter pack ultra-rapide avec TanStack Start, Bun et Tailwind CSS. Construit pour la performance, la sécurité et une DX optimale.",
        },
        { name: "twitter:image", content: `${APP_URL}/logo512.png` },
        { name: "twitter:image:alt", content: `${APP_NAME} - Modern Full-stack Template` },
        { name: "twitter:url", content: APP_URL },
        { name: "twitter:domain", content: "react-app-starter.com" },

        // Theme color
        { name: "theme-color", content: "#000000" },
        { name: "msapplication-TileColor", content: "#000000" },
        { name: "msapplication-navbutton-color", content: "#000000" },

        // Apple / Mobile
        { name: "mobile-web-app-capable", content: "yes" },
        { name: "apple-mobile-web-app-status-bar-style", content: "black-translucent" },
        { name: "apple-mobile-web-app-title", content: APP_NAME },
        { name: "format-detection", content: "telephone=no" },

        // Google Verification (replace with your real code)
        { name: "google-site-verification", content: "YOUR_GOOGLE_VERIFICATION_CODE" },

        // Additional SEO
        { name: "rating", content: "general" },
        { name: "distribution", content: "global" },
        { name: "revisit-after", content: "7 days" },
        { name: "coverage", content: "Worldwide" },
        { name: "HandheldFriendly", content: "True" },
        { name: "MobileOptimized", content: "320" },

        // Business
        { name: "application-name", content: APP_NAME },
        { name: "copyright", content: `${APP_NAME} © ${new Date().getFullYear()}` },

        // Security
        { httpEquiv: "X-UA-Compatible", content: "IE=edge" },
        { httpEquiv: "X-Content-Type-Options", content: "nosniff" },
      ],

      links: [
        {
          rel: "preload",
          href: appCss,
          as: "style",
          fetchpriority: "high",
        },
        { rel: "stylesheet", href: appCss },
        { rel: "preconnect", href: "https://fonts.googleapis.com" },
        { rel: "preconnect", href: "https://fonts.gstatic.com", crossOrigin: "anonymous" },
        { rel: "stylesheet", href: "https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" },

        // Canonical + hreflang (overridden per-page for locale-specific URLs)
        { rel: "canonical", href: APP_URL },
        { rel: "alternate", hrefLang: "fr", href: `${APP_URL}/fr` },
        { rel: "alternate", hrefLang: "en", href: `${APP_URL}/en` },
        { rel: "alternate", hrefLang: "x-default", href: `${APP_URL}/${DEFAULT_LOCALE}` },

        // Favicons
        { rel: "icon", type: "image/x-icon", href: "/favicon.ico" },
        { rel: "icon", type: "image/png", sizes: "32x32", href: "/favicon-32x32.png" },
        { rel: "icon", type: "image/png", sizes: "16x16", href: "/favicon-16x16.png" },
        { rel: "icon", type: "image/svg+xml", href: "/favicon.svg" },
        { rel: "apple-touch-icon", sizes: "180x180", href: "/apple-touch-icon.png" },
        { rel: "apple-touch-icon", sizes: "152x152", href: "/apple-touch-icon-152x152.png" },
        { rel: "apple-touch-icon", sizes: "120x120", href: "/apple-touch-icon-120x120.png" },

        // Manifest & Safari mask icon
        { rel: "manifest", href: "/site.webmanifest" },
        { rel: "mask-icon", href: "/safari-pinned-tab.svg", color: "#000000" },

        // DNS Prefetch & Preconnect
        { rel: "dns-prefetch", href: "https://fonts.googleapis.com" },
        { rel: "preconnect", href: "https://fonts.googleapis.com" },
        {
          rel: "preconnect",
          href: "https://fonts.gstatic.com",
          crossOrigin: "anonymous",
        },
        { rel: "dns-prefetch", href: "https://www.google-analytics.com" },
        { rel: "preconnect", href: "https://www.googletagmanager.com" },
      ],
  }),
  server: {
    middleware: [i18nMiddleware],
  },
  shellComponent: RootDocument,
});

function RootDocument({ children }: { children: React.ReactNode }) {
  const pathname = useLocation({
    select: (location) => location.pathname,
  });

  const locale = getLocaleFromPath(pathname) || DEFAULT_LOCALE;

  const i18nInstance = useMemo(() => {
    return setupI18n({
      locale,
      messages: ALL_MESSAGES,
    });
  }, [locale]);

  return (
    <html lang={locale} suppressHydrationWarning>
      <head>
        <HeadContent />
        {/* Anti-FOUC script for next-themes */}
        <script
          dangerouslySetInnerHTML={{
            __html: `(function(){try{var t=localStorage.getItem('theme')||'system';if(t==='system'){t=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}document.documentElement.classList.add(t);}catch(e){}})();`,
          }}
        />
      </head>
      <body>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <I18nProvider i18n={i18nInstance}>
            {children}
            <ToasterProvider />
            <TanStackDevtools
              config={{ position: "bottom-right" }}
              plugins={[
                { name: "Tanstack Router", render: <TanStackRouterDevtoolsPanel /> },
                TanStackQueryDevtools,
              ]}
            />
            <Scripts />
          </I18nProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
