import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight, Trophy, Zap, Shield, Flame } from "lucide-react";

const IPL_YEARS = Array.from({ length: 19 }, (_, i) => 2008 + i);

const MOCK_DATA = {
  2008: { winner: "Rajasthan Royals", topScorer: "Shaun Marsh", topWickets: "Sohail Tanvir", highlight: "The Inception of IPL" },
  2014: { winner: "Kolkata Knight Riders", topScorer: "Robin Uthappa", topWickets: "Mohit Sharma", highlight: "Gautam Gambhir's masterclass" },
  2023: { winner: "Chennai Super Kings", topScorer: "Shubman Gill", topWickets: "Mohammed Shami", highlight: "Dhoni's Last Ball Thriller" },
  2026: { winner: "Royal Challengers Bengaluru", topScorer: "Virat Kohli", topWickets: "Jasprit Bumrah", highlight: "The Era of 280+ Run Chases" },
};

export default function TimeMachine() {
  const [currentYear, setCurrentYear] = useState(2026);

  const handleNext = () => setCurrentYear((prev) => Math.min(2026, prev + 1));
  const handlePrev = () => setCurrentYear((prev) => Math.max(2008, prev - 1));

  // Fallback data if year not in mock
  const data = MOCK_DATA[currentYear as keyof typeof MOCK_DATA] || {
    winner: "Unknown",
    topScorer: "TBD",
    topWickets: "TBD",
    highlight: "Fetching Archives...",
  };

  return (
    <div className="w-full h-full flex flex-col items-center">
      {/* Year Selector */}
      <div className="flex items-center gap-6 mb-12 relative z-10">
        <button onClick={handlePrev} disabled={currentYear === 2008} className="p-3 glass-card rounded-full hover:bg-white/10 disabled:opacity-50 transition-all">
          <ChevronLeft className="w-6 h-6 text-brand-accent" />
        </button>

        <div className="flex gap-2 overflow-hidden w-64 justify-center items-center">
          <AnimatePresence mode="popLayout">
            <motion.h2
              key={currentYear}
              initial={{ y: 50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: -50, opacity: 0 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
              className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-br from-white to-white/50 drop-shadow-[0_0_10px_rgba(0,229,255,0.5)]"
            >
              {currentYear}
            </motion.h2>
          </AnimatePresence>
        </div>

        <button onClick={handleNext} disabled={currentYear === 2026} className="p-3 glass-card rounded-full hover:bg-white/10 disabled:opacity-50 transition-all">
          <ChevronRight className="w-6 h-6 text-brand-accent" />
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 w-full relative z-10">
        <StatCard icon={<Trophy className="w-6 h-6 text-yellow-400" />} title="Champions" value={data.winner} delay={0.1} />
        <StatCard icon={<Flame className="w-6 h-6 text-brand-orange" />} title="Orange Cap" value={data.topScorer} delay={0.2} />
        <StatCard icon={<Zap className="w-6 h-6 text-brand-purple" />} title="Purple Cap" value={data.topWickets} delay={0.3} />
        <StatCard icon={<Shield className="w-6 h-6 text-green-400" />} title="Era Highlight" value={data.highlight} delay={0.4} />
      </div>

      {/* Background Decorative Element */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-brand-accent/20 rounded-full blur-[120px] -z-10 pointer-events-none" />
    </div>
  );
}

function StatCard({ icon, title, value, delay }: { icon: React.ReactNode; title: string; value: string; delay: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="glass-card p-6 rounded-2xl flex flex-col items-start gap-4 border border-white/10 hover:border-brand-accent/50 group"
    >
      <div className="p-3 rounded-xl bg-white/5 group-hover:scale-110 transition-transform duration-300">
        {icon}
      </div>
      <div>
        <p className="text-sm text-white/50 mb-1">{title}</p>
        <p className="text-xl font-semibold text-white/90">{value}</p>
      </div>
    </motion.div>
  );
}
