---
name: domain-driven-critique
description: Critique a design or architecture against domain-driven design principles. Use when the user asks to "review this design", "critique the domain model", "check DDD alignment", or wants feedback on their architecture.
argument-hint: [design description, file path, or architecture overview]
disable-model-invocation: true
---

# Domain-Driven Design Critique

Evaluate an existing design or architecture against DDD principles, surfacing misalignments, anti-patterns, and concrete improvements.

## Input

**Design to Critique:** $ARGUMENTS

## Process

1. **Load Reference**
   - Read `resources/software-development/ddd-reference.md` in full. This is your checklist and source of truth.

2. **Parse the Input**
   - If the user provided file paths, read those files to understand the design.
   - If the user provided inline descriptions, parse the architecture from text.
   - If the user referenced prior conversation context, use that.
   - Build a mental model of: bounded contexts, aggregates, entities, value objects, services, events, and integration patterns currently in use.

3. **Strategic Alignment Check**
   - Are subdomains explicitly identified and classified (core/generic/supporting)?
   - Do bounded context boundaries align with linguistic boundaries (Ubiquitous Language)?
   - Is the context map explicit? Are integration patterns appropriate for the relationship type?
   - Is effort proportional to subdomain type? (Core gets the most investment, generic should be bought/adopted.)

4. **Tactical Alignment Check**
   - **Aggregate Sizing**: Apply Vernon's 4 rules. Flag aggregates that are too large (protect invariants that aren't real), reference other aggregates by object rather than ID, or enforce synchronous consistency where eventual would suffice.
   - **Value Object Usage**: Flag primitive obsession. Are concepts like Money, EmailAddress, DateRange modeled as VOs or raw primitives?
   - **Entity Identity**: Do entities have clear, stable identity? Is identity confused with value equality?
   - **Domain Event Design**: Are events named in past tense? Do they carry sufficient data? Are they used for cross-aggregate/cross-context communication?
   - **Repository Design**: One per aggregate root? Domain-oriented interface?

5. **Anti-Pattern Scan (Section 10)**
   Check against all anti-patterns from the reference:

   | Anti-Pattern | What to Look For |
   |-------------|-----------------|
   | Anaemic Domain Model | Entities with only getters/setters, logic in services |
   | God Aggregate | Aggregate protecting too many invariants, too many entities |
   | Primitive Obsession | Domain concepts as raw strings/ints instead of VOs |
   | Leaking Ubiquitous Language | Generic CRUD names instead of domain verbs |
   | Shared Kernel Creep | Shared code growing beyond its contract |
   | Big Ball of Mud (no BCs) | Everything in one context, no clear boundaries |
   | Event Soup | Events everywhere with no clear ownership or schema |
   | Repository as Query Engine | Repositories with arbitrary query methods |
   | Misplaced Domain Logic | Business rules in controllers, DTOs, or infrastructure |
   | Identity Crisis | Confusing entity identity with value equality |

6. **Supple Design Check (Section 4)**
   - Intention-Revealing Interfaces: Do method/class names communicate purpose?
   - Side-Effect-Free Functions: Are queries separated from commands?
   - Assertions/Contracts: Are invariants documented and enforced?
   - Conceptual Contours: Do abstractions align with domain concepts?
   - Standalone Classes: Can concepts be understood without deep dependency chains?
   - Closure of Operations: Do operations return the same type they operate on where appropriate?

7. **Complexity Check (Ousterhout)**
   - Deep modules: Are modules providing significant functionality behind simple interfaces?
   - Information hiding: Is implementation detail leaking across boundaries?
   - Errors out of existence: Could the design eliminate error cases rather than handle them?

## Output Format

Structure your response with these sections:

### Overall Assessment
1-2 sentences: Is this design well-aligned with DDD? What's the biggest concern?

### Strengths
Bullet list of what the design gets right. Be specific, reference DDD principles.

### Issues Found

| # | Issue | Severity | DDD Principle Violated | Recommendation |
|---|-------|----------|----------------------|----------------|
| 1 | ... | Critical / High / Medium / Low | ... | Concrete fix |

### Anti-Pattern Alerts
For each matched anti-pattern from the Section 10 scan:
- **Pattern name**: How it manifests in this design, with specific examples.
- Only include anti-patterns actually present. Don't force-fit.

### Supple Design Notes
Brief notes on intention-revealing interfaces, side-effect-free functions, and conceptual contours. Only flag issues, skip if clean.

### Recommended Next Steps
Prioritized list (most impactful first) of concrete changes. Each item should be actionable, not vague advice. Reference specific components/files when possible.
