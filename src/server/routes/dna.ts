import { Router } from "express";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import yaml from "js-yaml";

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

export default router;
