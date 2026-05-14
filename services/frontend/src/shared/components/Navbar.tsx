import { Trans } from '@lingui/react/macro'
import { Image } from '@unpic/react'
import LanguageSwitcher from './LanguageSwitcher'
import ThemeSwitcher from './ThemeSwitcher'
import { LocalizedLink } from './LocalizedLink'

export function Navbar() {
    return (
        <nav className="sticky top-0 z-10 border-b border-border bg-background/80 backdrop-blur">
            <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
                <LocalizedLink to="/" className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center overflow-hidden rounded-xl bg-primary/10">
                        <Image
                            src="/tanstack-circle-logo.png"
                            layout="constrained"
                            width={40}
                            height={40}
                            alt="TanStack Logo"
                        />
                    </div>
                    <div>
                        <p className="text-sm font-semibold">
                            <Trans>TanStack Start</Trans>
                        </p>
                        <p className="text-xs text-muted-foreground">
                            <Trans>Shadcn-inspired navbar</Trans>
                        </p>
                    </div>
                </LocalizedLink>

                <div className="flex items-center gap-4">
                    <ThemeSwitcher />
                    <LanguageSwitcher />
                    <LocalizedLink
                        to="/about"
                        className="text-sm font-medium text-muted-foreground transition hover:text-foreground"
                    >
                        <Trans>About</Trans>
                    </LocalizedLink>
                    <LocalizedLink
                        to="/todos"
                        className="text-sm font-medium text-muted-foreground transition hover:text-foreground"
                    >
                        <Trans>Todos</Trans>
                    </LocalizedLink>
                    <a
                        href="https://github.com/tanstack/start"
                        target="_blank"
                        rel="noreferrer"
                        className="text-sm font-medium text-muted-foreground transition hover:text-foreground"
                    >
                        <Trans>GitHub</Trans>
                    </a>
                </div>
            </div>
        </nav>
    )
}
