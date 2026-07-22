import React from "react";

interface ChartCardProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
  action?: React.ReactNode;
}

export default function ChartCard({ title, description, children, className = "", action }: ChartCardProps) {
  return (
    <div className={`bg-white border border-slate-200 rounded-2xl card-shadow flex flex-col ${className}`}>
      <div className="px-6 pt-5 pb-4 flex items-start justify-between">
        <div>
          <h3 className="font-display font-bold text-[15px] text-slate-800">{title}</h3>
          {description && <p className="text-xs text-slate-400 mt-1">{description}</p>}
        </div>
        {action && <div>{action}</div>}
      </div>
      <div className="px-6 pb-5 flex-1 min-h-0">
        {children}
      </div>
    </div>
  );
}
