import React from "react";

interface StatusBadgeProps {
  status: string;
}

const config: Record<string, { bg: string; text: string; dot: string }> = {
  Competitive: { bg: "bg-emerald-50", text: "text-emerald-700", dot: "bg-emerald-500" },
  "Needs Review": { bg: "bg-amber-50", text: "text-amber-700", dot: "bg-amber-500" },
  Overpriced: { bg: "bg-red-50", text: "text-red-700", dot: "bg-red-500" },
  Underpriced: { bg: "bg-blue-50", text: "text-blue-700", dot: "bg-blue-500" },
};

const fallback = { bg: "bg-slate-50", text: "text-slate-700", dot: "bg-slate-500" };

export default function StatusBadge({ status }: StatusBadgeProps) {
  const c = config[status] || fallback;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold ${c.bg} ${c.text}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${c.dot}`} />
      {status}
    </span>
  );
}
