# Skill: Code Review

## When to use
When reviewing code, discussing architecture decisions, or debugging technical problems.

## Procedures

### Code review checklist
1. **Correctness**: Does the code do what it's supposed to?
2. **Readability**: Can someone else understand this in 30 seconds?
3. **Performance**: Any obvious bottlenecks or unnecessary work?
4. **Security**: Any input validation missing? Secrets exposed?
5. **Error handling**: What happens when things go wrong?
6. **Testing**: Is it testable? Are edge cases covered?
7. **Simplicity**: Can this be simpler without losing functionality?

### Debugging approach
1. Reproduce the problem — understand exactly what's happening
2. Form a hypothesis — what could cause this?
3. Test the hypothesis — check logs, add debugging output
4. Fix and verify — make the smallest change that fixes it
5. Prevent recurrence — add tests, error handling, or documentation

### Architecture decisions
When discussing architecture:
1. What are the requirements? (functional + non-functional)
2. What are the constraints? (time, team size, existing systems)
3. What are at least 2-3 options?
4. What are the trade-offs of each?
5. Recommend one and explain why
