/**
 * Competitor Intelligence — Page 4
 * Understand competitors: who's cheapest, who's expensive, and where.
 */

import React, { useMemo, useState } from "react";
import { TestItem, PackageItem, StatsData, ES_PROVIDER_NAME } from "../types";
import KpiCard from "./ui/KpiCard";
import ChartCard from "./ui/ChartCard";
import {
  Users,
  TrendingDown,
  TrendingUp,
  Target,
  Search,
  ArrowUpDown,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface CompetitorIntelligenceViewProps {
  tests: TestItem[];
  packages: PackageItem[];
  stats: StatsData | null;
  formatPrice: (val: number | null) => string;
}

interface CompetitorProfile {
  provider_name: string;
  avg_price: number;
  cities: string[];
  test_count: number;
  diff_vs_es: number;
  position: string;
}

export default function CompetitorIntelligenceView({ tests, packages, stats, formatPrice }: CompetitorIntelligenceViewProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [sortField, setSortField] = useState<string>("avg_price");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  // ── ES average price ──────────────────────────────────────
  const esAvgPrice = useMemo(() => {
    const esTests = tests.filter((t) => t.provider_name === ES_PROVIDER_NAME && t.price !== null);
    if (esTests.length === 0) return 0;
    return esTests.reduce((s, t) => s + (t.price ?? 0), 0) / esTests.length;
  }, [tests]);

  // ── Build competitor profiles ─────────────────────────────
  const competitors = useMemo(() => {
    const providerMap: Record<string, { prices: number[]; cities: Set<string> }> = {};

    tests.forEach((t) => {
      if (t.provider_name === ES_PROVIDER_NAME || t.price === null) return;
      if (!providerMap[t.provider_name]) providerMap[t.provider_name] = { prices: [], cities: new Set() };
      providerMap[t.provider_name].prices.push(t.price);
      if (t.city) providerMap[t.provider_name].cities.add(t.city);
    });

    return Object.entries(providerMap).map(([name, data]) => {
      const avg = data.prices.reduce((s, p) => s + p, 0) / data.prices.length;
      const diff = esAvgPrice > 0 ? ((avg - esAvgPrice) / esAvgPrice) * 100 : 0;
      let position = "Similar";
      if (diff < -10) position = "Cheaper";
      else if (diff > 10) position = "More Expensive";

      return {
        provider_name: name,
        avg_price: Math.round(avg),
        cities: Array.from(data.cities),
        test_count: data.prices.length,
        diff_vs_es: Math.round(diff * 10) / 10,
        position,
      } as CompetitorProfile;
    });
  }, [tests, esAvgPrice]);

  // ── Filtered & sorted ─────────────────────────────────────
  const filtered = useMemo(() => {
    if (!searchQuery) return competitors;
    return competitors.filter((c) => c.provider_name.toLowerCase().includes(searchQuery.toLowerCase()));
  }, [competitors, searchQuery]);

  const sorted = useMemo(() => {
    return [...filtered].sort((a, b) => {
      const aVal = (a as any)[sortField];
      const bVal = (b as any)[sortField];
      if (typeof aVal === "string") return sortDir === "asc" ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      return sortDir === "asc" ? aVal - bVal : bVal - aVal;
    });
  }, [filtered, sortField, sortDir]);

  // ── KPIs ──────────────────────────────────────────────────
  const cheapest = [...filtered].sort((a, b) => a.avg_price - b.avg_price)[0];
  const mostExpensive = [...filtered].sort((a, b) => b.avg_price - a.avg_price)[0];
  const avgCompPrice = filtered.length > 0 ? Math.round(filtered.reduce((s, c) => s + c.avg_price, 0) / filtered.length) : 0;

  // ── Charts ────────────────────────────────────────────────
  const rankingData = useMemo(() => {
    return [...filtered].sort((a, b) => a.avg_price - b.avg_price).map((c) => ({
      name: c.provider_name.length > 18 ? c.provider_name.substring(0, 18) + "…" : c.provider_name,
      price: c.avg_price,
      fill: c.provider_name === ES_PROVIDER_NAME ? "#2563eb" : "#94a3b8",
    }));
  }, [competitors]);

  const cityComparisonData = useMemo(() => {
    const cities = [...new Set(tests.map((t) => t.city).filter(Boolean))].sort();
    return cities.map((city) => {
      const entry: Record<string, any> = { city };
      const esInCity = tests.filter((t) => t.city === city && t.provider_name === ES_PROVIDER_NAME && t.price !== null);
      entry["ES Healthcare"] = esInCity.length > 0 ? Math.round(esInCity.reduce((s, t) => s + (t.price ?? 0), 0) / esInCity.length) : 0;

      // Top 3 competitors by test count in this city
      const compProviders: Record<string, number[]> = {};
      tests.filter((t) => t.city === city && t.provider_name !== ES_PROVIDER_NAME && t.price !== null)
        .forEach((t) => {
          if (!compProviders[t.provider_name]) compProviders[t.provider_name] = [];
          compProviders[t.provider_name].push(t.price!);
        });
      const topComps = Object.entries(compProviders)
        .sort((a, b) => b[1].length - a[1].length)
        .slice(0, 3);
      topComps.forEach(([name, prices]) => {
        entry[name] = Math.round(prices.reduce((s, p) => s + p, 0) / prices.length);
      });
      return entry;
    });
  }, [tests]);

  // Heatmap data: provider x city → avg price
  const heatmapData = useMemo(() => {
    const allProviders = [...new Set(tests.map((t) => t.provider_name))].sort();
    const allCities = [...new Set(tests.map((t) => t.city).filter(Boolean))].sort();
    const rows: { provider: string; [key: string]: any }[] = [];

    allProviders.forEach((prov) => {
      const row: { provider: string; [key: string]: any } = { provider: prov.length > 16 ? prov.substring(0, 16) + "…" : prov };
      allCities.forEach((city) => {
        const pts = tests.filter((t) => t.provider_name === prov && t.city === city && t.price !== null);
        row[city] = pts.length > 0 ? Math.round(pts.reduce((s, t) => s + (t.price ?? 0), 0) / pts.length) : null;
      });
      rows.push(row);
    });
    return { rows, cities: allCities };
  }, [tests]);

  const handleSort = (field: string) => {
    if (sortField === field) setSortDir(sortDir === "asc" ? "desc" : "asc");
    else { setSortField(field); setSortDir("asc"); }
  };

  const SortableHeader = ({ field, children }: { field: string; children: React.ReactNode }) => (
    <th className="px-4 py-3.5 text-[10px] font-semibold text-slate-400 uppercase tracking-wider cursor-pointer hover:text-slate-600 select-none" onClick={() => handleSort(field)}>
      <div className="flex items-center gap-1">{children}<ArrowUpDown className="w-3 h-3" /></div>
    </th>
  );

  const barColors = ["#2563eb", "#059669", "#d97706", "#dc2626", "#7c3aed"];

  return (
    <div className="space-y-6">
      {/* Search */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search competitor..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-white border border-slate-200 text-slate-700 text-sm py-2.5 pl-9 pr-4 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all placeholder:text-slate-400"
          />
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard label="Cheapest Competitor" value={cheapest?.provider_name?.substring(0, 18) ?? "—"} icon={TrendingDown} subtitle={cheapest ? `Avg ${formatPrice(cheapest.avg_price)}` : ""} trend={cheapest ? { value: `${cheapest.diff_vs_es}% vs ES`, positive: cheapest.diff_vs_es < 0 } : null} />
        <KpiCard label="Most Expensive" value={mostExpensive?.provider_name?.substring(0, 18) ?? "—"} icon={TrendingUp} subtitle={mostExpensive ? `Avg ${formatPrice(mostExpensive.avg_price)}` : ""} />
        <KpiCard label="Avg Competitor Price" value={formatPrice(avgCompPrice)} icon={Target} subtitle="Across all competitors" />
        <KpiCard label="Competitors Tracked" value={competitors.length} icon={Users} subtitle="Active providers" accent />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Competitor Ranking" description="Which competitor is cheapest?">
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={rankingData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickLine={false} tickFormatter={(v) => `₹${v}`} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickLine={false} width={120} />
                <Tooltip formatter={(v: number) => [formatPrice(v), "Avg Price"]} />
                <Bar dataKey="price" radius={[0, 4, 4, 0]} maxBarSize={18}>
                  {rankingData.map((entry, idx) => (
                    <Cell key={idx} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard title="Average Pricing by Provider" description="How do competitor prices compare?">
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={rankingData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 9, fill: "#64748b" }} axisLine={false} tickLine={false} angle={-30} textAnchor="end" height={60} />
                <YAxis tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickLine={false} tickFormatter={(v) => `₹${v}`} />
                <Tooltip formatter={(v: number) => [formatPrice(v), "Avg Price"]} />
                <Bar dataKey="price" fill="#2563eb" radius={[4, 4, 0, 0]} maxBarSize={32} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>

      {/* Competitor Heatmap */}
      <div className="bg-white border border-slate-200 rounded-2xl card-shadow overflow-hidden">
        <div className="px-6 pt-5 pb-3">
          <h3 className="font-display font-bold text-[15px] text-slate-800">Competitor Heatmap</h3>
          <p className="text-xs text-slate-400 mt-1">Average price by provider and city — darker = more expensive</p>
        </div>
        <div className="overflow-x-auto px-6 pb-5">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr>
                <th className="px-3 py-2.5 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Provider</th>
                {heatmapData.cities.map((city) => (
                  <th key={city} className="px-3 py-2.5 text-[10px] font-semibold text-slate-400 uppercase tracking-wider text-center">{city}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {heatmapData.rows.map((row, i) => (
                <tr key={i} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-3 py-2.5 text-xs font-semibold text-slate-700">{row.provider}</td>
                  {heatmapData.cities.map((city) => {
                    const val = row[city];
                    if (val === null) return <td key={city} className="px-3 py-2.5 text-center text-slate-300 text-xs">—</td>;
                    // Color intensity based on price
                    const maxPrice = 2000;
                    const intensity = Math.min(val / maxPrice, 1);
                    const bg = `rgba(37, 99, 235, ${0.08 + intensity * 0.35})`;
                    return (
                      <td key={city} className="px-3 py-2.5 text-center">
                        <span className="text-[11px] font-semibold text-slate-700 px-2 py-1 rounded-lg inline-block" style={{ backgroundColor: bg }}>
                          ₹{val}
                        </span>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white border border-slate-200 rounded-2xl card-shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <SortableHeader field="provider_name">Provider</SortableHeader>
                <SortableHeader field="avg_price">Avg Price</SortableHeader>
                <th className="px-4 py-3.5 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Cities</th>
                <SortableHeader field="test_count"># Tests</SortableHeader>
                <SortableHeader field="diff_vs_es">Diff vs ES</SortableHeader>
                <th className="px-4 py-3.5 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Position</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {sorted.map((comp, i) => (
                <tr key={comp.provider_name} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-4 py-3.5 font-semibold text-slate-800">{comp.provider_name}</td>
                  <td className="px-4 py-3.5 font-semibold text-slate-700">{formatPrice(comp.avg_price)}</td>
                  <td className="px-4 py-3.5">
                    <div className="flex flex-wrap gap-1">
                      {comp.cities.map((c) => (
                        <span key={c} className="text-[10px] bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full font-medium">{c}</span>
                      ))}
                    </div>
                  </td>
                  <td className="px-4 py-3.5 text-center"><span className="bg-primary-50 text-primary px-2 py-0.5 rounded-full text-xs font-semibold">{comp.test_count}</span></td>
                  <td className="px-4 py-3.5">
                    <span className={`text-xs font-bold ${comp.diff_vs_es < -5 ? "text-competitive" : comp.diff_vs_es > 5 ? "text-overpriced" : "text-slate-500"}`}>
                      {comp.diff_vs_es > 0 ? "+" : ""}{comp.diff_vs_es}%
                    </span>
                  </td>
                  <td className="px-4 py-3.5">
                    <span className={`text-[11px] font-semibold px-2.5 py-1 rounded-full ${
                      comp.position === "Cheaper" ? "bg-emerald-50 text-emerald-700" :
                      comp.position === "More Expensive" ? "bg-red-50 text-red-700" :
                      "bg-slate-100 text-slate-600"
                    }`}>{comp.position}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
