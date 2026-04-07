import { useState, useEffect } from "react";

interface MemoryItem {
  id: number;
  type: string;
  title: string;
  content: string;
  tags: string;
  importance: number;
  created_at: string;
}

interface MemoryStats {
  total: number;
  byType: Record<string, number>;
  avgImportance: number;
}

export default function Memory() {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [stats, setStats] = useState<MemoryStats | null>(null);
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    title: "",
    content: "",
    type: "general",
    tags: "",
    importance: 5,
  });

  useEffect(() => {
    loadMemories();
    loadStats();
  }, []);

  async function loadMemories(query?: string) {
    const url = query ? `/api/memory?q=${encodeURIComponent(query)}` : "/api/memory";
    const res = await fetch(url);
    const data = await res.json();
    setMemories(data);
  }

  async function loadStats() {
    const res = await fetch("/api/memory/stats");
    setStats(await res.json());
  }

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    await loadMemories(search);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await fetch("/api/memory", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    setForm({ title: "", content: "", type: "general", tags: "", importance: 5 });
    setShowForm(false);
    loadMemories();
    loadStats();
  }

  async function handleDelete(id: number) {
    await fetch(`/api/memory/${id}`, { method: "DELETE" });
    loadMemories(search || undefined);
    loadStats();
  }

  const typeColors: Record<string, string> = {
    general: "bg-gray-700",
    episodic: "bg-purple-900",
    semantic: "bg-blue-900",
    procedural: "bg-green-900",
    emotional: "bg-pink-900",
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">Memory</h2>
          <p className="text-gray-400 text-sm">What you remember.</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-bio-600 hover:bg-bio-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          {showForm ? "Cancel" : "+ Store Memory"}
        </button>
      </div>

      {stats && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
            <p className="text-2xl font-bold text-bio-400">{stats.total}</p>
            <p className="text-xs text-gray-500">Total memories</p>
          </div>
          <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
            <p className="text-2xl font-bold text-neural-400">
              {stats.avgImportance.toFixed(1)}
            </p>
            <p className="text-xs text-gray-500">Avg importance</p>
          </div>
          <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
            <p className="text-2xl font-bold text-purple-400">
              {Object.keys(stats.byType).length}
            </p>
            <p className="text-xs text-gray-500">Memory types</p>
          </div>
        </div>
      )}

      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="bg-gray-900 rounded-xl p-5 border border-gray-800 mb-6 space-y-3"
        >
          <input
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            placeholder="Memory title"
            required
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500"
          />
          <textarea
            value={form.content}
            onChange={(e) => setForm({ ...form, content: e.target.value })}
            placeholder="What do you want to remember?"
            required
            rows={3}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500 resize-none"
          />
          <div className="flex gap-3">
            <select
              value={form.type}
              onChange={(e) => setForm({ ...form, type: e.target.value })}
              className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm"
            >
              <option value="general">General</option>
              <option value="episodic">Episodic</option>
              <option value="semantic">Semantic</option>
              <option value="procedural">Procedural</option>
              <option value="emotional">Emotional</option>
            </select>
            <input
              value={form.tags}
              onChange={(e) => setForm({ ...form, tags: e.target.value })}
              placeholder="Tags (comma-separated)"
              className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500"
            />
            <div className="flex items-center gap-2">
              <label className="text-xs text-gray-500">Importance:</label>
              <input
                type="range"
                min={1}
                max={10}
                value={form.importance}
                onChange={(e) =>
                  setForm({ ...form, importance: parseInt(e.target.value) })
                }
                className="w-20"
              />
              <span className="text-sm w-4">{form.importance}</span>
            </div>
          </div>
          <button
            type="submit"
            className="bg-bio-600 hover:bg-bio-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Store
          </button>
        </form>
      )}

      <form onSubmit={handleSearch} className="mb-6 flex gap-3">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search memories..."
          className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-bio-500 placeholder-gray-500"
        />
        <button
          type="submit"
          className="bg-gray-700 hover:bg-gray-600 text-white px-5 py-2.5 rounded-lg text-sm transition-colors"
        >
          Search
        </button>
      </form>

      <div className="space-y-3">
        {memories.length === 0 && (
          <div className="text-center py-12 text-gray-600">
            <p className="text-3xl mb-2">💭</p>
            <p>No memories yet. Start storing what matters.</p>
          </div>
        )}
        {memories.map((m) => (
          <div
            key={m.id}
            className="bg-gray-900 rounded-xl p-4 border border-gray-800 hover:border-gray-700 transition-colors"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span
                    className={`px-2 py-0.5 rounded text-xs ${typeColors[m.type] || "bg-gray-700"}`}
                  >
                    {m.type}
                  </span>
                  <span className="text-xs text-gray-500">
                    importance: {m.importance}/10
                  </span>
                </div>
                <h3 className="font-medium text-sm">{m.title}</h3>
                <p className="text-gray-400 text-sm mt-1 line-clamp-2">
                  {m.content}
                </p>
                {m.tags && (
                  <div className="flex gap-1.5 mt-2">
                    {m.tags.split(",").map((tag, i) => (
                      <span
                        key={i}
                        className="text-xs bg-gray-800 px-2 py-0.5 rounded"
                      >
                        {tag.trim()}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <button
                onClick={() => handleDelete(m.id)}
                className="text-gray-600 hover:text-red-400 text-xs ml-4"
              >
                delete
              </button>
            </div>
            <p className="text-xs text-gray-600 mt-2">
              {new Date(m.created_at).toLocaleDateString()}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
