# Documentation Rules – linkinthe.video

## The One Rule: DRY or Die

**Never repeat information across documents.**

This is not a suggestion. This is survival.

Solo founder → every duplicated line = double maintenance → technical debt → chaos.

---

## How to Write Docs

### Single Source of Truth

Every piece of information lives in **exactly one place**.

**Wrong:**
- README says "Philosophy: effortless monetization"
- zen.md says the same thing
- Now you update zen.md, forget README, docs diverge, confusion.

**Right:**
- README: "See [Philosophy](business/zen.md)"
- zen.md: Full philosophy
- One update, everywhere updated.

### Link, Don't Repeat

If you need to reference something:
- **Link to it** (e.g., "See [Tech Stack](techstack.md)")
- **Don't copy-paste** it

### When to Create a New Doc

Only when:
1. It's a distinct topic
2. Other docs will reference it
3. It will be maintained independently

Don't create docs for one-time notes. Use comments or inline.

---

## Document Index (Single Source)

- **index.md** → This file (documentation meta-rules)
- **zen.md** → Philosophy, core principles, decision framework
- **personas.md** → Target users, pain points, value prop
- **brandvoice.md** → Tone, language, messaging
- **designguide.md** → Visual system, colors, typography, components
- **brief.md** → Business decisions, GTM, pricing
- **techbrief.md** → Technical decisions, data models, pipeline, tech stack

If you're adding info and don't know where → check this index first.

---

## Maintenance Protocol

Before writing anything:

1. **Does this exist elsewhere?** → Link to it
2. **Is this a new topic?** → Create new doc, add to index
3. **Is this a detail of existing topic?** → Add to that doc

Before updating anything:

1. **Is this info duplicated?** → Find all copies, delete them, keep one
2. **Will this change affect other docs?** → Update links only, not content

---

## The Cost of Duplication

Duplicate one line → maintain two places → forget one → docs lie → decisions based on wrong info → product fails.

**DRY is not pedantic. DRY is survival.**
