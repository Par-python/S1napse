import NavBar from "../../components/navbar";

export default function Home() {
  return (
    <div
      className="flex min-h-screen flex-col font-sans"
      style={{
        backgroundImage: "url('/assets/bg_gradient.png')",
        backgroundPosition: "top center",
        backgroundRepeat: "no-repeat",
        backgroundSize: "100% auto",
      }}
      >

      <NavBar />

      <main className="flex flex-1 flex-col tems-center justify-center">
        <div className="flex flex-col items-center justify-center mt-40">
          <h1 className="text-9xl font-bold text-white">S<span className="text-purple-500">1</span>napse</h1>
          <p className="text-lg py-2 text-white">Telemetry made simple, open, and smart.</p>
          <button className="bg-linear-to-r from-[#963CCD] to-[#891BCD] hover:opacity-90 text-white border-2 border-[#763F98] text-xl font-medium px-6 py-2 rounded-full flex items-center gap-2 transition duration-200">
            Download
            <span className="text-xl">→</span>
          </button>
        </div>
        <div className="mt-8 px-5 w-full flex justify-center">
          <video
            className="w-full max-w-7xl rounded-[30px] border border-white overflow-hidden"
            src="/assets/header_vid.mp4"
            autoPlay
            loop
            muted
            playsInline
            controls={false}
          />
        </div>

        <div className="mt-20 w-full flex justify-center items-center text-3xl text-white text-center">
          What does <span className="font-bold italic px-2"> S1napse </span> offer?
        </div>
        <div className="mt-10 w-[80%] px-5 mx-auto">
          <div className="mx-auto w-full max-w-7xl grid grid-cols-1 gap-8 lg:grid-cols-2 lg:grid-rows-2">
            {/* Left Top: Real-Time Telemetry */}
            <div className="rounded-[30px] border border-white/20 bg-white/105  p-8 text-white">
              <h3 className="text-3xl font-bold leading-tight">
                Real-Time Telemetry,<br />Simplified
              </h3>
              <p className="mt-6 text-white/90">
                Watch your data come alive.
              </p>
              <p className="mt-2 text-white/90">
                Monitor speed, RPM, throttle, tire temps, and more through responsive,
                real-time dashboards.
              </p>
              <p className="mt-4 font-semibold">
                No locked features, no paywalls.
              </p>
            </div>
            {/* Right: Effortless Data Export (spans full height) */}
            <div className="rounded-[30px] border border-white/20 g-white/105  p-8 text-white lg:row-span-2 lg:col-start-2 h-full">
              <h3 className="text-3xl font-bold leading-tight">
                Effortless Data Export
              </h3>
              <p className="mt-6 text-white/90">
                Take full control of your telemetry data with effortless export options.
              </p>
              <p className="mt-2 text-white/90">
                Export session files in CSV, JSON, or other popular formats to analyze,
                share, or integrate into your own tools.
              </p>
              <ul className="mt-6 space-y-3 text-white/90">
                <li className="list-disc list-inside"><span className="font-semibold">Visualize laps</span> in your favorite spreadsheet or plotting software</li>
                <li className="list-disc list-inside"><span className="font-semibold">Feed data</span> into simulation tools</li>
                <li className="list-disc list-inside"><span className="font-semibold">Share</span> with teammates or coaches</li>
              </ul>
            </div>
            {/* Left Bottom: Lap Comparison */}
            <div className="rounded-[30px] border border-white/20 bg-white/105 p-8 text-white lg:row-start-2">
              <h3 className="text-3xl font-bold leading-tight">
                Lap Comparison<br />Made Easy
              </h3>
              <p className="mt-6 text-white/90">
                Compare your laps to spot improvements and fine‑tune your performance.
              </p>
            </div>
          </div>
        </div>
        </main> 
    </div>
  );
}
