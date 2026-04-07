# Skill: Meeting Processing

## When to use
When a user uploads or pastes a meeting transcript (VTT, plain text, or structured notes).

## Procedures

### VTT format parsing
VTT files have this structure:
```
WEBVTT

00:00:00.000 --> 00:00:05.000
Speaker Name
Spoken text here

00:00:05.000 --> 00:00:10.000
Another Speaker
Their text here
```

1. Parse timestamps and speaker names
2. Group consecutive lines by the same speaker
3. Identify unique speakers

### Processing steps
1. Read the full transcript
2. Identify all unique speakers/participants
3. Create a 3-5 sentence summary of the meeting
4. Extract every action item mentioned (look for "will do", "need to", "action:", "TODO", "by [date]")
5. Extract decisions (look for "decided", "agreed", "going with", "final answer")
6. Note any unresolved questions or follow-ups
7. Rate the meeting importance (1-10) based on content

### Output template
```
# Meeting: [Title]
**Date**: [Date]
**Attendees**: [Names]

## Summary
[3-5 bullet points]

## Action Items
- [ ] [Task] → [Owner] — Due: [Date]

## Decisions
- [Decision and rationale]

## Follow-ups
- [What to check on and when]
```
