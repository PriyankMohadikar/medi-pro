/**
 * Saved Custom Packages — Management Page
 * View, search, sort, edit, duplicate, and delete custom packages.
 */

import React, { useState, useEffect, useCallback } from "react";
import { CustomPackageData } from "../types";
import {
  fetchCustomPackages,
  deleteCustomPackage,
  duplicateCustomPackage,
} from "../api";
import {
  Search,
  Package,
  Eye,
  Edit3,
  Copy,
  Trash2,
  X,
  Loader2,
  AlertCircle,
  ChevronDown,
  ArrowUpDown,
  IndianRupee,
  TestTubeDiagonal,
  PercentCircle,
  TrendingDown,
  FolderOpen,
} from "lucide-react";

interface SavedPackagesViewProps {
  formatPrice: (val: number | null) => string;
  onEditPackage?: (pkg: CustomPackageData) => void;
}

type SortField = "suggested_package_price" | "market_average_price" | "expected_customer_savings" | "total_tests" | "package_name" | "created_at";
type SortOrder = "asc" | "desc";

export default function SavedPackagesView({ formatPrice, onEditPackage }: SavedPackagesViewProps) {
  const [packages, setPackages] = useState<CustomPackageData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<SortField>("created_at");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");
  const [viewingPackage, setViewingPackage] = useState<CustomPackageData | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  // ── Fetch packages ────────────────────────────────────────
  const loadPackages = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchCustomPackages(search || undefined, sortBy, sortOrder);
      setPackages(data);
    } catch (err: any) {
      setError(err.message || "Failed to load packages");
    } finally {
      setLoading(false);
    }
  }, [search, sortBy, sortOrder]);

  useEffect(() => {
    loadPackages();
  }, [loadPackages]);

  // ── Sort toggle ───────────────────────────────────────────
  const handleSort = (field: SortField) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("desc");
    }
  };

  // ── Duplicate ─────────────────────────────────────────────
  const handleDuplicate = async (id: number) => {
    setActionLoading(id);
    try {
      await duplicateCustomPackage(id);
      await loadPackages();
    } catch (err) {
      console.error("Failed to duplicate:", err);
    } finally {
      setActionLoading(null);
    }
  };

  // ── Delete ────────────────────────────────────────────────
  const handleDelete = async (id: number) => {
    setActionLoading(id);
    try {
      await deleteCustomPackage(id);
      setDeleteConfirm(null);
      await loadPackages();
    } catch (err) {
      console.error("Failed to delete:", err);
    } finally {
      setActionLoading(null);
    }
  };

  const sortLabels: Record<SortField, string> = {
    suggested_package_price: "Suggested Price",
    market_average_price: "Market Average",
    expected_customer_savings: "Customer Savings",
    total_tests: "Number of Tests",
    package_name: "Package Name",
    created_at: "Date Created",
  };

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 card-shadow">
        <div className="flex flex-col md:flex-row items-start md:items-center gap-4 justify-between">
          {/* Search */}
          <div className="relative flex-1 max-w-md w-full">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search packages..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl py-2.5 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all placeholder:text-slate-400"
            />
          </div>

          {/* Sort dropdown */}
          <div className="flex items-center gap-2">
            <span className="text-[11px] text-slate-400 font-medium">Sort by:</span>
            <div className="relative">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortField)}
                className="appearance-none bg-slate-50 border border-slate-200 rounded-lg py-2 pl-3 pr-8 text-xs font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary cursor-pointer"
              >
                {Object.entries(sortLabels).map(([key, label]) => (
                  <option key={key} value={key}>{label}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400 pointer-events-none" />
            </div>
            <button
              onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
              className="p-2 bg-slate-50 border border-slate-200 rounded-lg hover:bg-slate-100 transition-colors"
              title={`Sort ${sortOrder === "asc" ? "descending" : "ascending"}`}
            >
              <ArrowUpDown className="w-3.5 h-3.5 text-slate-500" />
            </button>
          </div>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 text-primary animate-spin" />
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="bg-red-50 border border-red-100 rounded-xl p-6 text-center">
          <AlertCircle className="w-8 h-8 text-red-400 mx-auto mb-3" />
          <p className="text-sm text-red-600 font-medium">{error}</p>
          <button onClick={loadPackages} className="mt-3 text-xs text-primary font-semibold hover:underline">
            Try Again
          </button>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && packages.length === 0 && (
        <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center card-shadow">
          <div className="w-16 h-16 bg-slate-50 rounded-2xl flex items-center justify-center mx-auto mb-5 border border-slate-100">
            <FolderOpen className="w-8 h-8 text-slate-300" />
          </div>
          <h3 className="font-display text-lg font-bold text-slate-700">No Saved Packages</h3>
          <p className="text-sm text-slate-400 mt-2 max-w-sm mx-auto">
            {search
              ? `No packages matching "${search}" were found. Try a different search term.`
              : "Create your first custom package using the Package Builder to get started."}
          </p>
        </div>
      )}

      {/* Package table */}
      {!loading && !error && packages.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-2xl card-shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="text-left px-5 py-3.5 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                    Package Name
                  </th>
                  <th className="text-center px-3 py-3.5 text-[11px] font-semibold text-slate-500 uppercase tracking-wider cursor-pointer hover:text-primary transition-colors" onClick={() => handleSort("total_tests")}>
                    # Tests {sortBy === "total_tests" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th className="text-right px-3 py-3.5 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                    Individual Total
                  </th>
                  <th className="text-center px-3 py-3.5 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                    Discount %
                  </th>
                  <th className="text-right px-3 py-3.5 text-[11px] font-semibold text-slate-500 uppercase tracking-wider cursor-pointer hover:text-primary transition-colors" onClick={() => handleSort("suggested_package_price")}>
                    Suggested Price {sortBy === "suggested_package_price" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th className="text-right px-3 py-3.5 text-[11px] font-semibold text-slate-500 uppercase tracking-wider cursor-pointer hover:text-primary transition-colors" onClick={() => handleSort("market_average_price")}>
                    Market Avg {sortBy === "market_average_price" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th className="text-right px-3 py-3.5 text-[11px] font-semibold text-slate-500 uppercase tracking-wider cursor-pointer hover:text-primary transition-colors" onClick={() => handleSort("expected_customer_savings")}>
                    Savings {sortBy === "expected_customer_savings" && (sortOrder === "asc" ? "↑" : "↓")}
                  </th>
                  <th className="text-center px-5 py-3.5 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {packages.map((pkg) => (
                  <tr key={pkg.package_id} className="table-row-hover group">
                    <td className="px-5 py-4">
                      <p className="text-sm font-semibold text-slate-800 group-hover:text-primary transition-colors">{pkg.package_name}</p>
                      <p className="text-[10px] text-slate-400 mt-0.5">
                        {pkg.created_at ? new Date(pkg.created_at).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }) : "—"}
                      </p>
                    </td>
                    <td className="px-3 py-4 text-center">
                      <span className="inline-flex items-center gap-1 bg-slate-100 px-2 py-0.5 rounded-md text-xs font-semibold text-slate-600">
                        {pkg.total_tests}
                      </span>
                    </td>
                    <td className="px-3 py-4 text-right text-sm font-medium text-slate-700">
                      {formatPrice(pkg.individual_total_price)}
                    </td>
                    <td className="px-3 py-4 text-center">
                      <span className="inline-flex items-center gap-1 bg-amber-50 text-amber-700 px-2 py-0.5 rounded-md text-xs font-semibold">
                        {pkg.discount_percentage ?? 0}%
                      </span>
                    </td>
                    <td className="px-3 py-4 text-right text-sm font-bold text-primary">
                      {formatPrice(pkg.suggested_package_price)}
                    </td>
                    <td className="px-3 py-4 text-right text-sm font-medium text-slate-600">
                      {formatPrice(pkg.market_average_price)}
                    </td>
                    <td className="px-3 py-4 text-right">
                      <span className="text-sm font-semibold text-emerald-600">
                        {formatPrice(pkg.expected_customer_savings)}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center justify-center gap-1">
                        <button
                          onClick={() => setViewingPackage(pkg)}
                          className="p-1.5 text-slate-400 hover:text-primary hover:bg-primary-50 rounded-lg transition-all"
                          title="View details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => onEditPackage?.(pkg)}
                          className="p-1.5 text-slate-400 hover:text-amber-600 hover:bg-amber-50 rounded-lg transition-all"
                          title="Edit package"
                        >
                          <Edit3 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDuplicate(pkg.package_id)}
                          disabled={actionLoading === pkg.package_id}
                          className="p-1.5 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all disabled:opacity-40"
                          title="Duplicate package"
                        >
                          {actionLoading === pkg.package_id ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Copy className="w-4 h-4" />
                          )}
                        </button>
                        <button
                          onClick={() => setDeleteConfirm(pkg.package_id)}
                          className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all"
                          title="Delete package"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="px-5 py-3 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
            <p className="text-[11px] text-slate-400 font-medium">
              {packages.length} package{packages.length !== 1 ? "s" : ""}
            </p>
          </div>
        </div>
      )}

      {/* ── View Modal ─────────────────────────────────────── */}
      {/* View Package Modal */}
      {viewingPackage && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-[100] flex items-center justify-center p-4" onClick={() => setViewingPackage(null)}>
          <div
            className="bg-white rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto shadow-2xl border border-slate-200 animate-fadeInUp"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="p-6 border-b border-slate-100 flex items-start justify-between">
              <div>
                <h2 className="font-display text-xl font-bold text-slate-800">{viewingPackage.package_name}</h2>
                <p className="text-xs text-slate-400 mt-1">
                  Created {viewingPackage.created_at ? new Date(viewingPackage.created_at).toLocaleString("en-IN") : "—"}
                </p>
              </div>
              <button
                onClick={() => setViewingPackage(null)}
                className="p-1.5 hover:bg-slate-100 rounded-lg text-slate-400 hover:text-slate-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* KPI Cards */}
            <div className="p-6 grid grid-cols-3 gap-4">
              <div className="bg-primary-50 rounded-xl p-4 border border-primary/10">
                <div className="flex items-center gap-2 mb-2">
                  <TestTubeDiagonal className="w-4 h-4 text-primary" />
                  <span className="text-[10px] text-primary font-semibold uppercase tracking-wider">Tests</span>
                </div>
                <p className="font-display text-2xl font-bold text-slate-800">{viewingPackage.total_tests}</p>
              </div>
              <div className="bg-emerald-50 rounded-xl p-4 border border-emerald-100">
                <div className="flex items-center gap-2 mb-2">
                  <IndianRupee className="w-4 h-4 text-emerald-600" />
                  <span className="text-[10px] text-emerald-600 font-semibold uppercase tracking-wider">Suggested Price</span>
                </div>
                <p className="font-display text-2xl font-bold text-slate-800">{formatPrice(viewingPackage.suggested_package_price)}</p>
              </div>
              <div className="bg-amber-50 rounded-xl p-4 border border-amber-100">
                <div className="flex items-center gap-2 mb-2">
                  <PercentCircle className="w-4 h-4 text-amber-600" />
                  <span className="text-[10px] text-amber-600 font-semibold uppercase tracking-wider">Discount</span>
                </div>
                <p className="font-display text-2xl font-bold text-slate-800">{viewingPackage.discount_percentage ?? 0}%</p>
              </div>
            </div>

            {/* Detail rows */}
            <div className="px-6 pb-4 space-y-2">
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-sm text-slate-500">Individual Total Price</span>
                <span className="text-sm font-semibold text-slate-800">{formatPrice(viewingPackage.individual_total_price)}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-sm text-slate-500">Market Average Price</span>
                <span className="text-sm font-semibold text-slate-800">{formatPrice(viewingPackage.market_average_price)}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-100">
                <span className="text-sm text-slate-500">Expected Customer Savings</span>
                <span className="text-sm font-bold text-emerald-600">{formatPrice(viewingPackage.expected_customer_savings)}</span>
              </div>
            </div>

            {/* Tests list */}
            <div className="px-6 pb-6">
              <h3 className="text-sm font-bold text-slate-700 mb-3 flex items-center gap-2">
                <TestTubeDiagonal className="w-4 h-4 text-slate-400" />
                Included Tests ({viewingPackage.tests.length})
              </h3>
              <div className="space-y-1.5">
                {viewingPackage.tests.map((test, idx) => (
                  <div key={test.id || idx} className="flex items-center justify-between py-2.5 px-3 bg-slate-50 rounded-lg border border-slate-100">
                    <div className="flex items-center gap-3">
                      <span className="w-6 h-6 bg-white rounded text-[10px] font-bold text-slate-500 flex items-center justify-center border border-slate-200">
                        {idx + 1}
                      </span>
                      <span className="text-sm font-medium text-slate-700">{test.test_name}</span>
                    </div>
                    <span className="text-sm font-semibold text-slate-600">{formatPrice(test.individual_price)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Delete Confirmation Dialog ─────────────────────── */}
      {deleteConfirm !== null && (
        <div 
          className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-[100] flex items-center justify-center p-4" 
          onClick={() => setDeleteConfirm(null)}
        >
          <div
            className="bg-white rounded-3xl w-full max-w-[440px] shadow-2xl border border-slate-100 p-6 sm:p-7 animate-fadeInUp relative flex flex-col"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header / Icon */}
            <div className="flex items-start gap-4 mb-3">
              <div className="w-12 h-12 bg-red-100/80 border border-red-200/60 rounded-2xl flex items-center justify-center shrink-0">
                <Trash2 className="w-6 h-6 text-red-600" />
              </div>
              <div className="pt-0.5">
                <h3 className="font-display text-xl font-bold text-slate-900 leading-tight">Delete Package</h3>
                <p className="text-xs font-semibold text-red-500 mt-0.5">This action cannot be undone</p>
              </div>
            </div>

            {/* Target Package Info Card */}
            {(() => {
              const targetPkg = packages.find(p => p.package_id === deleteConfirm);
              return targetPkg ? (
                <div className="bg-slate-50 border border-slate-200/80 rounded-2xl p-3.5 my-3 flex items-center justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Target Package</span>
                    <span className="text-sm font-bold text-slate-800 truncate block">{targetPkg.package_name}</span>
                  </div>
                  <span className="text-sm font-bold text-slate-700 bg-white px-2.5 py-1 rounded-lg border border-slate-200 shrink-0">
                    {formatPrice(targetPkg.package_price)}
                  </span>
                </div>
              ) : null;
            })()}

            <p className="text-sm text-slate-600 mb-6 leading-relaxed">
              Are you sure you want to delete this package? All associated tests and pricing data will be permanently removed.
            </p>

            {/* Action Buttons */}
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setDeleteConfirm(null)}
                className="flex-1 px-4 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl transition-all text-sm"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => handleDelete(deleteConfirm)}
                disabled={actionLoading === deleteConfirm}
                className="flex-1 px-4 py-3 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700 text-white font-semibold rounded-xl shadow-lg shadow-red-500/25 transition-all text-sm flex items-center justify-center gap-2 disabled:opacity-60"
              >
                {actionLoading === deleteConfirm ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Trash2 className="w-4 h-4" />
                )}
                <span>Delete</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
