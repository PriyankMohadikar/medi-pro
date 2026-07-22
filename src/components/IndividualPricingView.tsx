/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useMemo } from "react";
import { TestItem, StatsData } from "../types";
import {
  TrendingUp,
  CheckCircle,
  AlertTriangle,
  BarChart2,
  RotateCcw,
  Search,
} from "lucide-react";

interface IndividualPricingViewProps {
  tests: TestItem[];
  stats: StatsData | null;
  formatPrice: (val: number | null) => string;
}

export default function IndividualPricingView({
  tests,
  stats,
  formatPrice,
}: IndividualPricingViewProps) {
  // Filter states
  const [selectedCity, setSelectedCity] = useState("All Regions");
  const [selectedProvider, setSelectedProvider] = useState("All Providers");
  const [selectedCategory, setSelectedCategory] = useState("All Categories");
  const [searchQuery, setSearchQuery] = useState("");

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 12;

  // ── Unique values for filter dropdowns (from real data) ────
  const uniqueProviders = useMemo(() => {
    const set = new Set(tests.map((t) => t.provider_name).filter(Boolean));
    return Array.from(set).sort();
  }, [tests]);

  // ── Filter tests ──────────────────────────────────────────
  const filteredTests = useMemo(() => {
    return tests.filter((test) => {
      const matchCity =
        selectedCity === "All Regions" || test.city === selectedCity;
      const matchProvider =
        selectedProvider === "All Providers" ||
        test.provider_name === selectedProvider;
      const matchCategory =
        selectedCategory === "All Categories" ||
        test.category === selectedCategory;
      const matchSearch =
        test.test_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        test.provider_name.toLowerCase().includes(searchQuery.toLowerCase());

      return matchCity && matchProvider && matchCategory && matchSearch;
    });
  }, [tests, selectedCity, selectedProvider, selectedCategory, searchQuery]);

  // ── Pagination ────────────────────────────────────────────
  const totalPages = Math.ceil(filteredTests.length / itemsPerPage);
  const paginatedTests = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return filteredTests.slice(startIndex, startIndex + itemsPerPage);
  }, [filteredTests, currentPage]);

  // ── Derived metrics ───────────────────────────────────────
  const activeTestsCount = filteredTests.length;

  const avgPrice = useMemo(() => {
    const priced = filteredTests.filter((t) => t.price !== null);
    if (priced.length === 0) return 0;
    return priced.reduce((sum, t) => sum + (t.price ?? 0), 0) / priced.length;
  }, [filteredTests]);

  // ── Competitor avg helper ─────────────────────────────────
  const getCompetitorAvg = (testName: string, city: string, excludeProvider: string) => {
    const others = tests.filter(
      (t) =>
        t.test_name === testName &&
        t.city === city &&
        t.provider_name !== excludeProvider &&
        t.price !== null
    );
    if (others.length === 0) return null;
    return others.reduce((s, t) => s + (t.price ?? 0), 0) / others.length;
  };

  const highVarianceCount = useMemo(() => {
    return filteredTests.filter((test) => {
      if (test.price === null) return false;
      const compAvg = getCompetitorAvg(test.test_name, test.city, test.provider_name);
      if (compAvg === null || compAvg === 0) return false;
      return Math.abs((test.price - compAvg) / compAvg) * 100 > 15;
    }).length;
  }, [filteredTests, tests]);

  const resetFilters = () => {
    setSelectedCity("All Regions");
    setSelectedProvider("All Providers");
    setSelectedCategory("All Categories");
    setSearchQuery("");
    setCurrentPage(1);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h2 className="font-display text-3xl font-bold text-slate-800 tracking-tight">
            Individual Test Pricing
          </h2>
          <p className="font-sans text-sm text-slate-500 mt-1">
            Browse {tests.length} test prices across {stats?.total_providers ?? 0} providers in {stats?.cities?.length ?? 0} cities — live from PostgreSQL.
          </p>
        </div>
      </div>

      {/* Filters Area */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-4 bg-white p-5 border border-slate-200 rounded-2xl soft-shadow">
        <div className="md:col-span-3">
          <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
            City / Region
          </label>
          <select
            value={selectedCity}
            onChange={(e) => {
              setSelectedCity(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full bg-slate-50 border border-slate-200 text-slate-700 text-sm py-2 px-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary cursor-pointer transition-all"
          >
            <option>All Regions</option>
            {(stats?.cities ?? []).map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
        </div>

        <div className="md:col-span-3">
          <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
            Provider Network
          </label>
          <select
            value={selectedProvider}
            onChange={(e) => {
              setSelectedProvider(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full bg-slate-50 border border-slate-200 text-slate-700 text-sm py-2 px-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary cursor-pointer transition-all"
          >
            <option>All Providers</option>
            {uniqueProviders.map((p) => (
              <option key={p}>{p}</option>
            ))}
          </select>
        </div>

        <div className="md:col-span-3">
          <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1.5">
            Department / Category
          </label>
          <select
            value={selectedCategory}
            onChange={(e) => {
              setSelectedCategory(e.target.value);
              setCurrentPage(1);
            }}
            className="w-full bg-slate-50 border border-slate-200 text-slate-700 text-sm py-2 px-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary cursor-pointer transition-all"
          >
            <option>All Categories</option>
            {(stats?.categories ?? []).map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
        </div>

        <div className="md:col-span-3 flex items-end gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search test or provider..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
              className="w-full bg-slate-50 border border-slate-200 text-slate-700 text-sm py-2 pl-9 pr-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all placeholder:text-slate-400"
            />
          </div>
          <button
            onClick={resetFilters}
            className="p-2.5 border border-slate-200 hover:bg-slate-50 hover:text-slate-900 text-slate-500 rounded-xl transition-colors bg-white shadow-sm"
            title="Reset Filters"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Stats Summary Panel */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 border border-slate-200 rounded-2xl soft-shadow hover:soft-shadow-hover transition-all">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Matching Results
          </span>
          <p className="font-display text-3xl font-bold text-slate-800 mt-2">
            {activeTestsCount}
          </p>
          <div className="flex items-center text-emerald-600 text-xs font-medium mt-2">
            <TrendingUp className="w-3.5 h-3.5 mr-1" /> Active
          </div>
        </div>

        <div className="bg-white p-5 border border-slate-200 rounded-2xl soft-shadow hover:soft-shadow-hover transition-all">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Providers Shown
          </span>
          <p className="font-display text-3xl font-bold text-slate-800 mt-2">
            {new Set(filteredTests.map((t) => t.provider_name)).size}
          </p>
          <div className="flex items-center text-primary text-xs font-medium mt-2">
            <CheckCircle className="w-3.5 h-3.5 mr-1" /> In filter
          </div>
        </div>

        <div className="bg-white p-5 border border-slate-200 rounded-2xl soft-shadow hover:soft-shadow-hover transition-all">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            High Variances
          </span>
          <p className={`font-display text-3xl font-bold mt-2 ${highVarianceCount > 0 ? "text-rose-600" : "text-slate-800"}`}>
            {highVarianceCount}
          </p>
          <div className="flex items-center text-rose-600 text-xs font-medium mt-2">
            <AlertTriangle className="w-3.5 h-3.5 mr-1" /> &gt;15% variance
          </div>
        </div>

        <div className="bg-white p-5 border border-slate-200 rounded-2xl soft-shadow hover:soft-shadow-hover transition-all">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            Avg Price
          </span>
          <p className="font-display text-3xl font-bold text-slate-800 mt-2">
            {formatPrice(avgPrice)}
          </p>
          <div className="text-slate-500 text-xs font-medium mt-2">
            Filtered mean
          </div>
        </div>
      </div>

      {/* Main Grid Table */}
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Test Name</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Provider</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">City</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Category</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Price (₹)</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Comp Avg</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Variance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {paginatedTests.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-500 font-medium">
                    No tests matching selected filters.
                  </td>
                </tr>
              ) : (
                paginatedTests.map((test) => {
                  const compAvg = getCompetitorAvg(test.test_name, test.city, test.provider_name);
                  const variance = compAvg !== null && test.price !== null && compAvg > 0 ? ((test.price - compAvg) / compAvg) * 100 : null;
                  const isHigher = variance !== null && variance >= 0;

                  return (
                    <tr key={test.pricing_id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-4 font-medium text-slate-800">{test.test_name}</td>
                      <td className="px-6 py-4 text-slate-600">{test.provider_name}</td>
                      <td className="px-6 py-4 text-slate-600">{test.city}</td>
                      <td className="px-6 py-4">
                        <span className="text-[10px] font-semibold bg-slate-100 text-slate-600 px-2.5 py-1 rounded-full uppercase tracking-wide">
                          {test.category}
                        </span>
                      </td>
                      <td className="px-6 py-4 font-semibold text-slate-800">{formatPrice(test.price)}</td>
                      <td className="px-6 py-4 text-slate-500">{compAvg !== null ? formatPrice(compAvg) : "—"}</td>
                      <td className="px-6 py-4">
                        {variance !== null ? (
                          <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${isHigher ? "bg-rose-100 text-rose-700" : "bg-emerald-100 text-emerald-700"}`}>
                            {isHigher ? "+" : ""}{variance.toFixed(1)}%
                          </span>
                        ) : (
                          <span className="text-slate-300">—</span>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="px-6 py-4 bg-slate-50 flex justify-between items-center border-t border-slate-200">
          <span className="text-slate-500 text-sm font-medium">
            Showing {paginatedTests.length > 0 ? (currentPage - 1) * itemsPerPage + 1 : 0} to {Math.min(currentPage * itemsPerPage, filteredTests.length)} of {filteredTests.length} tests
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage((prev) => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className={`px-4 py-2 text-sm font-medium rounded-lg border transition-all ${
                currentPage === 1
                  ? "bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed"
                  : "bg-white border-slate-200 text-slate-700 hover:bg-slate-50 shadow-sm"
              }`}
            >
              Previous
            </button>
            <button
              onClick={() => setCurrentPage((prev) => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages || totalPages === 0}
              className={`px-4 py-2 text-sm font-medium rounded-lg border transition-all ${
                currentPage === totalPages || totalPages === 0
                  ? "bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed"
                  : "bg-white border-slate-200 text-slate-700 hover:bg-slate-50 shadow-sm"
              }`}
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
