'use client';

export default function NavBar() {
  return (
    <nav className="relative flex items-center justify-between px-4 sm:px-8 lg:px-20 py-4 sm:py-6 lg:py-8">
      {/* Left: Logo */}
      <div className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white">
        S<span className="text-purple-500">1</span>
      </div>

      {/* Center: Links */}
      <div className="absolute left-1/2 -translate-x-1/2 hidden sm:flex gap-6 md:gap-10 lg:gap-20 text-white/90 text-sm md:text-base lg:text-xl">
        <a href="#" className="hover:text-purple-400 transition-colors">
          Leaderboards
        </a>
        <a href="#" className="hover:text-purple-400 transition-colors">
          Documentation
        </a>
      </div>

      {/* Right: Login button */}
      <button className="bg-linear-to-r from-[#963CCD] to-[#891BCD] hover:opacity-90 text-white border-2 border-[#763F98] text-sm md:text-base lg:text-xl font-medium px-4 md:px-6 py-2 rounded-full flex items-center gap-2 transition duration-200">
        Login
        <span className="text-base md:text-lg lg:text-xl">→</span>
      </button>
    </nav>
  );
}
