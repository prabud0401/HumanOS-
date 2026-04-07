import { useState, useRef, useEffect } from "react";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  faculty?: string;
}

export default function Brain() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentFaculty, setCurrentFaculty] = useState<string>("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    fetch("/api/brain/history")
      .then((r) => r.json())
      .then((history: { role: string; content: string }[]) => {
        setMessages(
          history.map((h) => ({
            role: h.role as "user" | "assistant",
            content: h.content,
          }))
        );
      })
      .catch(() => {});
  }, []);

  async function sendMessage() {
    const text = input.trim();
    if (!text || isStreaming) return;

    setInput("");
    setIsStreaming(true);

    const userMsg: ChatMessage = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);

    const assistantMsg: ChatMessage = { role: "assistant", content: "", faculty: "" };
    setMessages((prev) => [...prev, assistantMsg]);

    try {
      const history = messages.slice(-20).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const response = await fetch("/api/brain/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, history }),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error("No response stream");

      let accumulated = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const data = JSON.parse(line.slice(6));
            if (data.faculty) setCurrentFaculty(data.faculty);
            if (data.done) continue;
            accumulated += data.text;
            setMessages((prev) => {
              const updated = [...prev];
              updated[updated.length - 1] = {
                role: "assistant",
                content: accumulated,
                faculty: data.faculty,
              };
              return updated;
            });
          } catch {
            // skip malformed SSE
          }
        }
      }
    } catch (err) {
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          role: "assistant",
          content: "Failed to connect to the brain. Is the server running?",
        };
        return updated;
      });
    } finally {
      setIsStreaming(false);
      inputRef.current?.focus();
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  async function clearHistory() {
    await fetch("/api/brain/history", { method: "DELETE" });
    setMessages([]);
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
        <div>
          <h2 className="text-xl font-bold">Brain</h2>
          <p className="text-sm text-gray-500">
            Talk to yourself.{" "}
            {currentFaculty && (
              <span className="text-bio-400">Active: {currentFaculty}</span>
            )}
          </p>
        </div>
        <button
          onClick={clearHistory}
          className="text-xs text-gray-500 hover:text-red-400 transition-colors px-3 py-1 rounded border border-gray-700 hover:border-red-800"
        >
          Clear history
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full text-gray-600">
            <div className="text-center">
              <p className="text-4xl mb-4">🧠</p>
              <p className="text-lg font-medium">Your brain is ready.</p>
              <p className="text-sm mt-1">
                Ask anything — reason, brainstorm, or just think out loud.
              </p>
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                msg.role === "user"
                  ? "bg-neural-700 text-white"
                  : "bg-gray-800 text-gray-200"
              }`}
            >
              {msg.faculty && msg.role === "assistant" && (
                <div className="text-xs text-bio-500 mb-1 font-medium">
                  {msg.faculty} faculty
                </div>
              )}
              <div className="whitespace-pre-wrap text-sm leading-relaxed">
                {msg.content}
                {isStreaming &&
                  i === messages.length - 1 &&
                  msg.role === "assistant" && (
                    <span className="inline-block w-2 h-4 bg-bio-400 ml-0.5 animate-pulse" />
                  )}
              </div>
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-gray-800 p-4">
        <div className="flex gap-3 items-end max-w-4xl mx-auto">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Talk to your brain..."
            rows={1}
            className="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-3 text-sm resize-none focus:outline-none focus:border-bio-500 placeholder-gray-500"
            style={{ minHeight: "44px", maxHeight: "120px" }}
            onInput={(e) => {
              const target = e.target as HTMLTextAreaElement;
              target.style.height = "auto";
              target.style.height = Math.min(target.scrollHeight, 120) + "px";
            }}
          />
          <button
            onClick={sendMessage}
            disabled={isStreaming || !input.trim()}
            className="bg-bio-600 hover:bg-bio-500 disabled:bg-gray-700 disabled:text-gray-500 text-white px-5 py-3 rounded-xl text-sm font-medium transition-colors"
          >
            {isStreaming ? "Thinking..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
