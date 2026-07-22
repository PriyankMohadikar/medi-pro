import React, { useEffect, useState, useRef } from "react";
import {
  Sparkles,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  Shield,
  Lightbulb,
  DollarSign,
  BarChart3,
  Package,
} from "lucide-react";
import Modal from "./ui/Modal";
import LoadingState from "./ui/LoadingState";
import ErrorState from "./ui/ErrorState";
import { sendChatMessage } from "../api";

interface PackageAiInsightModalProps {
  isOpen: boolean;
  onClose: () => void;
  pkg: any | null;
  esIndividualTotal: number;
  formatPrice: (val: number | null) => string;
}

interface AiInsightData {
  summary: string;
  recommendation: string;
  businessInsight: string;
  suggestedAction: string;
  riskLevel: "Low" | "Medium" | "High";
}

export default function PackageAiInsightModal({ isOpen, onClose, pkg, esIndividualTotal, formatPrice }: PackageAiInsightModalProps) {
  const [insight, setInsight] = useState<AiInsightData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (isOpen && pkg) {
      fetchInsight();
    }
    return () => {
      abortRef.current?.abort();
    };
  }, [isOpen, pkg, esIndividualTotal]);

  const fetchInsight = async () => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      setLoading(true);
      setError(null);
      setInsight(null);

      const savings = esIndividualTotal - pkg.package_price;
      const savingsPct = esIndividualTotal > 0 ? (savings / esIndividualTotal) * 100 : 0;

      const prompt = `Analyze this medical package pricing data and provide a structured insight.

Package Name: ${pkg.package_name}
Provider: ${pkg.provider_name}
City: ${pkg.city}
Package Price: ₹${pkg.package_price}
Number of Tests: ${pkg.test_count}
Tests Included: ${pkg.tests_included ? pkg.tests_included.join(", ") : "N/A"}

ES Healthcare Equivalent Individual Price: ₹${esIndividualTotal}
Difference (Savings vs ES Individual): ₹${savings} (${Math.round(savingsPct)}%)

Please respond with ONLY a JSON object (no markdown, no code blocks) with exactly these keys:
{
  "summary": "2-3 sentence AI summary of the package pricing situation and competitor strategy",
  "recommendation": "Specific pricing/product recommendation for ES Healthcare",
  "businessInsight": "Business insight about the market positioning of this package",
  "suggestedAction": "One-line recommended next action",
  "riskLevel": "Low or Medium or High"
}`;

      const response = await sendChatMessage(prompt, [], controller.signal);
      if (controller.signal.aborted) return;

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No response body");

      let fullText = "";
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        if (controller.signal.aborted) return;
        fullText += decoder.decode(value, { stream: true });
      }

      const parsed = parseAiResponse(fullText);
      setInsight(parsed);
    } catch (err: any) {
      if (err.name === "AbortError") return;
      console.error("AI Insight failed", err);
      setError(err.message || "Failed to get AI insight. Please try again.");
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false);
      }
    }
  };

  const parseAiResponse = (text: string): AiInsightData => {
    try {
      const cleaned = text.replace(/```json\s*/g, "").replace(/```\s*/g, "").trim();
      const jsonMatch = cleaned.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0]);
        return {
          summary: parsed.summary || "No summary available.",
          recommendation: parsed.recommendation || "No recommendation.",
          businessInsight: parsed.businessInsight || parsed.business_insight || "No business insight.",
          suggestedAction: parsed.suggestedAction || parsed.suggested_action || "Review package strategy.",
          riskLevel: (["Low", "Medium", "High"].includes(parsed.riskLevel || parsed.risk_level) ? (parsed.riskLevel || parsed.risk_level) : "Medium") as "Low" | "Medium" | "High",
        };
      }
    } catch {
      // Fall through to fallback
    }

    const savingsPct = esIndividualTotal > 0 ? ((esIndividualTotal - pkg.package_price) / esIndividualTotal) * 100 : 0;
    
    return {
      summary: text.slice(0, 300) || "AI analysis completed.",
      recommendation: savingsPct > 15 ? "Consider matching or beating this package price." : "Current individual pricing is competitive.",
      businessInsight: `This package offers ${Math.round(savingsPct)}% savings compared to individual testing.`,
      suggestedAction: "Monitor competitor package offerings.",
      riskLevel: savingsPct > 20 ? "High" : savingsPct > 5 ? "Medium" : "Low",
    };
  };

  if (!pkg) return null;

  const riskColors = {
    Low: { bg: "bg-emerald-50", text: "text-emerald-700", border: "border-emerald-200", icon: Shield },
    Medium: { bg: "bg-yellow-50", text: "text-yellow-700", border: "border-yellow-200", icon: AlertTriangle },
    High: { bg: "bg-red-50", text: "text-red-700", border: "border-red-200", icon: AlertTriangle },
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="AI Package Insight"
      subtitle={`${pkg.package_name} — ${pkg.provider_name}`}
      maxWidth="max-w-[640px]"
      footer={
        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 bg-slate-800 text-white rounded-xl text-sm font-bold hover:bg-slate-700 transition-colors shadow-sm"
          >
            Close
          </button>
        </div>
      }
    >
      <div className="p-6">
        {loading ? (
          <div className="space-y-4">
            <div className="flex items-center gap-3 p-4 bg-primary/5 border border-primary/20 rounded-xl">
              <Sparkles className="w-5 h-5 text-primary animate-pulse" />
              <div>
                <p className="text-sm font-bold text-slate-800">Analyzing package strategy...</p>
                <p className="text-xs text-slate-500 mt-0.5">AI is reviewing the package value and competitor pricing</p>
              </div>
            </div>
            <LoadingState message="Generating insight..." rows={4} />
          </div>
        ) : error ? (
          <ErrorState message={error} onRetry={fetchInsight} />
        ) : insight ? (
          <div className="space-y-5">
            <div className="p-5 bg-gradient-to-br from-primary/5 to-purple-50/50 border border-primary/15 rounded-2xl">
              <div className="flex items-start gap-3">
                <div className="w-9 h-9 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-primary uppercase tracking-wider mb-2">AI Summary</h3>
                  <p className="text-sm text-slate-700 leading-relaxed">{insight.summary}</p>
                </div>
              </div>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-100 rounded-xl">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-slate-200/60 flex items-center justify-center flex-shrink-0">
                  <Package className="w-4 h-4 text-slate-600" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Product Recommendation</h3>
                  <p className="text-sm font-semibold text-slate-800">{insight.recommendation}</p>
                </div>
              </div>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-100 rounded-xl">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-slate-200/60 flex items-center justify-center flex-shrink-0">
                  <Lightbulb className="w-4 h-4 text-slate-600" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Business Insight</h3>
                  <p className="text-sm font-semibold text-slate-800">{insight.businessInsight}</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className={`col-span-2 p-4 ${riskColors[insight.riskLevel].bg} border ${riskColors[insight.riskLevel].border} rounded-xl`}>
                <div className="flex items-start gap-3">
                  <div className={`w-8 h-8 rounded-lg bg-white/60 flex items-center justify-center flex-shrink-0`}>
                    {React.createElement(riskColors[insight.riskLevel].icon, {
                      className: `w-4 h-4 ${riskColors[insight.riskLevel].text}`,
                    })}
                  </div>
                  <div>
                    <h3 className={`text-xs font-bold ${riskColors[insight.riskLevel].text} uppercase tracking-wider mb-1`}>Competitive Threat Level</h3>
                    <p className={`text-lg font-black ${riskColors[insight.riskLevel].text}`}>{insight.riskLevel}</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="p-4 bg-slate-800 text-white rounded-xl">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center flex-shrink-0">
                  <BarChart3 className="w-4 h-4 text-white" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Recommended Action</h3>
                  <p className="text-sm font-semibold">{insight.suggestedAction}</p>
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </Modal>
  );
}
