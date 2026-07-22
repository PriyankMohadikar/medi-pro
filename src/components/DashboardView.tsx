/**
 * Executive Dashboard — Page 1
 * Management should understand the market in less than 30 seconds.
 */

import React, { useMemo, useState } from "react";
import { TestItem, PackageItem, StatsData, ActiveScreen, ES_PROVIDER_NAME } from "../types";
import KpiCard from "./ui/KpiCard";
import ChartCard from "./ui/ChartCard";
import FilterBar from "./ui/FilterBar";
import { useFilters } from "../hooks/useFilters";
import {
  IndianRupee,
  TrendingDown,
  TrendingUp,
  CheckCircle,
  AlertTriangle,
  Package,
  MapPin,
  ArrowRight,
  Lightbulb,
  ShieldCheck,
  Target,
  Zap,
  Crown,
  BarChart3,
} from "lucide-react";
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

interface DashboardViewProps {
  tests: TestItem[];
  packages: PackageItem[];
  stats: StatsData | null;
  formatPrice: (val: number | null) => string;
  onNavigateToScreen: (screen: ActiveScreen) => void;
}

export default function DashboardView({ tests, packages, stats, formatPrice, onNavigateToScreen }: DashboardViewProps) {
  const { filters, search, debouncedSearch, updateFilter, updateSearch, resetFilters } = useFilters();

  const uniqueProviders = useMemo(() => {
    const set = new Set(tests.map((t) => t.provider_name).filter(Boolean));
    return Array.from(set).sort();
  }, [tests]);

  // Apply filters
  const filteredTests = useMemo(() => {
    return tests.filter((t) => {
      if (filters.city !== "All" && t.city !== filters.city) return false;
      if (filters.category !== "All" && t.category !== filters.category) return false;
      if (filters.provider !== "All" && t.provider_name !== filters.provider) return false;
      if (debouncedSearch && !t.test_name.toLowerCase().includes(debouncedSearch.toLowerCase())) return false;
      return true;
    });
  }, [tests, filters.city, filters.category, filters.provider, debouncedSearch]);

  // ── KPI Computations ─────────────────────────────────────
  const esTests = useMemo(() => filteredTests.filter((t) => t.provider_name === ES_PROVIDER_NAME && t.price !== null), [filteredTests]);
  const compTests = useMemo(() => filteredTests.filter((t) => t.provider_name !== ES_PROVIDER_NAME && t.price !== null), [filteredTests]);

  const avgEsPrice = useMemo(() => {
    if (esTests.length === 0) return 0;
    return esTests.reduce((s, t) => s + (t.price ?? 0), 0) / esTests.length;
  }, [esTests]);

  const avgMarketPrice = useMemo(() => {
    if (compTests.length === 0) return 0;
    return compTests.reduce((s, t) => s + (t.price ?? 0), 0) / compTests.length;
  }, [compTests]);

  // Competitive vs Overpriced
  const { competitiveCount, overpricedCount } = useMemo(() => {
    let competitive = 0;
    let overpriced = 0;
    const esMap: Record<string, number> = {};
    esTests.forEach((t) => {
      const key = `${t.test_name}|${t.city}`;
      esMap[key] = t.price ?? 0;
    });

    Object.entries(esMap).forEach(([key, esPrice]) => {
      const [testName, city] = key.split("|");
      const comps = filteredTests.filter(
        (t) => t.test_name === testName && t.city === city && t.provider_name !== ES_PROVIDER_NAME && t.price !== null
      );
      if (comps.length === 0) return;
      const mktAvg = comps.reduce((s, t) => s + (t.price ?? 0), 0) / comps.length;
      if (mktAvg === 0) return;
      const diff = ((esPrice - mktAvg) / mktAvg) * 100;
      if (diff <= 5) competitive++;
      else if (diff > 10) overpriced++;
    });
    return { competitiveCount: competitive, overpricedCount: overpriced };
  }, [esTests, filteredTests]);

  const citiesCovered = useMemo(() => new Set(filteredTests.map((t) => t.city)).size, [filteredTests]);

  // ── Chart 1: ES vs Market by City (Grouped Bar) ──────────
  const cityComparisonData = useMemo(() => {
    const cities = [...new Set(filteredTests.map((t) => t.city))].sort();
    return cities.map((city) => {
      const esInCity = filteredTests.filter((t) => t.city === city && t.provider_name === ES_PROVIDER_NAME && t.price !== null);
      const compInCity = filteredTests.filter((t) => t.city === city && t.provider_name !== ES_PROVIDER_NAME && t.price !== null);
      return {
        city,
        "ES Healthcare": esInCity.length > 0 ? Math.round(esInCity.reduce((s, t) => s + (t.price ?? 0), 0) / esInCity.length) : 0,
        "Market Average": compInCity.length > 0 ? Math.round(compInCity.reduce((s, t) => s + (t.price ?? 0), 0) / compInCity.length) : 0,
      };
    });
  }, [filteredTests]);

  // ── Chart 2: Category Price Comparison ────────────────────
  const categoryComparisonData = useMemo(() => {
    const categories = Array.from(new Set(filteredTests.map((t) => t.category).filter(Boolean) as string[])).sort();
    return categories.map((cat) => {
      const esInCat = filteredTests.filter((t) => t.category === cat && t.provider_name === ES_PROVIDER_NAME && t.price !== null);
      const compInCat = filteredTests.filter((t) => t.category === cat && t.provider_name !== ES_PROVIDER_NAME && t.price !== null);
      const esAvg = esInCat.length > 0 ? Math.round(esInCat.reduce((s, t) => s + (t.price ?? 0), 0) / esInCat.length) : 0;
      const mktAvg = compInCat.length > 0 ? Math.round(compInCat.reduce((s, t) => s + (t.price ?? 0), 0) / compInCat.length) : 0;
      return {
        category: cat.length > 18 ? cat.substring(0, 18) + "…" : cat,
        "ES Healthcare": esAvg,
        "Market Average": mktAvg,
        diff: mktAvg > 0 ? Math.round(((esAvg - mktAvg) / mktAvg) * 100) : 0,
      };
    });
  }, [filteredTests]);

  // ── Chart 3: Pricing Position (Donut) ─────────────────────
  const pricingPositionData = useMemo(() => {
    let cheaper = 0, near = 0, higher = 0;
    const esMap: Record<string, number> = {};
    esTests.forEach((t) => { esMap[`${t.test_name}|${t.city}`] = t.price ?? 0; });

    Object.entries(esMap).forEach(([key, esPrice]) => {
      const [testName, city] = key.split("|");
      const comps = filteredTests.filter(
        (t) => t.test_name === testName && t.city === city && t.provider_name !== ES_PROVIDER_NAME && t.price !== null
      );
      if (comps.length === 0) return;
      const mktAvg = comps.reduce((s, t) => s + (t.price ?? 0), 0) / comps.length;
      if (mktAvg === 0) return;
      const diff = ((esPrice - mktAvg) / mktAvg) * 100;
      if (diff < -5) cheaper++;
      else if (diff <= 5) near++;
      else higher++;
    });
    return [
      { name: "Cheaper", value: cheaper, color: "#059669" },
      { name: "Near Market", value: near, color: "#2563eb" },
      { name: "Higher", value: higher, color: "#dc2626" },
    ];
  }, [esTests, filteredTests]);

  // ── Pricing Alerts (tests >15% above market) ──────────────
  const pricingAlerts = useMemo(() => {
    const alerts: { test: string; city: string; diff: number; esPrice: number; mktAvg: number }[] = [];
    const esMap: Record<string, { price: number; city: string; test: string }> = {};
    esTests.forEach((t) => {
      esMap[`${t.test_name}|${t.city}`] = { price: t.price ?? 0, city: t.city, test: t.test_name };
    });

    Object.entries(esMap).forEach(([key, data]) => {
      const [testName, city] = key.split("|");
      const comps = filteredTests.filter(
        (t) => t.test_name === testName && t.city === city && t.provider_name !== ES_PROVIDER_NAME && t.price !== null
      );
      if (comps.length === 0) return;
      const mktAvg = comps.reduce((s, t) => s + (t.price ?? 0), 0) / comps.length;
      if (mktAvg === 0) return;
      const diff = ((data.price - mktAvg) / mktAvg) * 100;
      if (diff > 15) {
        alerts.push({ test: data.test, city: data.city, diff: Math.round(diff), esPrice: data.price, mktAvg: Math.round(mktAvg) });
      }
    });
    return alerts.sort((a, b) => b.diff - a.diff).slice(0, 5);
  }, [esTests, filteredTests]);

  // ── Business Insights ─────────────────────────────────────
  const insights = useMemo(() => {
    // Most competitive city (lowest ES avg vs market)
    const cityDiffs = cityComparisonData
      .filter((c) => c["ES Healthcare"] > 0 && c["Market Average"] > 0)
      .map((c) => ({
        city: c.city,
        diff: ((c["ES Healthcare"] - c["Market Average"]) / c["Market Average"]) * 100,
      }));
    const mostCompetitive = cityDiffs.sort((a, b) => a.diff - b.diff)[0];

    // Most expensive category
    const catDiffs = categoryComparisonData
      .filter((c) => c["ES Healthcare"] > 0 && c["Market Average"] > 0)
      .map((c) => ({ category: c.category, diff: c.diff }));
    const mostExpensive = catDiffs.sort((a, b) => b.diff - a.diff)[0];

    // Largest gap
    const largestGap = pricingAlerts[0];

    // Best value package
    const pkgsWithValue = packages
      .filter((p) => p.package_price !== null && p.tests_included.length > 0)
      .map((p) => ({ name: p.package_name, provider: p.provider_name, price: p.package_price ?? 0, testCount: p.tests_included.length, valueRatio: (p.tests_included.length / (p.package_price ?? 1)) * 1000 }))
      .sort((a, b) => b.valueRatio - a.valueRatio);
    const bestPackage = pkgsWithValue[0];

    // Cheapest competitor
    const providerAvgs = [...new Set(filteredTests.filter((t) => t.provider_name !== ES_PROVIDER_NAME).map((t) => t.provider_name))].map((name) => {
      const pts = filteredTests.filter((t) => t.provider_name === name && t.price !== null);
      return { name, avg: pts.length > 0 ? pts.reduce((s, t) => s + (t.price ?? 0), 0) / pts.length : Infinity };
    });
    const cheapest = providerAvgs.sort((a, b) => a.avg - b.avg)[0];

    return { mostCompetitive, mostExpensive, largestGap, bestPackage, cheapest };
  }, [cityComparisonData, categoryComparisonData, pricingAlerts, packages, filteredTests]);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload) return null;
    return (
      <div className="bg-white border border-slate-200 rounded-xl px-4 py-3 shadow-lg text-xs">
        <p className="font-semibold text-slate-800 mb-2">{label}</p>
        {payload.map((p: any, i: number) => (
          <div key={i} className="flex items-center gap-2 mb-1">
            <span className="w-2 h-2 rounded-full" style={{ backgroundColor: p.color }} />
            <span className="text-slate-500">{p.name}:</span>
            <span className="font-semibold text-slate-800">{formatPrice(p.value)}</span>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <FilterBar
        cities={stats?.cities ?? []}
        categories={stats?.categories ?? []}
        providers={uniqueProviders}
        selectedCity={filters.city}
        selectedCategory={filters.category}
        selectedProvider={filters.provider}
        searchQuery={search}
        onCityChange={(c) => updateFilter("city", c)}
        onCategoryChange={(c) => updateFilter("category", c)}
        onProviderChange={(p) => updateFilter("provider", p)}
        onSearchChange={updateSearch}
        onReset={resetFilters}
        searchPlaceholder="Search test name..."
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <KpiCard label="Avg ES Price" value={formatPrice(avgEsPrice)} icon={IndianRupee} subtitle="ES Healthcare" />
        <KpiCard label="Avg Market Price" value={formatPrice(avgMarketPrice)} icon={TrendingDown} subtitle="Competitors" />
        <KpiCard label="Competitive Tests" value={competitiveCount} icon={CheckCircle} subtitle="≤5% of market" trend={{ value: "Well priced", positive: true }} />
        {/* <KpiCard label="Overpriced Tests" value={overpricedCount} icon={AlertTriangle} subtitle=">10% above market" trend={overpricedCount > 0 ? { value: "Needs attention", positive: false } : null} /> */}
        {/* <KpiCard label="Packages" value={packages.length} icon={Package} subtitle="Available" /> */}
        <KpiCard label="Cities Covered" value={citiesCovered} icon={MapPin} subtitle="Active regions" accent />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Chart 1: ES vs Market by City */}
        <ChartCard
          title="ES Healthcare vs Market Average"
          description="Average test price comparison by city — are we cheaper or expensive?"
          className="lg:col-span-8"
        >
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={cityComparisonData} barCategoryGap="20%">
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="city" tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} tickFormatter={(v) => `₹${v}`} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="ES Healthcare" fill="#2563eb" radius={[4, 4, 0, 0]} maxBarSize={40} />
                <Bar dataKey="Market Average" fill="#94a3b8" radius={[4, 4, 0, 0]} maxBarSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="flex items-center gap-6 mt-3 pt-3 border-t border-slate-100">
            <div className="flex items-center gap-2 text-xs text-slate-500"><span className="w-3 h-3 rounded bg-primary" />ES Healthcare</div>
            <div className="flex items-center gap-2 text-xs text-slate-500"><span className="w-3 h-3 rounded bg-slate-400" />Market Average</div>
          </div>
        </ChartCard>

        {/* Chart 3: Pricing Position Donut */}
        <ChartCard
          title="Pricing Position"
          description="Overall competitive stance"
          className="lg:col-span-4"
        >
          <div className="h-[300px] flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pricingPositionData}
                  innerRadius={65}
                  outerRadius={100}
                  paddingAngle={3}
                  dataKey="value"
                  cx="50%"
                  cy="50%"
                >
                  {pricingPositionData.map((entry, idx) => (
                    <Cell key={idx} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value: number, name: string) => [value + " tests", name]} />
                <Legend
                  verticalAlign="bottom"
                  iconType="circle"
                  iconSize={8}
                  formatter={(value) => <span className="text-xs text-slate-600 ml-1">{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>
      </div>

      {/* Charts Row 2: Category + Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Chart 2: Category Price Comparison */}
        <ChartCard
          title="Category Price Comparison"
          description="ES Healthcare vs market by category — which category has the biggest gap?"
          className="lg:col-span-8"
        >
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryComparisonData} layout="vertical" barCategoryGap="15%">
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} tickFormatter={(v) => `₹${v}`} />
                <YAxis dataKey="category" type="category" tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} width={130} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="ES Healthcare" fill="#2563eb" radius={[0, 4, 4, 0]} maxBarSize={18} />
                <Bar dataKey="Market Average" fill="#94a3b8" radius={[0, 4, 4, 0]} maxBarSize={18} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </ChartCard>

        {/* Pricing Alerts */}
        <div className="lg:col-span-4 bg-white border border-slate-200 rounded-2xl card-shadow flex flex-col">
          <div className="px-6 pt-5 pb-3">
            <h3 className="font-display font-bold text-[15px] text-slate-800 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-overpriced" />
              Pricing Alerts
            </h3>
            <p className="text-xs text-slate-400 mt-1">Tests priced &gt;15% above market</p>
          </div>
          <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-2">
            {pricingAlerts.length === 0 ? (
              <div className="p-6 text-center text-slate-400 text-sm">No overpriced tests found</div>
            ) : (
              pricingAlerts.map((alert, i) => (
                <div key={i} className="p-3 bg-red-50/50 border border-red-100 rounded-xl animate-fadeInUp" style={{ animationDelay: `${i * 80}ms` }}>
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-semibold text-slate-800">{alert.test}</p>
                      <p className="text-[11px] text-slate-500 mt-0.5">{alert.city} · ES {formatPrice(alert.esPrice)} vs Mkt {formatPrice(alert.mktAvg)}</p>
                    </div>
                    <span className="text-xs font-bold text-overpriced bg-red-100 px-2 py-0.5 rounded-full">
                      +{alert.diff}%
                    </span>
                  </div>
                  <p className="text-[10px] text-red-600 font-medium mt-1.5">↓ Recommended: Reduce Price</p>
                </div>
              ))
            )}
          </div>
          <div className="px-4 pb-4">
            <button
              onClick={() => onNavigateToScreen("test-pricing")}
              className="w-full py-2.5 text-sm font-semibold text-primary bg-primary-50 hover:bg-primary-light rounded-xl transition-colors flex items-center justify-center gap-2"
            >
              View All Tests <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Bottom: Business Insights */}
      {/* <div>
        <h3 className="font-display font-bold text-[15px] text-slate-800 mb-4 flex items-center gap-2">
          <Lightbulb className="w-4 h-4 text-primary" />
          Key Business Insights
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="bg-white border border-slate-200 rounded-2xl p-5 card-shadow hover:shadow-md transition-all">
            <div className="w-9 h-9 bg-emerald-50 rounded-lg flex items-center justify-center mb-3">
              <ShieldCheck className="w-5 h-5 text-competitive" />
            </div>
            <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Most Competitive City</p>
            <p className="font-display text-lg font-bold text-slate-800 mt-1">{insights.mostCompetitive?.city ?? "—"}</p>
            {insights.mostCompetitive && (
              <p className="text-xs text-competitive font-medium mt-1">{Math.round(insights.mostCompetitive.diff)}% vs market</p>
            )}
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-5 card-shadow hover:shadow-md transition-all">
            <div className="w-9 h-9 bg-red-50 rounded-lg flex items-center justify-center mb-3">
              <TrendingUp className="w-5 h-5 text-overpriced" />
            </div>
            <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Most Expensive Category</p>
            <p className="font-display text-lg font-bold text-slate-800 mt-1">{insights.mostExpensive?.category ?? "—"}</p>
            {insights.mostExpensive && (
              <p className="text-xs text-overpriced font-medium mt-1">+{insights.mostExpensive.diff}% above market</p>
            )}
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-5 card-shadow hover:shadow-md transition-all">
            <div className="w-9 h-9 bg-amber-50 rounded-lg flex items-center justify-center mb-3">
              <Target className="w-5 h-5 text-review" />
            </div>
            <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Largest Pricing Gap</p>
            <p className="font-display text-lg font-bold text-slate-800 mt-1">{insights.largestGap?.test ?? "—"}</p>
            {insights.largestGap && (
              <p className="text-xs text-review font-medium mt-1">+{insights.largestGap.diff}% in {insights.largestGap.city}</p>
            )}
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-5 card-shadow hover:shadow-md transition-all">
            <div className="w-9 h-9 bg-primary-50 rounded-lg flex items-center justify-center mb-3">
              <Crown className="w-5 h-5 text-primary" />
            </div>
            <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Highest Value Package</p>
            <p className="font-display text-lg font-bold text-slate-800 mt-1 truncate">{insights.bestPackage?.name ?? "—"}</p>
            {insights.bestPackage && (
              <p className="text-xs text-primary font-medium mt-1">{insights.bestPackage.testCount} tests · {formatPrice(insights.bestPackage.price)}</p>
            )}
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-5 card-shadow hover:shadow-md transition-all">
            <div className="w-9 h-9 bg-purple-50 rounded-lg flex items-center justify-center mb-3">
              <Zap className="w-5 h-5 text-purple-600" />
            </div>
            <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Cheapest Competitor</p>
            <p className="font-display text-lg font-bold text-slate-800 mt-1 truncate">{insights.cheapest?.name ?? "—"}</p>
            {insights.cheapest && (
              <p className="text-xs text-purple-600 font-medium mt-1">Avg {formatPrice(insights.cheapest.avg)}</p>
            )}
          </div>
        </div>
      </div> */}
    </div>
  );
}
