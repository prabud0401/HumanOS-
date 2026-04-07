# 🧬 HumanOS — Your Digital Clone

A standalone web app that **is you**. It has your personality, your memory, your skills, your financial sense, your habits. It thinks like you, remembers like you, and learns over time.

Under the hood, Claude (or any LLM) reads your "DNA" files and becomes you.

## Quick Start

```bash
git clone https://github.com/prabud0401/HumanOS-.git
cd HumanOS-
cp dna/.env.example dna/.env       # Add your Claude API key
pnpm install
pnpm dev                           # Opens http://localhost:3000
```

That's it. You're alive.

## How It Works

```
YOU (dna/identity.yaml)  →  defines WHO you are
    ↓
MIND (mind/*.md)         →  defines HOW each part of you thinks
    ↓
SKILLS (skills/*.md)     →  defines WHAT you can do
    ↓
BODY (src/)              →  the app that brings it all together
    ↓
Claude API               →  the intelligence that powers your clone
```

### The Human Body in Code

| Human Part | Folder/File | What It Does |
|---|---|---|
| DNA | `dna/identity.yaml` | Your name, values, background, goals |
| Personality | `dna/personality.md` | How you talk, think, decide |
| Consciousness | `mind/consciousness.md` | Routes input to the right mental faculty |
| Brain/Thinking | `mind/thinking.md` | Deep reasoning, analysis, creativity |
| Memory | `mind/memory.md` | Long-term recall, learning from past |
| Financial Sense | `mind/financial.md` | Money management, budgets, loans |
| Meeting Processing | `mind/meetings.md` | Transcript analysis, action items |
| Habits | `mind/habits.md` | Automatic routines on schedule |
| Health Monitor | `mind/health.md` | Self-awareness, system checks |
| Skills | `skills/*.md` | Learned abilities (add more over time) |

### Pages

- **Dashboard** — Body map showing health of each faculty
- **Brain** — Chat with yourself (streaming, auto-routes to the right faculty)
- **Memory** — Store, search, and manage memories
- **Financial** — Track income, expenses, loans, budgets
- **Meetings** — Upload transcripts, get AI-powered summaries and action items
- **Habits** — Manage automatic routines that run on schedule
- **Settings** — Edit your DNA, check API status, manage mind files

## Clone Yourself (for Aaqil or anyone)

Same steps as Quick Start. The only thing you change:

1. Edit `dna/identity.yaml` — put YOUR name, values, background
2. Edit `dna/personality.md` — describe how YOU think and talk
3. Add your Claude API key to `dna/.env`

Same mind, different DNA = different person. Just like real humans.

## Tech Stack

- **TypeScript** everywhere
- **React 19** + Vite + Tailwind CSS 4 (frontend)
- **Express.js 5** (backend API)
- **SQLite** via libsql (zero-config database)
- **Claude API** via Anthropic SDK (intelligence)
- One command: `pnpm dev` starts everything

## Project Structure

```
HumanOS/
  dna/                    # WHO YOU ARE
    identity.yaml         # Name, values, background
    personality.md        # How you think and talk
    .env                  # API keys (not committed)

  mind/                   # HOW EACH PART THINKS (system prompts)
    consciousness.md      # The "self" — routes to faculties
    thinking.md           # Reasoning, analysis
    memory.md             # Storing and recalling
    financial.md          # Money management
    meetings.md           # Transcript processing
    habits.md             # Routine definitions
    health.md             # Self-monitoring

  skills/                 # LEARNED ABILITIES
    financial-tracking.md
    meeting-processing.md
    knowledge-management.md
    code-review.md        # Add your own!

  src/
    server/               # Express API (nervous system)
    client/               # React UI (the face)

  data/                   # SQLite database (gitignored)
```

## Adding New Skills

Create a markdown file in `skills/`:

```markdown
# Skill: My New Skill

## When to use
Describe when this skill activates.

## Procedures
Step-by-step instructions for the LLM to follow.
```

The brain automatically picks up new skills.

## Contributors

- **Prabu Deva** — Creator
- **Aaqil Irshad** — Contributor

## License

MIT
