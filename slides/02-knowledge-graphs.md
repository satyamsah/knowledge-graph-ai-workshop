# Slide Deck: 02 — Knowledge Graphs 101
### (0:45–1:15, 30 min)

---

## Slide 1 — What is a Knowledge Graph?

A way to store information as **things** and **relationships between things**.

```
(Apple) ──[:MAKES]──> (iPhone)
(Steve Jobs) ──[:FOUNDED]──> (Apple)
(iPhone) ──[:COMPETES_WITH]──> (Samsung Galaxy)
```

Three building blocks:
- **Node** — a thing (person, company, product)
- **Relationship** — a directed connection with a type
- **Property** — a key-value attribute on a node or relationship

---

## Slide 2 — Nodes

A node represents an entity.

```
(n:Company {name: "Apple", founded: 1976, hq: "Cupertino"})
(n:Product {name: "iPhone", category: "smartphone", launched: 2007})
(n:Person  {name: "Steve Jobs", role: "Co-founder"})
```

- The label (`:Company`, `:Product`) is the *type*
- Properties are key-value pairs in `{}`
- Every node gets an internal id

---

## Slide 3 — Relationships

A relationship connects two nodes with direction and a type.

```
(Steve Jobs)-[:FOUNDED {year: 1976}]->(Apple)
(Apple)-[:MAKES {since: 2007}]->(iPhone)
(iPhone)-[:COMPETES_WITH]->(Samsung Galaxy)
```

- Always has a **direction** (but you can query both ways)
- The type is in `[:UPPERCASE]`
- Relationships can also have properties

---

## Slide 4 — A picture is worth a thousand rows

Traditional table (relational):

| company_id | product_id | relationship |
|---|---|---|
| 1 | 101 | MAKES |
| 1 | 102 | MAKES |

Knowledge graph:

```
(Apple) ──[:MAKES]──> (iPhone)
        ──[:MAKES]──> (MacBook)
        ──[:MAKES]──> (iPad)
```

The *graph* makes the structure of the data visible. Multi-hop queries become natural traversals.

---

## Slide 5 — Multi-hop is where graphs shine

**"Find all products made by companies founded by people who also founded other companies"**

In SQL: 3 JOINs, a subquery, messy.

In a graph: follow the arrows.

```
(Person)-[:FOUNDED]->(Company)-[:MAKES]->(Product)
```

---

## Slide 6 — Neo4j — the graph database we'll use

- Most popular graph database
- Uses **Cypher** as its query language (readable, like SQL but for graphs)
- Has a visual browser at `localhost:7474`
- Free community edition, easy to run with Docker

---

## Slide 7 — Our graph today

```
(Person) ──[:FOUNDED]──> (Company) ──[:MAKES]──> (Product)
                            │                        │
                     [:ACQUIRED]              [:COMPETES_WITH]
                            │                        │
                         (Company)               (Product)
                            │
                     [:PART_OF]
                            │
                         (Division)
```

Real entities we'll use:
- Companies: Apple, Google, Microsoft, Amazon, Meta, OpenAI, Nvidia
- People: Steve Jobs, Elon Musk, Jeff Bezos, Sundar Pichai, Sam Altman
- Products: iPhone, Android, Windows, AWS, ChatGPT, Gemini, VS Code

---

## Facilitator notes

- Draw the graph live on a whiteboard or use the diagram tool on screen
- Ask: "Can you think of a relationship between two of these companies?"
- Transition: "Let's open Neo4j and start creating this ourselves"
