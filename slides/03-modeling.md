# Slide Deck: 03 — Modeling Real-World Information
### (1:30–2:00, 30 min — after break)

---

## Slide 1 — Modeling is a design skill

There is no single "correct" graph model.
Good modeling asks: **what questions do I need to answer?**

Design around your queries, not around your data source.

---

## Slide 2 — The three questions to ask

1. **What are my entities?** → these become nodes
2. **How are they related?** → these become relationships
3. **What do I need to know about each?** → these become properties

---

## Slide 3 — Our domain: Tech companies & products

Entities:
- `Person`   — founders, CEOs
- `Company`  — Apple, Google, Microsoft, Amazon, Meta, OpenAI, Nvidia
- `Product`  — iPhone, Android, Windows, AWS, ChatGPT…
- `Division` — AWS is a division of Amazon, Google Cloud is a division of Google

Relationships:
- `(Person)-[:FOUNDED]->(Company)`
- `(Person)-[:CEO_OF]->(Company)`
- `(Company)-[:MAKES]->(Product)`
- `(Company)-[:ACQUIRED]->(Company)`
- `(Product)-[:COMPETES_WITH]->(Product)`
- `(Division)-[:PART_OF]->(Company)`

---

## Slide 4 — Good modeling habits

| Do | Don't |
|----|-------|
| Use nouns for node labels | Use verbs as labels |
| Use UPPER_SNAKE for relationship types | Use generic "RELATED_TO" |
| Put facts on nodes | Over-normalize into tiny nodes |
| Model for your queries | Model to mirror your source data |

---

## Slide 5 — A common mistake: over-normalizing

**Too granular:**
```
(iPhone) -[:HAS_ATTRIBUTE]-> (Attribute {key:"category", value:"smartphone"})
```

**Just right:**
```
(iPhone:Product {name:"iPhone", category:"smartphone"})
```

Save nodes for things you want to *traverse to* or *query by identity*.

---

## Slide 6 — Another common mistake: vague relationships

**Too vague:**
```
(Apple)-[:RELATED_TO]->(iPhone)
```

**Expressive:**
```
(Apple)-[:MAKES]->(iPhone)
```

Relationship types are your vocabulary. Rich types = richer queries.

---

## Facilitator notes

- Spend 5 min on whiteboard: "what would you model for Netflix? Spotify?"
- The goal is intuition — they don't need to master this today
- Transition: "Now let's actually load this data into Neo4j"
