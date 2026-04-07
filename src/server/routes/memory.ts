import { Router } from "express";
import {
  storeMemory,
  searchMemories,
  getAllMemories,
  getMemoryById,
  updateMemory,
  deleteMemory,
  getMemoryStats,
} from "../services/memory-store.js";

const router = Router();

router.get("/status", async (_req, res) => {
  const stats = await getMemoryStats();
  res.json({ status: "ok", faculty: "memory", ...stats });
});

router.get("/", async (req, res) => {
  try {
    const query = req.query.q as string | undefined;
    const limit = parseInt(req.query.limit as string) || 50;

    const results = query
      ? await searchMemories(query, limit)
      : await getAllMemories(limit);

    res.json(results);
  } catch {
    res.status(500).json({ error: "Failed to retrieve memories" });
  }
});

router.get("/stats", async (_req, res) => {
  try {
    const stats = await getMemoryStats();
    res.json(stats);
  } catch {
    res.status(500).json({ error: "Failed to get stats" });
  }
});

router.get("/:id", async (req, res) => {
  try {
    const memory = await getMemoryById(parseInt(req.params.id));
    if (!memory) {
      res.status(404).json({ error: "Memory not found" });
      return;
    }
    res.json(memory);
  } catch {
    res.status(500).json({ error: "Failed to retrieve memory" });
  }
});

router.post("/", async (req, res) => {
  try {
    const { title, content, type, tags, importance } = req.body;
    if (!title || !content) {
      res.status(400).json({ error: "Title and content are required" });
      return;
    }
    const memory = await storeMemory({ title, content, type, tags, importance });
    res.status(201).json(memory);
  } catch {
    res.status(500).json({ error: "Failed to store memory" });
  }
});

router.put("/:id", async (req, res) => {
  try {
    const updated = await updateMemory(parseInt(req.params.id), req.body);
    res.json(updated[0]);
  } catch {
    res.status(500).json({ error: "Failed to update memory" });
  }
});

router.delete("/:id", async (req, res) => {
  try {
    await deleteMemory(parseInt(req.params.id));
    res.json({ deleted: true });
  } catch {
    res.status(500).json({ error: "Failed to delete memory" });
  }
});

export default router;
