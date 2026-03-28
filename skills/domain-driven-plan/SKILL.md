---
name: domain-driven-plan
description: Draft a domain-driven design plan for a system or feature. Use when the user asks to "design a domain model", "plan the DDD", "model this domain", or wants strategic/tactical design guidance.
argument-hint: [system or feature description]
disable-model-invocation: true
---

# Domain-Driven Design Plan

Create a comprehensive DDD-informed design plan for the system or feature described by the user.

## Input

**System/Feature Description:** $ARGUMENTS

## Process

1. **Load Reference**
   - Read `resources/software-development/ddd-reference.md` in full. This is your primary source of truth for all DDD terminology, patterns, heuristics, and anti-patterns.

2. **Understand the Domain**
   - Parse the user's description for domain concepts, business rules, actors, and workflows.
   - If the user provided file paths or referenced existing code, read those files to understand the current state.
   - Identify the core problem the system solves and who the key stakeholders are.

3. **Strategic Design**
   - **Subdomain Identification**: Classify each subdomain as Core (competitive advantage), Generic (solved problem, buy/adopt), or Supporting (necessary but not differentiating).
   - **Bounded Context Boundaries**: Propose bounded contexts. Each BC should have a single Ubiquitous Language. Flag where the same term means different things (polysemes) as a BC boundary signal.
   - **Context Map**: Define relationships between BCs using integration patterns from the reference (Partnership, Shared Kernel, Customer-Supplier, Conformist, Anti-Corruption Layer, Open Host Service, Published Language, Separate Ways).

4. **Tactical Design** (for each Core bounded context)
   - **Aggregates**: Propose aggregate roots with their invariants. Apply Vernon's 4 rules: (1) protect true invariants, (2) small aggregates, (3) reference other aggregates by ID, (4) use eventual consistency across aggregate boundaries.
   - **Entities vs Value Objects**: Identify which concepts need identity tracking (entities) vs which are defined by their attributes (value objects). Default to VOs when possible.
   - **Domain Events**: Identify key state transitions that other contexts or aggregates need to know about. Name them in past tense (OrderPlaced, PaymentReceived).
   - **Domain Services**: Only for operations that don't naturally belong to any entity or VO. These should be stateless.
   - **Repositories**: One per aggregate root, exposing domain-oriented queries.

5. **Architecture Recommendations**
   - Apply the chained decision heuristic from Section 9 of the reference:
     - Subdomain type -> Business logic pattern (Transaction Script, Active Record, Domain Model, Event-Sourced Domain Model)
     - Business logic pattern -> Architecture (Layered, Ports & Adapters, CQRS)
     - Architecture -> Testing strategy
   - Recommend per-context, not one-size-fits-all. Supporting subdomains often need simpler patterns than core.

6. **Flag Uncertainties**
   - Per Section 0 of the reference: if domain knowledge is ambiguous, say so. Do not invent business rules.
   - Propose specific questions for domain expert validation.
   - Note where you made assumptions and what would change if those assumptions are wrong.

## Output Format

Structure your response with these sections:

### Domain Vision Statement
One paragraph capturing the core value proposition and strategic direction.

### Subdomain Map

| Subdomain | Type | Rationale |
|-----------|------|-----------|
| ... | Core / Generic / Supporting | Why this classification |

### Bounded Context Map
For each context: name, responsibility, Ubiquitous Language terms, and relationships to other contexts (with integration pattern).

### Core Domain Tactical Design
For each core bounded context:
- **Aggregates** (root entity, invariants protected, rough boundary)
- **Key Value Objects** (with equality semantics)
- **Domain Events** (name, trigger, payload sketch)
- **Services** (if any, with justification for why not on an entity/VO)

### Architecture Recommendations
Per-context recommendations following the chained decision heuristic. Include:
- Business logic pattern choice and why
- Architectural pattern choice and why
- Testing strategy recommendation

### Open Questions
Numbered list of questions that need domain expert input before finalizing the design. Prioritize by impact on the design.
