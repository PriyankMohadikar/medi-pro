import React, { useEffect, useState, useRef } from "react";
import { TrendingUp, TrendingDown, Award, AlertTriangle } from "lucide-react";
import Modal from "./ui/Modal";
import LoadingState from "./ui/LoadingState";
import ErrorState from "./ui/ErrorState";
import { fetchTests } from "../api";

interface CompareProvidersModalProps {
  isOpen: boolean;
  onClose: () => void;
  test: any | null;
  formatPrice: (val: number | null) => string;
}

export default function CompareProvidersModal({ isOpen, onClose, test, formatPrice }: CompareProvidersModalProps) {
  const [providers, setProviders] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (isOpen && test) {
      loadProviders();
    }
    return () => {
      abortRef.current?.abort();
    };
  }, [isOpen, test]);

  const loadProviders = async () => {
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
          t.price !== null
      );

      // Sort by price ascending
      comps.sort((a: any, b: any) => a.price - b.price);

      const esPrice = test.es_price;
      const mapped = comps.map((c: any, index: number) => {
        const diff = esPrice > 0 ? ((c.price - esPrice) / esPrice) * 100 : 0;
        return {
          ...c,
          rank: index + 1,
          diff_from_es: diff,
          is_lowest: index === 0,
          is_highest: index === comps.length - 1,
          is_es: c.provider_name === "ES Healthcare",
        };
      });

      setProviders(mapped);
    } catch (err: any) {
      if (err.name === "AbortError") return;
      console.error("Failed to load providers for comparison", err);
      setError("Failed to load provider data. Please try again.");
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false);
      }
    }
  };

  if (!test) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`Compare Providers: ${test.test_name}`}
      subtitle={`City: ${test.city}  •  Market Average: ${formatPrice(test.market_average)}`}
      footer={
        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 bg-white border border-slate-200 rounded-xl text-sm font-bold text-slate-600 hover:bg-slate-50 hover:text-slate-800 transition-colors shadow-sm"
          >
            Close
          </button>
        </div>
      }
    >
      <div className="p-6">
        {loading ? (
          <LoadingState message="Loading providers..." rows={5} />
        ) : error ? (
          <ErrorState message={error} onRetry={loadProviders} />
        ) : providers.length === 0 ? (
          <div className="text-center p-10 bg-slate-50 rounded-xl border border-slate-100">
            <p className="text-sm text-slate-500 font-medium">No provider data found.</p>
          </div>
        ) : (
          <div className="border border-slate-200 rounded-xl overflow-hidden">
            <table className="w-full text-left border-collapse">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-4 py-3 text-[11px] font-bold text-slate-500 uppercase tracking-wider">Rank</th>
                  <th className="px-4 py-3 text-[11px] font-bold text-slate-500 uppercase tracking-wider">Provider</th>
                  <th className="px-4 py-3 text-[11px] font-bold text-slate-500 uppercase tracking-wider">Price</th>
                  <th className="px-4 py-3 text-[11px] font-bold text-slate-500 uppercase tracking-wider">Difference</th>
                  <th className="px-4 py-3 text-[11px] font-bold text-slate-500 uppercase tracking-wider text-right">Highlight</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-sm">
                {providers.map((p) => (
                  <tr
                    key={`${p.provider_name}-${p.price}`}
                    className={`transition-colors ${
                      p.is_es
                        ? "bg-primary/5 border-l-4 border-l-primary"
                        : p.is_lowest
                        ? "bg-emerald-50/30 hover:bg-emerald-50/50"
                        : p.is_highest
                        ? "bg-red-50/30 hover:bg-red-50/50"
                        : "hover:bg-slate-50/50"
                    }`}
                  >
                    <td className="px-4 py-3.5 font-bold text-slate-400">#{p.rank}</td>
                    <td className="px-4 py-3.5">
                      <p className={`font-bold text-[13px] ${p.is_es ? "text-primary" : "text-slate-700"}`}>
                        {p.provider_name}
                      </p>
                    </td>
                    <td className="px-4 py-3.5 font-bold text-slate-800">{formatPrice(p.price)}</td>
                    <td className="px-4 py-3.5">
                      {p.is_es ? (
                        <span className="text-xs font-semibold text-slate-400">—</span>
                      ) : (
                        <span
                          className={`text-xs font-bold inline-flex items-center gap-1 ${
                            p.diff_from_es > 0
                              ? "text-red-500"
                              : p.diff_from_es < 0
                              ? "text-emerald-500"
                              : "text-slate-500"
                          }`}
                        >
                          {p.diff_from_es > 0 ? "+" : ""}
                          {Math.round(p.diff_from_es)}%
                          {p.diff_from_es > 0 ? (
                            <TrendingUp className="w-3 h-3" />
                          ) : p.diff_from_es < 0 ? (
                            <TrendingDown className="w-3 h-3" />
                          ) : null}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3.5 text-right">
                      {p.is_lowest && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold bg-emerald-100 text-emerald-700 px-2 py-1 rounded-md uppercase tracking-wider">
                          <Award className="w-3 h-3" /> Lowest
                        </span>
                      )}
                      {p.is_highest && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold bg-red-100 text-red-700 px-2 py-1 rounded-md uppercase tracking-wider">
                          <AlertTriangle className="w-3 h-3" /> Highest
                        </span>
                      )}
                      {p.is_es && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-bold bg-primary text-white px-2 py-1 rounded-md uppercase tracking-wider">
                          ES Healthcare
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Modal>
  );
}
