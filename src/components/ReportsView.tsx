/**
 * Reports — Page 7
 * Generate and export pricing and competitive intelligence reports.
 */

import React, { useState } from "react";
import { TestItem, PackageItem, StatsData } from "../types";
import {
  FileBarChart,
  Download,
  FileText,
  FileSpreadsheet,
  CheckCircle2,
  Calendar,
  Filter,
} from "lucide-react";

interface ReportsViewProps {
  tests: TestItem[];
  packages: PackageItem[];
  stats: StatsData | null;
  formatPrice: (val: number | null) => string;
}

const REPORT_TYPES = [
  {
    id: "pricing_master",
    title: "Master Pricing Report",
    description: "Complete list of all tests, categories, and current ES Healthcare prices across all cities.",
    icon: FileText,
    color: "text-blue-600",
    bg: "bg-blue-50",
  },
  {
    id: "competitor_benchmarking",
    title: "Competitor Benchmarking",
    description: "Detailed comparison of ES prices vs Market Average and top competitors by city.",
    icon: FileBarChart,
    color: "text-purple-600",
    bg: "bg-purple-50",
  },
  {
    id: "package_intelligence",
    title: "Package Intelligence",
    description: "Analysis of health packages, bundle discounts, and value rankings.",
    icon: FileSpreadsheet,
    color: "text-emerald-600",
    bg: "bg-emerald-50",
  },
  {
    id: "overpriced_alerts",
    title: "Overpriced Tests Alert",
    description: "Targeted list of tests where ES Healthcare is priced >10% above the market average.",
    icon: FileText,
    color: "text-red-600",
    bg: "bg-red-50",
  },
];

export default function ReportsView({ tests, packages, stats, formatPrice }: ReportsViewProps) {
  const [selectedFormat, setSelectedFormat] = useState<"CSV" | "PDF" | "XLSX">("CSV");
  const [isGenerating, setIsGenerating] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleExport = (reportId: string, title: string) => {
    setIsGenerating(reportId);
    setSuccessMsg(null);
    
    // Simulate report generation delay
    setTimeout(() => {
      setIsGenerating(null);
      setSuccessMsg(`Successfully generated ${title} (${selectedFormat})`);
      
      // In a real app, we would actually trigger a file download here
      // For this demo, we just show the success message
      setTimeout(() => setSuccessMsg(null), 3000);
    }, 1500);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header Area */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 card-shadow flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="font-display text-xl font-bold text-slate-800">Intelligence Reports</h2>
          <p className="text-sm text-slate-500 mt-1">Generate and export data for offline analysis and management presentations.</p>
        </div>
        
        <div className="flex items-center gap-4 bg-slate-50 p-2 border border-slate-200 rounded-xl">
          <span className="text-xs font-semibold text-slate-500 pl-2 uppercase tracking-wider">Export As</span>
          <div className="flex bg-white rounded-lg border border-slate-200 p-1">
            {["CSV", "PDF", "XLSX"].map((format) => (
              <button
                key={format}
                onClick={() => setSelectedFormat(format as any)}
                className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
                  selectedFormat === format
                    ? "bg-primary text-white shadow-sm"
                    : "text-slate-500 hover:text-slate-700 hover:bg-slate-50"
                }`}
              >
                {format}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Success Toast */}
      {successMsg && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 px-4 py-3 rounded-xl flex items-center gap-3 animate-slideIn">
          <CheckCircle2 className="w-5 h-5 text-emerald-500" />
          <span className="text-sm font-medium">{successMsg}</span>
        </div>
      )}

      {/* Reports Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {REPORT_TYPES.map((report) => {
          const Icon = report.icon;
          const isProcessing = isGenerating === report.id;
          
          return (
            <div key={report.id} className="bg-white border border-slate-200 rounded-2xl p-6 card-shadow hover:shadow-md transition-all group flex flex-col">
              <div className="flex items-start gap-4 mb-4">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 transition-transform group-hover:scale-110 ${report.bg} ${report.color}`}>
                  <Icon className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-display font-bold text-lg text-slate-800 group-hover:text-primary transition-colors">{report.title}</h3>
                  <p className="text-sm text-slate-500 mt-1 leading-relaxed">{report.description}</p>
                </div>
              </div>
              
              <div className="mt-auto pt-4 border-t border-slate-100 flex items-center justify-between">
                <div className="flex gap-3">
                  <span className="flex items-center gap-1.5 text-xs text-slate-400 font-medium bg-slate-50 px-2 py-1 rounded-md border border-slate-100">
                    <Calendar className="w-3.5 h-3.5" /> {new Date().toLocaleDateString()}
                  </span>
                  <span className="flex items-center gap-1.5 text-xs text-slate-400 font-medium bg-slate-50 px-2 py-1 rounded-md border border-slate-100">
                    <Filter className="w-3.5 h-3.5" /> All Cities
                  </span>
                </div>
                
                <button
                  onClick={() => handleExport(report.id, report.title)}
                  disabled={isGenerating !== null}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all ${
                    isProcessing
                      ? "bg-primary-50 text-primary cursor-wait"
                      : "bg-white border border-slate-200 text-slate-700 hover:border-primary hover:text-primary hover:bg-primary-50"
                  }`}
                >
                  {isProcessing ? (
                    <>Generating... <span className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" /></>
                  ) : (
                    <>Generate {selectedFormat} <Download className="w-4 h-4" /></>
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>
      
      {/* Configuration Area */}
      <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 flex items-start gap-4">
         <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center flex-shrink-0">
           <Filter className="w-5 h-5 text-slate-500" />
         </div>
         <div>
           <h4 className="font-semibold text-slate-800 text-sm">Advanced Report Configuration</h4>
           <p className="text-xs text-slate-500 mt-1 max-w-2xl">
             By default, reports include data for all cities and categories. To generate a report for a specific region or test category, configure your filters on the Executive Dashboard first, then return here to export.
           </p>
         </div>
      </div>
    </div>
  );
}
