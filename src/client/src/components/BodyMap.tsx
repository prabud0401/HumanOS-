interface BodyMapProps {
  faculties: Record<string, { status: string; message: string }>;
}

export default function BodyMap({ faculties }: BodyMapProps) {
  const statusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "#22c55e";
      case "degraded":
        return "#f59e0b";
      case "unhealthy":
        return "#ef4444";
      default:
        return "#6b7280";
    }
  };

  const organs = [
    { key: "brain", label: "Brain", x: 150, y: 55, icon: "🧠" },
    { key: "memory", label: "Memory", x: 150, y: 105, icon: "💭" },
    { key: "financial", label: "Financial", x: 100, y: 175, icon: "💰" },
    { key: "meetings", label: "Meetings", x: 200, y: 175, icon: "🎙️" },
    { key: "habits", label: "Habits", x: 150, y: 255, icon: "⏰" },
  ];

  return (
    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
      <svg viewBox="0 0 300 320" className="w-full max-w-sm mx-auto">
        {/* Body outline */}
        <ellipse cx="150" cy="50" rx="35" ry="40" fill="none" stroke="#334155" strokeWidth="1.5" />
        <line x1="150" y1="90" x2="150" y2="200" stroke="#334155" strokeWidth="1.5" />
        <line x1="150" y1="120" x2="80" y2="170" stroke="#334155" strokeWidth="1.5" />
        <line x1="150" y1="120" x2="220" y2="170" stroke="#334155" strokeWidth="1.5" />
        <line x1="150" y1="200" x2="110" y2="300" stroke="#334155" strokeWidth="1.5" />
        <line x1="150" y1="200" x2="190" y2="300" stroke="#334155" strokeWidth="1.5" />

        {organs.map((organ) => {
          const data = faculties[organ.key];
          const color = data ? statusColor(data.status) : "#6b7280";
          return (
            <g key={organ.key}>
              <circle
                cx={organ.x}
                cy={organ.y}
                r="22"
                fill={color}
                fillOpacity="0.15"
                stroke={color}
                strokeWidth="2"
              >
                <animate
                  attributeName="r"
                  values="22;24;22"
                  dur="2s"
                  repeatCount="indefinite"
                />
              </circle>
              <circle cx={organ.x} cy={organ.y} r="4" fill={color}>
                <animate
                  attributeName="opacity"
                  values="1;0.5;1"
                  dur="2s"
                  repeatCount="indefinite"
                />
              </circle>
              <text
                x={organ.x}
                y={organ.y - 28}
                textAnchor="middle"
                fontSize="16"
              >
                {organ.icon}
              </text>
              <text
                x={organ.x}
                y={organ.y + 38}
                textAnchor="middle"
                fill="#9ca3af"
                fontSize="10"
                fontWeight="500"
              >
                {organ.label}
              </text>
            </g>
          );
        })}

        <text x="150" y="315" textAnchor="middle" fill="#4b5563" fontSize="9">
          {Object.values(faculties).every((f) => f.status === "healthy")
            ? "All systems operational"
            : "Some systems need attention"}
        </text>
      </svg>
    </div>
  );
}
