import { createClient } from "@libsql/client";
import { drizzle } from "drizzle-orm/libsql";
import path from "path";
import { fileURLToPath } from "url";
import fs from "fs";
import * as schema from "./schema.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, "../../..");

const DB_PATH = path.join(ROOT, "data", "humanos.db");

let db: ReturnType<typeof drizzle<typeof schema>>;

export function initDB() {
  const dataDir = path.dirname(DB_PATH);
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }

  const client = createClient({
    url: `file:${DB_PATH}`,
  });

  db = drizzle(client, { schema });

  client.executeMultiple(`
    CREATE TABLE IF NOT EXISTS memories (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      type TEXT NOT NULL DEFAULT 'general',
      title TEXT NOT NULL,
      content TEXT NOT NULL,
      tags TEXT DEFAULT '',
      importance INTEGER DEFAULT 5,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS conversations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      faculty TEXT NOT NULL DEFAULT 'brain',
      role TEXT NOT NULL,
      content TEXT NOT NULL,
      created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS transactions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      type TEXT NOT NULL,
      category TEXT NOT NULL,
      amount REAL NOT NULL,
      currency TEXT NOT NULL DEFAULT 'LKR',
      description TEXT DEFAULT '',
      date TEXT NOT NULL,
      recurring INTEGER DEFAULT 0,
      recurring_period TEXT,
      created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS loans (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      total_amount REAL NOT NULL,
      remaining_amount REAL NOT NULL,
      monthly_payment REAL DEFAULT 0,
      interest_rate REAL DEFAULT 0,
      due_date TEXT,
      status TEXT NOT NULL DEFAULT 'active',
      created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS meetings (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      date TEXT NOT NULL,
      transcript TEXT,
      summary TEXT,
      action_items TEXT,
      attendees TEXT,
      status TEXT NOT NULL DEFAULT 'pending',
      created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS habits (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      description TEXT,
      schedule TEXT NOT NULL,
      prompt TEXT NOT NULL,
      faculty TEXT NOT NULL DEFAULT 'brain',
      enabled INTEGER DEFAULT 1,
      last_run TEXT,
      created_at TEXT NOT NULL
    );
  `);

  console.log("🧠 Database initialized at", DB_PATH);
  return db;
}

export function getDB() {
  if (!db) throw new Error("Database not initialized. Call initDB() first.");
  return db;
}
