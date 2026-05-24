"use client";

import { useState } from "react";
import { MessageSquare, Clock, Trophy, Target, Menu, Bell, User } from "lucide-react";
import { motion } from "framer-motion";
import TimeMachine from "@/components/TimeMachine";
import { PredictionArena, LiveLeaderboard } from "@/components/Predictions";
import { ChatRoom, Soundboard } from "@/components/Lounge";

export default function Home() {
  const [activeTab, setActiveTab] = useState("time-machine");

  const tabs = [
    { id: "time-machine", icon: Clock, label: "Time Machine" },
    { id: "predictions", icon: Target, label: "Live Predictions" },
    { id: "lounge", icon: MessageSquare, label: "Chai-Tapri Lounge" },
  ];

  return (
    <div className="flex h-screen w-full overflow-hidden">
      {/* Sidebar */}
      <aside className="w-20 lg:w-64 glass border-r flex flex-col items-center lg:items-start py-8 transition-all duration-300 z-20">
        <div className="px-4 lg:px-8 mb-12 w-full flex justify-center lg:justify-start items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-brand-accent to-brand-purple flex items-center justify-center shadow-lg shadow-brand-accent/20">
            <Trophy className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-xl font-bold hidden lg:block text-gradient">CricVerse</h1>
        </div>

        <nav className="flex-1 w-full px-2 lg:px-4 space-y-4">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center justify-center lg:justify-start gap-4 p-3 rounded-xl transition-all duration-300 ${
                  isActive
                    ? "bg-white/10 text-brand-accent border border-brand-accent/30 shadow-[0_0_15px_rgba(0,229,255,0.15)]"
                    : "text-white/60 hover:bg-white/5 hover:text-white"
                }`}
              >
                <Icon className={`w-6 h-6 ${isActive ? "text-brand-accent" : ""}`} />
                <span className="hidden lg:block font-medium">{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col relative overflow-hidden">
        {/* Top Navbar */}
        <header className="h-20 w-full glass border-b flex items-center justify-between px-8 z-10">
          <div className="flex items-center gap-4">
            <Menu className="w-6 h-6 text-white/80 lg:hidden cursor-pointer" />
            <h2 className="text-xl font-semibold capitalize tracking-wide hidden md:block">
              {activeTab.replace("-", " ")}
            </h2>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="glass-card p-2 rounded-full cursor-pointer hover:bg-white/10">
              <Bell className="w-5 h-5 text-white/80" />
            </div>
            <div className="flex items-center gap-3 glass-card px-4 py-2 rounded-full cursor-pointer">
              <User className="w-5 h-5 text-brand-accent" />
              <span className="font-medium text-sm hidden sm:block">Guest User</span>
            </div>
          </div>
        </header>

        {/* Dynamic Content */}
        <div className="flex-1 overflow-y-auto p-4 md:p-8 scrollbar-hide relative z-0">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="h-full"
          >
            {activeTab === "time-machine" && (
              <div className="h-full flex flex-col gap-6">
                <div className="glass-card p-8 rounded-3xl">
                  <h3 className="text-2xl font-bold mb-2">The IPL Time Machine</h3>
                  <p className="text-white/60">Scrub through history from 2008 to 2026. Relive the greatest moments.</p>
                </div>
                <div className="flex-1 flex items-center justify-center py-10">
                  <TimeMachine />
                </div>
              </div>
            )}

            {activeTab === "predictions" && (
              <div className="h-full flex flex-col gap-6">
                <div className="glass-card p-8 rounded-3xl bg-gradient-to-r from-brand-orange/20 to-transparent">
                  <h3 className="text-2xl font-bold mb-2">Live Match Predictions</h3>
                  <p className="text-white/60">Predict ball-by-ball. Top the leaderboard.</p>
                </div>
                <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div className="lg:col-span-2 glass-card rounded-3xl p-8">
                    <PredictionArena />
                  </div>
                  <div className="glass-card rounded-3xl p-8">
                    <LiveLeaderboard />
                  </div>
                </div>
              </div>
            )}

            {activeTab === "lounge" && (
              <div className="h-full flex flex-col gap-6">
                <div className="glass-card p-8 rounded-3xl bg-gradient-to-r from-brand-purple/20 to-transparent">
                  <h3 className="text-2xl font-bold mb-2">Chai-Tapri Lounge</h3>
                  <p className="text-white/60">Join the live commentary. React instantly.</p>
                </div>
                <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-6">
                  <div className="lg:col-span-3 glass-card rounded-3xl p-6 h-[500px]">
                    <ChatRoom />
                  </div>
                  <div className="glass-card rounded-3xl p-6 h-[500px]">
                    <Soundboard />
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        </div>
      </main>
    </div>
  );
}
