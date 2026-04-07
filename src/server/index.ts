import express from "express";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";
import dotenv from "dotenv";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, "../..");

dotenv.config({ path: path.join(ROOT, "dna", ".env") });

import { initDB } from "./db/index.js";
import { seedDefaultHabits, initHabits } from "./services/habit-scheduler.js";
import { checkCliAvailable, getConnectionStatus } from "./services/llm.js";
import brainRoutes from "./routes/brain.js";
import memoryRoutes from "./routes/memory.js";
import financialRoutes from "./routes/financial.js";
import meetingsRoutes from "./routes/meetings.js";
import habitsRoutes from "./routes/habits.js";
import healthRoutes from "./routes/health.js";
import dnaRoutes from "./routes/dna.js";

const app = express();
const PORT = parseInt(process.env.PORT || "3001", 10);

app.use(cors());
app.use(express.json({ limit: "10mb" }));

initDB();
seedDefaultHabits().then(() => initHabits());

app.use("/api/brain", brainRoutes);
app.use("/api/memory", memoryRoutes);
app.use("/api/financial", financialRoutes);
app.use("/api/meetings", meetingsRoutes);
app.use("/api/habits", habitsRoutes);
app.use("/api/health", healthRoutes);
app.use("/api/dna", dnaRoutes);

const distClient = path.join(ROOT, "dist", "client");
app.use(express.static(distClient));
app.get("/{*splat}", (_req, res) => {
  res.sendFile(path.join(distClient, "index.html"));
});

app.listen(PORT, async () => {
  await checkCliAvailable();
  const conn = getConnectionStatus();

  console.log(`\n🧬 HumanOS is alive on http://localhost:${PORT}`);
  console.log(`   DNA loaded from: ${path.join(ROOT, "dna")}`);
  console.log(`   Mind loaded from: ${path.join(ROOT, "mind")}`);
  console.log(`   Skills loaded from: ${path.join(ROOT, "skills")}`);
  console.log(`   🔌 Connection: ${conn.mode.toUpperCase()} — ${conn.details}\n`);
});

export default app;
