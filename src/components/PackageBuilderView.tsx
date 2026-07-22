/**
 * Custom Package Builder — Create & Edit
 * Build and price custom healthcare packages with live calculations.
 * Supports both create and edit modes with full API integration.
 */

import React, { useState, useMemo, useEffect } from "react";
import { TestItem, PackageItem, StatsData, CustomPackageData, ES_PROVIDER_NAME } from "../types";
import { createCustomPackage, updateCustomPackage } from "../api";
import {
  Search,
  Plus,
  X,
  Package,
  Calculator,
  Save,
  FileDown,
  CheckCircle,
  AlertCircle,
  Loader2,
  Edit3,
} from "lucide-react";

interface PackageBuilderViewProps {
  tests: TestItem[];
  packages: PackageItem[];
  stats: StatsData | null;
  formatPrice: (val: number | null) => string;
  editingPackage?: CustomPackageData | null;
  onSaveSuccess?: () => void;
  onCancelEdit?: () => void;
}

export default function PackageBuilderView({
  tests,
  packages,
  stats,
  formatPrice,
  editingPackage,
  onSaveSuccess,
  onCancelEdit,
}: PackageBuilderViewProps) {
  const [activeTab, setActiveTab] = useState<string>("ALL");
  const [testSearch, setTestSearch] = useState("");
  const [selectedTestNames, setSelectedTestNames] = useState<string[]>([]);
  const [bundleName, setBundleName] = useState("Custom Wellness Package");
  const [marginPercent, setMarginPercent] = useState(15);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<{ type: "success" | "error"; message: string } | null>(null);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  const isEditMode = !!editingPackage;

  // ── Pre-populate fields when editing ──────────────────────
  useEffect(() => {
    if (editingPackage) {
      setBundleName(editingPackage.package_name);
      setMarginPercent(editingPackage.discount_percentage ?? 15);
      setSelectedTestNames(editingPackage.tests.map((t) => t.test_name));
    }
  }, [editingPackage]);

  // Auto-dismiss toast
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 4000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  // ── Unique tests (ES Healthcare first, deduplicated) ──────
  const uniqueTests = useMemo(() => {
    const seen = new Set<string>();
    const result: TestItem[] = [];
    const sorted = [...tests].sort((a, b) =>
      a.provider_name === ES_PROVIDER_NAME ? -1 : b.provider_name === ES_PROVIDER_NAME ? 1 : 0
    );
    sorted.forEach((t) => {
      if (!seen.has(t.test_name) && t.price !== null) {
        seen.add(t.test_name);
        result.push(t);
      }
    });
    return result;
  }, [tests]);

  // ── Category tabs ─────────────────────────────────────────
  const categoryTabs = useMemo(() => ["ALL", ...(stats?.categories ?? [])], [stats]);

  // ── Filtered tests ────────────────────────────────────────
  const filteredTestsList = useMemo(() => {
    return uniqueTests.filter((test) => {
      const matchTab = activeTab === "ALL" || test.category === activeTab;
      const matchSearch = test.test_name.toLowerCase().includes(testSearch.toLowerCase());
      return matchTab && matchSearch;
    });
  }, [uniqueTests, activeTab, testSearch]);

  // ── Selected items ────────────────────────────────────────
  const selectedItems = useMemo(() => {
    return uniqueTests.filter((t) => selectedTestNames.includes(t.test_name));
  }, [uniqueTests, selectedTestNames]);

  // ── Pricing calculations ──────────────────────────────────
  const totalComponentCost = useMemo(() => {
    return selectedItems.reduce((sum, item) => sum + (item.price ?? 0), 0);
  }, [selectedItems]);

  // Market average for selected tests
  const marketAverage = useMemo(() => {
    if (selectedItems.length === 0) return 0;
    let total = 0;
    selectedItems.forEach((item) => {
      const compPrices = tests.filter(
        (t) => t.test_name === item.test_name && t.provider_name !== ES_PROVIDER_NAME && t.price !== null
      );
      if (compPrices.length > 0) {
        total += compPrices.reduce((s, t) => s + (t.price ?? 0), 0) / compPrices.length;
      } else {
        total += item.price ?? 0;
      }
    });
    return Math.round(total);
  }, [selectedItems, tests]);

  const suggestedPrice = Math.round(totalComponentCost * (1 - marginPercent / 100));
  const expectedSaving = totalComponentCost - suggestedPrice;
  const savingPct = totalComponentCost > 0 ? Math.round((expectedSaving / totalComponentCost) * 100) : 0;

  const handleAddTest = (testName: string) => {
    if (!selectedTestNames.includes(testName)) {
      setSelectedTestNames([...selectedTestNames, testName]);
      setValidationErrors([]);
    }
  };

  const handleRemoveTest = (testName: string) => {
    setSelectedTestNames(selectedTestNames.filter((n) => n !== testName));
  };

  // ── Validation ────────────────────────────────────────────
  const validate = (): boolean => {
    const errors: string[] = [];
    if (!bundleName.trim()) errors.push("Package name is required");
    if (selectedItems.length === 0) errors.push("At least one test must be selected");
    if (marginPercent < 0) errors.push("Discount cannot be negative");
    if (suggestedPrice <= 0 && selectedItems.length > 0) errors.push("Suggested price must be greater than zero");
    setValidationErrors(errors);
    return errors.length === 0;
  };

  // ── Save / Update ─────────────────────────────────────────
  const handleSave = async () => {
    if (!validate()) return;

    setSaving(true);
    try {
      const payload = {
        package_name: bundleName.trim(),
        total_tests: selectedItems.length,
        individual_total_price: totalComponentCost,
        discount_percentage: marginPercent,
        suggested_package_price: suggestedPrice,
        market_average_price: marketAverage,
        expected_customer_savings: expectedSaving,
        tests: selectedItems.map((item, i) => ({
          test_name: item.test_name,
          individual_price: item.price ?? 0,
          display_order: i,
        })),
      };

      if (isEditMode && editingPackage) {
        await updateCustomPackage(editingPackage.package_id, payload);
        setToast({ type: "success", message: "Package updated successfully!" });
      } else {
        await createCustomPackage(payload);
        setToast({ type: "success", message: "Package saved successfully!" });
        // Reset form after create
        setBundleName("Custom Wellness Package");
        setSelectedTestNames([]);
        setMarginPercent(15);
      }
      onSaveSuccess?.();
    } catch (err: any) {
      setToast({ type: "error", message: err.message || "Failed to save package" });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6 h-[calc(100vh-140px)] flex flex-col relative">
      {/* Toast notification */}
      {toast && (
        <div
          className={`fixed top-6 right-6 z-[100] flex items-center gap-3 px-5 py-3.5 rounded-xl shadow-lg border animate-fadeInUp ${
            toast.type === "success"
              ? "bg-emerald-50 border-emerald-200 text-emerald-800"
              : "bg-red-50 border-red-200 text-red-800"
          }`}
        >
          {toast.type === "success" ? (
            <CheckCircle className="w-5 h-5 text-emerald-500 flex-shrink-0" />
          ) : (
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
          )}
          <span className="text-sm font-medium">{toast.message}</span>
          <button onClick={() => setToast(null)} className="ml-2 p-0.5 hover:opacity-70 transition-opacity">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Edit mode banner */}
      {isEditMode && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl px-5 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Edit3 className="w-5 h-5 text-amber-600" />
            <div>
              <p className="text-sm font-semibold text-amber-800">Editing: {editingPackage?.package_name}</p>
              <p className="text-[11px] text-amber-600">Modify the package and click Update to save changes</p>
            </div>
          </div>
          <button
            onClick={onCancelEdit}
            className="px-4 py-2 text-sm font-medium text-amber-700 hover:bg-amber-100 rounded-lg transition-colors"
          >
            Cancel Edit
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-0">
        {/* LEFT: Available Tests */}
        <section className="lg:col-span-3 flex flex-col bg-white border border-slate-200 rounded-2xl overflow-hidden card-shadow">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <h2 className="text-sm font-bold text-slate-800">Available Tests</h2>
            <p className="text-[10px] text-slate-400 mt-0.5">{uniqueTests.length} unique tests</p>
          </div>

          {/* Tabs */}
          <div className="p-3 border-b border-slate-200 space-y-2.5">
            <div className="flex gap-1.5 overflow-x-auto pb-1">
              {categoryTabs.map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-2.5 py-1 text-[10px] font-semibold rounded-lg transition-all whitespace-nowrap ${
                    activeTab === tab ? "bg-primary text-white" : "bg-slate-100 text-slate-500 hover:bg-slate-200"
                  }`}
                >{tab}</button>
              ))}
            </div>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
              <input
                type="text"
                placeholder="Search tests..."
                value={testSearch}
                onChange={(e) => setTestSearch(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-lg py-2 pl-8 pr-3 text-xs focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all placeholder:text-slate-400"
              />
            </div>
          </div>

          {/* Test List */}
          <div className="flex-1 overflow-y-auto divide-y divide-slate-100">
            {filteredTestsList.map((test) => {
              const isSelected = selectedTestNames.includes(test.test_name);
              return (
                <div key={test.pricing_id} className={`p-3 flex items-center justify-between transition-colors ${isSelected ? "bg-primary-50" : "hover:bg-slate-50"}`}>
                  <div className="flex-1 min-w-0 pr-2">
                    <p className={`text-xs font-semibold truncate ${isSelected ? "text-primary" : "text-slate-700"}`}>{test.test_name}</p>
                    <p className="text-[10px] text-slate-400 mt-0.5 flex items-center gap-1.5">
                      <span className="bg-slate-100 px-1.5 py-0.5 rounded text-[9px]">{test.category}</span>
                      <span className="font-medium text-slate-500">{formatPrice(test.price)}</span>
                    </p>
                  </div>
                  <button
                    onClick={() => isSelected ? handleRemoveTest(test.test_name) : handleAddTest(test.test_name)}
                    className={`w-7 h-7 rounded-lg flex items-center justify-center transition-all flex-shrink-0 ${
                      isSelected ? "bg-primary text-white" : "bg-slate-100 text-slate-500 hover:bg-primary hover:text-white"
                    }`}
                  >
                    {isSelected ? <CheckCircle className="w-3.5 h-3.5" /> : <Plus className="w-3.5 h-3.5" />}
                  </button>
                </div>
              );
            })}
          </div>
        </section>

        {/* CENTER: Selected Tests */}
        <section className="lg:col-span-5 flex flex-col">
          <div className="flex-1 bg-white border border-slate-200 rounded-2xl flex flex-col card-shadow overflow-hidden">
            <div className="p-5 border-b border-slate-100 bg-slate-50/50">
              <h2 className="font-display text-lg font-bold text-slate-800">Package Configuration</h2>
              <input
                type="text"
                value={bundleName}
                onChange={(e) => {
                  setBundleName(e.target.value);
                  setValidationErrors([]);
                }}
                className={`mt-3 bg-white border rounded-lg px-3 py-2 text-sm font-semibold text-slate-800 w-full focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary ${
                  validationErrors.includes("Package name is required") ? "border-red-300 bg-red-50/30" : "border-slate-200"
                }`}
                placeholder="Package Name"
              />
              {/* Validation errors */}
              {validationErrors.length > 0 && (
                <div className="mt-3 space-y-1">
                  {validationErrors.map((err, i) => (
                    <p key={i} className="text-[11px] text-red-500 flex items-center gap-1.5">
                      <AlertCircle className="w-3 h-3 flex-shrink-0" />
                      {err}
                    </p>
                  ))}
                </div>
              )}
            </div>

            <div className="flex-1 overflow-y-auto p-5">
              {selectedItems.length === 0 ? (
                <div className="h-full border-2 border-dashed border-slate-200 rounded-xl flex flex-col items-center justify-center text-center p-8 bg-slate-50/30">
                  <div className="w-14 h-14 bg-white rounded-xl flex items-center justify-center shadow-sm border border-slate-100 mb-4">
                    <Package className="w-7 h-7 text-slate-300" />
                  </div>
                  <p className="text-sm font-semibold text-slate-500">No tests selected</p>
                  <p className="text-xs text-slate-400 mt-1 max-w-[220px]">
                    Select tests from the left panel to build your custom package.
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  {selectedItems.map((test, idx) => (
                    <div
                      key={test.test_name}
                      className="bg-white border border-slate-200 rounded-xl p-3.5 flex items-center gap-3 card-shadow animate-fadeInUp"
                      style={{ animationDelay: `${idx * 50}ms` }}
                    >
                      <div className="w-8 h-8 bg-primary-50 text-primary rounded-lg flex items-center justify-center flex-shrink-0 text-xs font-bold">
                        {idx + 1}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-slate-800 text-sm truncate">{test.test_name}</p>
                        <p className="text-[10px] text-slate-400 mt-0.5">{test.category}</p>
                      </div>
                      <span className="font-semibold text-slate-700 text-sm flex-shrink-0">{formatPrice(test.price)}</span>
                      <button onClick={() => handleRemoveTest(test.test_name)} className="p-1 hover:bg-red-50 text-slate-400 hover:text-red-500 rounded-lg transition-colors flex-shrink-0">
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </section>

        {/* RIGHT: Live Calculation */}
        <section className="lg:col-span-4 flex flex-col gap-5">
          {/* Pricing Engine */}
          <div className="bg-slate-900 rounded-2xl p-6 text-white relative overflow-hidden flex-shrink-0">
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/15 rounded-full blur-2xl" />

            <div className="flex items-center justify-between mb-5 relative z-10">
              <h3 className="font-display font-bold text-sm flex items-center gap-2">
                <Calculator className="w-4 h-4 text-primary-light" /> Live Calculation
              </h3>
              <span className="text-[9px] bg-primary/20 text-primary-light px-2 py-0.5 rounded-md font-bold tracking-wider border border-primary/30">
                AUTO
              </span>
            </div>

            <div className="space-y-3.5 text-sm relative z-10">
              <div className="flex justify-between">
                <span className="text-slate-400">Number of Tests</span>
                <span className="font-semibold">{selectedItems.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Individual Total Price</span>
                <span className="font-semibold">{formatPrice(totalComponentCost)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Market Average Price</span>
                <span className="font-medium text-slate-300">{formatPrice(marketAverage)}</span>
              </div>
              <div className="h-px bg-white/10" />
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Discount Percentage</span>
                <div className="flex items-center gap-2">
                  <input
                    type="range"
                    min="0"
                    max="50"
                    value={marginPercent}
                    onChange={(e) => setMarginPercent(Number(e.target.value))}
                    className="w-20 accent-primary"
                  />
                  <span className="font-semibold text-primary-light w-10 text-right">{marginPercent}%</span>
                </div>
              </div>
              <div className="h-px bg-white/10" />
              <div className="flex justify-between">
                <span className="text-slate-400">Expected Customer Savings</span>
                <span className="font-semibold text-emerald-400">{formatPrice(expectedSaving)} ({savingPct}%)</span>
              </div>
              <div className="flex justify-between items-end pt-2">
                <span className="text-white font-semibold">Suggested Package Price</span>
                <span className="font-display font-bold text-2xl text-primary-light leading-none">{formatPrice(suggestedPrice)}</span>
              </div>
            </div>

            <div className="flex gap-2 mt-6 relative z-10">
              <button
                onClick={handleSave}
                disabled={saving}
                className="flex-1 bg-primary hover:bg-primary-dark disabled:opacity-60 text-white font-semibold py-2.5 rounded-xl transition-colors flex items-center justify-center gap-2 text-sm"
              >
                {saving ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Save className="w-4 h-4" />
                )}
                {isEditMode ? "Update Package" : "Save Package"}
              </button>
              <button className="px-4 bg-white/10 hover:bg-white/20 text-white font-medium py-2.5 rounded-xl transition-colors text-sm">
                <FileDown className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Existing Packages */}
          <div className="bg-white border border-slate-200 rounded-2xl card-shadow flex flex-col flex-1 min-h-0">
            <div className="p-4 border-b border-slate-100 flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-800 flex items-center gap-2">
                <Package className="w-4 h-4 text-slate-400" /> Existing Packages
              </h3>
              <span className="bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full text-[10px] font-semibold">{packages.length}</span>
            </div>
            <div className="flex-1 overflow-y-auto p-3 space-y-2">
              {packages.slice(0, 8).map((pkg) => (
                <div key={pkg.package_id} className="p-3 bg-slate-50 border border-slate-100 rounded-xl hover:border-primary/20 transition-colors cursor-pointer group">
                  <div className="flex justify-between items-start">
                    <div className="min-w-0 flex-1">
                      <p className="font-semibold text-slate-800 text-xs truncate group-hover:text-primary transition-colors">{pkg.package_name}</p>
                      <p className="text-[10px] text-slate-400 mt-0.5">{pkg.provider_name} · {pkg.city}</p>
                    </div>
                    <span className="font-bold text-slate-700 text-xs flex-shrink-0 ml-2">{formatPrice(pkg.package_price)}</span>
                  </div>
                  {pkg.tests_included.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {pkg.tests_included.slice(0, 3).map((t) => (
                        <span key={t} className="text-[9px] bg-white border border-slate-200 text-slate-500 px-1.5 py-0.5 rounded font-medium truncate max-w-[90px]">{t}</span>
                      ))}
                      {pkg.tests_included.length > 3 && (
                        <span className="text-[9px] text-slate-400 font-medium px-1">+{pkg.tests_included.length - 3}</span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
