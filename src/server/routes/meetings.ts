import { Router } from "express";
import { getDB } from "../db/index.js";
import { meetings } from "../db/schema.js";
import { desc, eq } from "drizzle-orm";
import { chat, isLLMConfigured } from "../services/llm.js";

const router = Router();

router.get("/status", async (_req, res) => {
  const db = getDB();
  const all = await db.select().from(meetings);
  res.json({
    status: "ok",
    faculty: "meetings",
    total: all.length,
    pending: all.filter((m) => m.status === "pending").length,
    processed: all.filter((m) => m.status === "processed").length,
  });
});

router.get("/", async (_req, res) => {
  try {
    const db = getDB();
    const data = await db.select().from(meetings).orderBy(desc(meetings.createdAt));
    res.json(data);
  } catch {
    res.status(500).json({ error: "Failed to get meetings" });
  }
});

router.get("/:id", async (req, res) => {
  try {
    const db = getDB();
    const result = await db
      .select()
      .from(meetings)
      .where(eq(meetings.id, parseInt(req.params.id)))
      .limit(1);
    if (result.length === 0) {
      res.status(404).json({ error: "Meeting not found" });
      return;
    }
    res.json(result[0]);
  } catch {
    res.status(500).json({ error: "Failed to get meeting" });
  }
});

router.post("/", async (req, res) => {
  try {
    const { title, date, transcript, attendees } = req.body;
    if (!title || !date) {
      res.status(400).json({ error: "title and date are required" });
      return;
    }

    const db = getDB();
    const result = await db
      .insert(meetings)
      .values({
        title,
        date,
        transcript: transcript || null,
        attendees: attendees || null,
        summary: null,
        actionItems: null,
        status: transcript ? "pending" : "draft",
        createdAt: new Date().toISOString(),
      })
      .returning();

    res.status(201).json(result[0]);
  } catch {
    res.status(500).json({ error: "Failed to create meeting" });
  }
});

router.post("/:id/process", async (req, res) => {
  try {
    const db = getDB();
    const id = parseInt(req.params.id);
    const results = await db
      .select()
      .from(meetings)
      .where(eq(meetings.id, id))
      .limit(1);

    if (results.length === 0) {
      res.status(404).json({ error: "Meeting not found" });
      return;
    }

    const meeting = results[0];

    if (!meeting.transcript) {
      res.status(400).json({ error: "No transcript to process" });
      return;
    }

    if (!isLLMConfigured()) {
      res.status(503).json({
        error: "LLM not configured. Add ANTHROPIC_API_KEY to dna/.env",
      });
      return;
    }

    const result = await chat(
      "meetings",
      [
        {
          role: "user",
          content: `Process this meeting transcript and provide a structured summary.\n\nMeeting title: ${meeting.title}\nDate: ${meeting.date}\nAttendees: ${meeting.attendees || "Unknown"}\n\nTranscript:\n${meeting.transcript}`,
        },
      ],
      { skills: ["meeting-processing"] }
    );

    const actionItemsMatch = result.match(
      /## Action Items\n([\s\S]*?)(?=\n## |$)/
    );
    const actionItems = actionItemsMatch ? actionItemsMatch[1].trim() : "";

    await db
      .update(meetings)
      .set({
        summary: result,
        actionItems: actionItems || null,
        status: "processed",
      })
      .where(eq(meetings.id, id));

    const updated = await db
      .select()
      .from(meetings)
      .where(eq(meetings.id, id))
      .limit(1);

    res.json(updated[0]);
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : "Processing failed";
    res.status(500).json({ error: msg });
  }
});

router.delete("/:id", async (req, res) => {
  try {
    const db = getDB();
    await db.delete(meetings).where(eq(meetings.id, parseInt(req.params.id)));
    res.json({ deleted: true });
  } catch {
    res.status(500).json({ error: "Failed to delete meeting" });
  }
});

export default router;
