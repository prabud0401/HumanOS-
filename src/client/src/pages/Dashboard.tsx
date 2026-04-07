import { useState, useEffect } from "react";
import BodyMap from "../components/BodyMap";

interface HealthData {
  alive: boolean;
  name: string;
  dnaLoaded: boolean;
  llmConfigured: boolean;
  connection?: { mode: string; configured: boolean; details: string };
  status: string;
  timestamp: string;
  faculties: Record<
    string,
    {
      status: string;
      message: string;
      [key: string]: unknown;
    }
  >;
}

export default function Dashboard() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHealth();
    const interval = setInterval(loadHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  async function loadHealth() {
    try {
      const res = await fetch("/api/health");
      setHealth(await res.json());
    } catch {
      setHealth(null);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-500 animate-pulse">Waking up...</div>
      </div>
    );
  }

  if (!health) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-red-400">Cannot reach the nervous system. Is the server running?</div>
      </div>
    );
  }

  const statusColor =
    health.status === "healthy"
      ? "text-green-400"
      : health.status === "degraded"
        ? "text-yellow-400"
        : "text-red-400";

  const statusDot =
    health.status === "healthy"
      ? "bg-green-400"
      : health.status === "degraded"
        ? "bg-yellow-400"
        : "bg-red-400";

  return (
    <div className="p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className={`w-3 h-3 rounded-full ${statusDot} animate-pulse`} />
        <div>
          <h2 className="text-2xl font-bold">
            {health.name}
            <span className="text-gray-500 font-normal text-base ml-2">
              Digital Clone
            </span>
          </h2>
          <p className={`text-sm ${statusColor}`}>
            System {health.status}
            {!health.llmConfigured && (
              <span className="text-yellow-500 ml-2">
                — Brain not connected (go to Settings)
              </span>
            )}
            {health.connection && (
              <span className="text-gray-500 ml-2">
                · {health.connection.mode.toUpperCase()} mode
              </span>
            )}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-semibold mb-4">Body Map</h3>
          <BodyMap faculties={health.faculties} />
        </div>

        <div>
          <h3 className="text-lg font-semibold mb-4">Faculty Status</h3>
          <div className="space-y-3">
            {Object.entries(health.faculties).map(([name, data]) => {
              const icons: Record<string, string> = {
                brain: "🧠",
                memory: "💭",
                financial: "💰",
                meetings: "🎙️",
                habits: "⏰",
              };
              const color =
                data.status === "healthy"
                  ? "border-green-800 bg-green-950/30"
                  : data.status === "degraded"
                    ? "border-yellow-800 bg-yellow-950/30"
                    : "border-red-800 bg-red-950/30";

              return (
                <div
                  key={name}
                  className={`rounded-xl p-4 border ${color} transition-colors`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-xl">
                        {icons[name] || "🔵"}
                      </span>
                      <div>
                        <p className="font-medium text-sm capitalize">
                          {name}
                        </p>
                        <p className="text-xs text-gray-400">
                          {data.message}
                        </p>
                      </div>
                    </div>
                    <span
                      className={`text-xs px-2 py-1 rounded ${
                        data.status === "healthy"
                          ? "bg-green-900 text-green-300"
                          : data.status === "degraded"
                            ? "bg-yellow-900 text-yellow-300"
                            : "bg-red-900 text-red-300"
                      }`}
                    >
                      {data.status}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="mt-8 grid grid-cols-2 lg:grid-cols-4 gap-4">
        <QuickStat
          label="DNA Loaded"
          value={health.dnaLoaded ? "Yes" : "No"}
          color={health.dnaLoaded ? "text-bio-400" : "text-red-400"}
        />
        <QuickStat
          label={`Brain (${health.connection?.mode?.toUpperCase() || "—"})`}
          value={health.llmConfigured ? "Connected" : "Offline"}
          color={health.llmConfigured ? "text-bio-400" : "text-yellow-400"}
        />
        <QuickStat
          label="Total Faculties"
          value={String(Object.keys(health.faculties).length)}
          color="text-neural-400"
        />
        <QuickStat
          label="Last Check"
          value={new Date(health.timestamp).toLocaleTimeString()}
          color="text-gray-400"
        />
      </div>
    </div>
  );
}

function QuickStat({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color: string;
}) {
  return (
    <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
      <p className={`text-xl font-bold ${color}`}>{value}</p>
      <p className="text-xs text-gray-500">{label}</p>
    </div>
  );
}
