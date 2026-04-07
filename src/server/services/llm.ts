import Anthropic from "@anthropic-ai/sdk";
import { spawn } from "child_process";
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

export type ConnectionMode = "api" | "cli";

let client: Anthropic | null = null;
let _cliAvailable: boolean | null = null;

function getConnectionMode(): ConnectionMode {
  const mode = process.env.LLM_MODE?.toLowerCase();
  if (mode === "cli") return "cli";
  if (mode === "api") return "api";
  if (process.env.ANTHROPIC_API_KEY && !process.env.ANTHROPIC_API_KEY.startsWith("sk-ant-...")) {
    return "api";
  }
  return "cli";
}

function getApiClient(): Anthropic {
  if (!client) {
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey || apiKey.startsWith("sk-ant-...")) {
      throw new Error(
        "ANTHROPIC_API_KEY not set. Copy dna/.env.example to dna/.env and add your key, or switch to CLI mode."
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

// ── CLI mode helpers ──────────────────────────────────────────────

function runClaude(args: string[], stdin?: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const proc = spawn("claude", args, {
      stdio: ["pipe", "pipe", "pipe"],
      shell: true,
    });

    let stdout = "";
    let stderr = "";

    proc.stdout.on("data", (data: Buffer) => {
      stdout += data.toString();
    });
    proc.stderr.on("data", (data: Buffer) => {
      stderr += data.toString();
    });

    if (stdin) {
      proc.stdin.write(stdin);
      proc.stdin.end();
    }

    proc.on("close", (code) => {
      if (code === 0) {
        resolve(stdout.trim());
      } else {
        reject(new Error(`Claude CLI exited with code ${code}: ${stderr || stdout}`));
      }
    });

    proc.on("error", (err) => {
      reject(new Error(`Claude CLI not found. Install it with: npm install -g @anthropic-ai/claude-code\n${err.message}`));
    });
  });
}

function streamClaude(
  args: string[],
  stdin?: string
): { stdout: NodeJS.ReadableStream; process: ReturnType<typeof spawn> } {
  const proc = spawn("claude", args, {
    stdio: ["pipe", "pipe", "pipe"],
    shell: true,
  });

  if (stdin) {
    proc.stdin.write(stdin);
    proc.stdin.end();
  }

  return { stdout: proc.stdout, process: proc };
}

export async function checkCliAvailable(): Promise<boolean> {
  if (_cliAvailable !== null) return _cliAvailable;
  try {
    await runClaude(["--version"]);
    _cliAvailable = true;
  } catch {
    _cliAvailable = false;
  }
  return _cliAvailable;
}

// ── Unified chat functions ────────────────────────────────────────

export async function chat(
  faculty: Faculty,
  messages: Message[],
  options?: {
    extraContext?: string;
    skills?: string[];
    maxTokens?: number;
  }
): Promise<string> {
  const mode = getConnectionMode();
  const systemPrompt = buildSystemPrompt(
    faculty,
    options?.extraContext,
    options?.skills
  );

  if (mode === "cli") {
    return chatViaCli(systemPrompt, messages, options?.maxTokens);
  }
  return chatViaApi(systemPrompt, messages, options?.maxTokens);
}

async function chatViaApi(
  systemPrompt: string,
  messages: Message[],
  maxTokens?: number
): Promise<string> {
  const c = getApiClient();
  const model = process.env.ANTHROPIC_MODEL || "claude-sonnet-4-20250514";

  const response = await c.messages.create({
    model,
    max_tokens: maxTokens || 4096,
    system: systemPrompt,
    messages,
  });

  const textBlock = response.content.find((b) => b.type === "text");
  return textBlock ? textBlock.text : "";
}

async function chatViaCli(
  systemPrompt: string,
  messages: Message[],
  _maxTokens?: number
): Promise<string> {
  const lastUserMsg = [...messages].reverse().find((m) => m.role === "user");
  if (!lastUserMsg) throw new Error("No user message found");

  const conversationContext = messages
    .slice(0, -1)
    .map((m) => `${m.role === "user" ? "Human" : "Assistant"}: ${m.content}`)
    .join("\n\n");

  const fullPrompt = conversationContext
    ? `Previous conversation:\n${conversationContext}\n\nHuman: ${lastUserMsg.content}`
    : lastUserMsg.content;

  const model = process.env.ANTHROPIC_MODEL || "";
  const args = ["--print", "--system-prompt", systemPrompt];
  if (model) args.push("--model", model);

  return runClaude(args, fullPrompt);
}

// ── Unified stream functions ──────────────────────────────────────

export async function* chatStream(
  faculty: Faculty,
  messages: Message[],
  options?: {
    extraContext?: string;
    skills?: string[];
    maxTokens?: number;
  }
): AsyncGenerator<string> {
  const mode = getConnectionMode();
  const systemPrompt = buildSystemPrompt(
    faculty,
    options?.extraContext,
    options?.skills
  );

  if (mode === "cli") {
    yield* streamViaCli(systemPrompt, messages);
  } else {
    yield* streamViaApi(systemPrompt, messages, options?.maxTokens);
  }
}

async function* streamViaApi(
  systemPrompt: string,
  messages: Message[],
  maxTokens?: number
): AsyncGenerator<string> {
  const c = getApiClient();
  const model = process.env.ANTHROPIC_MODEL || "claude-sonnet-4-20250514";

  const stream = c.messages.stream({
    model,
    max_tokens: maxTokens || 4096,
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

async function* streamViaCli(
  systemPrompt: string,
  messages: Message[]
): AsyncGenerator<string> {
  const lastUserMsg = [...messages].reverse().find((m) => m.role === "user");
  if (!lastUserMsg) throw new Error("No user message found");

  const conversationContext = messages
    .slice(0, -1)
    .map((m) => `${m.role === "user" ? "Human" : "Assistant"}: ${m.content}`)
    .join("\n\n");

  const fullPrompt = conversationContext
    ? `Previous conversation:\n${conversationContext}\n\nHuman: ${lastUserMsg.content}`
    : lastUserMsg.content;

  const model = process.env.ANTHROPIC_MODEL || "";
  const args = ["--print", "--system-prompt", systemPrompt];
  if (model) args.push("--model", model);

  const { stdout, process: proc } = streamClaude(args, fullPrompt);

  const iterator = stdout[Symbol.asyncIterator]
    ? stdout[Symbol.asyncIterator]()
    : (async function* () {
        for await (const chunk of stdout as AsyncIterable<Buffer>) {
          yield chunk;
        }
      })();

  try {
    for await (const chunk of iterator) {
      yield chunk.toString();
    }
  } catch (err) {
    const exitCode = await new Promise<number | null>((resolve) => {
      proc.on("close", resolve);
      proc.on("error", () => resolve(null));
    });
    if (exitCode !== 0) {
      throw new Error(`Claude CLI streaming failed (exit code ${exitCode})`);
    }
  }
}

// ── Status helpers ────────────────────────────────────────────────

export function isLLMConfigured(): boolean {
  const mode = getConnectionMode();
  if (mode === "api") {
    const key = process.env.ANTHROPIC_API_KEY;
    return !!key && !key.startsWith("sk-ant-...");
  }
  return _cliAvailable === true;
}

export function getConnectionStatus(): {
  mode: ConnectionMode;
  configured: boolean;
  details: string;
} {
  const mode = getConnectionMode();

  if (mode === "api") {
    const key = process.env.ANTHROPIC_API_KEY;
    const configured = !!key && !key.startsWith("sk-ant-...");
    return {
      mode: "api",
      configured,
      details: configured
        ? `API key set (${key!.slice(0, 10)}...)`
        : "No API key — add ANTHROPIC_API_KEY to dna/.env",
    };
  }

  return {
    mode: "cli",
    configured: _cliAvailable === true,
    details:
      _cliAvailable === true
        ? "Claude CLI detected and ready"
        : _cliAvailable === false
          ? "Claude CLI not found — install: npm install -g @anthropic-ai/claude-code"
          : "Checking CLI availability...",
  };
}
