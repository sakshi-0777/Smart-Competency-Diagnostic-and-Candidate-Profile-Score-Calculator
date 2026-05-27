import React, {useState} from 'react'
import { API_BASE_URL } from "../config";
import {
  AlertCircle,
  BookOpen,
  Briefcase,
  CheckCircle2,
  HelpCircle,
  Loader2,
  Search,
  Upload,
} from 'lucide-react'

const UploadAndSummary = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState("");

  const handleFile = (e) => {
    setFile(e.target.files[0]);
    setResult(null);   // reset old result
    setError("");
  };

  const handleSearchJobs = async () => {
    if (!searchQuery.trim()) {
      setSearchError("Please enter keywords to search jobs.");
      return;
    }

    setSearchLoading(true);
    setSearchError("");
    setSearchResults([]);

    try {
      const res = await fetch(`${API_BASE_URL}/search_jobs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || data.message || "Search failed");
      }

      setSearchResults(data.jobs || []);
    } catch (err) {
      setSearchError(err.message || "Failed to search jobs");
    } finally {
      setSearchLoading(false);
    }
  };

  const analyzeResume = async () => {
    if (!file) {
      alert("Please upload a PDF resume.");
      return;
    }

    const formData = new FormData();
    formData.append("resume", file);

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await fetch(`${API_BASE_URL}/analyze_resume`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      console.log("API RESPONSE:", data);

      if (!res.ok) {
        throw new Error(data.error || data.message || "Something went wrong");
      }

      setResult(data);
    } catch (err) {
      console.error("ERROR:", err);
      setError(err.message || "Failed to analyze resume");
    } finally {
      setLoading(false);
    }
  };



  const fileName = file?.name || "No PDF selected";

  return (
    <div className="rounded-2xl border border-white/70 bg-white/85 p-4 shadow-xl shadow-blue-900/5 backdrop-blur sm:p-6">
      {/* Upload Section */}
      <div className="flex flex-col gap-4">
        <div className="grid gap-3 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center">
          <label
            className="group flex min-h-28 cursor-pointer flex-col justify-center rounded-xl border-2 border-dashed border-blue-200 bg-gradient-to-br from-blue-50 via-white to-emerald-50 p-4 transition-all duration-300 hover:-translate-y-0.5 hover:border-blue-400 hover:shadow-lg hover:shadow-blue-500/10"
            data-tooltip="Upload a PDF resume so the system can extract skills, jobs, and recommendations."
          >
            <input
              type="file"
              accept="application/pdf"
              onChange={handleFile}
              className="sr-only"
            />
            <span className="inline-flex items-center gap-3 text-sm font-semibold text-blue-800">
              <span className="rounded-lg bg-white p-2 text-blue-700 shadow-sm transition group-hover:bg-blue-700 group-hover:text-white">
                <Upload className="h-5 w-5" />
              </span>
              Choose resume PDF
            </span>
            <span className="mt-3 flex items-center gap-2 break-all text-sm text-slate-600">
              {file ? <CheckCircle2 className="h-4 w-4 flex-shrink-0 text-emerald-600" /> : <HelpCircle className="h-4 w-4 flex-shrink-0 text-blue-500" />}
              {fileName}
            </span>
          </label>
          <button
            onClick={analyzeResume}
            disabled={loading}
            className="inline-flex min-h-12 items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-700 via-cyan-600 to-emerald-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-700/20 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-xl hover:shadow-cyan-700/25 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60 lg:min-w-44"
            data-tooltip="Analyze the uploaded resume and generate matching jobs and courses."
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4" />}
            <span>{loading ? "Analyzing..." : "Analyze Resume"}</span>
          </button>
        </div>

        <div className="grid gap-3 rounded-xl border border-blue-100 bg-gradient-to-r from-white via-cyan-50 to-white p-3 md:grid-cols-[minmax(0,1fr)_auto] md:items-center">
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-blue-500" />
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search jobs by keyword, skill, or role"
              className="w-full rounded-xl border border-blue-100 bg-white/90 py-3 pl-10 pr-4 text-sm text-slate-800 shadow-sm outline-none transition focus:border-cyan-400 focus:ring-4 focus:ring-cyan-100"
              title="Try roles like React Developer, Data Analyst, or Python"
            />
          </div>
          <button
            onClick={handleSearchJobs}
            disabled={searchLoading}
            className="inline-flex min-h-12 items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-emerald-700/15 transition-all duration-300 hover:-translate-y-0.5 hover:from-emerald-700 hover:to-cyan-700 hover:shadow-xl hover:shadow-emerald-700/20 focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60 md:min-w-36"
            data-tooltip="Search job descriptions against the keywords you type."
          >
            {searchLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
            <span>{searchLoading ? "Searching..." : "Search Jobs"}</span>
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <p className="mt-4 inline-flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"><AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0" /> {error}</p>
      )}

      {/* Backend message (like model loading) */}
      {result?.message && (
        <p className="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-700">{result.message}</p>
      )}

      {searchError && (
        <p className="mt-4 inline-flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700"><AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0" /> {searchError}</p>
      )}

      {searchResults.length > 0 && (
        <div className="mt-4 rounded-xl border border-cyan-100 bg-gradient-to-br from-cyan-50 via-white to-emerald-50 p-4">
          <h2 className="inline-flex items-center gap-2 text-lg font-semibold text-slate-900" data-tooltip="Jobs ranked by how closely they match your search terms."><Search className="h-5 w-5 text-cyan-700" /> Search Results</h2>
          <ul className="mt-3 grid gap-3 text-sm text-slate-700 sm:grid-cols-2">
            {searchResults.map((job, i) => (
              <li key={i} className="rounded-xl border border-white/80 bg-white p-3 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-cyan-200 hover:shadow-lg">
                <div className="font-semibold text-slate-900">{job.title}</div>
                <div className="mt-1 text-xs font-medium text-cyan-700" title="Higher score means a closer keyword match">Score: {job.score?.toFixed(2)}</div>
                <div className="mt-2 line-clamp-4 text-sm text-slate-600">{job.description}</div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-3">
          {/* Left Panel */}
          <div className="space-y-5 xl:col-span-2">


            {/* Matching Jobs */}
            <section>
              <h2 className="inline-flex items-center gap-2 text-lg font-semibold text-slate-900" data-tooltip="Resume-based roles ranked by compatibility."><Briefcase className="h-5 w-5 text-blue-700" /> Matching Jobs</h2>
              <ul className="mt-3 grid gap-3 md:grid-cols-2">
                {result?.matched_jobs?.length > 0 ? (
                  result.matched_jobs.map((job, i) => (
                    <li key={i} className="rounded-xl border border-blue-100 bg-gradient-to-br from-white to-blue-50 p-4 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-blue-300 hover:shadow-lg">
                      <div className="font-semibold text-sm text-slate-900">{job.title}</div>
                      <div className="mt-2 h-2 overflow-hidden rounded-full bg-blue-100" title={`Match score: ${job.score?.toFixed(2)}`}>
                        <div className="h-full rounded-full bg-gradient-to-r from-blue-600 to-emerald-500" style={{ width: `${Math.min((job.score || 0) * 100, 100)}%` }}></div>
                      </div>
                      <div className="mt-1 text-xs font-medium text-blue-700">Score: {job.score?.toFixed(2)}</div>
                      <p className="mt-2 line-clamp-5 text-sm text-slate-600">{job.description}</p>
                    </li>
                  ))
                ) : (
                  <li className="rounded-lg bg-slate-50 p-3 text-sm text-slate-600">No matching jobs</li>
                )}
              </ul>
            </section>

            {/* Recommended Courses */}
            <section>
              <h2 className="inline-flex items-center gap-2 text-lg font-semibold text-slate-900" data-tooltip="Courses selected from the skill gaps found in your resume."><BookOpen className="h-5 w-5 text-emerald-700" /> Recommended Courses</h2>
              <ul className="mt-3 grid gap-3 md:grid-cols-2">
                {result?.recommended_courses?.length > 0 ? (
                  result.recommended_courses.map((c, i) => (
                    <li key={i} className="rounded-xl border border-emerald-100 bg-gradient-to-br from-white to-emerald-50 p-4 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-emerald-300 hover:shadow-lg" title={`Open course on ${c.platform || 'learning platform'}`}>
                      <a href={c.url || '#'} target="_blank" rel="noopener noreferrer" className="font-semibold text-sm text-blue-700 transition hover:text-emerald-700 hover:underline">
                        {c.title}
                      </a>
                      <div className="mt-2 inline-flex rounded-full bg-emerald-100 px-2 py-1 text-xs font-medium text-emerald-800">{c.platform}</div>
                    </li>
                  ))
                ) : (
                  <li className="rounded-lg bg-slate-50 p-3 text-sm text-slate-600">No recommendations</li>
                )}
              </ul>
            </section>

          </div>

          
        </div>
      )}
    </div>

  )
}

export default UploadAndSummary
