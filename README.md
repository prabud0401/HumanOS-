# HumanOS — Clone Yourself

A self-replicable digital twin framework that maps every software component to a human organ. Configure your DNA, launch with Docker, and let your AI twin handle meetings, projects, finances, and team communication — in YOUR style.

## The Idea

Every person has a unique combination of knowledge, personality, decision-making style, and professional context. HumanOS captures all of that in a single `identity.yaml` config file (your **DNA**), then builds a fully autonomous AI twin around it.

**Your friend can clone this repo, edit their own DNA, and have their own twin running in minutes.**

## Architecture — The Human Body

| Organ | Software Component | Core Tech |
|---|---|---|
| **Brain** | AI Engine & Decision Making | Claude API, Paperclip |
| **Heart** | Event Bus / Message Queue | Redis, Celery |
| **Lungs** | Data Ingestion | Graph API, Webhooks |
| **Eyes** | Monitoring Dashboard | Grafana, Prometheus, React |
| **Ears** | Input Listeners | Webhooks, Calendar Watchers |
| **Voice** | Communication Output | Slack/Teams Bot, SMTP |
| **Hands** | Agent Commander | Paperclip, Playwright, Git |
| **Skeleton** | Infrastructure | Docker, K8s, PostgreSQL |
| **Nervous System** | Event-Driven Architecture | WebSocket, OpenTelemetry |
| **Immune System** | Security & Defense | AES-256, RBAC, Vault |
| **Digestive** | Data Processing Pipeline | Whisper, Claude, NLP |
| **Circulatory** | API Layer | DRF, GraphQL |
| **Memory** | Knowledge Base | ChromaDB, .knowledge/ |
| **Endocrine** | Priority & Scheduling | Celery Beat, Cron |
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
├── dna/                          # YOUR unique identity
│   ├── identity.yaml             # DNA config (10 chromosomes)
│   ├── identity.example.yaml     # Template for new clones
│   ├── .env                      # Secrets (gitignored)
│   ├── .env.example              # Secret template
│   └── .gitignore                # Protects identity.yaml and .env
├── organs/                       # One folder per body system
│   ├── brain/                    # AI engine, decision making
│   ├── heart/                    # Event bus, message queue
│   ├── lungs/                    # Data ingestion
│   ├── eyes/                     # Monitoring dashboards
│   ├── ears/                     # Input listeners, webhooks
│   ├── voice/                    # Communication output
│   ├── hands/                    # Agent commander, execution
│   ├── skeleton/                 # Infrastructure, Docker, DB
│   ├── nervous-system/           # WebSocket, events, tracing
│   ├── immune-system/            # Security, encryption, RBAC
│   ├── digestive-system/         # Data processing pipeline
│   ├── circulatory-system/       # API layer, data flow
│   ├── memory/                   # Knowledge base, vector DB
│   ├── endocrine/                # Priority engine, scheduling
│   ├── financial-cortex/         # Personal finance module
│   └── reproductive/             # Self-clone, templates
├── docs/                         # Documentation
│   └── blueprint.html            # Interactive architecture blueprint
├── scripts/                      # Utility scripts
├── templates/                    # Shared templates
├── .github/
│   └── workflows/                # CI/CD pipelines
├── docker-compose.yml            # One-command launch
├── requirements.txt              # Python dependencies
├── package.json                  # JS dependencies
└── README.md                     # This file
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

## Interactive Blueprint

Open `docs/blueprint.html` in a browser for the full interactive architecture with:
- Anatomical SVG body diagram with clickable organs
- Detailed specs for all 16 organ modules
- Circular data flow visualization
- Financial cortex mock UI
- Complete tools & MCP inventory
- Step-by-step self-clone guide
- 12-month development roadmap

## License

MIT — Clone yourself freely.
