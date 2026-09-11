# Data Model — Tech Knowledge Graph

This is the structure of the graph we build in the workshop.
Every query we write is based on this model.

---

## Node Types

| Label | Properties | Description |
|-------|-----------|-------------|
| `Company` | `name`, `founded` (year), `hq` (city) | A tech company |
| `Product` | `name`, `category`, `launched` (year) | A product or service |
| `Person` | `name` | A founder or CEO |

**Product categories:** `AI`, `cloud`, `smartphone`, `laptop`, `tablet`, `wearable`, `mobile OS`, `desktop OS`, `dev tool`, `dev platform`, `email`, `web service`, `social media`, `messaging`, `AI assistant`, `GPU`, `EV`

---

## Relationship Types

```
(Person)  -[:FOUNDED]->       (Company)
(Person)  -[:CEO_OF]->        (Company)
(Company) -[:MAKES]->         (Product)
(Company) -[:ACQUIRED]->      (Company)
(Product) -[:COMPETES_WITH]-> (Product)
```

---

## Visual Layout

```
(Person)
   │
   ├──[:FOUNDED]──────> (Company) ──[:MAKES]──────> (Product)
   │                       │                            │
   └──[:CEO_OF]────────>   │                    [:COMPETES_WITH]
                     [:ACQUIRED]                        │
                            │                        (Product)
                         (Company)
```

---

## Data Loaded by seed.py

### Companies (10)
| Name | Founded | HQ |
|------|---------|-----|
| Apple | 1976 | Cupertino |
| Google | 1998 | Mountain View |
| Microsoft | 1975 | Redmond |
| Amazon | 1994 | Seattle |
| Meta | 2004 | Menlo Park |
| OpenAI | 2015 | San Francisco |
| Nvidia | 1993 | Santa Clara |
| Tesla | 2003 | Austin |
| SpaceX | 2002 | Hawthorne |
| Anthropic | 2021 | San Francisco |

### People (12)
| Name | Role |
|------|------|
| Steve Jobs | Co-founder, Apple |
| Steve Wozniak | Co-founder, Apple |
| Bill Gates | Founder, Microsoft |
| Jeff Bezos | Founder & CEO, Amazon |
| Mark Zuckerberg | Founder & CEO, Meta |
| Elon Musk | Founder, Tesla & SpaceX |
| Larry Page | Co-founder, Google |
| Sergey Brin | Co-founder, Google |
| Sundar Pichai | CEO, Google |
| Sam Altman | Founder & CEO, OpenAI |
| Jensen Huang | Founder & CEO, Nvidia |
| Dario Amodei | Founder & CEO, Anthropic |

### Products (25)
| Name | Company | Category | Launched |
|------|---------|----------|---------|
| iPhone | Apple | smartphone | 2007 |
| MacBook | Apple | laptop | 2006 |
| iPad | Apple | tablet | 2010 |
| Apple Watch | Apple | wearable | 2015 |
| Xcode | Apple | dev tool | 2003 |
| Android | Google | mobile OS | 2008 |
| Google Search | Google | web service | 1998 |
| Gmail | Google | email | 2004 |
| Google Cloud | Google | cloud | 2008 |
| Gemini | Google | AI | 2023 |
| Windows | Microsoft | desktop OS | 1985 |
| Azure | Microsoft | cloud | 2010 |
| VS Code | Microsoft | dev tool | 2015 |
| GitHub | Microsoft | dev platform | 2008 |
| Copilot | Microsoft | AI | 2023 |
| AWS | Amazon | cloud | 2006 |
| Alexa | Amazon | AI assistant | 2014 |
| Facebook | Meta | social media | 2004 |
| Instagram | Meta | social media | 2010 |
| WhatsApp | Meta | messaging | 2009 |
| ChatGPT | OpenAI | AI | 2022 |
| Claude | Anthropic | AI | 2023 |
| H100 | Nvidia | GPU | 2022 |
| Tesla Model S | Tesla | EV | 2012 |
| Autopilot | Tesla | AI | 2014 |

### Relationships
| Type | Examples |
|------|---------|
| `[:FOUNDED]` | Larry Page → Google, Elon Musk → Tesla, Elon Musk → SpaceX |
| `[:CEO_OF]` | Sundar Pichai → Google, Sam Altman → OpenAI |
| `[:MAKES]` | Apple → iPhone, Microsoft → Azure |
| `[:ACQUIRED]` | Microsoft → GitHub, Meta → Instagram, Meta → WhatsApp |
| `[:COMPETES_WITH]` | AWS ↔ Azure, ChatGPT ↔ Gemini, ChatGPT ↔ Claude |

---

## Useful queries to explore the model

```cypher
-- See all node labels
CALL db.labels()

-- See all relationship types
CALL db.relationshipTypes()

-- Count everything
MATCH (n) RETURN labels(n)[0] AS type, COUNT(n) AS count ORDER BY count DESC

-- See the full graph (limit for performance)
MATCH (n) RETURN n LIMIT 60
```
