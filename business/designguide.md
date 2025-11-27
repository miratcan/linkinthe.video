# linkinthe.video – Design Guide

This document is the single source of truth for all visual decisions.
Every pixel must serve **[ZEN-EFFORTLESS]** – the experience must feel instant and magical.

---

## 1. Core Philosophy

We are clean, fast, and functional.
Think: Linear + Vercel + Stripe's clarity.

No decoration for decoration's sake.
Whitespace is our most powerful tool.
Beauty comes from perfect typography, generous spacing, and clear hierarchy.

If something doesn't make the flow faster or clearer, kill it.

---

## 2. Tech Stack

**Framework:** Tailwind CSS + shadcn/ui

**Why this combo:**
- Tailwind: Utility-first, fast iteration, LLM-friendly
- shadcn/ui: Accessible components, copy-paste model, full control
- Both are the most LLM-friendly UI stack (important for AI-assisted development)

**Rules:**
- Use Tailwind utilities, not custom CSS
- Use shadcn/ui components as base, customize as needed
- All colors via Tailwind config / CSS variables
- No inline styles

---

## 3. Color Palette

### Base (Light Mode)
- **Background:** `bg-white` / `#FFFFFF`
- **Surface:** `bg-gray-50` / `#F9FAFB` (cards, inputs)
- **Border:** `border-gray-200` / `#E5E7EB`

### Text
- **Primary:** `text-gray-900` / `#111827`
- **Secondary:** `text-gray-600` / `#4B5563`
- **Muted:** `text-gray-400` / `#9CA3AF`

### Accent
- **Primary accent:** `bg-blue-600` / `#2563EB` (buttons, links)
- **Hover:** `bg-blue-700` / `#1D4ED8`
- **Success:** `text-green-600` / `#16A34A`
- **Error:** `text-red-600` / `#DC2626`

### Dark Mode (planned)
Will be added later using Tailwind's dark: prefix.
Invert to dark background, light text, same accent structure.

---

## 4. Typography

**Font:** System stack (Tailwind default)
```
font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
```

**Sizes:**
- Body: `text-base` (16px)
- Small: `text-sm` (14px)
- Headings: `text-xl` to `text-3xl`
- Hero: `text-4xl` to `text-5xl`

**Weights:**
- Normal: `font-normal` (400)
- Medium: `font-medium` (500)
- Semibold: `font-semibold` (600)

**Line height:** Tailwind defaults (1.5 for body, tighter for headings)

---

## 5. Spacing

Use Tailwind's spacing scale. Common values:
- `p-4` / `m-4` (16px) – default padding
- `p-6` / `m-6` (24px) – card padding
- `gap-4` (16px) – between items
- `space-y-8` (32px) – between sections

**Max width:**
- Content: `max-w-3xl` (768px)
- Wide content: `max-w-5xl` (1024px)
- Full page: `max-w-7xl` (1280px)

---

## 6. Border Radius

- Default: `rounded-lg` (8px)
- Buttons: `rounded-md` (6px)
- Full round: `rounded-full` (avatars, pills)

Consistent 8px radius everywhere. No 4px, no 12px.

---

## 7. Shadows

Minimal shadows. Flat by default.

- Cards: `shadow-sm` on hover only
- Modals: `shadow-lg`
- No shadows on buttons

---

## 8. Component Guidelines

### Buttons (shadcn/ui)
- Primary: `bg-blue-600 text-white hover:bg-blue-700`
- Secondary: `bg-gray-100 text-gray-900 hover:bg-gray-200`
- Ghost: `hover:bg-gray-100`
- Height: `h-10` minimum (touch-friendly)

### Cards
- Background: `bg-white` or `bg-gray-50`
- Border: `border border-gray-200`
- Padding: `p-6`
- Radius: `rounded-lg`

### Forms (shadcn/ui)
- Input height: `h-10`
- Focus ring: `ring-2 ring-blue-500`
- Error state: `border-red-500`

### Tables
- Header: `bg-gray-50 text-gray-600 text-sm font-medium`
- Rows: `border-b border-gray-100`
- Hover: `hover:bg-gray-50`

### Progress Bar
- Track: `bg-gray-200 rounded-full`
- Fill: `bg-blue-600 rounded-full`
- Height: `h-2`

---

## 9. Public Product Page

The most important screen. Must look like something Sarah is proud to share.

**Layout:**
1. Header: Video title + creator name
2. Product list: Icon + name + description + link button
3. Footer: "Powered by linkinthe.video" (subtle)

**Style:**
- Clean, generous whitespace
- Product images: `rounded-lg`, consistent size
- Link buttons: Subtle, not aggressive
- Mobile-first: Thumb-friendly, readable

---

## 10. Checklist (before every PR)

- [ ] Uses Tailwind utilities only (no custom CSS unless necessary)
- [ ] Uses shadcn/ui components where applicable
- [ ] Colors from defined palette
- [ ] Consistent 8px radius
- [ ] Mobile responsive
- [ ] Touch-friendly (min 44px tap targets)
- [ ] No unnecessary animations
- [ ] Feels fast and effortless

---

## 11. Anti-Patterns (forbidden)

- No custom CSS when Tailwind works
- No !important
- No inline styles
- No arbitrary values (`w-[347px]`) — use scale
- No heavy animations (fade-in max 150ms if needed)
- No gradients unless intentional
- No decorative elements that don't serve function
