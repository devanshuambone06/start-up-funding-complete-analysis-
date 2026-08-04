import React from "react";

export function Card({ children, className = "" }) {
  return (
    <div
      className={`bg-slate-900/60 border border-slate-800 rounded-2xl p-6  ${className}`}
    >
      {children}
    </div>
  );
}

export function Badge({ children, tone = "purple" }) {
  const tones = {
    purple: "bg-violet-500/15 text-violet-300 border-violet-500/30",
    green: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
    blue: "bg-blue-500/15 text-blue-300 border-blue-500/30",
    amber: "bg-amber-500/15 text-amber-300 border-amber-500/30",
    red: "bg-rose-500/15 text-rose-300 border-rose-500/30",
    gray: "bg-slate-500/15 text-slate-300 border-slate-500/30",
  };
  return (
    <span
      className={`text-[11px] font-semibold tracking-wide uppercase px-2.5 py-1 rounded-full border ${tones[tone]}`}
    >
      {children}
    </span>
  );
}

export function levelTone(level) {
  if (level === "Low") return "green";
  if (level === "Medium") return "amber";
  if (level === "High") return "red";
  return "gray";
}

export function ProgressBar({ value, max = 100, color = "#8b5cf6" }) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  return (
    <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
      <div
        className="h-full rounded-full transition-all duration-700"
        style={{ width: `${pct}%`, backgroundColor: color }}
      />
    </div>
  );
}

export function ScoreStat({ icon: Icon, title, value, tag, color }) {
  return (
    <Card>
      <div className="flex items-center justify-between mb-5">
        <div
          className="w-10 h-10 rounded-xl flex items-center justify-center"
          style={{ backgroundColor: `${color}22`, color }}
        >
          <Icon size={20} />
        </div>
        <Badge tone="gray">{tag}</Badge>
      </div>
      <div className="flex items-end justify-between mb-3">
        <p className="text-slate-300 font-medium">{title}</p>
        <p className="text-2xl font-bold" style={{ color }}>
          {value}
        </p>
      </div>
      <ProgressBar value={value} color={color} />
      <div className="flex justify-between text-[11px] text-slate-500 mt-2 font-mono">
        <span>0</span>
        <span>50</span>
        <span>100</span>
      </div>
    </Card>
  );
}

export function SectionHeader({ title, subtitle, right }) {
  return (
    <div className="flex items-start justify-between mb-5">
      <div>
        <h3 className="text-white font-semibold text-lg">{title}</h3>
        {subtitle && <p className="text-slate-500 text-sm mt-0.5">{subtitle}</p>}
      </div>
      {right}
    </div>
  );
}
