# .knowledge/ — HumanOS Shared Knowledge Base

This is the **shared** knowledge base for the HumanOS project. Both contributors (and any future contributors) read and write here.

## What Goes Here (Shared)

Everything related to building HumanOS as a product:
- Design decisions (ADRs)
- Meeting notes between contributors
- Session logs (what was built, when, by whom)
- Rules and coding standards
- Reference documents

## What Does NOT Go Here (Private)

Your personal identity stays in `dna/identity.yaml` (gitignored). Your twin's learned behaviors, personal meeting transcripts, and financial data are private to your local instance.

## Structure

```
.knowledge/
├── README.md          <- This file
├── meetings/          <- Contributor meetings, design discussions
│   └── MASTER.md      <- Index of all meetings
├── sessions/          <- Development session logs
│   └── MASTER.md      <- Index of all sessions
├── decisions/         <- Architecture Decision Records (ADRs)
│   └── MASTER.md      <- Index of all decisions
├── rules/             <- Coding standards, contribution guidelines
├── references/        <- Research, API docs, design references
└── inbox/             <- Drop zone for raw ideas and notes
```

## Contributors

| Name | GitHub | Role | Since |
|------|--------|------|-------|
| Prabu Ravichandran | @prabud0401 | Creator, Lead Architect | 2026-04-06 |
| Aaqil Irshad | — | Co-builder, Contributor | 2026-04-06 |

## How It Works

1. **Before you code**: Check `.knowledge/decisions/` for existing ADRs
2. **During a session**: Log what you're building in `.knowledge/sessions/`
3. **After a meeting**: Summarize in `.knowledge/meetings/`
4. **Made a design choice?**: Create an ADR in `.knowledge/decisions/`
5. **Found useful info?**: Add to `.knowledge/references/`
