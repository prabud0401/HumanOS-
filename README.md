# HumanOS — Clone Yourself

A self-replicable digital twin framework that maps every software component to a human organ. Configure your DNA, launch with Docker, and let your AI twin handle meetings, projects, finances, and team communication — in YOUR style.

## The Idea

Every person has a unique combination of knowledge, personality, decision-making style, and professional context. HumanOS captures all of that in a single `identity.yaml` config file (your **DNA**), then builds a fully autonomous AI twin around it.

**Your friend can clone this repo, edit their own DNA, and have their own twin running in minutes.**

## Architecture — Organic Architecture

HumanOS uses a custom hybrid pattern called **Organic Architecture** — a combination of Modular Monolith, Event-Driven, and Ports & Adapters designed around the human body metaphor. No standard pattern alone fits a digital twin system.

### 7 Core Principles

1. **Organ Autonomy** — Each organ is a self-contained Django app (models, tasks, APIs, health checks). Developers work on separate organs with zero conflicts.
2. **Circulatory Event Bus** — Organs never call each other directly. All communication flows through the Heart (Redis Streams event bus).
3. **Nervous Reflex Arcs** — Time-critical operations bypass the bus via synchronous reflex handlers.
4. **DNA-Driven Bootstrap** — `identity.yaml` configures every organ at startup. Different DNA = different behavior, zero code changes.
5. **Ports & Adapters per Organ** — Abstract ports with concrete adapters per platform. Adding Zoom = one new file.
6. **Immune Middleware** — Security wraps every organ automatically (rate limiting, audit, encryption).
7. **Evolutionary Extraction** — Start as a monolith; extract any organ into a microservice later via the event bus.

### Core Infrastructure (`core/`)

| File | Role | Metaphor |
|---|---|---|
| `dna_loader.py` | Parses `identity.yaml`, builds typed config, injects into organs | DNA → Gene expression |
| `bus.py` | Event bus with InMemory (dev) and Redis Streams (prod) | Heart / Circulatory system |
| `pulse.py` | Health monitoring — checks every organ, reports system health | Pulse / Vital signs |
| `immune.py` | Security middleware — rate limiting, audit, data sanitization | Immune defenses |
| `reflex.py` | Synchronous fast-path for urgent operations | Nervous reflex arcs |

### Organ Map

| Organ | Software Component | Core Tech |
|---|---|---|
| **Brain** | AI Engine & Decision Making | Claude API, Paperclip |
| **Heart** | Event Bus / Message Queue | Redis Streams, Celery |
| **Lungs** | Data Ingestion | Graph API, Webhooks |
| **Eyes** | Monitoring Dashboard | React, D3.js |
| **Ears** | Input Listeners | Webhooks, Calendar Watchers |
| **Voice** | Communication Output | Slack/Teams Bot, SMTP |
| **Hands** | Agent Commander | GitHub API, Azure DevOps, Shell |
| **Skeleton** | Project Structure & Config | Django, Templates |
| **Nervous System** | Real-time Signals | WebSocket, SSE |
| **Immune System** | Security & Defense | AES-256, RBAC, OAuth2, JWT |
| **Digestive** | Data Processing Pipeline | VTT/PDF Parsing, NLP |
| **Circulatory** | Data Transport / Pipelines | Celery, Async Transport |
| **Memory** | Knowledge Base / Vector DB | ChromaDB, Pinecone |
| **Endocrine** | Scheduler / Timer System | Celery Beat, APScheduler |
| **Financial Cortex** | Personal Finance | Django, Chart.js, Pandas |
| **Reproductive** | Self-Replication | Git, Docker, YAML |

## Quick Start

```bash
# 1. Clone
git clone https://github.com/your-org/HumanOS.git
cd HumanOS

# 2. Configure your DNA
cp dna/identity.example.yaml dna/identity.yaml
cp dna/.env.example dna/.env
# Edit both files with YOUR data

# 3. Launch
docker-compose up -d
```

Open `http://localhost:8000` — your twin is alive.

## Folder Structure

```
HumanOS/
├── core/                          # Skeleton — shared infrastructure
│   ├── __init__.py
│   ├── dna_loader.py              # Parses identity.yaml, injects config
│   ├── bus.py                     # Event bus (Heart implementation)
│   ├── pulse.py                   # Health monitor for all organs
│   ├── immune.py                  # Security middleware
│   └── reflex.py                  # Synchronous reflex arc registry
├── dna/                           # YOUR unique identity (gitignored)
│   ├── identity.yaml              # DNA config (10 chromosomes)
│   ├── identity.example.yaml      # Template for new clones
│   ├── .env                       # Secrets (gitignored)
│   ├── .env.example               # Secret template
│   └── .gitignore                 # Protects identity.yaml and .env
├── organs/                        # 16 organ Django apps
│   ├── brain/                     # AI engine, decision making
│   ├── heart/                     # Event bus, message queue
│   ├── lungs/                     # Data ingestion
│   ├── eyes/                      # Monitoring dashboards
│   ├── ears/                      # Input listeners, webhooks
│   ├── voice/                     # Communication output
│   ├── hands/                     # Agent commander, execution
│   ├── skeleton/                  # Project structure, config
│   ├── nervous_system/            # WebSocket, real-time signals
│   ├── immune_system/             # Security, encryption, RBAC
│   ├── digestive_system/          # Data processing pipeline
│   ├── circulatory_system/        # Data transport, pipelines
│   ├── memory/                    # Knowledge base, vector DB
│   ├── endocrine/                 # Scheduler, timer system
│   ├── financial_cortex/          # Personal finance module
│   └── reproductive/              # Self-clone, templates
├── docs/                          # Documentation
│   └── blueprint.html             # Interactive architecture blueprint
├── .knowledge/                    # Shared project knowledge
├── scripts/                       # Utility scripts
├── templates/                     # Shared templates
├── .github/
│   └── workflows/                 # CI/CD pipelines
├── docker-compose.yml             # One-command launch
├── requirements.txt               # Python dependencies
├── package.json                   # JS dependencies
└── README.md                      # This file
```

## DNA Configuration (identity.yaml)

Your identity has 10 "chromosomes":

| # | Chromosome | What It Controls |
|---|---|---|
| 1 | Identity | Name, timezone, locale, avatar |
| 2 | Personality | Communication style, decision speed, risk tolerance, work hours |
| 3 | Professional | Role, company, tech stack, active projects |
| 4 | AI Engine | Model choice, temperature, adapter, vector DB |
| 5 | Connections | Platform OAuth (Teams, Google, Zoom, GitHub, Slack) |
| 6 | Financial | Income, expenses, loans, budget, savings goals |
| 7 | Knowledge | Paths to .knowledge/ folders, file patterns |
| 8 | Agents | Paperclip config, hierarchy, agent count |
| 9 | Preferences | Theme, notifications, auto-pilot level |
| 10 | Security | Encryption, token rotation, audit retention |

## Tools & Dependencies

### MCP Servers
- `filesystem` — File operations
- `github` — Repo management
- `browser` — Web automation
- `postgres` — Database
- `memory` — Persistent AI memory
- `slack` — Team communication
- `google-calendar` — Calendar integration
- `fetch` — HTTP requests

### Key Packages
- **Backend**: Django, DRF, Celery, Redis, ChromaDB, Anthropic SDK, MS Graph SDK, Playwright, Whisper
- **Frontend**: React, Vite, Tailwind, MUI, D3.js, Chart.js, Socket.io

### External APIs
- Claude API (brain reasoning)
- Microsoft Graph (Teams, Calendar, Email)
- Google Workspace (Calendar, Drive, Meet)
- Zoom API (recordings, transcripts)
- GitHub API (repos, PRs, issues)
- Whisper / Azure Speech (speech-to-text)

## Self-Clone Guide

1. Fork/clone this repo
2. Copy `dna/identity.example.yaml` → `dna/identity.yaml`
3. Fill in your identity (name, timezone, personality)
4. Configure platform connections (OAuth keys)
5. Set up financial data (optional)
6. Copy `dna/.env.example` → `dna/.env`, fill secrets
7. Run `docker-compose up -d`
8. Connect your Paperclip instance (optional)
9. Feed initial knowledge (meeting history, docs)
10. Your twin is alive and learning

## Organ Development Guide

Every organ follows the same **cell structure** — a standardized file layout:

```
organs/brain/                    # Example: Brain organ
├── __init__.py                  # Module docstring
├── apps.py                      # Django AppConfig + DNA injection + event subscriptions
├── models.py                    # Django ORM models
├── ports.py                     # Abstract interfaces (ABC classes)
├── adapters/                    # Concrete implementations per platform
│   ├── __init__.py
│   ├── claude_adapter.py
│   ├── openai_adapter.py
│   └── local_adapter.py
├── events.py                    # PUBLISHES + SUBSCRIBES lists + handle_event()
├── services.py                  # Service layer orchestrating ports + business logic
├── tasks.py                     # Celery async tasks (with ImportError fallback)
├── api.py                       # Django Ninja REST endpoints
├── health.py                    # Health check -> (HealthStatus, str, dict)
├── dna.py                       # Organ-specific config from identity.yaml
└── tests/
    ├── test_models.py
    ├── test_adapters.py
    └── test_events.py
```

### Creating a New Organ

1. Create the folder under `organs/` with subdirs `adapters/` and `tests/`.
2. Define your **ports** (abstract interfaces) in `ports.py`.
3. Implement **adapters** for each external platform.
4. Declare **events** — what you publish and subscribe to.
5. Wire everything in `apps.py` → `ready()`: load DNA, subscribe to bus, register health.
6. Write your **service layer** to orchestrate the logic.
7. Expose via **api.py** (Django Ninja router).
8. Add a **health check** so the Pulse Monitor can track you.

### Event Communication

```python
# In your organ's events.py:
PUBLISHES = ["artifacts.ingested", "ingestion.failed"]
SUBSCRIBES = ["meeting.detected", "meeting.retry"]

def handle_event(event: Event) -> None:
    # Route to appropriate handler based on event.type
    ...
```

Organs communicate exclusively through events on the bus. Never import from another organ directly.

### Port/Adapter Pattern

```python
# ports.py — Define the abstract interface
class MeetingIngestionPort(ABC):
    @abstractmethod
    def authenticate(self, config) -> Token: ...
    @abstractmethod
    def download(self, artifact_ref, token) -> bytes: ...

# adapters/teams_adapter.py — Concrete implementation
class TeamsAdapter(MeetingIngestionPort):
    def authenticate(self, config):
        return graph_client.acquire_token(config.tenant_id, ...)
```

Adding a new platform = one new adapter file. Zero changes to the organ's core logic.

## Interactive Blueprint

Open `docs/blueprint.html` in a browser for the full interactive architecture with:
- Anatomical SVG body diagram with clickable organs
- Detailed specs for all 16 organ modules
- Circular data flow visualization
- Financial cortex mock UI
- Complete tools & MCP inventory
- **Organic Architecture** — principles, diagrams, cell structure, event contracts, comparison table
- Step-by-step self-clone guide
- 12-month development roadmap

## License

MIT — Clone yourself freely.
