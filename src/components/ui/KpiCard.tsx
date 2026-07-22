import React from "react";
import type { LucideIcon } from "lucide-react";

interface KpiCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  subtitle?: string;
  trend?: { value: string; positive: boolean } | null;
  accent?: boolean;
}

export default function KpiCard({ label, value, icon: Icon, subtitle, trend, accent }: KpiCardProps) {
  if (accent) {
    return (
      <div className="bg-gradient-to-br from-primary to-primary-dark rounded-2xl p-5 text-white relative overflow-hidden group hover:shadow-lg transition-all">
        <div className="absolute -right-6 -bottom-6 w-24 h-24 bg-white/10 rounded-full blur-xl" />
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-semibold text-white/70 uppercase tracking-wider">{label}</span>
            <div className="w-8 h-8 bg-white/15 rounded-lg flex items-center justify-center">
              <Icon className="w-4 h-4 text-white/90" />
            </div>
          </div>
          <p className="font-display text-2xl font-bold text-white leading-none">{value}</p>
          {subtitle && <p className="text-xs text-white/60 mt-2 font-medium">{subtitle}</p>}
          {trend && (
            <p className={`text-xs font-semibold mt-2 ${trend.positive ? "text-emerald-300" : "text-rose-300"}`}>
              {trend.value}
            </p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-5 hover:shadow-md transition-all group">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{label}</span>
        <div className="w-8 h-8 bg-slate-50 rounded-lg flex items-center justify-center group-hover:bg-primary-50 transition-colors">
          <Icon className="w-4 h-4 text-slate-400 group-hover:text-primary transition-colors" />
        </div>
      </div>
      <p className="font-display text-2xl font-bold text-slate-800 leading-none">{value}</p>
      {subtitle && <p className="text-xs text-slate-400 mt-2 font-medium">{subtitle}</p>}
      {trend && (
        <p className={`text-xs font-semibold mt-2 ${trend.positive ? "text-competitive" : "text-overpriced"}`}>
          {trend.value}
        </p>
      )}
    </div>
  );
}
