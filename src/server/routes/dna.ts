import { Router } from "express";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import yaml from "js-yaml";
import { getConnectionStatus, checkCliAvailable, chat } from "../services/llm.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, "../../..");

const router = Router();

router.get("/", (_req, res) => {
  try {
    const identityPath = path.join(ROOT, "dna", "identity.yaml");
    const personalityPath = path.join(ROOT, "dna", "personality.md");

    const identity = fs.existsSync(identityPath)
      ? yaml.load(fs.readFileSync(identityPath, "utf-8"))
      : {};

    const personality = fs.existsSync(personalityPath)
      ? fs.readFileSync(personalityPath, "utf-8")
      : "";

    res.json({ identity, personality });
  } catch (err) {
    res.status(500).json({ error: "Failed to read DNA" });
  }
});

router.put("/", (req, res) => {
  try {
    const { identity, personality } = req.body;
    const identityPath = path.join(ROOT, "dna", "identity.yaml");
    const personalityPath = path.join(ROOT, "dna", "personality.md");

    if (identity) {
      fs.writeFileSync(identityPath, yaml.dump(identity), "utf-8");
    }
    if (personality !== undefined) {
      fs.writeFileSync(personalityPath, personality, "utf-8");
    }

    res.json({ saved: true });
  } catch (err) {
    res.status(500).json({ error: "Failed to save DNA" });
  }
});

router.get("/connection", async (_req, res) => {
  const cliAvailable = await checkCliAvailable();
  const status = getConnectionStatus();
  res.json({ ...status, cliAvailable });
});

router.post("/connection/test", async (_req, res) => {
  try {
    const result = await chat("consciousness", [
      { role: "user", content: "Say 'Hello, I am alive!' in one short sentence." },
    ], { maxTokens: 50 });
    res.json({ success: true, response: result });
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : "Unknown error";
    res.json({ success: false, error: msg });
  }
});

router.put("/connection/mode", (req, res) => {
  const { mode } = req.body;
  if (!["api", "cli"].includes(mode)) {
    res.status(400).json({ error: "Mode must be 'api' or 'cli'" });
    return;
  }

  const envPath = path.join(ROOT, "dna", ".env");
  let envContent = "";
  if (fs.existsSync(envPath)) {
    envContent = fs.readFileSync(envPath, "utf-8");
  }

  if (/^LLM_MODE=.*/m.test(envContent)) {
    envContent = envContent.replace(/^LLM_MODE=.*/m, `LLM_MODE=${mode}`);
  } else {
    envContent = `LLM_MODE=${mode}\n${envContent}`;
  }

  fs.writeFileSync(envPath, envContent, "utf-8");
  process.env.LLM_MODE = mode;

  res.json({ saved: true, mode });
});

router.put("/connection/apikey", (req, res) => {
  const { apiKey } = req.body;
  if (!apiKey) {
    res.status(400).json({ error: "apiKey is required" });
    return;
  }

  const envPath = path.join(ROOT, "dna", ".env");
  let envContent = "";
  if (fs.existsSync(envPath)) {
    envContent = fs.readFileSync(envPath, "utf-8");
  }

  if (/^ANTHROPIC_API_KEY=.*/m.test(envContent)) {
    envContent = envContent.replace(/^ANTHROPIC_API_KEY=.*/m, `ANTHROPIC_API_KEY=${apiKey}`);
  } else {
    envContent += `\nANTHROPIC_API_KEY=${apiKey}`;
  }

  fs.writeFileSync(envPath, envContent, "utf-8");
  process.env.ANTHROPIC_API_KEY = apiKey;

  res.json({ saved: true });
});

export default router;
