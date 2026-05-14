import { defineConfig, loadEnv } from "vite";
import { devtools } from "@tanstack/devtools-vite";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import viteReact from "@vitejs/plugin-react";
import viteTsConfigPaths from "vite-tsconfig-paths";
import tailwindcss from "@tailwindcss/vite";
import { lingui } from "@lingui/vite-plugin";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  const proxyConfig = {
    "/api/users": {
      target: env.VITE_USERS_API_URL,
      changeOrigin: true,
      rewrite: (path: string) => path.replace(/^\/api\/users/, ""),
    },
    "/api/books": {
      target: env.VITE_BOOKS_API_URL,
      changeOrigin: true,
      rewrite: (path: string) => path.replace(/^\/api\/books/, ""),
    },
    "/api/loans": {
      target: env.VITE_LOANS_API_URL,
      changeOrigin: true,
      rewrite: (path: string) => path.replace(/^\/api\/loans/, ""),
    },
    "/api/recommendations": {
      target: env.VITE_RECOMMENDATION_API_URL,
      changeOrigin: true,
      rewrite: (path: string) => path.replace(/^\/api\/recommendations/, ""),
    },
  };

  return {
    plugins: [
      devtools({
        eventBusConfig: {
          port: 42071,
        },
      }),
      viteTsConfigPaths({
        projects: ["./tsconfig.json"],
      }),
      tanstackStart({
        router: {
          routesDirectory: "app",
          routeFileIgnorePattern: "\\.ts$",
        },
      }),
      viteReact({
        babel: {
          plugins: ["@lingui/babel-plugin-lingui-macro"],
        },
      }),
      tailwindcss(),
      lingui(),
    ],
    server: {
      proxy: proxyConfig,
      allowedHosts: ["127.0.0.1", "0.0.0.0", "localhost"],
    },
  };
});
