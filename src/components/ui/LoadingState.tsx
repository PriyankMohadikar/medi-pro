import React from "react";
import { Loader2 } from "lucide-react";

interface LoadingStateProps {
  message?: string;
  rows?: number; // number of skeleton rows
}

export default function LoadingState({
  message = "Loading data...",
  rows = 4,
}: LoadingStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-6">
      <Loader2 className="w-8 h-8 text-primary animate-spin mb-4" />
      <p className="text-sm font-semibold text-slate-500 mb-6">{message}</p>
      <div className="w-full space-y-3 max-w-md">
        {Array.from({ length: rows }).map((_, i) => (
          <div
            key={i}
            className="h-10 bg-slate-100 rounded-xl w-full animate-pulse"
            style={{ animationDelay: `${i * 100}ms` }}
          />
        ))}
      </div>
    </div>
  );
}
