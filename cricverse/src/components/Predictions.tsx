import { useState } from "react";
import { motion } from "framer-motion";
import { CircleDot, TrendingUp, Trophy } from "lucide-react";

export function PredictionArena() {
  const [selectedOption, setSelectedOption] = useState<string | null>(null);

  const options = [
    { id: "dot", label: "Dot Ball", multiplier: "1.5x", color: "bg-gray-500/20 text-gray-300" },
    { id: "single", label: "1 Run", multiplier: "1.2x", color: "bg-blue-500/20 text-blue-300" },
    { id: "four", label: "Boundary (4)", multiplier: "3.0x", color: "bg-brand-accent/20 text-brand-accent" },
    { id: "six", label: "Maximum (6)", multiplier: "5.0x", color: "bg-brand-orange/20 text-brand-orange" },
    { id: "wicket", label: "Wicket!", multiplier: "8.0x", color: "bg-red-500/20 text-red-400" },
  ];

  return (
    <div className="w-full h-full flex flex-col items-center justify-center gap-8">
      <div className="text-center space-y-2">
        <h4 className="text-xl font-semibold flex items-center justify-center gap-2">
          <CircleDot className="w-5 h-5 text-red-500 animate-pulse" />
          Over 14.3
        </h4>
        <p className="text-white/60">Predict the outcome of the next delivery!</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 w-full max-w-2xl">
        {options.map((opt) => (
          <button
            key={opt.id}
            onClick={() => setSelectedOption(opt.id)}
            className={`p-4 rounded-2xl border transition-all duration-300 flex flex-col items-center gap-2 ${
              selectedOption === opt.id
                ? "border-brand-accent shadow-[0_0_20px_rgba(0,229,255,0.3)] bg-white/10 scale-105"
                : "border-white/10 hover:bg-white/5 hover:border-white/30"
            }`}
          >
            <span className={`px-3 py-1 rounded-full text-xs font-bold ${opt.color}`}>
              {opt.multiplier}
            </span>
            <span className="font-medium text-lg">{opt.label}</span>
          </button>
        ))}
      </div>

      <button
        disabled={!selectedOption}
        className="px-8 py-3 rounded-full bg-gradient-to-r from-brand-accent to-brand-purple text-white font-bold text-lg disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 transition-transform"
      >
        Lock Prediction
      </button>
    </div>
  );
}

export function LiveLeaderboard() {
  const leaderboard = [
    { rank: 1, name: "CricketGod_99", points: 2450 },
    { rank: 2, name: "ThalaFan7", points: 2320 },
    { rank: 3, name: "HitmanRO", points: 2100 },
    { rank: 4, name: "KingKohli18", points: 1950 },
    { rank: 5, name: "Guest User", points: 150, isCurrent: true },
  ];

  return (
    <div className="w-full h-full flex flex-col">
      <div className="flex items-center gap-2 mb-6">
        <TrendingUp className="w-6 h-6 text-brand-orange" />
        <h4 className="text-xl font-semibold">Live Standings</h4>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 scrollbar-hide">
        {leaderboard.map((user) => (
          <motion.div
            key={user.rank}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: user.rank * 0.1 }}
            className={`flex items-center justify-between p-4 rounded-xl border ${
              user.isCurrent
                ? "bg-brand-purple/20 border-brand-purple/50"
                : "bg-white/5 border-white/5"
            }`}
          >
            <div className="flex items-center gap-4">
              <span className={`font-bold w-6 text-center ${
                user.rank === 1 ? "text-yellow-400" :
                user.rank === 2 ? "text-gray-300" :
                user.rank === 3 ? "text-amber-600" : "text-white/50"
              }`}>
                #{user.rank}
              </span>
              <span className={`font-medium ${user.isCurrent ? "text-brand-accent" : ""}`}>
                {user.name}
              </span>
            </div>
            <div className="flex items-center gap-1 text-white/80">
              <span className="font-bold">{user.points}</span>
              <span className="text-xs text-white/40">pts</span>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
