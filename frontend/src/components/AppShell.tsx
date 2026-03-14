import { NavLink, Outlet } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  Network,
  Play,
  SlidersHorizontal,
} from "lucide-react";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/people", icon: Users, label: "People" },
  { to: "/org", icon: Network, label: "Organization" },
  { to: "/simulation", icon: Play, label: "Simulation" },
  { to: "/explorer", icon: SlidersHorizontal, label: "Score Explorer" },
];

export function AppShell() {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-56 bg-zinc-900 border-r border-zinc-800 flex flex-col shrink-0">
        <div className="p-4 border-b border-zinc-800">
          <h1 className="text-lg font-bold text-emerald-400 tracking-tight">
            TalentGraph
          </h1>
          <p className="text-xs text-zinc-500 mt-0.5">Workforce Simulator</p>
        </div>
        <nav className="flex-1 p-2 space-y-0.5">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive
                    ? "bg-emerald-500/15 text-emerald-400"
                    : "text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200"
                }`
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="p-3 border-t border-zinc-800 text-xs text-zinc-600">
          v0.3.0
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto p-6">
        <Outlet />
      </main>
    </div>
  );
}
