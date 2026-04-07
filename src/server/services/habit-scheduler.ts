import cron from "node-cron";
import { getDB } from "../db/index.js";
import { habits } from "../db/schema.js";
import { eq } from "drizzle-orm";
import { chat, isLLMConfigured } from "./llm.js";

const activeTasks: Map<number, cron.ScheduledTask> = new Map();

export async function initHabits() {
  const db = getDB();
  const allHabits = await db.select().from(habits);

  for (const habit of allHabits) {
    if (habit.enabled) {
      scheduleHabit(habit.id, habit.schedule, habit.prompt, habit.faculty);
    }
  }

  console.log(`⏰ ${allHabits.filter((h) => h.enabled).length} habits scheduled`);
}

export function scheduleHabit(
  id: number,
  schedule: string,
  prompt: string,
  faculty: string
) {
  const existing = activeTasks.get(id);
  if (existing) existing.stop();

  if (!cron.validate(schedule)) {
    console.warn(`Invalid cron schedule for habit ${id}: ${schedule}`);
    return;
  }

  const task = cron.schedule(schedule, async () => {
    console.log(`⏰ Running habit ${id}: ${prompt.slice(0, 50)}...`);

    if (!isLLMConfigured()) {
      console.log("  Skipped — LLM not configured");
      return;
    }

    try {
      const result = await chat(faculty as any, [
        { role: "user", content: prompt },
      ]);
      console.log(`  Result: ${result.slice(0, 100)}...`);

      const db = getDB();
      await db
        .update(habits)
        .set({ lastRun: new Date().toISOString() })
        .where(eq(habits.id, id));
    } catch (err) {
      console.error(`  Habit ${id} failed:`, err);
    }
  });

  activeTasks.set(id, task);
}

export function stopHabit(id: number) {
  const task = activeTasks.get(id);
  if (task) {
    task.stop();
    activeTasks.delete(id);
  }
}

export function stopAll() {
  for (const [id, task] of activeTasks) {
    task.stop();
    activeTasks.delete(id);
  }
}

export async function seedDefaultHabits() {
  const db = getDB();
  const existing = await db.select().from(habits);
  if (existing.length > 0) return;

  const defaults = [
    {
      name: "Morning Review",
      description: "Start the day by reviewing priorities and tasks",
      schedule: "0 8 * * *",
      prompt:
        "It's morning. Review my recent tasks and memories. What should I focus on today? Give me a brief, actionable priority list.",
      faculty: "thinking",
    },
    {
      name: "Weekly Financial Summary",
      description: "Summarize the week's financial activity",
      schedule: "0 9 * * 0",
      prompt:
        "Summarize my financial activity for this week. Income, expenses, and any notable patterns. Keep it brief and actionable.",
      faculty: "financial",
    },
    {
      name: "Monthly Reflection",
      description: "Reflect on the month's learnings and progress",
      schedule: "0 10 1 * *",
      prompt:
        "It's the start of a new month. What were the key things I learned last month? What goals did I make progress on? What should I focus on this month?",
      faculty: "thinking",
    },
  ];

  for (const h of defaults) {
    await db.insert(habits).values({
      name: h.name,
      description: h.description,
      schedule: h.schedule,
      prompt: h.prompt,
      faculty: h.faculty,
      enabled: true,
      createdAt: new Date().toISOString(),
    });
  }

  console.log("⏰ Default habits seeded");
}
