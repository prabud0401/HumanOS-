import { sqliteTable, text, integer, real } from "drizzle-orm/sqlite-core";

export const memories = sqliteTable("memories", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  type: text("type").notNull().default("general"),
  title: text("title").notNull(),
  content: text("content").notNull(),
  tags: text("tags").default(""),
  importance: integer("importance").default(5),
  createdAt: text("created_at")
    .notNull()
    .$defaultFn(() => new Date().toISOString()),
  updatedAt: text("updated_at")
    .notNull()
    .$defaultFn(() => new Date().toISOString()),
});

export const conversations = sqliteTable("conversations", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  faculty: text("faculty").notNull().default("brain"),
  role: text("role").notNull(),
  content: text("content").notNull(),
  createdAt: text("created_at")
    .notNull()
    .$defaultFn(() => new Date().toISOString()),
});

export const transactions = sqliteTable("transactions", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  type: text("type").notNull(),
  category: text("category").notNull(),
  amount: real("amount").notNull(),
  currency: text("currency").notNull().default("LKR"),
  description: text("description").default(""),
  date: text("date").notNull(),
  recurring: integer("recurring", { mode: "boolean" }).default(false),
  recurringPeriod: text("recurring_period"),
  createdAt: text("created_at")
    .notNull()
    .$defaultFn(() => new Date().toISOString()),
});

export const loans = sqliteTable("loans", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  name: text("name").notNull(),
  totalAmount: real("total_amount").notNull(),
  remainingAmount: real("remaining_amount").notNull(),
  monthlyPayment: real("monthly_payment").default(0),
  interestRate: real("interest_rate").default(0),
  dueDate: text("due_date"),
  status: text("status").notNull().default("active"),
  createdAt: text("created_at")
    .notNull()
    .$defaultFn(() => new Date().toISOString()),
});

export const meetings = sqliteTable("meetings", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  title: text("title").notNull(),
  date: text("date").notNull(),
  transcript: text("transcript"),
  summary: text("summary"),
  actionItems: text("action_items"),
  attendees: text("attendees"),
  status: text("status").notNull().default("pending"),
  createdAt: text("created_at")
    .notNull()
    .$defaultFn(() => new Date().toISOString()),
});

export const habits = sqliteTable("habits", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  name: text("name").notNull(),
  description: text("description"),
  schedule: text("schedule").notNull(),
  prompt: text("prompt").notNull(),
  faculty: text("faculty").notNull().default("brain"),
  enabled: integer("enabled", { mode: "boolean" }).default(true),
  lastRun: text("last_run"),
  createdAt: text("created_at")
    .notNull()
    .$defaultFn(() => new Date().toISOString()),
});
