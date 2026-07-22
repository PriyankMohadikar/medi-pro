import React, { useState, useCallback } from "react";
import type { LucideIcon } from "lucide-react";
import { Loader2 } from "lucide-react";

interface ActionButtonProps {
  icon: LucideIcon;
  label: string;
  onClick: () => void;
  colorClass?: string;       // hover text color, e.g. "hover:text-blue-600"
  hoverBgClass?: string;     // hover bg, e.g. "hover:bg-blue-50"
  disabled?: boolean;
  loading?: boolean;
}

export default function ActionButton({
  icon: Icon,
  label,
  onClick,
  colorClass = "hover:text-slate-800",
  hoverBgClass = "hover:bg-slate-100",
  disabled = false,
  loading = false,
}: ActionButtonProps) {
  const [showTooltip, setShowTooltip] = useState(false);

  const handleClick = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      e.preventDefault();
      if (!disabled && !loading) {
        onClick();
      }
    },
    [onClick, disabled, loading]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" || e.key === " ") {
        e.stopPropagation();
        e.preventDefault();
        if (!disabled && !loading) {
          onClick();
        }
      }
    },
    [onClick, disabled, loading]
  );

  return (
    <div className="relative inline-flex">
      <button
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        onFocus={() => setShowTooltip(true)}
        onBlur={() => setShowTooltip(false)}
        disabled={disabled || loading}
        className={`
          p-1.5 rounded-lg transition-all duration-150
          text-slate-400 ${colorClass} ${hoverBgClass}
          disabled:opacity-40 disabled:cursor-not-allowed
          focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 focus-visible:ring-offset-1
          relative z-[1]
        `}
        tabIndex={0}
        role="button"
        aria-label={label}
        type="button"
      >
        {loading ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Icon className="w-4 h-4" />
        )}
      </button>

      {/* Tooltip */}
      {showTooltip && !disabled && (
        <div
          className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2.5 py-1 bg-slate-800 text-white text-[10px] font-semibold rounded-md whitespace-nowrap z-[300] pointer-events-none shadow-lg"
          role="tooltip"
        >
          {label}
          <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-px">
            <div className="w-0 h-0 border-x-[4px] border-x-transparent border-t-[4px] border-t-slate-800" />
          </div>
        </div>
      )}
    </div>
  );
}
