'use client';

export default function NavBar() {
  return (
    <nav className="relative flex items-center justify-between px-20 py-8">
      {/* Left: Logo */}
      <div className="text-5xl font-bold text-white">
        S<span className="text-purple-500">1</span>
      </div>

      {/* Center: Links */}
      <div className="absolute left-1/2 -translate-x-1/2 flex gap-20 text-white/90 text-xl">
        <a href="#" className="hover:text-purple-400 transition-colors">
          Leaderboards
        </a>
        <a href="#" className="hover:text-purple-400 transition-colors">
          Documentation
        </a>
      </div>

      {/* Right: Login button */}
      <button className="bg-linear-to-r from-[#963CCD] to-[#891BCD] hover:opacity-90 text-white border-2 border-[#763F98] text-xl font-medium px-6 py-2 rounded-full flex items-center gap-2 transition duration-200">
        Login
        <span className="text-xl">→</span>
      </button>
    </nav>
  );
}
