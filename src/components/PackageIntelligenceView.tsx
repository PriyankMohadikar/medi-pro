/**
 * Package Intelligence — Page 3
 * Analyze health packages: value, pricing, and competitive positioning.
 */

import React, { useMemo, useState } from "react";
import { TestItem, PackageItem, StatsData, ES_PROVIDER_NAME } from "../types";
import KpiCard from "./ui/KpiCard";
import ChartCard from "./ui/ChartCard";
import {
  Package,
  TrendingDown,
  Crown,
  IndianRupee,
  Search,
  ArrowUpDown,
} from "lucide-react";
import PackageDetailsDrawer from "./PackageDetailsDrawer";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";

interface PackageIntelligenceViewProps {
  tests: TestItem[];
  packages: PackageItem[];
  stats: StatsData | null;
  formatPrice: (val: number | null) => string;
}

interface AnalyzedPackage {
  package_name: string;
  provider_name: string;
  city: string;
  package_price: number;
  test_count: number;
  individual_cost: number;
  savings: number;
  savings_pct: number;
  tests_included: string[];
}

export default function PackageIntelligenceView({ tests, packages, stats, formatPrice }: PackageIntelligenceViewProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [sortField, setSortField] = useState<string>("savings_pct");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 12;

  const [activePackage, setActivePackage] = useState<AnalyzedPackage | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const handleViewPackage = (pkg: AnalyzedPackage) => {
    setActivePackage(pkg);
    setIsDrawerOpen(true);
  };

  // ── Analyze packages ──────────────────────────────────────
  const analyzedPackages = useMemo(() => {
    return packages
      .filter((p) => p.package_price !== null && p.tests_included.length > 0)
      .map((pkg) => {
        // Sum up individual test costs using cheapest available price for each test in the same city
        let individualCost = 0;
        pkg.tests_included.forEach((testName) => {
          const testPrices = tests.filter(
            (t) => t.test_name.toLowerCase() === testName.toLowerCase() && t.city === pkg.city && t.price !== null
          );
          if (testPrices.length > 0) {
            // Use the provider's own price if available, otherwise market average
            const ownPrice = testPrices.find((t) => t.provider_name === pkg.provider_name);
            individualCost += ownPrice?.price ?? (testPrices.reduce((s, t) => s + (t.price ?? 0), 0) / testPrices.length);
          }
        });

        const savings = individualCost - (pkg.package_price ?? 0);
        const savingsPct = individualCost > 0 ? (savings / individualCost) * 100 : 0;

        return {
          package_name: pkg.package_name,
          provider_name: pkg.provider_name,
          city: pkg.city,
          package_price: pkg.package_price ?? 0,
          test_count: pkg.tests_included.length,
          individual_cost: Math.round(individualCost),
          savings: Math.round(savings),
          savings_pct: Math.round(savingsPct * 10) / 10,
          tests_included: pkg.tests_included,
        } as AnalyzedPackage;
      });
  }, [packages, tests]);

  // ── Filtered and sorted ───────────────────────────────────
  const filtered = useMemo(() => {
    if (!searchQuery) return analyzedPackages;
    return analyzedPackages.filter((p) =>
      p.package_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.provider_name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [analyzedPackages, searchQuery]);

  const sorted = useMemo(() => {
    return [...filtered].sort((a, b) => {
      const aVal = (a as any)[sortField] ?? 0;
      const bVal = (b as any)[sortField] ?? 0;
      if (typeof aVal === "string") return sortDir === "asc" ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      return sortDir === "asc" ? aVal - bVal : bVal - aVal;
    });
  }, [filtered, sortField, sortDir]);

  const totalPages = Math.ceil(sorted.length / itemsPerPage);
  const paginated = sorted.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

  // ── KPIs ──────────────────────────────────────────────────
  const avgPackagePrice = analyzedPackages.length > 0 ? analyzedPackages.reduce((s, p) => s + p.package_price, 0) / analyzedPackages.length : 0;
  const avgSaving = analyzedPackages.length > 0 ? analyzedPackages.reduce((s, p) => s + p.savings, 0) / analyzedPackages.length : 0;
  const bestValue = [...analyzedPackages].sort((a, b) => b.savings_pct - a.savings_pct)[0];
  const highestPriced = [...analyzedPackages].sort((a, b) => b.package_price - a.package_price)[0];

  // ── Charts ────────────────────────────────────────────────
  const priceComparisonData = useMemo(() => {
    return [...analyzedPackages].sort((a, b) => b.package_price - a.package_price).slice(0, 10).map((p) => ({
      name: p.package_name.length > 20 ? p.package_name.substring(0, 20) + "…" : p.package_name,
      price: p.package_price,
    }));
  }, [analyzedPackages]);

  const valueRankingData = useMemo(() => {
    return [...analyzedPackages].filter((p) => p.savings_pct > 0).sort((a, b) => b.savings_pct - a.savings_pct).slice(0, 10).map((p) => ({
      name: p.package_name.length > 20 ? p.package_name.substring(0, 20) + "…" : p.package_name,
      saving: p.savings_pct,
    }));
  }, [analyzedPackages]);

  const testsPerPackageData = useMemo(() => {
    const buckets: Record<string, number> = {};
    analyzedPackages.forEach((p) => {
      const key = `${p.test_count} tests`;
      buckets[key] = (buckets[key] || 0) + 1;
    });
    return Object.entries(buckets).map(([k, v]) => ({ name: k, count: v })).sort((a, b) => parseInt(a.name) - parseInt(b.name));
  }, [analyzedPackages]);

  const providerDistribution = useMemo(() => {
    const map: Record<string, number> = {};
    analyzedPackages.forEach((p) => { map[p.provider_name] = (map[p.provider_name] || 0) + 1; });
    const colors = ["#2563eb", "#059669", "#d97706", "#dc2626", "#7c3aed", "#0891b2", "#c026d3", "#ea580c"];
    return Object.entries(map).map(([name, count], i) => ({ name, value: count, color: colors[i % colors.length] }));
  }, [analyzedPackages]);

  const handleSort = (field: string) => {
    if (sortField === field) setSortDir(sortDir === "asc" ? "desc" : "asc");
    else { setSortField(field); setSortDir("desc"); }
    setCurrentPage(1);
  };

  const SortableHeader = ({ field, children }: { field: string; children: React.ReactNode }) => (
    <th className="px-4 py-3.5 text-[10px] font-semibold text-slate-400 uppercase tracking-wider cursor-pointer hover:text-slate-600 select-none" onClick={() => handleSort(field)}>
      <div className="flex items-center gap-1">{children}<ArrowUpDown className="w-3 h-3" /></div>
    </th>
  );

  return (
    <div className="space-y-6">
      {/* Search */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search packages or providers..."
            value={searchQuery}
            onChange={(e) => { setSearchQuery(e.target.value); setCurrentPage(1); }}
            className="w-full bg-white border border-slate-200 text-slate-700 text-sm py-2.5 pl-9 pr-4 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all placeholder:text-slate-400"
          />
        </div>
        <span className="text-xs text-slate-400 font-medium">{filtered.length} packages</span>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard label="Avg Package Price" value={formatPrice(avgPackagePrice)} icon={IndianRupee} subtitle="Across all packages" />
        <KpiCard label="Avg Saving" value={formatPrice(avgSaving)} icon={TrendingDown} subtitle="Package vs individual" trend={{ value: "Bundle discount", positive: true }} />
        <KpiCard label="Best Value Package" value={bestValue?.package_name?.substring(0, 20) ?? "—"} icon={Crown} subtitle={bestValue ? `${bestValue.savings_pct}% savings` : ""} />
        <KpiCard label="Highest Priced" value={highestPriced ? formatPrice(highestPriced.package_price) : "—"} icon={Package} subtitle={highestPriced?.package_name?.substring(0, 20) ?? ""} accent />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Package Price Comparison" description="Top 10 most expensive packages">
          <div className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={priceComparisonData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickLine={false} tickFormatter={(v) => `₹${v}`} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickLine={false} width={130} />
                <Tooltip formatter={(v: number) => [formatPrice(v), "Price"]} />
                <Bar dataKey="price" fill="#2563eb" radius={[0, 4, 4, 0]} maxBarSize={18} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard title="Package Value Ranking" description="Which package gives maximum value?">
          <div className="h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={valueRankingData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickLine={false} tickFormatter={(v) => `${v}%`} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickLine={false} width={130} />
                <Tooltip formatter={(v: number) => [`${v}%`, "Savings"]} />
                <Bar dataKey="saving" fill="#059669" radius={[0, 4, 4, 0]} maxBarSize={18} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard title="Tests Per Package" description="Package size distribution">
          <div className="h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={testsPerPackageData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 10, fill: "#64748b" }} axisLine={false} tickLine={false} />
                <Tooltip formatter={(v: number) => [v, "Packages"]} />
                <Bar dataKey="count" fill="#7c3aed" radius={[4, 4, 0, 0]} maxBarSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        <ChartCard title="Package Distribution" description="Packages by provider">
          <div className="h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={providerDistribution} innerRadius={55} outerRadius={85} paddingAngle={3} dataKey="value" cx="50%" cy="50%">
                  {providerDistribution.map((entry, idx) => (<Cell key={idx} fill={entry.color} />))}
                </Pie>
                <Tooltip formatter={(v: number, name: string) => [v + " packages", name]} />
                <Legend verticalAlign="bottom" iconType="circle" iconSize={8} formatter={(v) => <span className="text-xs text-slate-600 ml-1">{v}</span>} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>

      {/* Table */}
      <div className="bg-white border border-slate-200 rounded-2xl card-shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <SortableHeader field="package_name">Package Name</SortableHeader>
                <th className="px-4 py-3.5 text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Provider</th>
                <SortableHeader field="package_price">Price</SortableHeader>
                <SortableHeader field="test_count"># Tests</SortableHeader>
                <SortableHeader field="individual_cost">Individual Cost</SortableHeader>
                <SortableHeader field="savings">Savings</SortableHeader>
                <SortableHeader field="savings_pct">Savings %</SortableHeader>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {paginated.length === 0 ? (
                <tr><td colSpan={7} className="px-4 py-12 text-center text-slate-400">No packages found.</td></tr>
              ) : (
                paginated.map((pkg, i) => (
                  <tr key={`${pkg.package_name}-${pkg.provider_name}-${i}`} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-4 py-3.5 font-semibold text-slate-800 text-[13px]">{pkg.package_name}</td>
                    <td className="px-4 py-3.5 text-slate-500 text-[13px]">{pkg.provider_name}</td>
                    <td className="px-4 py-3.5 font-semibold text-slate-800">{formatPrice(pkg.package_price)}</td>
                    <td className="px-4 py-3.5 text-center">
                      <button 
                        onClick={() => handleViewPackage(pkg)} 
                        className="bg-primary-50 text-primary px-2.5 py-0.5 rounded-full text-xs font-semibold hover:bg-primary hover:text-white transition-colors cursor-pointer"
                        title="View Package Details"
                      >
                        {pkg.test_count} Tests
                      </button>
                    </td>
                    <td className="px-4 py-3.5 text-slate-500">{formatPrice(pkg.individual_cost)}</td>
                    <td className="px-4 py-3.5 font-medium text-competitive">{pkg.savings > 0 ? formatPrice(pkg.savings) : "—"}</td>
                    <td className="px-4 py-3.5">
                      <span className={`text-xs font-bold ${pkg.savings_pct > 0 ? "text-competitive" : "text-slate-400"}`}>
                        {pkg.savings_pct > 0 ? `${pkg.savings_pct}%` : "—"}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        <div className="px-6 py-4 bg-slate-50 flex justify-between items-center border-t border-slate-200">
          <span className="text-slate-400 text-xs font-medium">{sorted.length} total packages</span>
          <div className="flex gap-2">
            <button onClick={() => setCurrentPage((p) => Math.max(p - 1, 1))} disabled={currentPage === 1} className="px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-200 bg-white text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed">Previous</button>
            <span className="px-3 py-1.5 text-xs font-semibold text-slate-600">{currentPage} / {totalPages || 1}</span>
            <button onClick={() => setCurrentPage((p) => Math.min(p + 1, totalPages))} disabled={currentPage >= totalPages} className="px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-200 bg-white text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed">Next</button>
          </div>
        </div>
      </div>

      <PackageDetailsDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        pkg={activePackage}
        tests={tests}
        formatPrice={formatPrice}
      />
    </div>
  );
}
