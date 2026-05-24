import { useState } from "react";
import { Send, Mic, Volume2, Flame, ThumbsUp } from "lucide-react";

export function ChatRoom() {
  const [messages, setMessages] = useState([
    { id: 1, user: "ThalaFan7", text: "What an over by Bumrah! 🔥", time: "19:42" },
    { id: 2, user: "CricketGod_99", text: "Match is slipping away from RR now.", time: "19:43" },
    { id: 3, user: "HitmanRO", text: "Need a six here! Come on!", time: "19:44" },
  ]);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages([...messages, { id: Date.now(), user: "Guest User", text: input, time: "Now" }]);
    setInput("");
  };

  return (
    <div className="w-full h-full flex flex-col">
      <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2 scrollbar-hide flex flex-col justify-end">
        {messages.map((msg) => (
          <div key={msg.id} className="glass-card p-3 rounded-lg bg-white/5 border-none">
            <div className="flex items-baseline justify-between mb-1">
              <span className={`font-semibold text-sm ${msg.user === "Guest User" ? "text-brand-accent" : "text-brand-purple"}`}>
                {msg.user}
              </span>
              <span className="text-[10px] text-white/40">{msg.time}</span>
            </div>
            <p className="text-sm text-white/90">{msg.text}</p>
          </div>
        ))}
      </div>

      <div className="flex items-center gap-2 relative">
        <button className="p-3 rounded-full hover:bg-white/10 text-white/60 transition-colors">
          <Mic className="w-5 h-5" />
        </button>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Type a message..."
          className="flex-1 bg-white/5 border border-white/10 rounded-full px-4 py-3 outline-none focus:border-brand-accent/50 text-sm transition-colors"
        />
        <button
          onClick={handleSend}
          className="p-3 rounded-full bg-brand-accent text-brand-blue hover:scale-105 transition-transform"
        >
          <Send className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}

export function Soundboard() {
  const sounds = [
    { id: "whistle", icon: Volume2, label: "Whistle", color: "text-yellow-400" },
    { id: "dhol", icon: Flame, label: "Dhol Beats", color: "text-brand-orange" },
    { id: "cheer", icon: ThumbsUp, label: "Crowd Cheer", color: "text-green-400" },
    { id: "siren", icon: Volume2, label: "Air Raid", color: "text-red-400" },
  ];

  return (
    <div className="w-full h-full flex flex-col items-center justify-center gap-6">
      <div className="text-center">
        <h4 className="text-lg font-semibold mb-1">Live Reactions</h4>
        <p className="text-xs text-white/50">Tap to play globally in the room</p>
      </div>

      <div className="grid grid-cols-2 gap-4 w-full">
        {sounds.map((sound) => {
          const Icon = sound.icon;
          return (
            <button
              key={sound.id}
              className="glass-card aspect-square rounded-2xl flex flex-col items-center justify-center gap-3 hover:scale-105 active:scale-95 transition-all group border-white/10 hover:border-white/30"
            >
              <div className={`p-4 rounded-full bg-white/5 group-hover:bg-white/10 transition-colors ${sound.color}`}>
                <Icon className="w-8 h-8" />
              </div>
              <span className="text-sm font-medium text-white/80">{sound.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
