import { NavLink, Outlet } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  LayoutDashboard,
  Users,
  Network,
  Play,
  SlidersHorizontal,
  BookOpen,
  Globe,
  Target,
  Building2,
  Gamepad2,
  FolderKanban,
} from "lucide-react";

const navItems = [
  { to: "/", icon: LayoutDashboard, labelKey: "nav.dashboard" },
  { to: "/people", icon: Users, labelKey: "nav.people" },
  { to: "/org", icon: Network, labelKey: "nav.organization" },
  { to: "/simulation", icon: Play, labelKey: "nav.simulation" },
  { to: "/game", icon: Gamepad2, labelKey: "nav.gameMode" },
  { to: "/projects", icon: FolderKanban, labelKey: "nav.projects" },
  { to: "/recommendations", icon: Target, labelKey: "nav.recommendations" },
  { to: "/setup", icon: Building2, labelKey: "nav.setup" },
  { to: "/explorer", icon: SlidersHorizontal, labelKey: "nav.explorer" },
  { to: "/how-it-works", icon: BookOpen, labelKey: "nav.howItWorks" },
];

export function AppShell() {
  const { t, i18n } = useTranslation();

  const toggleLanguage = () => {
    const next = i18n.language === "ko" ? "en" : "ko";
    i18n.changeLanguage(next);
    localStorage.setItem("talentgraph-lang", next);
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-56 bg-zinc-900 border-r border-zinc-800 flex flex-col shrink-0">
        <div className="p-4 border-b border-zinc-800">
          <h1 className="text-lg font-bold text-emerald-400 tracking-tight">
            {t("app.title")}
          </h1>
          <p className="text-xs text-zinc-500 mt-0.5">{t("app.subtitle")}</p>
        </div>
        <nav className="flex-1 p-2 space-y-0.5 overflow-y-auto">
          {navItems.map(({ to, icon: Icon, labelKey }) => (
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
              {t(labelKey)}
            </NavLink>
          ))}
        </nav>

        {/* Language toggle + version */}
        <div className="p-3 border-t border-zinc-800 space-y-2">
          <button
            onClick={toggleLanguage}
            className="flex items-center gap-2 w-full px-2 py-1.5 rounded-lg text-xs text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200 transition-colors"
          >
            <Globe size={14} />
            <span>{i18n.language === "ko" ? "English" : "한국어"}</span>
            <span className="ml-auto text-zinc-600 uppercase">
              {i18n.language}
            </span>
          </button>
          <div className="text-xs text-zinc-600">v0.4.0</div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto p-6">
        <Outlet />
      </main>
    </div>
  );
}
