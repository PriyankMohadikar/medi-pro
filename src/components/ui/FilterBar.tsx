import React from "react";
import { Search, RotateCcw } from "lucide-react";

interface FilterBarProps {
  cities: string[];
  categories: string[];
  providers?: string[];
  statuses?: string[];
  testNames?: string[];
  selectedCity: string;
  selectedCategory: string;
  selectedProvider?: string;
  selectedStatus?: string;
  searchQuery: string;
  onCityChange: (city: string) => void;
  onCategoryChange: (category: string) => void;
  onProviderChange?: (provider: string) => void;
  onStatusChange?: (status: string) => void;
  onSearchChange: (query: string) => void;
  onReset: () => void;
  searchPlaceholder?: string;
  children?: React.ReactNode;
}

export default function FilterBar({
  cities,
  categories,
  providers,
  statuses,
  testNames,
  selectedCity,
  selectedCategory,
  selectedProvider,
  selectedStatus,
  searchQuery,
  onCityChange,
  onCategoryChange,
  onProviderChange,
  onStatusChange,
  onSearchChange,
  onReset,
  searchPlaceholder = "Search...",
  children
}: FilterBarProps) {
  const selectClasses =
    "w-full bg-white border border-slate-200 text-slate-700 text-sm py-2.5 px-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary cursor-pointer transition-all appearance-none";

  return (
    <div className="flex flex-wrap items-end gap-3 bg-white p-4 border border-slate-200 rounded-2xl card-shadow">
      <div className="flex-1 min-w-[160px]">
        <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
          City
        </label>
        <select value={selectedCity} onChange={(e) => onCityChange(e.target.value)} className={selectClasses}>
          <option value="All">All Cities</option>
          {cities.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      <div className="flex-1 min-w-[160px]">
        <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
          Category
        </label>
        <select value={selectedCategory} onChange={(e) => onCategoryChange(e.target.value)} className={selectClasses}>
          <option value="All">All Categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      {providers && onProviderChange && (
        <div className="flex-1 min-w-[160px]">
          <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
            Provider
          </label>
          <select value={selectedProvider} onChange={(e) => onProviderChange(e.target.value)} className={selectClasses}>
            <option value="All">All Providers</option>
            {providers.map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </div>
      )}

      {statuses && onStatusChange && (
        <div className="flex-1 min-w-[160px]">
          <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
            Status
          </label>
          <select value={selectedStatus} onChange={(e) => onStatusChange(e.target.value)} className={selectClasses}>
            <option value="All">All Statuses</option>
            {statuses.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
      )}

      {testNames ? (
        <div className="flex-1 min-w-[200px]">
          <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
            Test Name
          </label>
          <select value={searchQuery} onChange={(e) => onSearchChange(e.target.value)} className={selectClasses}>
            <option value="">All Tests</option>
            {testNames.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
      ) : (
        <div className="flex-1 min-w-[200px]">
          <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
            Search
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder={searchPlaceholder}
              value={searchQuery}
              onChange={(e) => onSearchChange(e.target.value)}
              className="w-full bg-white border border-slate-200 text-slate-700 text-sm py-2.5 pl-9 pr-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all placeholder:text-slate-400"
            />
          </div>
        </div>
      )}

      <button
        onClick={onReset}
        className="p-2.5 border border-slate-200 hover:bg-slate-50 text-slate-400 hover:text-slate-600 rounded-xl transition-colors bg-white flex-shrink-0"
        title="Reset Filters"
      >
        <RotateCcw className="w-4 h-4" />
      </button>

      {children && (
        <div className="flex-shrink-0">
          {children}
        </div>
      )}
    </div>
  );
}
