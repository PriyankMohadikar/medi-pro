import React, { useState } from "react";
import Drawer from "./ui/Drawer";
import { Package, Activity, IndianRupee, PieChart, Info, Building2, Layers, Sparkles } from "lucide-react";
import { TestItem, ES_PROVIDER_NAME } from "../types";
import PackageAiInsightModal from "./PackageAiInsightModal";

interface PackageDetailsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  pkg: any | null; // AnalyzedPackage with tests_included
  tests: TestItem[];
  formatPrice: (val: number | null) => string;
}

export default function PackageDetailsDrawer({ isOpen, onClose, pkg, tests, formatPrice }: PackageDetailsDrawerProps) {
  const [aiModalOpen, setAiModalOpen] = useState(false);

  if (!pkg) return null;

  // 1. Calculate ES Healthcare Comparison on the fly
  let esIndividualTotal = 0;
  const includedTestsData = pkg.tests_included.map((testName: string) => {
    // Find all prices for this test in this city
    const testPrices = tests.filter((t) => t.test_name.toLowerCase() === testName.toLowerCase() && t.city === pkg.city && t.price !== null);
    
    // Find ES Healthcare price
    const esTest = testPrices.find((t) => t.provider_name === ES_PROVIDER_NAME);
    const esPrice = esTest?.price ?? null;
    
    // Find competitor price or market average
    const providerPrice = testPrices.find((t) => t.provider_name === pkg.provider_name)?.price;
    const avgPrice = testPrices.length > 0 ? testPrices.reduce((sum, t) => sum + (t.price ?? 0), 0) / testPrices.length : 0;
    const compPrice = providerPrice ?? avgPrice;

    // Add to ES Total
    esIndividualTotal += esPrice ?? avgPrice; // Fallback to avg if ES doesn't have it

    // Return data for the table
    return {
      name: testName,
      category: testPrices[0]?.category || "General",
      compPrice: compPrice,
      esPrice: esPrice
    };
  });

  const diffES = esIndividualTotal - pkg.package_price;
  const isESMoreExpensive = diffES > 0;
  
  let esRecommendation = "ES Healthcare pricing is already competitive.";
  if (diffES > 1500) {
    esRecommendation = "ES Healthcare individual tests are significantly more expensive. Consider creating a similar package.";
  } else if (diffES > 500) {
    esRecommendation = "Consider a slight discount or a custom package to match this offer.";
  } else if (diffES < -500) {
    esRecommendation = "ES Healthcare individual pricing is cheaper than this package. Excellent positioning.";
  }

  // ── Detail row helper ───────────────────────────────
  const SummaryRow = ({ label, value, valueClass = "text-slate-800" }: { label: string; value: React.ReactNode; valueClass?: string }) => (
    <div className="flex items-center justify-between py-2 border-b border-slate-50 last:border-0">
      <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{label}</span>
      <span className={`text-sm font-bold ${valueClass}`}>{value}</span>
    </div>
  );

  return (
    <>
      <Drawer
        isOpen={isOpen}
        onClose={onClose}
        title={pkg.package_name}
        width="w-full sm:w-[550px]"
        subtitle={
          <div className="flex items-center gap-3 text-xs font-medium text-slate-500 mt-1">
            <span className="flex items-center gap-1"><Building2 className="w-3.5 h-3.5" /> {pkg.provider_name}</span>
            <span className="flex items-center gap-1"><Layers className="w-3.5 h-3.5" /> {pkg.test_count} Tests</span>
          </div>
        }
        footer={
          <div className="flex items-center gap-3">
            <button
              onClick={onClose}
              className="flex-1 py-2.5 bg-white border border-slate-200 rounded-xl text-sm font-bold text-slate-600 hover:bg-slate-50 hover:text-slate-800 transition-colors shadow-sm"
            >
              Close
            </button>
            <button
              onClick={() => setAiModalOpen(true)}
              className="flex-[2] flex items-center justify-center gap-2 py-2.5 bg-slate-900 text-white rounded-xl text-sm font-bold hover:bg-slate-800 transition-colors shadow-sm"
            >
              <Sparkles className="w-4 h-4" /> AI Analyze Package
            </button>
          </div>
        }
      >
        <div className="p-6 space-y-8">
          
          {/* ── SECTION 1: Package Information ──────────────── */}
          <div className="grid grid-cols-2 gap-3">
            <div className="p-4 bg-slate-50 border border-slate-100 rounded-xl">
              <div className="flex items-center gap-2 text-slate-500 mb-1">
                <Package className="w-4 h-4" />
                <span className="text-[10px] font-bold uppercase tracking-wider">Package Price</span>
              </div>
              <p className="text-xl font-black text-slate-800">{formatPrice(pkg.package_price)}</p>
            </div>
            <div className="p-4 bg-slate-50 border border-slate-100 rounded-xl">
              <div className="flex items-center gap-2 text-slate-500 mb-1">
                <Activity className="w-4 h-4" />
                <span className="text-[10px] font-bold uppercase tracking-wider">Number of Tests</span>
              </div>
              <p className="text-xl font-black text-slate-800">{pkg.test_count}</p>
            </div>
          </div>

          {/* ── SECTION 2: Included Tests ───────────────────── */}
          <div>
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3 flex items-center justify-between">
              Included Tests
              <span className="bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full text-[10px] font-semibold">{pkg.test_count} Total</span>
            </h3>
            <div className="border border-slate-200 rounded-xl overflow-hidden">
              <div className="max-h-[250px] overflow-y-auto custom-scrollbar">
                <table className="w-full text-left border-collapse relative">
                  <thead className="bg-slate-50 sticky top-0 z-10">
                    <tr>
                      <th className="px-4 py-2.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200">Test Name</th>
                      <th className="px-4 py-2.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider border-b border-slate-200">Category</th>
                      <th className="px-4 py-2.5 text-[10px] font-bold text-slate-500 uppercase tracking-wider text-right border-b border-slate-200">Price</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-sm">
                    {includedTestsData.map((t, idx) => (
                      <tr key={idx} className="hover:bg-slate-50 transition-colors">
                        <td className="px-4 py-3 font-semibold text-slate-700 text-xs">{t.name}</td>
                        <td className="px-4 py-3">
                          <span className="text-[9px] font-bold bg-white border border-slate-200 text-slate-500 px-2 py-0.5 rounded whitespace-nowrap">
                            {t.category}
                          </span>
                        </td>
                        <td className="px-4 py-3 font-semibold text-slate-600 text-xs text-right">
                          {formatPrice(Math.round(t.compPrice))}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* ── SECTION 3: Price Summary ────────────────────── */}
          <div>
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3">Price Summary</h3>
            <div className="bg-slate-50/70 rounded-xl border border-slate-100 px-5 py-2">
              <SummaryRow label="Individual Tests Total" value={formatPrice(pkg.individual_cost)} />
              <SummaryRow label="Package Price" value={formatPrice(pkg.package_price)} valueClass="text-primary" />
              <SummaryRow 
                label="Customer Savings" 
                value={
                  <span className="inline-flex items-center gap-1.5 text-emerald-600">
                    {formatPrice(pkg.savings)}
                    <span className="bg-emerald-100 text-emerald-700 px-1.5 py-0.5 rounded text-[10px]">
                      {pkg.savings_pct}%
                    </span>
                  </span>
                } 
              />
            </div>
          </div>

          {/* ── SECTION 4: ES Healthcare Comparison ─────────── */}
          <div>
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3 flex items-center gap-2">
              <Info className="w-4 h-4 text-slate-400" /> ES Healthcare Comparison
            </h3>
            
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-sm">
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">ES Individual Total</p>
                  <p className="text-lg font-black text-slate-800">{formatPrice(Math.round(esIndividualTotal))}</p>
                </div>
                <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-sm">
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Difference</p>
                  <p className={`text-lg font-black ${isESMoreExpensive ? "text-red-600" : "text-emerald-600"}`}>
                    {isESMoreExpensive ? "+" : ""}{formatPrice(Math.round(diffES))}
                  </p>
                </div>
              </div>

              <div className={`p-4 rounded-xl border ${isESMoreExpensive ? 'bg-amber-50/50 border-amber-200' : 'bg-emerald-50/50 border-emerald-200'}`}>
                <h4 className={`text-xs font-bold uppercase tracking-wider mb-1 ${isESMoreExpensive ? 'text-amber-800' : 'text-emerald-800'}`}>Recommendation</h4>
                <p className={`text-sm font-semibold ${isESMoreExpensive ? 'text-amber-900' : 'text-emerald-900'}`}>
                  {esRecommendation}
                </p>
              </div>
            </div>
          </div>
          
        </div>
      </Drawer>

      <PackageAiInsightModal 
        isOpen={aiModalOpen}
        onClose={() => setAiModalOpen(false)}
        pkg={pkg}
        esIndividualTotal={esIndividualTotal}
        formatPrice={formatPrice}
      />
    </>
  );
}
