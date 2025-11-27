import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "linkinthe.video frontend",
  description: "Next.js app router UI scaffolded with Tailwind and shadcn/ui.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="flex min-h-screen flex-col">
          <header className="border-b bg-card/60 backdrop-blur">
            <div className="container-page flex items-center justify-between gap-4 py-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-sm font-semibold uppercase text-primary">
                  li
                </div>
                <div>
                  <p className="text-xs font-medium uppercase tracking-[0.2em] text-muted-foreground">linkinthe.video</p>
                  <p className="text-lg font-semibold leading-tight text-foreground">Creator landing hub</p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <span className="h-2 w-2 rounded-full bg-emerald-500" aria-hidden />
                <span>App Router ready</span>
              </div>
            </div>
          </header>

          <main className="container-page flex-1 py-10">{children}</main>

          <footer className="border-t bg-card/60">
            <div className="container-page py-4 text-sm text-muted-foreground">
              Next.js 14 + Tailwind + shadcn/ui starter for linkinthe.video
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
