import { Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Brain from "./pages/Brain";
import Financial from "./pages/Financial";
import Meetings from "./pages/Meetings";
import Memory from "./pages/Memory";
import Habits from "./pages/Habits";
import Settings from "./pages/Settings";

const navItems = [
  { to: "/", label: "Dashboard", icon: "🫀" },
  { to: "/brain", label: "Brain", icon: "🧠" },
  { to: "/memory", label: "Memory", icon: "💭" },
  { to: "/financial", label: "Financial", icon: "💰" },
  { to: "/meetings", label: "Meetings", icon: "🎙️" },
  { to: "/habits", label: "Habits", icon: "⏰" },
  { to: "/settings", label: "Settings", icon: "🧬" },
];

export default function App() {
  return (
    <div className="flex h-screen">
      <nav className="w-56 bg-gray-900 border-r border-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <h1 className="text-lg font-bold text-bio-400">HumanOS</h1>
          <p className="text-xs text-gray-500">Your Digital Clone</p>
        </div>
        <div className="flex-1 py-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                  isActive
                    ? "bg-gray-800 text-white border-r-2 border-bio-500"
                    : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/50"
                }`
              }
            >
              <span className="text-base">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </div>
        <div className="p-4 border-t border-gray-800 text-xs text-gray-600">
          v0.1.0 — alive
        </div>
      </nav>

      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/brain" element={<Brain />} />
          <Route path="/memory" element={<Memory />} />
          <Route path="/financial" element={<Financial />} />
          <Route path="/meetings" element={<Meetings />} />
          <Route path="/habits" element={<Habits />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  );
}
