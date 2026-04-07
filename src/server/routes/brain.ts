import { Router } from "express";
import { chatStream, isLLMConfigured, type Message } from "../services/llm.js";
import { routeMessageLocal } from "../services/consciousness.js";
import { getDB } from "../db/index.js";
import { conversations } from "../db/schema.js";
import { eq, desc } from "drizzle-orm";

const router = Router();

router.get("/status", (_req, res) => {
  res.json({
    status: "ok",
    faculty: "brain",
    llmConfigured: isLLMConfigured(),
  });
});

router.get("/history", async (_req, res) => {
  try {
    const db = getDB();
    const history = await db
      .select()
      .from(conversations)
      .where(eq(conversations.faculty, "brain"))
      .orderBy(desc(conversations.createdAt))
      .limit(100);

    res.json(history.reverse());
  } catch (err) {
    res.status(500).json({ error: "Failed to load history" });
  }
});

router.post("/chat", async (req, res) => {
  try {
    const { message, history = [] } = req.body as {
      message: string;
      history?: Message[];
    };

    if (!message) {
      res.status(400).json({ error: "Message is required" });
      return;
    }

    const faculty = routeMessageLocal(message);
    const skillMap: Record<string, string[]> = {
      thinking: ["code-review"],
      financial: ["financial-tracking"],
      meetings: ["meeting-processing"],
      memory: ["knowledge-management"],
      habits: [],
      health: [],
    };

    if (!isLLMConfigured()) {
      res.setHeader("Content-Type", "text/event-stream");
      res.setHeader("Cache-Control", "no-cache");
      res.setHeader("Connection", "keep-alive");

      const fallback = `I'm your digital clone, but my brain isn't connected yet.\n\n**Two ways to connect:**\n1. **CLI mode** — Install Claude CLI: \`npm install -g @anthropic-ai/claude-code\` then \`claude auth login\`\n2. **API mode** — Add your API key to \`dna/.env\`: \`ANTHROPIC_API_KEY=sk-ant-...\`\n\nGo to **Settings** to configure.\n\n**Routed to**: ${faculty} faculty\n**Skills loaded**: ${skillMap[faculty]?.join(", ") || "none"}`;

      res.write(`data: ${JSON.stringify({ text: fallback, faculty, done: false })}\n\n`);
      res.write(`data: ${JSON.stringify({ text: "", faculty, done: true })}\n\n`);
      res.end();
      return;
    }

    const db = getDB();

    await db.insert(conversations).values({
      faculty: "brain",
      role: "user",
      content: message,
      createdAt: new Date().toISOString(),
    });

    const messages: Message[] = [
      ...history.slice(-20),
      { role: "user" as const, content: message },
    ];

    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");

    let fullResponse = "";

    for await (const chunk of chatStream(faculty, messages, {
      skills: skillMap[faculty],
    })) {
      fullResponse += chunk;
      res.write(
        `data: ${JSON.stringify({ text: chunk, faculty, done: false })}\n\n`
      );
    }

    await db.insert(conversations).values({
      faculty: "brain",
      role: "assistant",
      content: fullResponse,
      createdAt: new Date().toISOString(),
    });

    res.write(
      `data: ${JSON.stringify({ text: "", faculty, done: true })}\n\n`
    );
    res.end();
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : "Unknown error";
    if (!res.headersSent) {
      res.status(500).json({ error: errorMsg });
    } else {
      res.write(
        `data: ${JSON.stringify({ error: errorMsg, done: true })}\n\n`
      );
      res.end();
    }
  }
});

router.delete("/history", async (_req, res) => {
  try {
    const db = getDB();
    await db.delete(conversations).where(eq(conversations.faculty, "brain"));
    res.json({ cleared: true });
  } catch {
    res.status(500).json({ error: "Failed to clear history" });
  }
});

export default router;
