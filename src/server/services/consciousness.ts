import { chat, type Message } from "./llm.js";

export type Faculty =
  | "thinking"
  | "memory"
  | "financial"
  | "meetings"
  | "habits"
  | "health";

const ROUTING_PROMPT = `Based on the user's message, determine which mental faculty should handle it.
Respond with ONLY one of these words: thinking, memory, financial, meetings, habits, health.

Rules:
- "thinking" for general questions, analysis, reasoning, brainstorming, coding, advice
- "memory" for requests to remember, recall, search knowledge, or "what did I..."
- "financial" for money, income, expenses, budgets, loans, savings, investments
- "meetings" for processing transcripts, meeting summaries, action items
- "habits" for routines, schedules, reminders, recurring behaviors
- "health" for system status, how am I doing, self-checks

If unsure, respond with "thinking".`;

export async function routeMessage(message: string): Promise<Faculty> {
  try {
    const result = await chat("consciousness", [{ role: "user", content: message }], {
      extraContext: ROUTING_PROMPT,
      maxTokens: 20,
    });

    const faculty = result.trim().toLowerCase() as Faculty;
    const valid: Faculty[] = [
      "thinking",
      "memory",
      "financial",
      "meetings",
      "habits",
      "health",
    ];

    return valid.includes(faculty) ? faculty : "thinking";
  } catch {
    return "thinking";
  }
}

export function routeMessageLocal(message: string): Faculty {
  const lower = message.toLowerCase();

  if (
    /\b(remember|recall|memory|memories|forget|learned|knew|know about)\b/.test(lower)
  )
    return "memory";

  if (
    /\b(money|salary|expense|income|loan|budget|rent|payment|lkr|usd|rupee|financial|spend|spent|earned|due|bill|subscription)\b/.test(
      lower
    )
  )
    return "financial";

  if (
    /\b(meeting|transcript|vtt|summary|action items|attendees|minutes)\b/.test(lower)
  )
    return "meetings";

  if (/\b(habit|routine|schedule|reminder|daily|weekly|monthly|cron)\b/.test(lower))
    return "habits";

  if (/\b(health|status|check|system|diagnostic|alive)\b/.test(lower))
    return "health";

  return "thinking";
}
