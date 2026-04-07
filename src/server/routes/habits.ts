import { Router } from "express";
import { getDB } from "../db/index.js";
import { habits } from "../db/schema.js";
import { desc, eq } from "drizzle-orm";
import { scheduleHabit, stopHabit } from "../services/habit-scheduler.js";

const router = Router();

router.get("/status", async (_req, res) => {
  const db = getDB();
  const all = await db.select().from(habits);
  res.json({
    status: "ok",
    faculty: "habits",
    total: all.length,
    enabled: all.filter((h) => h.enabled).length,
  });
});

router.get("/", async (_req, res) => {
  try {
    const db = getDB();
    const data = await db.select().from(habits).orderBy(desc(habits.createdAt));
    res.json(data);
  } catch {
    res.status(500).json({ error: "Failed to get habits" });
  }
});

router.post("/", async (req, res) => {
  try {
    const { name, description, schedule, prompt, faculty } = req.body;
    if (!name || !schedule || !prompt) {
      res.status(400).json({ error: "name, schedule, and prompt are required" });
      return;
    }
    const db = getDB();
    const result = await db
      .insert(habits)
      .values({
        name,
        description: description || null,
        schedule,
        prompt,
        faculty: faculty || "thinking",
        enabled: true,
        createdAt: new Date().toISOString(),
      })
      .returning();

    const habit = result[0];
    scheduleHabit(habit.id, habit.schedule, habit.prompt, habit.faculty);

    res.status(201).json(habit);
  } catch {
    res.status(500).json({ error: "Failed to create habit" });
  }
});

router.put("/:id/toggle", async (req, res) => {
  try {
    const db = getDB();
    const id = parseInt(req.params.id);
    const existing = await db
      .select()
      .from(habits)
      .where(eq(habits.id, id))
      .limit(1);

    if (existing.length === 0) {
      res.status(404).json({ error: "Habit not found" });
      return;
    }

    const habit = existing[0];
    const newEnabled = !habit.enabled;

    await db.update(habits).set({ enabled: newEnabled }).where(eq(habits.id, id));

    if (newEnabled) {
      scheduleHabit(id, habit.schedule, habit.prompt, habit.faculty);
    } else {
      stopHabit(id);
    }

    res.json({ ...habit, enabled: newEnabled });
  } catch {
    res.status(500).json({ error: "Failed to toggle habit" });
  }
});

router.delete("/:id", async (req, res) => {
  try {
    const db = getDB();
    const id = parseInt(req.params.id);
    stopHabit(id);
    await db.delete(habits).where(eq(habits.id, id));
    res.json({ deleted: true });
  } catch {
    res.status(500).json({ error: "Failed to delete habit" });
  }
});

export default router;
