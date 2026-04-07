import { getDB } from "../db/index.js";
import { memories } from "../db/schema.js";
import { eq, like, or, desc } from "drizzle-orm";

export interface MemoryInput {
  type?: string;
  title: string;
  content: string;
  tags?: string;
  importance?: number;
}

export async function storeMemory(input: MemoryInput) {
  const db = getDB();
  const now = new Date().toISOString();
  const result = await db
    .insert(memories)
    .values({
      type: input.type || "general",
      title: input.title,
      content: input.content,
      tags: input.tags || "",
      importance: input.importance || 5,
      createdAt: now,
      updatedAt: now,
    })
    .returning();
  return result[0];
}

export async function searchMemories(query: string, limit = 20) {
  const db = getDB();
  const pattern = `%${query}%`;
  return db
    .select()
    .from(memories)
    .where(
      or(
        like(memories.title, pattern),
        like(memories.content, pattern),
        like(memories.tags, pattern)
      )
    )
    .orderBy(desc(memories.importance))
    .limit(limit);
}

export async function getAllMemories(limit = 50) {
  const db = getDB();
  return db
    .select()
    .from(memories)
    .orderBy(desc(memories.createdAt))
    .limit(limit);
}

export async function getMemoryById(id: number) {
  const db = getDB();
  const results = await db
    .select()
    .from(memories)
    .where(eq(memories.id, id))
    .limit(1);
  return results[0] || null;
}

export async function updateMemory(
  id: number,
  updates: Partial<MemoryInput>
) {
  const db = getDB();
  return db
    .update(memories)
    .set({
      ...updates,
      updatedAt: new Date().toISOString(),
    })
    .where(eq(memories.id, id))
    .returning();
}

export async function deleteMemory(id: number) {
  const db = getDB();
  return db.delete(memories).where(eq(memories.id, id));
}

export async function getMemoryStats() {
  const db = getDB();
  const all = await db.select().from(memories);
  const types: Record<string, number> = {};
  for (const m of all) {
    types[m.type] = (types[m.type] || 0) + 1;
  }
  return {
    total: all.length,
    byType: types,
    avgImportance: all.length
      ? all.reduce((sum, m) => sum + (m.importance || 0), 0) / all.length
      : 0,
  };
}
