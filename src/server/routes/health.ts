import { Router } from "express";
import { isLLMConfigured, getConnectionStatus } from "../services/llm.js";
import { getDB } from "../db/index.js";
import { memories, conversations, transactions, loans, meetings, habits } from "../db/schema.js";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import yaml from "js-yaml";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, "../../..");

const router = Router();

router.get("/", async (_req, res) => {
  try {
    const db = getDB();

    const [memCount, convCount, txCount, loanCount, meetCount, habitCount] =
      await Promise.all([
        db.select().from(memories),
        db.select().from(conversations),
        db.select().from(transactions),
        db.select().from(loans),
        db.select().from(meetings),
        db.select().from(habits),
      ]);

    const identityPath = path.join(ROOT, "dna", "identity.yaml");
    let dnaLoaded = false;
    let dnaName = "Unknown";
    try {
      const identity = yaml.load(fs.readFileSync(identityPath, "utf-8")) as Record<string, unknown>;
      dnaLoaded = true;
      dnaName = (identity.name as string) || "Unknown";
    } catch {}

    const faculties = {
      brain: {
        status: isLLMConfigured() ? "healthy" : "degraded",
        message: isLLMConfigured()
          ? `${convCount.length} conversations`
          : "LLM not configured — add ANTHROPIC_API_KEY",
        conversations: convCount.length,
      },
      memory: {
        status: "healthy",
        message: `${memCount.length} memories stored`,
        count: memCount.length,
      },
      financial: {
        status: "healthy",
        message: `${txCount.length} transactions, ${loanCount.length} loans`,
        transactions: txCount.length,
        loans: loanCount.length,
      },
      meetings: {
        status: "healthy",
        message: `${meetCount.length} meetings`,
        count: meetCount.length,
      },
      habits: {
        status: "healthy",
        message: `${habitCount.filter((h) => h.enabled).length}/${habitCount.length} active`,
        active: habitCount.filter((h) => h.enabled).length,
        total: habitCount.length,
      },
    };

    const allHealthy = Object.values(faculties).every(
      (f) => f.status === "healthy"
    );

    const connection = getConnectionStatus();

    res.json({
      alive: true,
      name: dnaName,
      dnaLoaded,
      llmConfigured: isLLMConfigured(),
      connection,
      status: allHealthy ? "healthy" : "degraded",
      timestamp: new Date().toISOString(),
      faculties,
    });
  } catch (err) {
    res.status(500).json({
      alive: true,
      status: "unhealthy",
      error: err instanceof Error ? err.message : "Unknown error",
    });
  }
});

export default router;
