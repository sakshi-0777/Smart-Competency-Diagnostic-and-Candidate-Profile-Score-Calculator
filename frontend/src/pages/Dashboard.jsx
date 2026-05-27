import React, {useEffect , useState} from 'react'
import { useAuth } from '../context/AuthContext'
import UploadAndSummary from '../components/UploadAndSummary'
import { Link } from 'react-router-dom'
import { API_BASE_URL } from "../config";
import {
  Award,
  BarChart3,
  BrainCircuit,
  CheckCircle2,
  GraduationCap,
  Info,
  Loader2,
  MessageCircle,
  PenLine,
  TrendingUp,
  UploadCloud
} from 'lucide-react'

const Dashboard = () => {
  const { user, token } = useAuth();

  const [profile, setProfile] = useState(null);
  const [modelStatus, setModelStatus] = useState("loading");
  const [progress, setProgress] = useState(0);
  const displayName = profile?.name || user?.name || 'Candidate';
  const isModelReady = modelStatus === "ready";

  const featureCards = [
    {
      to: "/quiz",
      icon: BrainCircuit,
      title: "Competency Quiz",
      description: "Take our diagnostic quiz to assess your skills",
      color: "from-blue-600 to-cyan-500",
      tooltip: "Start a skill quiz and calculate competency scores.",
    },
    {
      to: "/skill-analysis",
      icon: BarChart3,
      title: "Skill Gap Analysis",
      description: "Identify gaps and get personalized recommendations",
      color: "from-emerald-600 to-teal-500",
      tooltip: "Compare current skills with target role requirements.",
    },
    {
      to: "/learning-paths",
      icon: GraduationCap,
      title: "Learning Pathways",
      description: "Follow structured learning paths to upskill",
      color: "from-violet-600 to-fuchsia-500",
      tooltip: "Open guided paths for courses and practice.",
    },
    {
      to: "/resume-wizard",
      icon: PenLine,
      title: "Resume Wizard",
      description: "Generate professional resumes automatically",
      color: "from-orange-500 to-rose-500",
      tooltip: "Build a polished resume from your profile.",
    },
    {
      to: "/market-insights",
      icon: TrendingUp,
      title: "Market Insights",
      description: "Real-time job market trends and insights",
      color: "from-red-500 to-amber-500",
      tooltip: "Explore current demand trends by role and skill.",
    },
    {
      to: "/community",
      icon: MessageCircle,
      title: "Community Forum",
      description: "Connect with peers and mentors",
      color: "from-cyan-600 to-sky-500",
      tooltip: "Discuss learning goals with peers and mentors.",
    },
    {
      to: "/certifications",
      icon: Award,
      title: "Certifications",
      description: "Earn verified skill certifications",
      color: "from-yellow-500 to-lime-500",
      tooltip: "View certifications and verified skill badges.",
    },
  ];

  // ---------------- FETCH PROFILE ---------------- //
  useEffect(() => {
    if (!token) return;

    fetch(`${API_BASE_URL}/profile`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then((data) => setProfile(data.user))
      .catch(console.error);
  }, [token]);

  // ---------------- CHECK MODEL STATUS ---------------- //
  useEffect(() => {
    const interval = setInterval(() => {
      fetch(`${API_BASE_URL}/model_status`)
        .then((res) => res.json())
        .then((data) => {
          setModelStatus(data.status);

          if (data.progress !== undefined) {
            setProgress(data.progress);
          }

          // Stop polling when ready
          if (data.status === "ready") {
            clearInterval(interval);
          }
        })
        .catch(console.error);
    }, 1000); // check every 1 sec

    return () => clearInterval(interval);
  }, []);

  // ---------------- UI ---------------- //
  return (
    <div className="min-h-full bg-[radial-gradient(circle_at_top_left,rgba(14,165,233,0.18),transparent_30%),linear-gradient(135deg,#f8fbff_0%,#ecfeff_45%,#f7fee7_100%)]">
      <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8 lg:py-6">

        {/* HEADER */}
        <header className="mb-5 overflow-hidden rounded-2xl border border-white/70 bg-white/80 p-5 shadow-xl shadow-blue-900/5 backdrop-blur sm:p-6">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p className="inline-flex items-center gap-2 rounded-full bg-cyan-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-cyan-800">
                <Info className="h-3.5 w-3.5" />
                Candidate dashboard
              </p>
              <h1 className="mt-3 text-2xl font-bold text-slate-950 sm:text-3xl">
                Welcome, {displayName}
              </h1>
              <p className="mt-2 max-w-2xl text-sm text-slate-600 sm:text-base">
                Review your skill profile, analyze resume fit, and move into guided learning from one workspace.
              </p>
            </div>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:min-w-[28rem]">
              <div className="rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 px-4 py-3 text-white shadow-lg shadow-blue-700/15" title="Resume, quiz, and learning modules are available from this dashboard.">
                <p className="text-xs font-medium text-blue-100">Modules</p>
                <p className="mt-1 text-2xl font-bold">7</p>
              </div>
              <div className="rounded-xl bg-gradient-to-br from-emerald-600 to-teal-500 px-4 py-3 text-white shadow-lg shadow-emerald-700/15" title="Model status updates automatically while the page is open.">
                <p className="text-xs font-medium text-emerald-100">AI model</p>
                <p className="mt-1 inline-flex items-center gap-1.5 text-lg font-bold capitalize">
                  {isModelReady ? <CheckCircle2 className="h-4 w-4" /> : <Loader2 className="h-4 w-4 animate-spin" />}
                  {modelStatus}
                </p>
              </div>
              <div className="col-span-2 rounded-xl bg-gradient-to-br from-slate-900 to-blue-800 px-4 py-3 text-white shadow-lg shadow-slate-900/15 sm:col-span-1" title="Resume analysis supports PDF upload.">
                <p className="text-xs font-medium text-blue-100">Resume</p>
                <p className="mt-1 inline-flex items-center gap-1.5 text-lg font-bold">
                  <UploadCloud className="h-4 w-4" />
                  PDF
                </p>
              </div>
            </div>
          </div>
        </header>

        {/* MODEL LOADING SCREEN */}
        {modelStatus === "loading" && (
          <div className="mb-5 rounded-2xl border border-blue-100 bg-white/85 p-4 shadow-xl shadow-blue-900/5 backdrop-blur sm:p-5">
            <div className="mb-3 flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
              <h2 className="text-base font-semibold text-slate-900">
                AI model is loading
              </h2>
              <p className="text-sm font-medium text-blue-700">{progress}% completed</p>
            </div>

            {/* Progress Bar */}
            <div className="h-3 w-full overflow-hidden rounded-full bg-blue-100" title={`${progress}% completed`}>
              <div
                className="h-3 rounded-full bg-gradient-to-r from-blue-600 via-cyan-500 to-emerald-500 transition-all duration-500"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* ERROR STATE */}
        {modelStatus === "error" && (
          <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">
            Failed to load model. Please refresh.
          </div>
        )}

        <div className="space-y-6">

            {/* FEATURE CARDS */}
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {featureCards.map((card) => {
                const Icon = card.icon;
                return (
                  <Link
                    key={card.to}
                    to={card.to}
                    className="group rounded-2xl border border-white/70 bg-white/85 p-5 shadow-lg shadow-blue-900/5 backdrop-blur transition-all duration-300 hover:-translate-y-1 hover:border-cyan-200 hover:shadow-2xl hover:shadow-cyan-700/10 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-offset-2"
                    data-tooltip={card.tooltip}
                  >
                    <div className="mb-4 flex items-start justify-between gap-3">
                      <div className={`inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${card.color} text-white shadow-lg transition-transform duration-300 group-hover:scale-110`}>
                        <Icon className="h-6 w-6" />
                      </div>
                      <span className="rounded-full bg-cyan-50 px-2.5 py-1 text-xs font-semibold text-cyan-700">
                        Open
                      </span>
                    </div>
                    <h3 className="mb-2 text-lg font-semibold text-slate-950 sm:text-xl">{card.title}</h3>
                    <p className="text-sm leading-6 text-slate-600">{card.description}</p>
                  </Link>
                );
              })}
            </div>

            {/* RESUME ANALYSIS SECTION */}
            <div className="rounded-2xl border border-white/70 bg-white/75 p-4 shadow-xl shadow-blue-900/5 backdrop-blur sm:p-6">
              <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h2 className="text-xl font-bold text-slate-950 sm:text-2xl">Resume Analysis & Job Matching</h2>
                  <p className="mt-1 text-sm text-slate-600">Upload a resume, analyze skill fit, and search job matches.</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <span className="w-fit rounded-full bg-gradient-to-r from-blue-100 to-emerald-100 px-3 py-1 text-xs font-semibold text-blue-800" title="Supports PDF resume analysis">PDF supported</span>
                  <span className={`w-fit rounded-full px-3 py-1 text-xs font-semibold ${isModelReady ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}`}>
                    {isModelReady ? 'Ready to analyze' : 'Model warming up'}
                  </span>
                </div>
              </div>
              <UploadAndSummary />
            </div>

          </div>

      </div>
    </div>
  );
}

export default Dashboard
