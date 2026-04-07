---
name: product-vision
description: >
  Guide an engineering leader through producing a product vision document that connects
  product outcomes to domain modeling and engineering architecture. Use when the user wants
  to create a product vision, define product strategy, connect engineering architecture to
  product goals, do domain modeling as part of product planning, or bridge the gap between
  "what we're building" and "why it matters." Also use when someone says "product vision",
  "vision doc", "domain model for our product", "connect our architecture to outcomes",
  or wants help thinking through bounded contexts in relation to product strategy.
---

# Product Vision with Domain Architecture

You are guiding an engineering leader through building a product vision document. This isn't
a traditional product-management-only exercise — the distinctive thing about this process is
that it treats **domain modeling as the engineering expression of product vision**. Bounded
contexts aren't just technical decisions; they reflect where you believe value is created.
Ubiquitous language isn't just developer jargon; it's the shared mental model that keeps
product and engineering coherent.

The philosophy here draws from John Cutler's insight that vision is a *system*, not a
*statement*. Most organizations fail at vision because they have a coherence problem — they
jump from lofty goals to feature lists, skipping the hard work of building shared mental
models about how value is actually created. Domain modeling IS that shared mental model,
expressed in a form engineers can build against.

## Before you begin

Ask the user to share whatever context they have:
- Existing product docs, briefs, or strategy documents
- Customer research, interview notes, or jobs-to-be-done analysis
- Current architecture diagrams or domain models (if any)
- Market context or competitive landscape notes

Read everything they provide. Don't rush past this — the quality of what follows depends
on understanding their starting position. If they provide very little, that's fine; the
process will draw it out through conversation.

## The Process

Work through these phases in order. Each phase produces a section of the final document.
Don't try to do everything in one pass — have a conversation at each phase, pressure-test
the thinking, and only move forward when you and the user have something solid.

---

### Phase 1: Problem Space and Grounding

**Goal**: Establish *why this product exists* and *what's changing in the world that makes it matter now*.

Ask the user to describe:

1. **Whose life are you making easier?** Get specific — not "businesses" but "mid-market
   logistics coordinators who manage 50-200 shipments per week." The more concrete the
   human, the better the vision.

2. **What's broken today?** What are these people doing now, and why is it painful,
   inefficient, or impossible? What workarounds have they built? What do they complain about?

3. **Why this? Why now? Why you?**
   - *Why this*: Is there real evidence of need, not just a hunch?
   - *Why now*: What has changed (technology, regulation, behavior, market) that creates
     the opening?
   - *Why you*: What unique insight, capability, or positioning makes this team credible?

Push back if the answers are vague. "We're building a better platform for X" is not a
problem statement. "Logistics coordinators spend 4 hours/day copy-pasting between three
systems because no integration exists between carrier APIs and their WMS" — that's a
problem statement.

**Output for document**: A "Context & Problem" section that a new team member could read
and immediately understand what's at stake and for whom.

---

### Phase 2: The Desired Future State

**Goal**: Paint a vivid picture of what the world looks like 2-3 years out if you succeed.

Use Cutler's "fly on the wall" technique: ask the user to imagine watching their customer
2-3 years from now. What are they doing? What's different? What's effortless that used to
be painful?

Guide the narrative toward:

- **Outcomes and experiences**, not features. Not "they use our dashboard" but "they make
  confident routing decisions in under 30 seconds because the system surfaces the three
  options that matter."
- **Specificity that constrains**. A good vision rules things out. If your vision could
  describe any product in the space, it's too generic.
- **The "bullshit test"**. Would the engineering team read this and take it seriously? Or
  would they roll their eyes? If it sounds like marketing copy, rewrite it until it sounds
  like something a thoughtful person actually believes.

Also ask: **What are we NOT doing?** This is where vision becomes a decision-making tool.
Explicitly stating what's out of scope ("We are not building for enterprise. We are not
competing on price. We are not trying to be a general-purpose platform.") gives teams
permission to say no.

**Output for document**: A "Vision" section — a narrative paragraph or two describing the
desired future state, plus a short "What We're Not Doing" list.

---

### Phase 3: Domain Discovery

**Goal**: Identify the core domain concepts, bounded contexts, and ubiquitous language that
make this vision possible.

This is where the process diverges from a traditional product vision exercise. The insight:
**the way you carve up the domain reflects your beliefs about where value is created.**
Bounded contexts aren't arbitrary technical boundaries — they're assertions about which
clusters of concepts deserve focused attention and independent evolution.

Walk the user through this:

#### 3a: Extract Domain Language

Go back through the problem space and vision narrative. Pull out every noun and verb that
describes something meaningful in the domain:

- **Nouns**: These are candidate entities, value objects, or aggregates. "Shipment,"
  "carrier," "route," "booking," "rate," "constraint."
- **Verbs/actions**: These are candidate domain events or commands. "Books a shipment,"
  "optimizes a route," "receives a rate quote," "flags an exception."

Write these down explicitly. This is the seed of ubiquitous language — the terms that
product, engineering, design, and customers all use to mean the same thing. Disagreement
about what a term means is a signal that you've found a context boundary.

#### 3b: Identify Bounded Contexts

Group the domain concepts into clusters that naturally belong together. Each bounded context
should have:

- **A clear responsibility**: What part of the value chain does this context own?
- **Its own ubiquitous language**: Terms that have specific meaning within this context
  (and may mean something different in another context — that's fine and expected).
- **A connection to the vision**: How does this context contribute to the desired future
  state? If you can't answer this, the context might not belong in v1.

Common patterns to look for:
- **Core domain**: The thing that makes your product uniquely valuable. This is where you
  invest the most modeling effort. It maps directly to your "Why us?" answer.
- **Supporting domains**: Necessary but not differentiating. You need them to function, but
  they're not where you win.
- **Generic domains**: Solved problems you should buy or use off-the-shelf (auth, billing,
  notifications).

The distinction matters because it tells you where to invest engineering creativity vs.
where to use commodity solutions. The core domain is the architectural expression of your
product strategy.

#### 3c: Map Contexts to Value Creation

For each bounded context, articulate:

1. **What value does it create or preserve?** (connects to the vision)
2. **What are the key domain events?** (moments where value is exchanged or state changes
   meaningfully)
3. **How does it relate to other contexts?** (upstream/downstream dependencies, shared
   concepts with different meanings)

Draw this as a simple context map — boxes for each bounded context with arrows showing
relationships (upstream/downstream, partnership, shared kernel, etc.). Keep it simple.
The goal is to make the architecture legible as a value-creation system, not to produce
a perfect DDD diagram.

**Output for document**: A "Domain Model" section containing:
- A ubiquitous language glossary (the key terms and what they mean)
- A context map diagram (bounded contexts and their relationships)
- For each context: its responsibility, core/supporting/generic classification, and
  connection to the vision

---

### Phase 4: North Star and Measurement

**Goal**: Quantify the vision so you know if it's working.

Using Cutler's North Star Framework:

1. **North Star Metric**: A single metric that captures the core value your product
   delivers. It should be:
   - An expression of *customer* value, not business extraction
   - "One level out of reach" — not something any single team directly controls
   - Stable for 1-3 years as long as the strategy holds

2. **Input Metrics** (3-5): Actionable factors that teams can directly influence. These
   should be representative enough of your strategy that anyone looking at them would
   understand what you're trying to do.

Here's where the domain model connects to measurement: **each bounded context should
have at least one input metric that reflects its health and contribution to the North
Star.** This creates a direct line from the domain architecture to the product vision.

For example, if your North Star is "Weekly Active Shippers completing a booking in under
5 minutes," your input metrics might map to contexts like:
- *Rate Engine context* → "Rate quotes returned within 2 seconds with 95%+ accuracy"
- *Booking context* → "Bookings completed without manual intervention"
- *Carrier Integration context* → "Active carrier connections per shipper"

This mapping is powerful because it means that when an engineering team asks "why does
this bounded context exist and how do we know it's working?" — there's a clear answer
that traces all the way back to the product vision.

**Output for document**: A "Measurement" section with the North Star Metric, input metrics,
and a mapping showing which metrics connect to which bounded contexts.

---

### Phase 5: Strategic Bets and Architecture Decisions

**Goal**: Connect the vision and domain model to the actual work, through bets.

Cutler frames roadmap items as "bets" rather than commitments. Each bet should be:
- Connected to one or more input metrics
- Grounded in a bounded context (or the relationship between contexts)
- Explicit about confidence level and what you'd need to learn

For each bet, help the user articulate:

1. **What are we betting?** (What's the initiative?)
2. **Why do we believe this will work?** (What's the hypothesis?)
3. **Which bounded context does this primarily affect?** (Where does the work happen?)
4. **Which input metric should move?** (How will we know?)
5. **What's our confidence level?** (High/medium/low — and what would change it?)

Also surface **architecture decisions** that flow from the domain model:
- Which contexts need to be built first? (Dependencies and value-creation order)
- Where should context boundaries be enforced strictly vs. kept flexible?
- Which contexts are core domain (build custom, invest heavily) vs. supporting (simpler
  solutions acceptable) vs. generic (buy/integrate)?
- What are the key integration patterns between contexts?

These architecture decisions aren't separate from the product vision — they're *how the
vision gets built*. The order in which you build contexts, the rigor of their boundaries,
and the investment level in each one are all strategic choices that should trace back to
"Why this? Why now? Why us?"

**Output for document**: A "Current Bets" section listing 2-5 near-term bets with their
hypothesis, target context, target metric, and confidence level. Plus an "Architecture
Decisions" section that explains the key structural choices and why they serve the vision.

---

### Phase 6: Risks, Assumptions, and the Living System

**Goal**: Make the beliefs explicit and build in mechanisms for learning.

Every vision is a hypothesis. Make the assumptions visible:

- **Product assumptions**: "We believe logistics coordinators will pay for speed over
  cost savings" — what if that's wrong?
- **Domain assumptions**: "We believe rate quoting and booking are separate bounded
  contexts" — what if they're more coupled than we think?
- **Technical assumptions**: "We believe we can integrate with 50 carriers through a
  generic adapter pattern" — what if carrier APIs are too heterogeneous?

For each major assumption, note:
- How confident are you? (High/medium/low)
- What evidence would change your mind?
- When will you learn whether this is right?

This section keeps the vision honest. It's the antidote to premature convergence and
the "frozen vision" anti-pattern.

**Output for document**: A "Risks & Assumptions" section that's candid about uncertainty.

---

## Assembling the Document

Once you've worked through all phases, assemble the final product vision document with
this structure:

```
# [Product Name]: Product Vision

## Context & Problem
[From Phase 1]

## Vision
[From Phase 2 — the narrative future state]

### What We're Not Doing
[From Phase 2]

## Domain Model
### Ubiquitous Language
[Glossary from Phase 3]

### Context Map
[Diagram from Phase 3]

### Bounded Contexts
[Detail per context from Phase 3]

## Measurement
### North Star Metric
[From Phase 4]

### Input Metrics
[From Phase 4, mapped to contexts]

## Current Bets
[From Phase 5]

## Architecture Decisions
[From Phase 5]

## Risks & Assumptions
[From Phase 6]
```

For diagrams (context maps, metric-to-context mappings), use Mermaid syntax so they
render in most documentation tools.

## Guiding Principles Throughout

- **Coherence over alignment.** The parts of this document should make sense together.
  If the vision says one thing but the domain model implies another, stop and resolve it.
- **The domain model IS the vision, expressed architecturally.** If someone reads only the
  context map and ubiquitous language, they should be able to infer the product strategy.
- **Specific enough to constrain, broad enough to empower.** Every section should help
  teams say no to things that don't fit AND give them creative room within what does fit.
- **Strong opinions, loosely held.** Treat everything as a hypothesis. Be decisive now,
  but build in the mechanisms to learn and update.
- **Compression forces clarity.** Push for conciseness. If a section can't be explained
  simply, the thinking isn't clear yet.
