import React, { useState, useEffect, useCallback } from "react";
import { StatsData } from "../types";
import { fetchAnalyzedTests, exportAnalyzedTests } from "../api";
import { useFilters } from "../hooks/useFilters";
import { ActionProvider, useAction } from "./ui/ActionContext";
import FilterBar from "./ui/FilterBar";
import StatusBadge from "./ui/StatusBadge";
import ActionButton from "./ui/ActionButton";
import TestDetailsDrawer from "./TestDetailsDrawer";
import CompareProvidersModal from "./CompareProvidersModal";
import PricingSimulatorModal from "./PricingSimulatorModal";
import AiInsightModal from "./AiInsightModal";
import {
  ArrowUpDown,
  Eye,
  GitCompare,
  Sparkles,
  Calculator,
  Download,
  Loader2,
  Activity,
  Target,
} from "lucide-react";

// ── Inner component that uses ActionContext ───────────
function TestPricingInner({
  stats,
  formatPrice,
}: {
  stats: StatsData | null;
  formatPrice: (val: number | null) => string;
}) {
  const { activeAction, selectedTest, openAction, closeAction } = useAction();

  // Shared Filter State Hook
  const {
    filters,
    search,
    debouncedSearch,
    pagination,
    updateFilter,
    updateSearch,
    handleSort,
    resetFilters,
    updatePagination,
  } = useFilters();

  // Data State
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();

    const loadData = async () => {
      try {
        setLoading(true);
        const res = await fetchAnalyzedTests(
          {
            city: filters.city,
            category: filters.category,
            status: filters.status,
            recommendation: filters.recommendation,
            search: debouncedSearch,
            sort_by: pagination.sortField,
            sort_dir: pagination.sortDir,
            page: pagination.page,
            page_size: pagination.pageSize,
          },
          controller.signal
        );

        setData(res);
      } catch (err: any) {
        if (err.name === "AbortError") return;
        console.error("Failed to fetch analyzed tests", err);
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    };

    loadData();

    return () => {
      controller.abort();
    };
  }, [
    filters.city,
    filters.category,
    filters.status,
    filters.recommendation,
    debouncedSearch,
    pagination.sortField,
    pagination.sortDir,
    pagination.page,
    pagination.pageSize,
  ]);

  const exportCSV = async () => {
    try {
      const exportData = await exportAnalyzedTests({
        city: filters.city,
        category: filters.category,
        status: filters.status,
        recommendation: filters.recommendation,
        search: debouncedSearch,
      });

      if (!exportData || !exportData.items) return;
      const headers = [
        "Test Name",
        "Category",
        "City",
        "ES Price",
        "Lowest",
        "Highest",
        "Market Avg",
        "Diff %",
        "Status",
        "Recommendation",
      ];
      const rows = exportData.items.map((t: any) => [
        t.test_name,
        t.category,
        t.city,
        t.es_price,
        t.lowest_price,
        t.highest_price,
        t.market_average,
        t.difference_pct,
        t.status,
        t.recommendation,
      ]);

      const csvContent = [headers, ...rows]
        .map((e) => e.join(","))
        .join("\n");
      const blob = new Blob([csvContent], {
        type: "text/csv;charset=utf-8;",
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", "pricing_analysis.csv");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      console.error("Failed to export", err);
    }
  };

  const SortableHeader = ({
    field,
    children,
  }: {
    field: string;
    children: React.ReactNode;
  }) => (
    <th
      className="px-4 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider cursor-pointer hover:text-slate-800 hover:bg-slate-100 transition-colors select-none sticky top-0 bg-slate-50 z-10 border-b border-slate-200"
      onClick={() => handleSort(field)}
    >
      <div className="flex items-center gap-1.5">
        {children}
        <ArrowUpDown className="w-3.5 h-3.5 text-slate-400" />
      </div>
    </th>
  );

  const getRowClass = (status: string) => {
    switch (status) {
      case "Competitive":
        return "hover:bg-emerald-50/50";
      case "Needs Review":
        return "hover:bg-yellow-50/50";
      case "Overpriced":
        return "hover:bg-red-50/50";
      case "Underpriced":
        return "hover:bg-blue-50/50";
      default:
        return "hover:bg-slate-50";
    }
  };

  const getRecommendationTooltip = (rec: string) => {
    if (rec === "Review Immediately")
      return "Price is highly disconnected from the market.";
    if (rec === "Reduce Price")
      return "ES Healthcare price is much higher than market average.";
    if (rec === "Maintain Current Price")
      return "ES Healthcare price is near the market average.";
    if (rec === "Monitor Competitors")
      return "ES Healthcare price is slightly higher than the market average.";
    if (rec === "Price Leader")
      return "ES Healthcare price is lower than all competitors.";
    if (rec === "Increase Price")
      return "ES Healthcare price is significantly underpriced but not the lowest.";
    if (rec === "Highly Competitive")
      return "Price is extremely optimized for the market.";
    return "Requires management review.";
  };

  // ── Action handlers via context ─────────────────────
  const handleViewDetails = useCallback(
    (test: any) => openAction("details", test),
    [openAction]
  );
  const handleCompare = useCallback(
    (test: any) => openAction("compare", test),
    [openAction]
  );
  const handleSimulator = useCallback(
    (test: any) => openAction("simulator", test),
    [openAction]
  );
  const handleAiInsight = useCallback(
    (test: any) => openAction("ai-insight", test),
    [openAction]
  );

  return (
    <div className="space-y-6">
      {/* Unified Filter Bar */}
      <FilterBar
        cities={stats?.cities ?? []}
        categories={stats?.categories ?? []}
        statuses={["Competitive", "Needs Review", "Overpriced", "Underpriced"]}
        testNames={stats?.test_names ?? []}
        selectedCity={filters.city}
        selectedCategory={filters.category}
        selectedStatus={filters.status}
        searchQuery={search}
        onCityChange={(c) => updateFilter("city", c)}
        onCategoryChange={(c) => updateFilter("category", c)}
        onStatusChange={(s) => updateFilter("status", s)}
        onSearchChange={updateSearch}
        onReset={resetFilters}
        searchPlaceholder="Search test name..."
      >
        <button
          onClick={exportCSV}
          className="px-5 py-2.5 bg-slate-900 text-white rounded-xl text-sm font-semibold hover:bg-slate-800 transition-colors flex items-center gap-2 shadow-sm"
        >
          <Download className="w-4 h-4" /> Export CSV
        </button>
      </FilterBar>

      {/* Top Summary Cards (6 Columns) */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div
          className="p-4 bg-white border border-slate-200 rounded-2xl flex flex-col justify-center items-center text-center shadow-sm"
          title="Total number of tests currently filtered"
        >
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">
            Total Tests
          </p>
          <p className="text-2xl font-black text-slate-800">
            {data?.total_tests || 0}
          </p>
        </div>
        <div
          className="p-4 bg-emerald-50 border border-emerald-100 rounded-2xl flex flex-col justify-center items-center text-center shadow-sm"
          title="Tests within an optimal competitive pricing range (-5% to +5% difference)"
        >
          <p className="text-[10px] font-bold text-emerald-600 uppercase tracking-wider mb-1">
            Competitive
          </p>
          <p className="text-2xl font-black text-emerald-700">
            {data?.competitive_tests || 0}
          </p>
        </div>
        <div
          className="p-4 bg-yellow-50 border border-yellow-100 rounded-2xl flex flex-col justify-center items-center text-center shadow-sm"
          title="Tests slightly above market average (+5% to +15% difference)"
        >
          <p className="text-[10px] font-bold text-yellow-600 uppercase tracking-wider mb-1">
            Needs Review
          </p>
          <p className="text-2xl font-black text-yellow-700">
            {data?.needs_review_tests || 0}
          </p>
        </div>
        <div
          className="p-4 bg-red-50 border border-red-100 rounded-2xl flex flex-col justify-center items-center text-center shadow-sm"
          title="Tests significantly above market average (> +15% difference)"
        >
          <p className="text-[10px] font-bold text-red-600 uppercase tracking-wider mb-1">
            Overpriced
          </p>
          <p className="text-2xl font-black text-red-700">
            {data?.overpriced_tests || 0}
          </p>
        </div>
        <div
          className="p-4 bg-blue-50 border border-blue-100 rounded-2xl flex flex-col justify-center items-center text-center shadow-sm"
          title="Tests significantly below market average (< -10% difference)"
        >
          <p className="text-[10px] font-bold text-blue-600 uppercase tracking-wider mb-1">
            Underpriced
          </p>
          <p className="text-2xl font-black text-blue-700">
            {data?.underpriced_tests || 0}
          </p>
        </div>
        <div
          className="p-4 bg-slate-800 border border-slate-700 rounded-2xl flex flex-col justify-center items-center text-center shadow-sm"
          title="Average price difference percentage across all currently filtered tests"
        >
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">
            Avg Diff %
          </p>
          <p
            className={`text-2xl font-black ${
              data?.average_difference_pct > 0
                ? "text-red-400"
                : "text-emerald-400"
            }`}
          >
            {data?.average_difference_pct > 0 ? "+" : ""}
            {data?.average_difference_pct || 0}%
          </p>
        </div>
      </div>

      {/* Quick Insights Panel */}
      <div className="bg-white border border-slate-200 rounded-2xl p-4 flex items-center gap-6 overflow-x-auto custom-scrollbar whitespace-nowrap shadow-sm">
        <div className="flex items-center gap-2 text-sm font-bold text-slate-800 border-r border-slate-200 pr-6">
          <Activity className="w-5 h-5 text-primary" /> Quick Insights
        </div>

        {data?.top_5_overpriced?.[0] && (
          <div className="flex items-center gap-2">
            <span className="text-[11px] font-bold text-slate-400 uppercase">
              Most Overpriced:
            </span>
            <span className="text-sm font-bold text-red-600">
              {data.top_5_overpriced[0].name} (+{data.top_5_overpriced[0].value}
              %)
            </span>
          </div>
        )}

        {data?.top_5_lowest?.[0] && (
          <div className="flex items-center gap-2 pl-4 border-l border-slate-100">
            <span className="text-[11px] font-bold text-slate-400 uppercase">
              Most Underpriced:
            </span>
            <span className="text-sm font-bold text-blue-600">
              {data.top_5_lowest[0].name} ({data.top_5_lowest[0].value}%)
            </span>
          </div>
        )}

        <div className="flex items-center gap-2 pl-4 border-l border-slate-100">
          <span className="text-[11px] font-bold text-slate-400 uppercase">
            Expensive Cat:
          </span>
          <span className="text-sm font-bold text-slate-700">
            {data?.most_expensive_category}
          </span>
        </div>
      </div>

      {/* Analytics Summary Bar */}
      <div className="bg-slate-800 text-white rounded-xl px-5 py-3 flex items-center justify-between shadow-sm">
        <div className="text-sm font-medium">
          Showing{" "}
          <span className="font-bold text-white">
            {data?.items?.length > 0
              ? (pagination.page - 1) * pagination.pageSize + 1
              : 0}
            –
            {Math.min(
              pagination.page * pagination.pageSize,
              data?.total || 0
            )}
          </span>{" "}
          of{" "}
          <span className="font-bold text-white">{data?.total || 0}</span>{" "}
          Tests
        </div>
        <div className="flex gap-6 text-xs font-medium text-slate-300">
          <div>
            Competitive:{" "}
            <span className="text-emerald-400 font-bold">
              {data?.competitive_tests || 0}
            </span>
          </div>
          <div>
            Review:{" "}
            <span className="text-yellow-400 font-bold">
              {data?.needs_review_tests || 0}
            </span>
          </div>
          <div>
            Overpriced:{" "}
            <span className="text-red-400 font-bold">
              {data?.overpriced_tests || 0}
            </span>
          </div>
        </div>
      </div>

      {/* Main Table */}
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden relative">
        <div className="overflow-x-auto min-h-[450px]">
          {loading && (
            <div className="absolute inset-0 bg-white/60 backdrop-blur-[2px] z-20 flex flex-col items-center justify-center gap-3 pointer-events-none">
              <Loader2 className="w-8 h-8 text-primary animate-spin" />
              <span className="text-sm font-semibold text-slate-600">
                Loading analysis...
              </span>
            </div>
          )}

          <table className="w-full min-w-[1100px] text-left border-collapse whitespace-nowrap">
            <thead className="bg-slate-50">
              <tr>
                <SortableHeader field="test_name">Test Name</SortableHeader>
                <th className="px-4 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider sticky top-0 bg-slate-50 z-10 border-b border-slate-200">
                  Category
                </th>
                <th className="px-4 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider sticky top-0 bg-slate-50 z-10 border-b border-slate-200">
                  City
                </th>
                <SortableHeader field="es_price">ES Price</SortableHeader>
                <SortableHeader field="lowest_price">Lowest</SortableHeader>
                <SortableHeader field="highest_price">Highest</SortableHeader>
                <SortableHeader field="market_average">
                  Market Avg
                </SortableHeader>
                <SortableHeader field="difference_pct">Diff %</SortableHeader>
                <SortableHeader field="status">Status</SortableHeader>

                <th className="px-4 py-4 text-[10px] font-bold text-slate-500 uppercase tracking-wider text-right sticky top-0 bg-slate-50 z-10 border-b border-slate-200">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {!loading && !data?.items?.length ? (
                <tr>
                  <td colSpan={10} className="px-4 py-20 text-center">
                    <div className="flex flex-col items-center gap-3">
                      <Target className="w-12 h-12 text-slate-300" />
                      <p className="text-slate-500 font-medium text-base">
                        No matching tests found.
                      </p>
                      <button
                        onClick={resetFilters}
                        className="text-primary hover:underline text-sm font-semibold"
                      >
                        Clear Filters
                      </button>
                    </div>
                  </td>
                </tr>
              ) : (
                data?.items?.map((test: any, i: number) => (
                  <tr
                    key={`${test.test_name}-${test.city}-${i}`}
                    className={`transition-colors ${getRowClass(
                      test.status
                    )} group`}
                  >
                    <td className="px-4 py-4 font-bold text-slate-800 text-[13px]">
                      {test.test_name}
                    </td>
                    <td className="px-4 py-4">
                      <span className="text-[10px] font-bold bg-white border border-slate-200 text-slate-500 px-2.5 py-1 rounded-md whitespace-nowrap">
                        {test.category}
                      </span>
                    </td>
                    <td className="px-4 py-4 text-slate-500 text-[13px] font-medium">
                      {test.city}
                    </td>
                    <td className="px-4 py-4 font-black text-slate-800">
                      {formatPrice(test.es_price)}
                    </td>
                    <td className="px-4 py-4 text-emerald-600 font-bold">
                      {formatPrice(test.lowest_price)}
                    </td>
                    <td className="px-4 py-4 text-red-600 font-bold">
                      {formatPrice(test.highest_price)}
                    </td>
                    <td className="px-4 py-4 text-slate-600 font-bold">
                      {formatPrice(test.market_average)}
                    </td>
                    <td className="px-4 py-4">
                      <span
                        className={`text-xs font-black px-2 py-1 rounded ${
                          test.difference_pct > 15
                            ? "bg-red-100 text-red-700"
                            : test.difference_pct > 5
                            ? "bg-yellow-100 text-yellow-700"
                            : test.difference_pct < -5
                            ? "bg-emerald-100 text-emerald-700"
                            : "text-slate-600"
                        }`}
                      >
                        {test.difference_pct > 0 ? "+" : ""}
                        {test.difference_pct}%
                      </span>
                    </td>
                    <td className="px-4 py-4 relative">
                      <div
                        title={getRecommendationTooltip(test.recommendation)}
                      >
                        <StatusBadge status={test.status} />
                      </div>
                    </td>


                    {/* ── Actions Cell ────────────────── */}
                    <td className="px-4 py-4 text-right">
                      <div className="flex items-center justify-end gap-1 relative z-[11]">
                        <ActionButton
                          icon={Eye}
                          label="View Details"
                          onClick={() => handleViewDetails(test)}
                          colorClass="hover:text-slate-800"
                          hoverBgClass="hover:bg-slate-200"
                        />
                        <ActionButton
                          icon={GitCompare}
                          label="Compare Providers"
                          onClick={() => handleCompare(test)}
                          colorClass="hover:text-blue-600"
                          hoverBgClass="hover:bg-blue-50"
                        />
                        <ActionButton
                          icon={Calculator}
                          label="Pricing Simulator"
                          onClick={() => handleSimulator(test)}
                          colorClass="hover:text-emerald-600"
                          hoverBgClass="hover:bg-emerald-50"
                        />
                        <ActionButton
                          icon={Sparkles}
                          label="AI Pricing Insight"
                          onClick={() => handleAiInsight(test)}
                          colorClass="hover:text-primary"
                          hoverBgClass="hover:bg-primary/10"
                        />
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="flex items-center justify-between px-6 py-4 bg-slate-50 border-t border-slate-200">
          <div className="flex items-center gap-2">
            <button
              onClick={() =>
                updatePagination("page", Math.max(1, pagination.page - 1))
              }
              disabled={pagination.page === 1 || loading}
              className="px-4 py-2 bg-white border border-slate-200 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-50 hover:text-slate-900 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              Previous
            </button>
            <span className="text-xs font-semibold text-slate-700 px-4 bg-white py-2 rounded-xl border border-slate-200 shadow-sm">
              Page {pagination.page} of {data?.total_pages || 1}
            </span>
            <button
              onClick={() =>
                updatePagination(
                  "page",
                  Math.min(data?.total_pages || 1, pagination.page + 1)
                )
              }
              disabled={
                pagination.page === (data?.total_pages || 1) || loading
              }
              className="px-4 py-2 bg-white border border-slate-200 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-50 hover:text-slate-900 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      {/* ── Modals & Drawers (via ActionContext) ─────── */}
      <TestDetailsDrawer
        isOpen={activeAction === "details"}
        onClose={closeAction}
        test={selectedTest}
        formatPrice={formatPrice}
      />
      <CompareProvidersModal
        isOpen={activeAction === "compare"}
        onClose={closeAction}
        test={selectedTest}
        formatPrice={formatPrice}
      />
      <PricingSimulatorModal
        isOpen={activeAction === "simulator"}
        onClose={closeAction}
        test={selectedTest}
        formatPrice={formatPrice}
      />
      <AiInsightModal
        isOpen={activeAction === "ai-insight"}
        onClose={closeAction}
        test={selectedTest}
        formatPrice={formatPrice}
      />
    </div>
  );
}

// ── Exported component wraps with ActionProvider ──────
interface TestPricingViewProps {
  tests: any[];
  stats: StatsData | null;
  formatPrice: (val: number | null) => string;
}

export default function TestPricingView({
  stats,
  formatPrice,
}: TestPricingViewProps) {
  return (
    <ActionProvider>
      <TestPricingInner stats={stats} formatPrice={formatPrice} />
    </ActionProvider>
  );
}
