import { useNavigate } from "react-router-dom";
import { useState } from "react";
import axios from "axios";

function SignupPage() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showSocialModal, setShowSocialModal] = useState(false);
  const [socialProvider, setSocialProvider] = useState("");

  const handleSignup = async () => {
    setError("");

    if (!username || !email || !password || !confirmPassword) {
      setError("Please fill in all fields.");
      return;
    }
    if (username.trim().length < 2) {
      setError("Username must be at least 2 characters.");
      return;
    }
    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      const res = await axios.post("http://127.0.0.1:8000/auth/signup", {
        username: username.trim(),
        email: email.trim(),
        password,
      });

      localStorage.setItem("token", res.data.token);
      localStorage.setItem("user", JSON.stringify(res.data.user));
      navigate("/app");

    } catch (err) {
      const msg = err.response?.data?.detail || "Signup failed. Please try again.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleSocialClick = (provider) => {
    setSocialProvider(provider);
    setShowSocialModal(true);
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden text-white">

      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-black via-[#0f172a] to-purple-900" />
      <div className="absolute w-[700px] h-[700px] bg-pink-500 blur-[200px] opacity-30 right-0" />

      {/* ── Coming Soon Modal ── */}
      {showSocialModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setShowSocialModal(false)}
          />
          <div className="relative z-10 bg-[#1a1f35] border border-white/20 rounded-2xl p-10 w-[400px] text-center shadow-2xl">
            <div className="text-5xl mb-4">
              {socialProvider === "Google" ? "🔵" : "🔷"}
            </div>
            <h3 className="text-2xl font-semibold mb-2">
              {socialProvider} Login
            </h3>
            <p className="text-gray-400 text-sm mb-6">
              {socialProvider} OAuth integration is coming soon!
              For now, please create an account using your email and password.
            </p>
            <button
              onClick={() => setShowSocialModal(false)}
              className="w-full bg-gradient-to-r from-purple-500 to-pink-500 py-3 rounded-xl font-semibold hover:scale-105 transition"
            >
              Got it
            </button>
          </div>
        </div>
      )}

      {/* Card */}
      <div className="relative z-10 backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl p-12 w-[500px] shadow-2xl">

        <h2 className="text-3xl font-semibold mb-2 text-center">Create Account</h2>
        <p className="text-center text-gray-400 text-sm mb-8">Join Resume Intelligence today</p>

        {/* Error */}
        {error && (
          <div className="mb-5 px-4 py-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
            ⚠️ {error}
          </div>
        )}

        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full mb-5 bg-transparent border-b border-gray-400 py-3 text-lg focus:outline-none focus:border-pink-400 placeholder-gray-400 transition"
        />
        <input
          type="email"
          placeholder="Email ID"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full mb-5 bg-transparent border-b border-gray-400 py-3 text-lg focus:outline-none focus:border-pink-400 placeholder-gray-400 transition"
        />
        <input
          type="password"
          placeholder="Password (min 6 characters)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full mb-5 bg-transparent border-b border-gray-400 py-3 text-lg focus:outline-none focus:border-pink-400 placeholder-gray-400 transition"
        />
        <input
          type="password"
          placeholder="Confirm Password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSignup()}
          className="w-full mb-6 bg-transparent border-b border-gray-400 py-3 text-lg focus:outline-none focus:border-pink-400 placeholder-gray-400 transition"
        />

        {/* Signup Button */}
        <button
          onClick={handleSignup}
          disabled={loading}
          className="w-full bg-gradient-to-r from-purple-500 to-pink-500 py-3.5 rounded-xl font-semibold text-lg hover:scale-105 hover:shadow-lg transition duration-300 disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:scale-100"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
              </svg>
              Creating account...
            </span>
          ) : "SIGN UP"}
        </button>

        {/* Divider */}
        <div className="my-6 flex items-center gap-3">
          <div className="flex-1 h-px bg-white/10" />
          <span className="text-gray-400 text-sm">or continue with</span>
          <div className="flex-1 h-px bg-white/10" />
        </div>

        {/* Social Buttons */}
        <div className="flex gap-4">
          <button
            onClick={() => handleSocialClick("Google")}
            className="flex items-center justify-center gap-3 flex-1 border border-white/20 py-3 rounded-lg hover:bg-white/10 hover:border-pink-400 hover:scale-105 transition duration-300"
          >
            <img src="/google.png" alt="Google" className="w-6 h-6" />
            <span className="text-sm font-medium">Google</span>
          </button>
          <button
            onClick={() => handleSocialClick("Facebook")}
            className="flex items-center justify-center gap-3 flex-1 border border-white/20 py-3 rounded-lg hover:bg-white/10 hover:border-pink-400 hover:scale-105 transition duration-300"
          >
            <img src="/facebook.png" alt="Facebook" className="w-6 h-6" />
            <span className="text-sm font-medium">Facebook</span>
          </button>
        </div>

        <p className="text-center text-sm text-gray-400 mt-6">
          Already have an account?{" "}
          <span
            onClick={() => navigate("/login")}
            className="text-pink-400 cursor-pointer hover:underline"
          >
            Login
          </span>
        </p>

      </div>
    </div>
  );
}

export default SignupPage;