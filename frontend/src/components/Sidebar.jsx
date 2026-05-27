import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  BarChart3,
  BrainCircuit,
  File,
  GraduationCap,
  Home,
  LogOut,
  Settings,
  Sparkles,
  TrendingUp,
  Trophy,
  Users,
  X,
} from 'lucide-react';

const Sidebar = ({ isOpen, toggleSidebar }) => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const menuItems = [
    { path: '/', icon: Home, label: 'Dashboard', hint: 'Overview, resume analysis, and recommendations' },
    { path: '/quiz', icon: BrainCircuit, label: 'Competency Quiz', hint: 'Measure your current skill competency' },
    { path: '/skill-analysis', icon: BarChart3, label: 'Skill Gap Analysis', hint: 'Compare skills against target roles' },
    { path: '/learning-paths', icon: GraduationCap, label: 'Learning Pathways', hint: 'Follow guided course pathways' },
    { path: '/resume-wizard', icon: File, label: 'Resume Wizard', hint: 'Create and improve your resume' },
    { path: '/market-insights', icon: TrendingUp, label: 'Market Insights', hint: 'Explore job market trends' },
    { path: '/community', icon: Users, label: 'Community Forum', hint: 'Connect with peers and mentors' },
    { path: '/certifications', icon: Trophy, label: 'Certifications', hint: 'View skill certificates and badges' },
  ];

  const isActive = (path) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-950/45 backdrop-blur-sm lg:hidden"
          onClick={toggleSidebar}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 z-50 flex h-full w-[min(19rem,86vw)] transform flex-col overflow-hidden border-r border-white/20 bg-gradient-to-b from-slate-950 via-blue-950 to-cyan-900 text-white shadow-2xl shadow-blue-950/30 transition-transform duration-300 ease-in-out lg:w-72 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0 lg:static lg:inset-0`}
        aria-label="Main navigation"
      >
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(34,211,238,0.28),transparent_34%),linear-gradient(160deg,rgba(16,185,129,0.14),transparent_46%)]" />
        <div className="pointer-events-none absolute inset-x-3 top-3 h-24 rounded-3xl bg-white/8 blur-2xl" />

        {/* Header */}
        <div className="relative flex flex-shrink-0 items-center justify-between border-b border-white/15 px-4 py-3">
          <div className="flex min-w-0 items-center gap-3">
            <div className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-2xl bg-white/95 text-blue-700 shadow-lg shadow-cyan-950/20">
              <Sparkles className="h-5 w-5" />
            </div>
            <div className="min-w-0">
              <span className="block truncate text-lg font-bold">SkillCompass</span>
              <span className="block truncate text-xs font-medium text-cyan-100">Competency platform</span>
            </div>
          </div>
          <button
            onClick={toggleSidebar}
            className="inline-flex h-10 w-10 items-center justify-center rounded-xl text-white transition hover:bg-white/15 focus:outline-none focus:ring-2 focus:ring-cyan-200 lg:hidden"
            aria-label="Close navigation menu"
            title="Close menu"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* User Info */}
        <div className="relative flex-shrink-0 border-b border-white/15 p-3">
          <div className="rounded-2xl border border-white/15 bg-white/10 p-2.5 shadow-lg shadow-blue-950/10 backdrop-blur">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-cyan-300 to-emerald-300 text-blue-950 shadow-md">
                <span className="font-bold">
                {user?.name?.charAt(0)?.toUpperCase() || 'U'}
                </span>
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold">{user?.name || 'User'}</p>
                <p className="truncate text-xs text-cyan-100">{user?.email || 'user@example.com'}</p>
              </div>
            </div>
            <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
              <div className="rounded-xl bg-white/10 px-3 py-2">
                <p className="text-cyan-100">Mode</p>
                <p className="font-semibold text-white">Diagnostic</p>
              </div>
              <div className="rounded-xl bg-emerald-300/15 px-3 py-2">
                <p className="text-cyan-100">Status</p>
                <p className="font-semibold text-emerald-100">Active</p>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="sidebar-scroll relative min-h-0 flex-1 overflow-y-auto px-3 py-3">
          <p className="px-3 pb-2 text-[0.68rem] font-bold uppercase tracking-wide text-cyan-100/75">
            Workspace
          </p>
          <div className="space-y-1.5">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => window.innerWidth < 1024 && toggleSidebar()}
                className={`group flex min-h-11 items-center gap-3 rounded-xl px-3 py-2 text-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-cyan-200 ${
                  active
                    ? 'bg-white text-blue-800 shadow-lg shadow-cyan-950/20'
                    : 'text-cyan-50 hover:bg-white/14 hover:text-white'
                }`}
                title={item.hint}
              >
                <span className={`flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg transition ${
                  active
                    ? 'bg-gradient-to-br from-blue-600 to-cyan-500 text-white'
                    : 'bg-white/10 text-cyan-100 group-hover:bg-white/20'
                }`}>
                  <Icon className="h-5 w-5" />
                </span>
                <span className="min-w-0 flex-1 truncate font-semibold">{item.label}</span>
                {active && <span className="h-2 w-2 rounded-full bg-emerald-400 shadow shadow-emerald-300" />}
              </Link>
            );
          })}
          </div>
        </nav>

        {/* Settings & Logout */}
        <div className="relative flex-shrink-0 space-y-1.5 border-t border-white/15 p-3">
          <Link
            to="/settings"
            onClick={() => window.innerWidth < 1024 && toggleSidebar()}
            className={`group flex min-h-11 items-center gap-3 rounded-xl px-3 py-2 text-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-cyan-200 ${
              isActive('/settings')
                ? 'bg-white text-blue-800 shadow-lg shadow-cyan-950/20'
                : 'text-cyan-50 hover:bg-white/14 hover:text-white'
            }`}
            title="Manage account preferences"
          >
            <span className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg bg-white/10 text-cyan-100 group-hover:bg-white/20">
              <Settings className="h-5 w-5" />
            </span>
            <span className="font-semibold">Settings</span>
          </Link>

          <button
            onClick={logout}
            className="group flex min-h-11 w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm text-cyan-50 transition-all duration-200 hover:bg-red-500/20 hover:text-white focus:outline-none focus:ring-2 focus:ring-red-200"
            title="Sign out of your account"
          >
            <span className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg bg-white/10 text-cyan-100 group-hover:bg-red-500/25">
              <LogOut className="h-5 w-5" />
            </span>
            <span className="font-semibold">Logout</span>
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
