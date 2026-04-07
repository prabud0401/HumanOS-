import Anthropic from "@anthropic-ai/sdk";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import yaml from "js-yaml";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, "../../..");

type Faculty =
  | "consciousness"
  | "thinking"
  | "memory"
  | "financial"
  | "meetings"
  | "habits"
  | "health";

let client: Anthropic | null = null;

function getClient(): Anthropic {
  if (!client) {
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey || apiKey.startsWith("sk-ant-...")) {
      throw new Error(
        "ANTHROPIC_API_KEY not set. Copy dna/.env.example to dna/.env and add your key."
      );
    }
    client = new Anthropic({ apiKey });
  }
  return client;
}

function readFile(relativePath: string): string {
  const fullPath = path.join(ROOT, relativePath);
  if (!fs.existsSync(fullPath)) return "";
  return fs.readFileSync(fullPath, "utf-8");
}

function loadDNA(): { identity: Record<string, unknown>; personality: string } {
  const identityRaw = readFile("dna/identity.yaml");
  const identity = identityRaw ? (yaml.load(identityRaw) as Record<string, unknown>) : {};
  const personality = readFile("dna/personality.md");
  return { identity, personality };
}

function loadMind(faculty: Faculty): string {
  return readFile(`mind/${faculty}.md`);
}

function loadSkills(skillNames: string[]): string {
  return skillNames
    .map((name) => readFile(`skills/${name}.md`))
    .filter(Boolean)
    .join("\n\n---\n\n");
}

export function buildSystemPrompt(
  faculty: Faculty,
  extraContext?: string,
  skillNames?: string[]
): string {
  const { identity, personality } = loadDNA();
  const mindPrompt = loadMind(faculty);
  const skillsText = skillNames ? loadSkills(skillNames) : "";

  const parts: string[] = [];

  parts.push(`# DNA — Who You Are\n\n${yaml.dump(identity)}`);
  parts.push(personality);
  parts.push(mindPrompt);

  if (skillsText) {
    parts.push(`# Active Skills\n\n${skillsText}`);
  }

  if (extraContext) {
    parts.push(`# Additional Context\n\n${extraContext}`);
  }

  return parts.filter(Boolean).join("\n\n---\n\n");
}

export type Message = { role: "user" | "assistant"; content: string };

export async function chat(
  faculty: Faculty,
  messages: Message[],
  options?: {
    extraContext?: string;
    skills?: string[];
    maxTokens?: number;
  }
): Promise<string> {
  const client = getClient();
  const model = process.env.ANTHROPIC_MODEL || "claude-sonnet-4-20250514";
  const systemPrompt = buildSystemPrompt(
    faculty,
    options?.extraContext,
    options?.skills
  );

  const response = await client.messages.create({
    model,
    max_tokens: options?.maxTokens || 4096,
    system: systemPrompt,
    messages,
  });

  const textBlock = response.content.find((b) => b.type === "text");
  return textBlock ? textBlock.text : "";
}

export async function* chatStream(
  faculty: Faculty,
  messages: Message[],
  options?: {
    extraContext?: string;
    skills?: string[];
    maxTokens?: number;
  }
): AsyncGenerator<string> {
  const client = getClient();
  const model = process.env.ANTHROPIC_MODEL || "claude-sonnet-4-20250514";
  const systemPrompt = buildSystemPrompt(
    faculty,
    options?.extraContext,
    options?.skills
  );

  const stream = client.messages.stream({
    model,
    max_tokens: options?.maxTokens || 4096,
    system: systemPrompt,
    messages,
  });

  for await (const event of stream) {
    if (
      event.type === "content_block_delta" &&
      event.delta.type === "text_delta"
    ) {
      yield event.delta.text;
    }
  }
}

export function isLLMConfigured(): boolean {
  const key = process.env.ANTHROPIC_API_KEY;
  return !!key && !key.startsWith("sk-ant-...");
}
