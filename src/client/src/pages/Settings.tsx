import { useState, useEffect } from "react";

interface DNAData {
  identity: Record<string, unknown>;
  personality: string;
}

interface ConnectionData {
  mode: "api" | "cli";
  configured: boolean;
  details: string;
  cliAvailable: boolean;
}

export default function Settings() {
  const [dna, setDna] = useState<DNAData | null>(null);
  const [personalityText, setPersonalityText] = useState("");
  const [identityFields, setIdentityFields] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const [connection, setConnection] = useState<ConnectionData | null>(null);
  const [apiKeyInput, setApiKeyInput] = useState("");
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  useEffect(() => {
    loadDNA();
    loadConnection();
  }, []);

  async function loadDNA() {
    try {
      const res = await fetch("/api/dna");
      const data: DNAData = await res.json();
      setDna(data);
      setPersonalityText(data.personality);

      const flat: Record<string, string> = {};
      for (const [key, val] of Object.entries(data.identity)) {
        flat[key] = Array.isArray(val) ? val.join(", ") : String(val || "");
      }
      setIdentityFields(flat);
    } catch {
      setDna(null);
    }
  }

  async function loadConnection() {
    try {
      const res = await fetch("/api/dna/connection");
      setConnection(await res.json());
    } catch {}
  }

  async function switchMode(mode: "api" | "cli") {
    await fetch("/api/dna/connection/mode", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode }),
    });
    setTestResult(null);
    loadConnection();
  }

  async function saveApiKey() {
    if (!apiKeyInput.trim()) return;
    await fetch("/api/dna/connection/apikey", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ apiKey: apiKeyInput.trim() }),
    });
    setApiKeyInput("");
    loadConnection();
  }

  async function testConnection() {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await fetch("/api/dna/connection/test", { method: "POST" });
      const data = await res.json();
      setTestResult({
        success: data.success,
        message: data.success ? `Brain responded: "${data.response}"` : data.error,
      });
    } catch {
      setTestResult({ success: false, message: "Could not reach the server" });
    } finally {
      setTesting(false);
    }
  }

  async function handleSave() {
    setSaving(true);
    setSaved(false);

    const identity: Record<string, unknown> = {};
    for (const [key, val] of Object.entries(identityFields)) {
      if (["values", "goals", "languages", "interests"].includes(key)) {
        identity[key] = val.split(",").map((v) => v.trim()).filter(Boolean);
      } else {
        identity[key] = val;
      }
    }

    await fetch("/api/dna", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ identity, personality: personalityText }),
    });

    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  }

  const fieldLabels: Record<string, string> = {
    name: "Name",
    full_name: "Full Name",
    background: "Background",
    values: "Values (comma-separated)",
    goals: "Goals (comma-separated)",
    communication_style: "Communication Style",
    languages: "Languages (comma-separated)",
    timezone: "Timezone",
    interests: "Interests (comma-separated)",
  };

  const fieldOrder = [
    "name", "full_name", "background", "values", "goals",
    "communication_style", "languages", "timezone", "interests",
  ];

  return (
    <div className="p-6 max-w-3xl">
      <h2 className="text-2xl font-bold mb-2">Settings</h2>
      <p className="text-gray-400 text-sm mb-6">Edit your DNA and brain connection.</p>

      {/* ── Brain Connection ────────────────────────────────── */}
      <div className="bg-gray-900 rounded-xl p-5 border border-gray-800 mb-6">
        <h3 className="text-lg font-semibold mb-4">🔌 Brain Connection</h3>
        <p className="text-sm text-gray-400 mb-4">
          Choose how your clone's brain connects to Claude.
        </p>

        <div className="grid grid-cols-2 gap-3 mb-4">
          {/* CLI option */}
          <button
            onClick={() => switchMode("cli")}
            className={`rounded-xl p-4 border text-left transition-all ${
              connection?.mode === "cli"
                ? "border-bio-500 bg-bio-950/30"
                : "border-gray-700 bg-gray-800 hover:border-gray-600"
            }`}
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="text-lg">⌨️</span>
              <span className="font-semibold text-sm">CLI Mode</span>
              {connection?.mode === "cli" && (
                <span className="text-xs bg-bio-600 text-white px-2 py-0.5 rounded">Active</span>
              )}
            </div>
            <p className="text-xs text-gray-400">
              Uses your local Claude CLI. No API key needed — uses your Claude subscription.
            </p>
            <div className="mt-2">
              {connection?.cliAvailable ? (
                <span className="text-xs text-green-400">Claude CLI detected</span>
              ) : (
                <span className="text-xs text-yellow-400">CLI not found</span>
              )}
            </div>
          </button>

          {/* API option */}
          <button
            onClick={() => switchMode("api")}
            className={`rounded-xl p-4 border text-left transition-all ${
              connection?.mode === "api"
                ? "border-neural-500 bg-neural-950/30"
                : "border-gray-700 bg-gray-800 hover:border-gray-600"
            }`}
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="text-lg">🔑</span>
              <span className="font-semibold text-sm">API Mode</span>
              {connection?.mode === "api" && (
                <span className="text-xs bg-neural-600 text-white px-2 py-0.5 rounded">Active</span>
              )}
            </div>
            <p className="text-xs text-gray-400">
              Uses Anthropic API directly. Requires an API key. Pay per token.
            </p>
            <div className="mt-2">
              {connection?.mode === "api" && connection.configured ? (
                <span className="text-xs text-green-400">{connection.details}</span>
              ) : (
                <span className="text-xs text-gray-500">Needs API key</span>
              )}
            </div>
          </button>
        </div>

        {/* Mode-specific setup */}
        {connection?.mode === "cli" && !connection.cliAvailable && (
          <div className="bg-yellow-950/30 border border-yellow-800 rounded-lg p-4 mb-4">
            <p className="text-sm text-yellow-300 font-medium mb-2">Install Claude CLI</p>
            <div className="bg-gray-900 rounded-lg p-3 font-mono text-xs text-gray-300 space-y-1">
              <p>npm install -g @anthropic-ai/claude-code</p>
              <p>claude auth login</p>
            </div>
            <p className="text-xs text-yellow-500 mt-2">
              After installing, restart HumanOS and it will auto-detect the CLI.
            </p>
          </div>
        )}

        {connection?.mode === "api" && (
          <div className="mb-4">
            <label className="block text-xs text-gray-400 mb-1">Anthropic API Key</label>
            <div className="flex gap-2">
              <input
                type="password"
                value={apiKeyInput}
                onChange={(e) => setApiKeyInput(e.target.value)}
                placeholder={connection.configured ? "••••••••••• (saved)" : "sk-ant-..."}
                className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-neural-500 font-mono"
              />
              <button
                onClick={saveApiKey}
                disabled={!apiKeyInput.trim()}
                className="bg-neural-700 hover:bg-neural-600 disabled:bg-gray-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                Save Key
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Get your key at{" "}
              <a href="https://console.anthropic.com" target="_blank" rel="noopener" className="text-neural-400 underline">
                console.anthropic.com
              </a>
            </p>
          </div>
        )}

        {/* Connection status + test */}
        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm ${
            connection?.configured
              ? "bg-green-950/30 border border-green-800 text-green-300"
              : "bg-gray-800 border border-gray-700 text-gray-400"
          }`}>
            <span className={`w-2 h-2 rounded-full ${connection?.configured ? "bg-green-400 animate-pulse" : "bg-gray-600"}`} />
            {connection?.configured ? "Connected" : "Not connected"}
            <span className="text-xs opacity-60">({connection?.mode.toUpperCase()})</span>
          </div>

          <button
            onClick={testConnection}
            disabled={testing}
            className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-sm transition-colors"
          >
            {testing ? "Testing..." : "Test Connection"}
          </button>
        </div>

        {testResult && (
          <div className={`mt-3 rounded-lg p-3 text-sm ${
            testResult.success
              ? "bg-green-950/30 border border-green-800 text-green-300"
              : "bg-red-950/30 border border-red-800 text-red-300"
          }`}>
            {testResult.success ? "✅ " : "❌ "}{testResult.message}
          </div>
        )}
      </div>

      {/* ── DNA Identity ────────────────────────────────────── */}
      {!dna && (
        <div className="text-gray-500">Loading DNA...</div>
      )}

      {dna && (
        <>
          <div className="bg-gray-900 rounded-xl p-5 border border-gray-800 mb-6">
            <h3 className="text-lg font-semibold mb-4">🧬 Identity (identity.yaml)</h3>
            <div className="space-y-3">
              {fieldOrder.map((key) => {
                const isLong = ["background", "communication_style"].includes(key);
                return (
                  <div key={key}>
                    <label className="block text-xs text-gray-400 mb-1">
                      {fieldLabels[key] || key}
                    </label>
                    {isLong ? (
                      <textarea
                        value={identityFields[key] || ""}
                        onChange={(e) =>
                          setIdentityFields({ ...identityFields, [key]: e.target.value })
                        }
                        rows={2}
                        className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500 resize-none"
                      />
                    ) : (
                      <input
                        value={identityFields[key] || ""}
                        onChange={(e) =>
                          setIdentityFields({ ...identityFields, [key]: e.target.value })
                        }
                        className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500"
                      />
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          <div className="bg-gray-900 rounded-xl p-5 border border-gray-800 mb-6">
            <h3 className="text-lg font-semibold mb-4">🧠 Personality (personality.md)</h3>
            <textarea
              value={personalityText}
              onChange={(e) => setPersonalityText(e.target.value)}
              rows={12}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500 resize-none font-mono"
            />
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={handleSave}
              disabled={saving}
              className="bg-bio-600 hover:bg-bio-500 disabled:bg-gray-700 text-white px-6 py-2.5 rounded-lg text-sm font-medium transition-colors"
            >
              {saving ? "Saving..." : "Save DNA"}
            </button>
            {saved && (
              <span className="text-sm text-bio-400 animate-pulse">
                DNA updated — your clone will use the new identity.
              </span>
            )}
          </div>
        </>
      )}

      {/* ── Mind Files ──────────────────────────────────────── */}
      <div className="mt-10 pt-6 border-t border-gray-800">
        <h3 className="text-lg font-semibold mb-3">Mind Files</h3>
        <p className="text-sm text-gray-400 mb-3">
          These markdown files define how each part of your mind thinks. Edit them directly in the <code className="bg-gray-800 px-1 rounded">mind/</code> folder.
        </p>
        <div className="grid grid-cols-2 gap-2">
          {[
            "consciousness.md", "thinking.md", "memory.md", "financial.md",
            "meetings.md", "habits.md", "health.md",
          ].map((f) => (
            <div key={f} className="bg-gray-800 rounded-lg px-3 py-2 text-xs text-gray-400 font-mono">
              mind/{f}
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6">
        <h3 className="text-lg font-semibold mb-3">Skills</h3>
        <p className="text-sm text-gray-400 mb-3">
          Learned abilities. Add new ones as markdown files in the <code className="bg-gray-800 px-1 rounded">skills/</code> folder.
        </p>
        <div className="grid grid-cols-2 gap-2">
          {[
            "financial-tracking.md", "meeting-processing.md",
            "knowledge-management.md", "code-review.md",
          ].map((f) => (
            <div key={f} className="bg-gray-800 rounded-lg px-3 py-2 text-xs text-gray-400 font-mono">
              skills/{f}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
