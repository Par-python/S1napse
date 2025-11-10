import Image from "next/image";
import NavBar from "../../components/navbar";

export default function Home() {
  return (
    <div
      className="flex min-h-screen flex-col font-sans bg-no-repeat bg-top sm:bg-cover lg:bg-[length:100%_auto]"
      style={{
        backgroundImage: "url('/assets/bg_gradient.png')",
      }}
      >

      <NavBar />

      <main className="flex flex-1 flex-col tems-center justify-center">
        <div className="flex flex-col items-center justify-center mt-40">
          <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl xl:text-9xl font-bold text-white">
            S<span className="text-purple-500">1</span>napse
          </h1>
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

        <div className="mt-16 sm:mt-20 w-full flex justify-center items-center text-center text-2xl sm:text-3xl md:text-4xl text-white px-4">
          What does <span className="font-bold italic px-2"> S1napse </span> offer?
        </div>
        <div className="mt-10 w-full px-4 mx-auto">
          <div className="mx-auto w-full max-w-6xl grid grid-cols-1 gap-6 lg:grid-cols-2 lg:grid-rows-2">
            {/* Left Top: Real-Time Telemetry */}
            <div className="rounded-[28px] border border-white/20 bg-black/40 p-6 text-white shadow-[0_0_30px_-10px_rgba(0,0,0,0.6)]">
              <h3 className="text-3xl font-bold leading-tight">
                Real-Time Telemetry,<br />Simplified
              </h3>
              <div className="mt-4 w-full md:float-right md:-ml-6 md:-mr-3 md:mb-2 md:mt-0 md:w-60 lg:w-72 lg:-ml-20 lg:-mr-6 xl:w-80">
                <Image
                  src="/assets/realtime-graph.png"
                  alt="Real-time telemetry graph"
                  width={920}
                  height={660}
                  className="w-full"
                  priority
                />
              </div>

              <p className="mt-12 text-white/90 leading-relaxed md:mt-17 md:pr-16">
                Watch your data come alive.
              </p>
              <p className="mt-1 text-white/90 leading-relaxed md:pr-6">
                Monitor speed, RPM, throttle, tire temps, and more through responsive,
                real-time dashboards.
              </p>
              <p className="mt-1 font-semibold text-white md:mt-2 md:pt-2 md:block md:w-full md:clear-right">
                No locked features, no paywalls.
              </p>
              <div className="clear-both" />
            </div>
            {/* Right: Effortless Data Export (spans full height) */}
            <div className="flex flex-col rounded-[28px] border border-white/20 bg-black/40 p-6 text-white shadow-[0_0_30px_-10px_rgba(0,0,0,0.6)] lg:row-span-2 lg:col-start-2">
              <h3 className="text-3xl font-bold leading-tight">
                Effortless Data Export
              </h3>
              <p className="mt-6 text-white/90 leading-relaxed">
                Take full control of your telemetry data with effortless export options.
              </p>
              <p className="mt-4 text-white/90 leading-relaxed">
                Export session files in CSV, JSON, or other popular formats to analyze,
                share, or integrate into your own tools.
              </p>
              <ul className="mt-6 space-y-2 text-white/90 leading-relaxed">
                <li className="list-disc list-inside"><span className="font-semibold text-white">Visualize laps</span> in your favorite spreadsheet or plotting software</li>
                <li className="list-disc list-inside"><span className="font-semibold text-white">Feed data</span> into simulation tools</li>
                <li className="list-disc list-inside"><span className="font-semibold text-white">Share</span> your performance with friends or coaches</li>
              </ul>
              <div className="mt-8">
                <Image
                  src="/assets/data-graph.png"
                  alt="Exported telemetry data visualization"
                  width={720}
                  height={320}
                  className="w-full rounded-[22px] border border-white/15 bg-black/60"
                />
              </div>
            </div>
            {/* Left Bottom: Lap Comparison */}
            <div className="rounded-[28px] border border-white/20 bg-black/40 p-6 text-white shadow-[0_0_30px_-10px_rgba(0,0,0,0.6)] lg:row-start-2">
              <h3 className="text-3xl font-bold leading-tight">
                Lap Comparison<br />Made Easy
              </h3>
              <div className="mt-4 w-full md:float-right md:ml-6 md:mt-0 md:w-44 lg:w-52">
                <Image
                  src="/assets/lap-graph.png"
                  alt="Lap comparison chart"
                  width={720}
                  height={260}
                  className="w-full rounded-[20px] border border-white/15 bg-black/60"
                />
              </div>
              <p className="mt-6 text-white/90 leading-relaxed md:mt-0">
                Compare your laps to spot improvements and fine‑tune your performance.
              </p>
              <div className="clear-both" />
            </div>
          </div>
        </div>
        </main> 
    </div>
  );
}
