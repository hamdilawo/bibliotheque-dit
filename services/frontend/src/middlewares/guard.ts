import { createMiddleware } from "@tanstack/react-start";
import { redirect } from "@tanstack/react-router";

const AUTH_COOKIE = "auth_token";
const LOGIN_PATH = "/login";

/**
 * Auth guard middleware — protect routes that require authentication.
 *
 * Usage in a route file:
 *   server: { middleware: [guardMiddleware] }
 *
 * Customize AUTH_COOKIE and LOGIN_PATH above to match your auth strategy.
 */
export const guardMiddleware = createMiddleware().server(
  async ({ next, request }) => {
    const cookies = request.headers.get("cookie") ?? "";
    const hasToken = cookies
      .split(";")
      .some((c) => c.trim().startsWith(`${AUTH_COOKIE}=`));

    if (!hasToken) {
      const url = new URL(request.url);
      throw redirect({
        href: `${LOGIN_PATH}?redirect=${encodeURIComponent(url.pathname)}`,
        statusCode: 307,
      });
    }

    return next();
  },
);
