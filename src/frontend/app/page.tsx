import { Button } from "@/components/ui/button";

const highlights = [
  { title: "App Router", body: "Next.js 14 app directory with typed routes enabled.", badge: "Next.js" },
  { title: "Tailwind ready", body: "Tailwind + CSS variables wired for quick theming.", badge: "Tailwind" },
  { title: "shadcn/ui", body: "Headless UI primitives; Button example below.", badge: "UI" },
];

export default function HomePage() {
  return (
    <div className="space-y-10">
      <section className="grid gap-8 rounded-xl border bg-card/50 p-8 shadow-sm md:grid-cols-5">
        <div className="md:col-span-3 space-y-4">
          <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Frontend preview</p>
          <h1 className="text-3xl font-semibold leading-tight text-foreground md:text-4xl">
            Next.js app router scaffold for linkinthe.video
          </h1>
          <p className="text-base text-muted-foreground">
            Strict TypeScript, Tailwind, and shadcn/ui are configured. Use this page to validate
            styles, components, and dev server wiring.
          </p>
          <div className="flex flex-wrap gap-3">
            <Button>Primary Button</Button>
            <Button variant="outline">Outline Button</Button>
            <Button variant="ghost">Ghost Button</Button>
          </div>
        </div>
        <div className="md:col-span-2 space-y-3 rounded-lg border bg-background/60 p-4">
          <p className="text-sm font-medium text-muted-foreground">Quick checks</p>
          <ul className="space-y-2 text-sm text-foreground">
            {highlights.map((item) => (
              <li key={item.title} className="flex items-start gap-2 rounded-md border border-border/80 bg-card/60 p-3">
                <span className="rounded-full bg-primary/10 px-2 py-1 text-[11px] font-semibold uppercase tracking-[0.15em] text-primary">
                  {item.badge}
                </span>
                <div>
                  <p className="font-semibold leading-tight">{item.title}</p>
                  <p className="text-muted-foreground">{item.body}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {["Pages", "Components", "Config"].map((label) => (
          <div key={label} className="rounded-xl border bg-card/60 p-6 shadow-sm">
            <p className="text-sm font-semibold text-muted-foreground">{label}</p>
            <p className="mt-2 text-lg font-semibold text-foreground">Ready to extend</p>
            <p className="text-sm text-muted-foreground">
              Start by editing `app/page.tsx`, adding UI in `components/ui`, and updating tokens in
              `tailwind.config.ts`.
            </p>
          </div>
        ))}
      </section>
    </div>
  );
}
