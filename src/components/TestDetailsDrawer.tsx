import React, { useEffect, useState, useRef } from "react";
import { TrendingUp, TrendingDown, Activity, MapPin, Tag } from "lucide-react";
import Drawer from "./ui/Drawer";
import StatusBadge from "./ui/StatusBadge";
import LoadingState from "./ui/LoadingState";
import ErrorState from "./ui/ErrorState";
import { fetchTests } from "../api";

interface TestDetailsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  test: any | null;
  formatPrice: (val: number | null) => string;
}

export default function TestDetailsDrawer({ isOpen, onClose, test, formatPrice }: TestDetailsDrawerProps) {
  const [competitors, setCompetitors] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (isOpen && test) {
      loadCompetitors();
    }
    return () => {
      abortRef.current?.abort();
    };
  }, [isOpen, test]);

  const loadCompetitors = async () => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      setLoading(true);
      setError(null);
      const allTests = await fetchTests({ city: test.city });
      if (controller.signal.aborted) return;

      const comps = allTests.filter(
        (t: any) =>
          t.test_name.toLowerCase() === test.test_name.toLowerCase() &&
          t.provider_name !== "ES Healthcare" &&
          t.price !== null
      );
      comps.sort((a: any, b: any) => a.price - b.price);
      setCompetitors(comps);
    } catch (err: any) {
      if (err.name === "AbortError") return;
      console.error("Failed to load competitors", err);
      setError("Failed to load competitor data. Please try again.");
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false);
      }
    }
  };

  if (!test) return null;

  const isOverpriced = test.difference_pct > 0;

  // ── Detail row helper ───────────────────────────────
  const DetailRow = ({ label, value, className = "" }: { label: string; value: React.ReactNode; className?: string }) => (
    <div className="flex items-center justify-between py-2.5 border-b border-slate-50 last:border-0">
      <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{label}</span>
      <span className={`text-sm font-bold ${className}`}>{value}</span>
    </div>
  );

  const subtitle = (
    <div className="flex items-center gap-3 text-xs font-medium text-slate-500">
      <span className="flex items-center gap-1"><Tag className="w-3.5 h-3.5" /> {test.category}</span>
      <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" /> {test.city}</span>
    </div>
  );

  return (
    <Drawer
      isOpen={isOpen}
      onClose={onClose}
      title={test.test_name}
      subtitle={subtitle}
      footer={
        <button
          onClick={onClose}
          className="w-full py-2.5 bg-white border border-slate-200 rounded-xl text-sm font-bold text-slate-600 hover:bg-slate-50 hover:text-slate-800 transition-colors shadow-sm"
        >
          Close Details
        </button>
      }
    >
      <div className="p-6 space-y-8">
        {/* ── Status & Recommendation ──────────────── */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider">Pricing Status</h3>
            <StatusBadge status={test.status} />
          </div>

          <div
            className={`p-4 rounded-xl border ${
              test.status === "Overpriced"
                ? "bg-red-50/50 border-red-100 text-red-800"
                : test.status === "Needs Review"
                ? "bg-yellow-50/50 border-yellow-100 text-yellow-800"
                : test.status === "Underpriced"
                ? "bg-blue-50/50 border-blue-100 text-blue-800"
                : "bg-emerald-50/50 border-emerald-100 text-emerald-800"
            }`}
          >
            <div className="flex items-start gap-3">
              <Activity className="w-5 h-5 mt-0.5 flex-shrink-0" />
              <div>
                <h4 className="font-bold text-sm">Recommendation: {test.recommendation}</h4>
                <p className="text-xs mt-1 opacity-80">
                  Based on market analysis, ES Healthcare price is {Math.abs(test.difference_pct)}%{" "}
                  {isOverpriced ? "higher" : "lower"} than the market average in {test.city}.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* ── Market Metrics ───────────────────────── */}
        <div>
          <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4">Market Metrics</h3>
          <div className="bg-slate-50/70 rounded-xl border border-slate-100 px-5 py-2">
            <DetailRow label="ES Healthcare Price" value={formatPrice(test.es_price)} className="text-slate-800" />
            <DetailRow label="Lowest Competitor" value={formatPrice(test.lowest_price)} className="text-emerald-600" />
            <DetailRow label="Highest Competitor" value={formatPrice(test.highest_price)} className="text-red-600" />
            <DetailRow label="Market Average" value={formatPrice(test.market_average)} className="text-slate-600" />
            <DetailRow
              label="Difference %"
              value={
                <span className={`inline-flex items-center gap-1 ${isOverpriced ? "text-red-600" : "text-emerald-600"}`}>
                  {isOverpriced ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                  {isOverpriced ? "+" : ""}
                  {test.difference_pct}%
                </span>
              }
            />
            <DetailRow label="Status" value={<StatusBadge status={test.status} />} />
            <DetailRow label="Recommendation" value={test.recommendation} className="text-slate-700" />
          </div>
        </div>

        {/* ── Competitor List ──────────────────────── */}
        <div>
          <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-4 flex justify-between items-center">
            Competitor Prices
            {!loading && (
              <span className="text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full font-semibold">
                {competitors.length} Found
              </span>
            )}
          </h3>

          {loading ? (
            <LoadingState message="Loading competitors..." rows={3} />
          ) : error ? (
            <ErrorState message={error} onRetry={loadCompetitors} />
          ) : competitors.length === 0 ? (
            <div className="text-center p-6 bg-slate-50 border border-slate-100 rounded-xl">
              <p className="text-sm text-slate-500 font-medium">No competitor data found in {test.city}.</p>
            </div>
          ) : (
            <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1 custom-scrollbar">
              {competitors.map((comp, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-white border border-slate-100 rounded-lg hover:border-slate-200 transition-colors shadow-sm"
                >
                  <div>
                    <p className="text-[13px] font-bold text-slate-700">{comp.provider_name}</p>
                    <p className="text-[10px] text-slate-400 font-medium">{comp.provider_type || "Diagnostic Lab"}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-slate-800">{formatPrice(comp.price)}</p>
                    {comp.price < test.es_price && (
                      <p className="text-[10px] font-bold text-red-500">Cheaper</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Drawer>
  );
}
