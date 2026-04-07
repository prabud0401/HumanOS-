import { useState, useEffect } from "react";

interface DNAData {
  identity: Record<string, unknown>;
  personality: string;
}

export default function Settings() {
  const [dna, setDna] = useState<DNAData | null>(null);
  const [personalityText, setPersonalityText] = useState("");
  const [identityFields, setIdentityFields] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [health, setHealth] = useState<{ llmConfigured: boolean; name: string } | null>(null);

  useEffect(() => {
    loadDNA();
    fetch("/api/health")
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => {});
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
    "name",
    "full_name",
    "background",
    "values",
    "goals",
    "communication_style",
    "languages",
    "timezone",
    "interests",
  ];

  return (
    <div className="p-6 max-w-3xl">
      <h2 className="text-2xl font-bold mb-2">Settings</h2>
      <p className="text-gray-400 text-sm mb-6">Edit your DNA — who you are, how you think.</p>

      <div className="mb-6 flex gap-4">
        <div className={`rounded-lg px-4 py-3 border text-sm ${health?.llmConfigured ? "border-green-800 bg-green-950/30 text-green-300" : "border-yellow-800 bg-yellow-950/30 text-yellow-300"}`}>
          {health?.llmConfigured ? "🧠 Brain connected (Claude API)" : "⚠️ Brain disconnected — add ANTHROPIC_API_KEY to dna/.env"}
        </div>
      </div>

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

      <div className="mt-10 pt-6 border-t border-gray-800">
        <h3 className="text-lg font-semibold mb-3">Mind Files</h3>
        <p className="text-sm text-gray-400 mb-3">
          These markdown files define how each part of your mind thinks. Edit them directly in the <code className="bg-gray-800 px-1 rounded">mind/</code> folder.
        </p>
        <div className="grid grid-cols-2 gap-2">
          {[
            "consciousness.md",
            "thinking.md",
            "memory.md",
            "financial.md",
            "meetings.md",
            "habits.md",
            "health.md",
          ].map((f) => (
            <div
              key={f}
              className="bg-gray-800 rounded-lg px-3 py-2 text-xs text-gray-400 font-mono"
            >
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
            "financial-tracking.md",
            "meeting-processing.md",
            "knowledge-management.md",
            "code-review.md",
          ].map((f) => (
            <div
              key={f}
              className="bg-gray-800 rounded-lg px-3 py-2 text-xs text-gray-400 font-mono"
            >
              skills/{f}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
