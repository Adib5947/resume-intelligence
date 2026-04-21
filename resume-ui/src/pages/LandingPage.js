import { useNavigate } from "react-router-dom";
import { useState } from "react";

function LandingPage() {
  const navigate = useNavigate();

  const [dragStart, setDragStart] = useState(null);
  const [translateY, setTranslateY] = useState(0);
  const [locked, setLocked] = useState(false);

  const handleStart = (e) => {
    if (locked) return;
    setDragStart(e.clientY);
  };

  const handleMove = (e) => {
    if (dragStart === null || locked) return;
    const diff = dragStart - e.clientY;
    if (diff > 0) {
      setTranslateY(Math.min(diff, window.innerHeight));
    }
  };

  const handleEnd = () => {
    if (translateY > 150) {
      setTranslateY(window.innerHeight);
      setLocked(true);
    } else {
      setTranslateY(0);
    }
    setDragStart(null);
  };

  const handleStartApp = () => {
    const token = localStorage.getItem("token");
    if (!token) {
      navigate("/login");
    } else {
      navigate("/app");
    }
  };

  return (
    <div
      className="h-screen w-full overflow-hidden text-white"
      onMouseDown={handleStart}
      onMouseMove={handleMove}
      onMouseUp={handleEnd}
      onMouseLeave={handleEnd}
    >
      <div
        className="transition-all duration-500"
        style={{ transform: `translateY(-${translateY}px)` }}
      >

        {/* ===================== */}
        {/* FIRST SCREEN */}
        {/* ===================== */}
        <section className="h-screen flex flex-col justify-center items-center relative overflow-hidden">

          {/* Background */}
          <div className="absolute inset-0 bg-gradient-to-br from-black via-[#0f172a] to-purple-900" />
          <div className="absolute w-[700px] h-[700px] bg-pink-500 blur-[200px] opacity-30 right-0" />

          <div className="relative z-10 text-center max-w-4xl px-6">
            <img
              src="/logo.png"
              alt="logo"
              className="w-28 h-28 mx-auto mb-8 rounded-xl border border-white/20 shadow-lg"
            />
            <h1 className="text-6xl md:text-8xl font-bold leading-tight mb-6">
              Resume{" "}
              <span className="bg-gradient-to-r from-purple-400 via-pink-500 to-indigo-400 text-transparent bg-clip-text">
                Intelligence
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-gray-300">
              Turn your CV into a job-winning weapon
            </p>
            <p className="mt-8 text-sm text-gray-500">
              Click + Drag Up ↑
            </p>
          </div>
        </section>

        {/* ===================== */}
        {/* SECOND SCREEN */}
        {/* ===================== */}
        <section className="h-screen flex items-center justify-between px-32 relative overflow-hidden">

          {/* Background */}
          <div className="absolute inset-0 bg-gradient-to-br from-black via-[#0f172a] to-purple-900" />
          <div className="absolute right-0 w-[600px] h-[600px] bg-pink-500 blur-[180px] opacity-30" />

          {/* LEFT */}
          <div className="relative z-10 max-w-2xl">
            <h1 className="text-6xl md:text-7xl font-bold leading-tight">
              Match Your Resume <br />
              <span className="text-pink-500">With Real Job Signals</span>
            </h1>
            <p className="mt-8 text-lg text-gray-300 max-w-lg">
              Get instant AI-powered insights, identify missing skills, and
              optimize your resume for real-world job descriptions.
            </p>
            <button
              onClick={handleStartApp}
              className="mt-10 bg-gradient-to-r from-pink-500 to-orange-500 px-8 py-4 text-lg rounded-xl hover:scale-105 transition shadow-lg"
            >
              Launch Matcher →
            </button>
          </div>

          {/* RIGHT FLOATING */}
          <div className="relative w-[650px] h-[500px] hidden md:block">
            <img
              src="/floating1.png"
              alt="cv1"
              className="absolute w-80 animate-float1 drop-shadow-[0_20px_40px_rgba(0,0,0,0.6)]"
              style={{ top: "5%", left: "5%" }}
            />
            <img
              src="/floating2.png"
              alt="cv2"
              className="absolute w-96 animate-float2 drop-shadow-[0_20px_40px_rgba(0,0,0,0.6)]"
              style={{ top: "35%", left: "45%" }}
            />
          </div>

        </section>

      </div>

      {/* ANIMATIONS */}
      <style>{`
        @keyframes float1 {
          0% { transform: translateY(0px) rotate(-5deg); }
          50% { transform: translateY(-25px) rotate(5deg); }
          100% { transform: translateY(0px) rotate(-5deg); }
        }
        @keyframes float2 {
          0% { transform: translateY(0px) rotate(6deg); }
          50% { transform: translateY(-30px) rotate(-6deg); }
          100% { transform: translateY(0px) rotate(6deg); }
        }
        .animate-float1 { animation: float1 6s ease-in-out infinite; }
        .animate-float2 { animation: float2 7s ease-in-out infinite; }
      `}</style>

    </div>
  );
}

export default LandingPage;