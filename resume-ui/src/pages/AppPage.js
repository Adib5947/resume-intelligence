import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function AppPage() {
  const navigate = useNavigate();
  const [jobDesc, setJobDesc] = useState("");
  const [resume, setResume] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showResult, setShowResult] = useState(false);
  const [user, setUser] = useState(null);

  // ── Load user from localStorage on mount ──
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
      return;
    }
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login");
  };

  const handleMatch = async () => {
    if (!jobDesc.trim()) {
      setError("Please paste a job description.");
      return;
    }
    if (!resume) {
      setError("Please upload your resume (PDF).");
      return;
    }

    setError(null);
    setLoading(true);
    setShowResult(false);

    const formData = new FormData();
    formData.append("file", resume);
    formData.append("job_description", jobDesc);

    try {
      const res = await axios.post("http://127.0.0.1:8000/match", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(res.data);
      setShowResult(true);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail ||
        "Failed to connect to backend. Make sure the server is running on http://127.0.0.1:8000"
      );
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 75) return { bar: "from-green-400 to-emerald-500", text: "text-green-400" };
    if (score >= 50) return { bar: "from-yellow-400 to-orange-400", text: "text-yellow-400" };
    return { bar: "from-red-400 to-pink-500", text: "text-red-400" };
  };

  return (
    <div className="min-h-screen relative overflow-hidden text-white flex flex-col">

      {/* BACKGROUND */}
      <div className="absolute inset-0 bg-gradient-to-br from-black via-[#0f172a] to-purple-900" />
      <div className="absolute w-[800px] h-[800px] bg-pink-500 blur-[220px] opacity-30 right-0 top-0" />

      {/* FLOATING IMAGES */}
      <img src="/floating1.png" alt="" className="absolute left-[40px] top-1/2 -translate-y-1/2 w-[480px] opacity-20 blur-[2px] animate-floatSlow1 pointer-events-none" />
      <img src="/floating2.png" alt="" className="absolute right-[40px] top-1/2 -translate-y-1/2 w-[520px] opacity-20 blur-[2px] animate-floatSlow2 pointer-events-none" />

      {/* HEADER */}
      <div className="relative z-10 flex items-center justify-between p-6">
        <div className="flex items-center gap-3">
          <img src="/logo.png" alt="logo" className="w-10 h-10 rounded-lg border border-white/20" />
          <h1 className="text-xl font-semibold">Resume Intelligence</h1>
        </div>

        {/* User info + logout */}
        <div className="flex items-center gap-4">
          {user && (
            <span className="text-sm text-gray-300">
              👋 Hello, <span className="text-pink-400 font-medium">{user.username}</span>
            </span>
          )}
          <button
            onClick={handleLogout}
            className="text-sm px-4 py-2 border border-white/20 rounded-lg hover:bg-white/10 hover:border-pink-400 transition"
          >
            Logout
          </button>
        </div>
      </div>

      {/* MAIN */}
      <div className="flex-1 flex items-center justify-center px-6 overflow-hidden py-6">
        <div className="relative w-full max-w-6xl">

          <div className={`flex gap-6 transition-all duration-700 ease-in-out ${showResult ? "justify-between" : "justify-center"}`}>

            {/* ===== LEFT CARD — INPUT ===== */}
            <div className={`transition-all duration-700 ease-in-out ${showResult ? "w-[48%]" : "w-full max-w-xl"}`}>
              <div className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl p-10 shadow-2xl">

                <h2 className="text-3xl font-semibold mb-6">Paste Job Description</h2>

                <textarea
                  value={jobDesc}
                  onChange={(e) => setJobDesc(e.target.value)}
                  placeholder="Paste FULL job description here..."
                  className="w-full h-48 bg-transparent border border-white/20 rounded-xl p-4 focus:outline-none focus:border-pink-400 transition resize-none text-sm"
                />

                {/* FILE INPUT */}
                <label className="mt-4 flex items-center justify-between px-4 py-3 border border-white/20 rounded-xl cursor-pointer hover:border-pink-400 hover:shadow-lg transition group">
                  <span className="text-sm text-gray-300 group-hover:text-white truncate max-w-[70%]">
                    {resume ? resume.name : "Upload your Resume"}
                  </span>
                  <span className="text-xs px-3 py-1 rounded-md bg-white/10 group-hover:bg-gradient-to-r from-purple-500 to-pink-500 transition whitespace-nowrap">
                    Choose File
                  </span>
                  <input
                    type="file"
                    accept=".pdf"
                    className="hidden"
                    onChange={(e) => setResume(e.target.files[0])}
                  />
                </label>

                {/* ERROR */}
                {error && (
                  <p className="mt-3 text-red-400 text-sm bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-2">
                    ⚠️ {error}
                  </p>
                )}

                {/* BUTTON */}
                <button
                  onClick={handleMatch}
                  disabled={loading}
                  className="mt-6 w-full bg-gradient-to-r from-purple-500 to-pink-500 py-4 rounded-xl font-semibold text-lg hover:scale-105 transition disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:scale-100"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                      </svg>
                      Analyzing...
                    </span>
                  ) : "Match Resume ✓"}
                </button>

              </div>
            </div>

            {/* ===== RIGHT CARD — RESULTS ===== */}
            {showResult && result && (
              <div className="w-[48%] transition-all duration-700 ease-in-out">
                <div className="backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl p-10 shadow-2xl h-full overflow-y-auto max-h-[75vh]">

                  <h2 className="text-3xl font-semibold mb-6">AI Analysis Result</h2>

                  {/* MATCH SCORE */}
                  <div className="mb-6">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm text-gray-400">Match Score</span>
                      <span className={`text-2xl font-bold ${getScoreColor(result.match_score).text}`}>
                        {result.match_score}%
                      </span>
                    </div>
                    <div className="w-full bg-white/10 rounded-full h-3">
                      <div
                        className={`bg-gradient-to-r ${getScoreColor(result.match_score).bar} h-3 rounded-full transition-all duration-1000`}
                        style={{ width: `${result.match_score}%` }}
                      />
                    </div>
                  </div>

                  <div className="space-y-4 text-sm">

                    {/* JOB DETAILS */}
                    <Item label="Company Name" value={result.company} />
                    <Item label="Position" value={result.position} />
                    <Item label="Salary Range" value={result.salary} />
                    <Item label="Address" value={result.address} />
                    <Item label="Experience" value={result.experience} />
                    <Item label="Deadline" value={result.deadline} />

                    {/* RESPONSIBILITIES */}
                    {result.responsibilities && result.responsibilities.length > 0 && (
                      <div>
                        <p className="text-gray-400 text-xs mb-2">Responsibilities</p>
                        <ul className="space-y-1">
                          {result.responsibilities.map((r, i) => (
                            <li key={i} className="text-gray-300 flex items-start gap-2">
                              <span className="text-pink-400 mt-0.5">•</span>
                              <span>{r}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* REQUIREMENTS */}
                    {result.requirements && result.requirements.length > 0 && (
                      <div>
                        <p className="text-gray-400 text-xs mb-2">📌 Requirements</p>
                        <ul className="space-y-1">
                          {result.requirements.map((r, i) => (
                            <li key={i} className="text-gray-300 flex items-start gap-2">
                              <span className="text-blue-400 mt-0.5">•</span>
                              <span>{r}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* MATCHED SKILLS */}
                    {result.matched_skills && result.matched_skills.length > 0 && (
                      <div>
                        <p className="text-gray-400 text-xs mb-2">✅ Matched Skills</p>
                        <div className="flex flex-wrap gap-2">
                          {result.matched_skills.map((s, i) => (
                            <span key={i} className="px-2 py-1 bg-green-500/20 border border-green-500/30 text-green-400 rounded-lg text-xs">
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* MISSING SKILLS */}
                    {result.missing_skills && result.missing_skills.length > 0 && (
                      <div>
                        <p className="text-gray-400 text-xs mb-2">❌ Missing Skills</p>
                        <div className="flex flex-wrap gap-2">
                          {result.missing_skills.map((s, i) => (
                            <span key={i} className="px-2 py-1 bg-red-500/20 border border-red-500/30 text-red-400 rounded-lg text-xs">
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* MISSING IMPORTANT SKILLS */}
                    {result.missing_important_skills && result.missing_important_skills.length > 0 && (
                      <div>
                        <p className="text-gray-400 text-xs mb-2">⚠️ Important Skills to Add</p>
                        <div className="flex flex-wrap gap-2">
                          {result.missing_important_skills.map((s, i) => (
                            <span key={i} className="px-2 py-1 bg-orange-500/20 border border-orange-500/30 text-orange-400 rounded-lg text-xs">
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* SUGGESTIONS */}
                    {result.suggestions && result.suggestions.length > 0 && (
                      <div>
                        <p className="text-gray-400 text-xs mb-2">💡 AI Suggestions</p>
                        <ul className="space-y-1">
                          {result.suggestions.map((s, i) => (
                            <li key={i} className="text-purple-300 flex items-start gap-2">
                              <span className="text-purple-400 mt-0.5">→</span>
                              <span>{s}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                  </div>
                </div>
              </div>
            )}

          </div>
        </div>
      </div>

      {/* ANIMATIONS */}
      <style>{`
        @keyframes floatSlow1 {
          0% { transform: translateY(-50%) translateY(0px) rotate(-5deg); }
          50% { transform: translateY(-50%) translateY(-30px) rotate(5deg); }
          100% { transform: translateY(-50%) translateY(0px) rotate(-5deg); }
        }
        @keyframes floatSlow2 {
          0% { transform: translateY(-50%) translateY(0px) rotate(5deg); }
          50% { transform: translateY(-50%) translateY(-35px) rotate(-5deg); }
          100% { transform: translateY(-50%) translateY(0px) rotate(5deg); }
        }
        .animate-floatSlow1 { animation: floatSlow1 10s ease-in-out infinite; }
        .animate-floatSlow2 { animation: floatSlow2 12s ease-in-out infinite; }
      `}</style>

    </div>
  );
}

function Item({ label, value }) {
  return (
    <div>
      <p className="text-gray-400 text-xs">{label}</p>
      <p className="mt-1 text-gray-300">{value || "Not Mentioned"}</p>
    </div>
  );
}

export default AppPage;