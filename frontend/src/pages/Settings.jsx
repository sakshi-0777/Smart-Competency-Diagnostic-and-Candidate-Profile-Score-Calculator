import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  Bell,
  CheckCircle2,
  Eye,
  Loader2,
  Lock,
  Mail,
  RotateCcw,
  Save,
  Shield,
  User
} from 'lucide-react';

const defaultPreferences = {
  newFeatures: true,
  weeklyReports: true,
  forumUpdates: false,
  profileVisible: false,
  shareProgress: false
};

const Toggle = ({ checked, label, description, children, onChange }) => (
  <label className="group flex cursor-pointer items-start gap-3 rounded-xl border border-blue-100 bg-white/80 p-4 shadow-sm transition-all hover:-translate-y-0.5 hover:border-cyan-200 hover:shadow-lg">
    <span className="mt-0.5 flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-blue-100 to-emerald-100 text-blue-700">
      {children}
    </span>
    <span className="min-w-0 flex-1">
      <span className="block font-semibold text-slate-900">{label}</span>
      <span className="mt-1 block text-sm leading-5 text-slate-600">{description}</span>
    </span>
    <input
      type="checkbox"
      checked={checked}
      onChange={onChange}
      className="sr-only"
    />
    <span className={`relative mt-1 h-6 w-11 flex-shrink-0 rounded-full transition ${checked ? 'bg-emerald-500' : 'bg-slate-300'}`}>
      <span className={`absolute top-1 h-4 w-4 rounded-full bg-white shadow transition ${checked ? 'left-6' : 'left-1'}`}></span>
    </span>
  </label>
);

const Settings = () => {
  const { user, token } = useAuth();
  const [profile, setProfile] = useState({
    name: user?.name || '',
    email: user?.email || ''
  });
  const [passwords, setPasswords] = useState({
    currentPassword: '',
    newPassword: ''
  });
  const [preferences, setPreferences] = useState(defaultPreferences);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const savedPreferences = localStorage.getItem('settings_preferences');
    if (savedPreferences) {
      try {
        setPreferences({ ...defaultPreferences, ...JSON.parse(savedPreferences) });
      } catch (err) {
        console.error('Failed to parse settings preferences', err);
      }
    }

    if (!token) {
      setLoading(false);
      return;
    }

    fetch('http://localhost:5000/profile', {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(response => response.json())
      .then(data => {
        if (data.user) {
          setProfile({
            name: data.user.name || '',
            email: data.user.email || ''
          });
        }
      })
      .catch(() => setError('Unable to load profile details.'))
      .finally(() => setLoading(false));
  }, [token]);

  const updatePreference = (key) => {
    setPreferences(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const resetForm = () => {
    setProfile({
      name: user?.name || '',
      email: user?.email || ''
    });
    setPasswords({ currentPassword: '', newPassword: '' });
    setPreferences(defaultPreferences);
    setMessage('');
    setError('');
  };

  const saveSettings = async () => {
    setSaving(true);
    setMessage('');
    setError('');

    try {
      localStorage.setItem('settings_preferences', JSON.stringify(preferences));

      const payload = {
        name: profile.name.trim(),
        email: profile.email.trim()
      };

      if (passwords.newPassword) {
        payload.current_password = passwords.currentPassword;
        payload.new_password = passwords.newPassword;
      }

      const response = await fetch('http://localhost:5000/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || data.message || 'Unable to save settings.');
      }

      if (data.user) {
        localStorage.setItem('user', JSON.stringify(data.user));
        setProfile({
          name: data.user.name || '',
          email: data.user.email || ''
        });
      }

      setPasswords({ currentPassword: '', newPassword: '' });
      setMessage('Settings saved successfully.');
    } catch (err) {
      setError(err.message || 'Unable to save settings.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-full items-center justify-center bg-[linear-gradient(135deg,#f8fbff_0%,#ecfeff_45%,#f7fee7_100%)] p-6">
        <div className="text-center">
          <Loader2 className="mx-auto h-10 w-10 animate-spin text-blue-600" />
          <p className="mt-3 text-sm font-medium text-slate-600">Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-full bg-[radial-gradient(circle_at_top_left,rgba(14,165,233,0.18),transparent_30%),linear-gradient(135deg,#f8fbff_0%,#ecfeff_45%,#f7fee7_100%)] px-4 py-5 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl">
        <header className="mb-5 rounded-2xl border border-white/70 bg-white/80 p-5 shadow-xl shadow-blue-900/5 backdrop-blur sm:p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="inline-flex items-center gap-2 rounded-full bg-cyan-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-cyan-800">
                <Shield className="h-3.5 w-3.5" />
                Account controls
              </p>
              <h1 className="mt-3 text-2xl font-bold text-slate-950 sm:text-3xl">Settings</h1>
              <p className="mt-2 text-sm text-slate-600">Manage profile details, notifications, privacy, and password security.</p>
            </div>
            <div className="rounded-xl bg-gradient-to-br from-blue-700 to-cyan-600 px-4 py-3 text-white shadow-lg shadow-blue-700/15">
              <p className="text-xs font-medium text-blue-100">Signed in as</p>
              <p className="mt-1 max-w-52 truncate text-sm font-bold">{profile.email || 'User'}</p>
            </div>
          </div>
        </header>

        {message && (
          <div className="mb-4 flex items-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-700">
            <CheckCircle2 className="h-4 w-4" />
            {message}
          </div>
        )}
        {error && (
          <div className="mb-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
            {error}
          </div>
        )}

        <div className="grid gap-5 lg:grid-cols-[minmax(0,1.05fr)_minmax(320px,0.95fr)]">
          <section className="rounded-2xl border border-white/70 bg-white/85 p-5 shadow-xl shadow-blue-900/5 backdrop-blur sm:p-6">
            <div className="mb-5 flex items-center gap-3">
              <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 text-white">
                <User className="h-5 w-5" />
              </span>
              <div>
                <h2 className="text-xl font-bold text-slate-950">Profile</h2>
                <p className="text-sm text-slate-600">Keep your account identity current.</p>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">Name</label>
                <input
                  type="text"
                  value={profile.name}
                  onChange={(e) => setProfile(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full rounded-xl border border-blue-100 bg-white px-4 py-3 text-sm text-slate-800 outline-none transition focus:border-cyan-400 focus:ring-4 focus:ring-cyan-100"
                  placeholder="Your name"
                />
              </div>
              <div>
                <label className="mb-2 block text-sm font-semibold text-slate-700">Email</label>
                <div className="relative">
                  <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-blue-500" />
                  <input
                    type="email"
                    value={profile.email}
                    onChange={(e) => setProfile(prev => ({ ...prev, email: e.target.value }))}
                    className="w-full rounded-xl border border-blue-100 bg-white py-3 pl-10 pr-4 text-sm text-slate-800 outline-none transition focus:border-cyan-400 focus:ring-4 focus:ring-cyan-100"
                    placeholder="your@email.com"
                  />
                </div>
              </div>
            </div>

            <div className="mt-6 border-t border-blue-100 pt-5">
              <div className="mb-4 flex items-center gap-3">
                <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-slate-900 to-blue-800 text-white">
                  <Lock className="h-5 w-5" />
                </span>
                <div>
                  <h2 className="font-bold text-slate-950">Password</h2>
                  <p className="text-sm text-slate-600">Leave blank to keep your current password.</p>
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <input
                  type="password"
                  value={passwords.currentPassword}
                  onChange={(e) => setPasswords(prev => ({ ...prev, currentPassword: e.target.value }))}
                  className="w-full rounded-xl border border-blue-100 bg-white px-4 py-3 text-sm text-slate-800 outline-none transition focus:border-cyan-400 focus:ring-4 focus:ring-cyan-100"
                  placeholder="Current password"
                />
                <input
                  type="password"
                  value={passwords.newPassword}
                  onChange={(e) => setPasswords(prev => ({ ...prev, newPassword: e.target.value }))}
                  className="w-full rounded-xl border border-blue-100 bg-white px-4 py-3 text-sm text-slate-800 outline-none transition focus:border-cyan-400 focus:ring-4 focus:ring-cyan-100"
                  placeholder="New password"
                />
              </div>
            </div>
          </section>

          <section className="space-y-5">
            <div className="rounded-2xl border border-white/70 bg-white/85 p-5 shadow-xl shadow-blue-900/5 backdrop-blur">
              <h2 className="mb-4 text-xl font-bold text-slate-950">Notifications</h2>
              <div className="space-y-3">
                <Toggle checked={preferences.newFeatures} label="New features" description="Receive updates when new platform tools are available." onChange={() => updatePreference('newFeatures')}>
                  <Bell className="h-5 w-5" />
                </Toggle>
                <Toggle checked={preferences.weeklyReports} label="Weekly reports" description="Get a weekly summary of your progress and activity." onChange={() => updatePreference('weeklyReports')}>
                  <CheckCircle2 className="h-5 w-5" />
                </Toggle>
                <Toggle checked={preferences.forumUpdates} label="Forum updates" description="Notify me when community discussions are active." onChange={() => updatePreference('forumUpdates')}>
                  <Mail className="h-5 w-5" />
                </Toggle>
              </div>
            </div>

            <div className="rounded-2xl border border-white/70 bg-white/85 p-5 shadow-xl shadow-blue-900/5 backdrop-blur">
              <h2 className="mb-4 text-xl font-bold text-slate-950">Privacy</h2>
              <div className="space-y-3">
                <Toggle checked={preferences.profileVisible} label="Profile visibility" description="Allow other users to discover your profile." onChange={() => updatePreference('profileVisible')}>
                  <Eye className="h-5 w-5" />
                </Toggle>
                <Toggle checked={preferences.shareProgress} label="Share learning progress" description="Show completed pathways and certificates publicly." onChange={() => updatePreference('shareProgress')}>
                  <Shield className="h-5 w-5" />
                </Toggle>
              </div>
            </div>
          </section>
        </div>

        <div className="sticky bottom-0 mt-5 border-t border-white/70 bg-white/80 px-4 py-3 shadow-2xl shadow-blue-900/10 backdrop-blur sm:rounded-2xl sm:border">
          <div className="mx-auto flex max-w-6xl flex-col gap-3 sm:flex-row sm:justify-end">
            <button
              type="button"
              onClick={resetForm}
              className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-blue-100 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:border-blue-300 hover:bg-blue-50"
            >
              <RotateCcw className="h-4 w-4" />
              Reset
            </button>
            <button
              type="button"
              onClick={saveSettings}
              disabled={saving || !profile.name.trim() || !profile.email.trim()}
              className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-700 via-cyan-600 to-emerald-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-700/20 transition hover:-translate-y-0.5 hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-60"
            >
              {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
