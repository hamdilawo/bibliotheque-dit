import { useRouter } from "@tanstack/react-router";
import type { ErrorComponentProps } from "@tanstack/react-router";
import { Trans } from "@lingui/react/macro";

export default function ErrorBoundary({ error, reset }: ErrorComponentProps) {
  const router = useRouter();
  const isDev = import.meta.env.DEV;

  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center px-6 py-10">
      <div className="relative w-full max-w-xl overflow-hidden rounded-3xl border border-border/70 bg-card/80 p-10 text-center shadow-2xl backdrop-blur fade-pop">
        <div className="pointer-events-none absolute -left-16 -top-20 h-56 w-56 rounded-full bg-destructive/10 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-24 -right-10 h-64 w-64 rounded-full bg-secondary/25 blur-3xl" />

        <div className="relative z-10 space-y-4">
          <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground">
            <Trans>Error</Trans>
          </p>
          <h1 className="text-5xl font-semibold tracking-tight sm:text-6xl">
            500
          </h1>
          <p className="text-base text-muted-foreground sm:text-lg">
            <Trans>Something went wrong. Our team has been notified.</Trans>
          </p>

          {isDev && error && (
            <pre className="mt-4 rounded-xl bg-muted px-4 py-3 text-left text-xs text-destructive overflow-auto max-h-40">
              {error.message}
              {error.stack && `\n\n${error.stack}`}
            </pre>
          )}

          <div className="mt-6 flex justify-center gap-3">
            <button
              onClick={() => reset()}
              className="rounded-full border border-border bg-background px-4 py-2 text-sm font-medium text-foreground shadow-sm hover:bg-accent transition-colors"
            >
              <Trans>Try again</Trans>
            </button>
            <button
              onClick={() => router.navigate({ href: "/" })}
              className="rounded-full border border-primary bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow-sm hover:opacity-90 transition-opacity"
            >
              <Trans>Back to home</Trans>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
