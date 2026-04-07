import { useState, useEffect } from "react";

interface Meeting {
  id: number;
  title: string;
  date: string;
  transcript: string | null;
  summary: string | null;
  action_items: string | null;
  attendees: string | null;
  status: string;
  created_at: string;
}

export default function Meetings() {
  const [meetingsList, setMeetings] = useState<Meeting[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [selectedMeeting, setSelectedMeeting] = useState<Meeting | null>(null);
  const [processing, setProcessing] = useState<number | null>(null);
  const [form, setForm] = useState({
    title: "",
    date: new Date().toISOString().split("T")[0],
    transcript: "",
    attendees: "",
  });

  useEffect(() => {
    loadMeetings();
  }, []);

  async function loadMeetings() {
    const res = await fetch("/api/meetings");
    setMeetings(await res.json());
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await fetch("/api/meetings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    setForm({ title: "", date: new Date().toISOString().split("T")[0], transcript: "", attendees: "" });
    setShowForm(false);
    loadMeetings();
  }

  async function processMeeting(id: number) {
    setProcessing(id);
    try {
      const res = await fetch(`/api/meetings/${id}/process`, { method: "POST" });
      const data = await res.json();
      if (data.error) {
        alert(data.error);
      } else {
        setSelectedMeeting(data);
        loadMeetings();
      }
    } finally {
      setProcessing(null);
    }
  }

  async function deleteMeeting(id: number) {
    await fetch(`/api/meetings/${id}`, { method: "DELETE" });
    if (selectedMeeting?.id === id) setSelectedMeeting(null);
    loadMeetings();
  }

  async function viewMeeting(id: number) {
    const res = await fetch(`/api/meetings/${id}`);
    setSelectedMeeting(await res.json());
  }

  const statusColors: Record<string, string> = {
    draft: "bg-gray-700 text-gray-300",
    pending: "bg-yellow-900 text-yellow-300",
    processed: "bg-green-900 text-green-300",
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">Meeting Processing</h2>
          <p className="text-gray-400 text-sm">Listen, summarize, extract what matters.</p>
        </div>
        <button
          onClick={() => { setShowForm(!showForm); setSelectedMeeting(null); }}
          className="bg-bio-600 hover:bg-bio-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          {showForm ? "Cancel" : "+ New Meeting"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-gray-900 rounded-xl p-5 border border-gray-800 mb-6 space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="Meeting title" required className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500" />
            <input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm" />
          </div>
          <input value={form.attendees} onChange={(e) => setForm({ ...form, attendees: e.target.value })} placeholder="Attendees (comma-separated)" className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500" />
          <textarea
            value={form.transcript}
            onChange={(e) => setForm({ ...form, transcript: e.target.value })}
            placeholder="Paste meeting transcript or VTT content here..."
            rows={8}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-bio-500 resize-none font-mono"
          />
          <button type="submit" className="bg-bio-600 hover:bg-bio-500 text-white px-5 py-2 rounded-lg text-sm font-medium transition-colors">Save Meeting</button>
        </form>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-semibold mb-3">Meetings</h3>
          <div className="space-y-2">
            {meetingsList.length === 0 && (
              <div className="text-center py-12 text-gray-600">
                <p className="text-3xl mb-2">🎙️</p>
                <p>No meetings yet. Add one to get started.</p>
              </div>
            )}
            {meetingsList.map((m) => (
              <div
                key={m.id}
                onClick={() => viewMeeting(m.id)}
                className={`bg-gray-900 rounded-lg p-3 border cursor-pointer transition-colors ${
                  selectedMeeting?.id === m.id ? "border-bio-500" : "border-gray-800 hover:border-gray-700"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">{m.title}</p>
                    <p className="text-xs text-gray-500">{m.date}{m.attendees ? ` · ${m.attendees}` : ""}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded text-xs ${statusColors[m.status] || "bg-gray-700"}`}>
                      {m.status}
                    </span>
                    {m.status === "pending" && (
                      <button
                        onClick={(e) => { e.stopPropagation(); processMeeting(m.id); }}
                        disabled={processing === m.id}
                        className="text-xs text-bio-400 hover:text-bio-300"
                      >
                        {processing === m.id ? "Processing..." : "Process"}
                      </button>
                    )}
                    <button
                      onClick={(e) => { e.stopPropagation(); deleteMeeting(m.id); }}
                      className="text-xs text-gray-600 hover:text-red-400"
                    >
                      ×
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div>
          {selectedMeeting && (
            <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
              <h3 className="text-lg font-semibold mb-1">{selectedMeeting.title}</h3>
              <p className="text-xs text-gray-500 mb-4">{selectedMeeting.date}</p>

              {selectedMeeting.summary ? (
                <div className="prose prose-invert prose-sm max-w-none">
                  <h4 className="text-sm font-semibold text-bio-400 mb-2">Summary</h4>
                  <div className="whitespace-pre-wrap text-sm text-gray-300 leading-relaxed">
                    {selectedMeeting.summary}
                  </div>
                </div>
              ) : selectedMeeting.transcript ? (
                <div>
                  <h4 className="text-sm font-semibold text-gray-400 mb-2">Transcript (raw)</h4>
                  <pre className="text-xs text-gray-500 whitespace-pre-wrap max-h-64 overflow-y-auto bg-gray-800 rounded-lg p-3">
                    {selectedMeeting.transcript}
                  </pre>
                </div>
              ) : (
                <p className="text-gray-500 text-sm">No content yet.</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
