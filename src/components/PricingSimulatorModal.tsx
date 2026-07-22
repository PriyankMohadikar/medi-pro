import React, { useState, useEffect, useRef, useCallback } from "react";
import {
  TrendingUp,
  TrendingDown,
  Target,
  Activity,
  RotateCcw,
  Check,
  ArrowDown,
  ArrowUp,
  Minus,
} from "lucide-react";
import Modal from "./ui/Modal";
import StatusBadge from "./ui/StatusBadge";
import LoadingState from "./ui/LoadingState";
import ErrorState from "./ui/ErrorState";
import { fetchTests } from "../api";

interface PricingSimulatorModalProps {
  isOpen: boolean;
  onClose: () => void;
  test: any | null;
  formatPrice: (val: number | null) => string;
}

export default function PricingSimulatorModal({ isOpen, onClose, test, formatPrice }: PricingSimulatorModalProps) {
  const [simulatedPrice, setSimulatedPrice] = useState<number>(0);
  const [competitors, setCompetitors] = useState<number[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (isOpen && test) {
      setSimulatedPrice(test.es_price || 0);
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
      setCompetitors(comps.map((c: any) => c.price));
    } catch (err: any) {
      if (err.name === "AbortError") return;
      console.error("Failed to load competitors", err);
      setError("Failed to load market data.");
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false);
      }
    }
  };

  const handleSliderChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSimulatedPrice(Number(e.target.value));
  }, []);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseInt(e.target.value, 10);
    if (!isNaN(val) && val >= 0) {
      setSimulatedPrice(val);
    }
  }, []);

  const handleReset = useCallback(() => {
    setSimulatedPrice(test?.es_price || 0);
  }, [test]);

  if (!test) return null;

  // ── Computed simulation metrics ─────────────────────
  const marketAvg = competitors.length > 0 ? competitors.reduce((s, p) => s + p, 0) / competitors.length : 0;
  const diffPct = marketAvg > 0 ? ((simulatedPrice - marketAvg) / marketAvg) * 100 : 0;
  const roundedDiff = Math.round(diffPct * 10) / 10;

  // Rank among all prices
  const allPrices = [...competitors, simulatedPrice].sort((a, b) => a - b);
  const rank = allPrices.indexOf(simulatedPrice) + 1;
  const totalProviders = allPrices.length;

  // Status
  let simStatus = "Competitive";
  if (diffPct > 15) simStatus = "Overpriced";
  else if (diffPct > 5) simStatus = "Needs Review";
  else if (diffPct < -10) simStatus = "Underpriced";

  // Recommendation
  let simRecommendation = "Maintain Current Price";
  if (diffPct > 25) simRecommendation = "Review Immediately";
  else if (diffPct > 15) simRecommendation = "Reduce Price";
  else if (diffPct > 5) simRecommendation = "Monitor Competitors";
  else if (diffPct < -20) simRecommendation = simulatedPrice < Math.min(...competitors) ? "Price Leader" : "Increase Price";
  else if (diffPct < -5) simRecommendation = "Highly Competitive";

  // Projected savings (difference from current price)
  const projectedSavings = simulatedPrice - test.es_price;

  // Slider range
  const minMarket = Math.min(...competitors, test.es_price);
  const maxMarket = Math.max(...competitors, test.es_price);
  const sliderMin = Math.max(0, Math.floor(minMarket * 0.3));
  const sliderMax = Math.ceil(maxMarket * 2);



  // ── Metric card helper ──────────────────────────────
  const MetricCard = ({ label, children, className = "" }: { label: string; children: React.ReactNode; className?: string }) => (
    <div className={`p-4 bg-slate-50 rounded-xl border border-slate-100 ${className}`}>
      <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2">{label}</p>
      <div>{children}</div>
    </div>
  );

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Pricing Simulator"
      subtitle={`${test.test_name} — ${test.city}`}
      maxWidth="max-w-[640px]"
      footer={
        <div className="flex items-center justify-between">
          <p className="text-xs text-slate-400 italic font-medium">
            Simulation only — database is not updated.
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={handleReset}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-white border border-slate-200 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-50 hover:text-slate-800 transition-colors shadow-sm"
            >
              <RotateCcw className="w-3.5 h-3.5" /> Reset
            </button>
            <button
              onClick={onClose}
              className="inline-flex items-center gap-1.5 px-5 py-2 bg-slate-800 text-white rounded-xl text-xs font-bold hover:bg-slate-700 transition-colors shadow-sm"
            >
              <Check className="w-3.5 h-3.5" /> Apply Simulation
            </button>
          </div>
        </div>
      }
    >
      <div className="p-6 space-y-6">
        {loading ? (
          <LoadingState message="Loading market data..." rows={3} />
        ) : error ? (
          <ErrorState message={error} onRetry={loadCompetitors} />
        ) : (
          <>
            {/* ── Current ES Price ─────────────────── */}
            <div className="bg-white border border-slate-200 rounded-2xl p-5">
              <div className="flex items-center justify-between mb-1">
                <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">Current ES Healthcare Price</p>
                <span className="text-xs font-semibold text-slate-400 line-through">{formatPrice(test.es_price)}</span>
              </div>
              <p className="text-3xl font-black text-slate-800 mb-0.5">{formatPrice(test.es_price)}</p>
            </div>

            {/* ── Simulation Controls ──────────────── */}
            <div className="bg-primary/5 border border-primary/20 rounded-2xl p-5 space-y-4">
              <div className="flex items-end justify-between">
                <div>
                  <label className="text-xs font-bold text-primary uppercase tracking-wider block mb-1">
                    Simulated Price
                  </label>
                  <div className="flex items-center gap-1.5">
                    <span className="text-2xl font-bold text-slate-800">₹</span>
                    <input
                      type="number"
                      value={simulatedPrice}
                      onChange={handleInputChange}
                      min={0}
                      className="w-28 text-2xl font-bold bg-transparent border-b-2 border-primary/30 focus:border-primary outline-none py-1 text-slate-800"
                    />
                  </div>
                </div>
                <div className="text-right">
                  {projectedSavings !== 0 && (
                    <div className={`inline-flex items-center gap-1 text-xs font-bold px-2 py-1 rounded-md ${
                      projectedSavings > 0 ? "bg-red-100 text-red-700" : "bg-emerald-100 text-emerald-700"
                    }`}>
                      {projectedSavings > 0 ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />}
                      {projectedSavings > 0 ? "+" : ""}{formatPrice(projectedSavings)}
                    </div>
                  )}
                </div>
              </div>

              <div>
                <input
                  type="range"
                  min={sliderMin}
                  max={sliderMax}
                  value={simulatedPrice}
                  onChange={handleSliderChange}
                  className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-primary"
                />
                <div className="flex justify-between text-[10px] font-medium text-slate-400 mt-1.5">
                  <span>{formatPrice(sliderMin)}</span>
                  <span className="text-primary font-bold">Market Avg: {formatPrice(Math.round(marketAvg))}</span>
                  <span>{formatPrice(sliderMax)}</span>
                </div>
              </div>
            </div>

            {/* ── Projected Impact ─────────────────── */}
            <div>
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                <Activity className="w-4 h-4" /> Projected Impact
              </h3>

              <div className="space-y-3">
                {/* Row 1: Simulated Price + Market Average */}
                <div className="grid grid-cols-2 gap-3">
                  <MetricCard label="Simulated Price">
                    <p className="text-xl font-black text-slate-800">{formatPrice(simulatedPrice)}</p>
                  </MetricCard>
                  <MetricCard label="Market Average">
                    <p className="text-xl font-bold text-slate-600">{formatPrice(Math.round(marketAvg))}</p>
                  </MetricCard>
                </div>

                {/* Row 2: Difference % + Competitive Status */}
                <div className="grid grid-cols-2 gap-3">
                  <MetricCard label="Difference %">
                    <div className="flex items-center gap-1.5">
                      {roundedDiff > 0 ? (
                        <TrendingUp className="w-5 h-5 text-red-500" />
                      ) : roundedDiff < 0 ? (
                        <TrendingDown className="w-5 h-5 text-emerald-500" />
                      ) : (
                        <Minus className="w-5 h-5 text-slate-400" />
                      )}
                      <p className={`text-xl font-black ${roundedDiff > 0 ? "text-red-600" : roundedDiff < 0 ? "text-emerald-600" : "text-slate-600"}`}>
                        {roundedDiff > 0 ? "+" : ""}{roundedDiff}%
                      </p>
                    </div>
                  </MetricCard>
                  <MetricCard label="Competitive Status">
                    <StatusBadge status={simStatus} />
                  </MetricCard>
                </div>

                {/* Row 3: Expected Recommendation (full width) */}
                <MetricCard label="Expected Recommendation">
                  <p className="text-sm font-bold text-slate-800">{simRecommendation}</p>
                </MetricCard>

                {/* Row 4: Market Ranking + Projected Savings */}
                <div className="grid grid-cols-2 gap-3">
                  <MetricCard label="Market Ranking">
                    <div className="flex items-center gap-2">
                      <Target className="w-5 h-5 text-primary" />
                      <p className="text-lg font-bold text-slate-800">
                        #{rank} <span className="text-xs font-semibold text-slate-400">of {totalProviders}</span>
                      </p>
                    </div>
                  </MetricCard>
                  <MetricCard label="Projected Savings">
                    <p className={`text-lg font-bold ${projectedSavings > 0 ? "text-red-600" : projectedSavings < 0 ? "text-emerald-600" : "text-slate-500"}`}>
                      {projectedSavings > 0 ? "+" : ""}{formatPrice(projectedSavings)}
                      <span className="text-xs font-semibold text-slate-400 ml-1">vs current</span>
                    </p>
                  </MetricCard>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </Modal>
  );
}
