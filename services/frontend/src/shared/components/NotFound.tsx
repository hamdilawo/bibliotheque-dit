import { useRouter } from "@tanstack/react-router";
import { Trans } from "@lingui/react/macro";

export default function NotFound() {
  const router = useRouter();

  return (
    <div className="min-h-screen bg-background text-foreground flex items-center justify-center px-6 py-10">
      <div className="relative w-full max-w-xl overflow-hidden rounded-3xl border border-border/70 bg-card/80 p-10 text-center shadow-2xl backdrop-blur fade-pop">
        <div className="pointer-events-none absolute -left-16 -top-20 h-56 w-56 rounded-full bg-primary/10 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-24 -right-10 h-64 w-64 rounded-full bg-secondary/25 blur-3xl" />
        <div className="relative z-10 space-y-4">
          <p className="text-xs uppercase tracking-[0.3em] text-muted-foreground">
            Oops
          </p>
          <h1 className="text-5xl font-semibold tracking-tight sm:text-6xl">
            404
          </h1>
          <p className="text-base text-muted-foreground sm:text-lg">
            <Trans>
              The page you are looking for has drifted off course. Let&apos;s
              guide you back home.
            </Trans>
          </p>
          <div className="mt-6 flex justify-center gap-3">
            <button
              onClick={() => router.history.back()}
              className="rounded-full border border-border bg-background px-4 py-2 text-sm font-medium text-foreground shadow-sm hover:bg-accent transition-colors"
            >
              <Trans>Go back</Trans>
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
