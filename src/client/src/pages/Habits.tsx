import { useState, useEffect } from "react";

interface Habit {
  id: number;
  name: string;
  description: string | null;
  schedule: string;
  prompt: string;
  faculty: string;
  enabled: boolean;
  last_run: string | null;
  created_at: string;
}

export default function Habits() {
  const [habitsList, setHabits] = useState<Habit[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    name: "",
    description: "",
    schedule: "0 8 * * *",
    prompt: "",
    faculty: "thinking",
  });

  useEffect(() => {
    loadHabits();
  }, []);

  async function loadHabits() {
    const res = await fetch("/api/habits");
    setHabits(await res.json());
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await fetch("/api/habits", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    setForm({ name: "", description: "", schedule: "0 8 * * *", prompt: "", faculty: "thinking" });
    setShowForm(false);
    loadHabits();
  }

  async function toggleHabit(id: number) {
    await fetch(`/api/habits/${id}/toggle`, { method: "PUT" });
    loadHabits();
  }

  async function deleteHabit(id: number) {
    await fetch(`/api/habits/${id}`, { method: "DELETE" });
    loadHabits();
  }

  const scheduleLabels: Record<string, string> = {
    "0 8 * * *": "Daily at 8:00 AM",
    "0 9 * * 0": "Weekly on Sunday at 9:00 AM",
    "0 10 1 * *": "Monthly on 1st at 10:00 AM",
    "0 20 * * *": "Daily at 8:00 PM",
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">Habits & Routines</h2>
          <p className="text-gray-400 text-sm">Automatic behaviors that run on schedule.</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-bio-600 hover:bg-bio-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          {showForm ? "Cancel" : "+ New Habit"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-gray-900 rounded-xl p-5 border border-gray-800 mb-6 space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Habit name" required className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500" />
            <select value={form.schedule} onChange={(e) => setForm({ ...form, schedule: e.target.value })} className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm">
              <option value="0 8 * * *">Daily at 8:00 AM</option>
              <option value="0 20 * * *">Daily at 8:00 PM</option>
              <option value="0 9 * * 0">Weekly (Sunday 9 AM)</option>
              <option value="0 9 * * 1">Weekly (Monday 9 AM)</option>
              <option value="0 10 1 * *">Monthly (1st at 10 AM)</option>
            </select>
          </div>
          <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Description (optional)" className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500" />
          <textarea
            value={form.prompt}
            onChange={(e) => setForm({ ...form, prompt: e.target.value })}
            placeholder="What should the brain think about? (the prompt that runs on schedule)"
            required
            rows={3}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500 resize-none"
          />
          <div className="flex gap-3 items-center">
            <select value={form.faculty} onChange={(e) => setForm({ ...form, faculty: e.target.value })} className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm">
              <option value="thinking">Thinking</option>
              <option value="financial">Financial</option>
              <option value="memory">Memory</option>
              <option value="health">Health</option>
            </select>
            <button type="submit" className="bg-bio-600 hover:bg-bio-500 text-white px-5 py-2 rounded-lg text-sm font-medium transition-colors">Create Habit</button>
          </div>
        </form>
      )}

      <div className="space-y-3">
        {habitsList.length === 0 && (
          <div className="text-center py-12 text-gray-600">
            <p className="text-3xl mb-2">⏰</p>
            <p>No habits yet. Create automatic routines.</p>
          </div>
        )}
        {habitsList.map((h) => (
          <div key={h.id} className={`bg-gray-900 rounded-xl p-4 border transition-colors ${h.enabled ? "border-gray-800" : "border-gray-800/50 opacity-60"}`}>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-medium text-sm">{h.name}</h3>
                  <span className="text-xs bg-gray-800 px-2 py-0.5 rounded">{h.faculty}</span>
                </div>
                {h.description && <p className="text-xs text-gray-500 mb-1">{h.description}</p>}
                <p className="text-xs text-gray-600">
                  📅 {scheduleLabels[h.schedule] || h.schedule}
                  {h.last_run && ` · Last run: ${new Date(h.last_run).toLocaleString()}`}
                </p>
                <p className="text-xs text-gray-700 mt-1 italic">"{h.prompt.slice(0, 100)}{h.prompt.length > 100 ? "..." : ""}"</p>
              </div>
              <div className="flex items-center gap-2 ml-4">
                <button
                  onClick={() => toggleHabit(h.id)}
                  className={`text-xs px-3 py-1 rounded border transition-colors ${
                    h.enabled
                      ? "border-bio-600 text-bio-400 hover:bg-bio-900/20"
                      : "border-gray-700 text-gray-500 hover:bg-gray-800"
                  }`}
                >
                  {h.enabled ? "Active" : "Paused"}
                </button>
                <button onClick={() => deleteHabit(h.id)} className="text-xs text-gray-600 hover:text-red-400">delete</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
