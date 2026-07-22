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
} from "lucide-react";
import Modal from "./ui/Modal";
import LoadingState from "./ui/LoadingState";
import ErrorState from "./ui/ErrorState";
import { sendChatMessage } from "../api";

interface AiInsightModalProps {
  isOpen: boolean;
  onClose: () => void;
  test: any | null;
  formatPrice: (val: number | null) => string;
}

interface AiInsightData {
  summary: string;
  recommendation: string;
  businessInsight: string;
  suggestedPrice: string;
  riskLevel: "Low" | "Medium" | "High";
  action: string;
}

export default function AiInsightModal({ isOpen, onClose, test, formatPrice }: AiInsightModalProps) {
  const [insight, setInsight] = useState<AiInsightData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    if (isOpen && test) {
      fetchInsight();
    }
    return () => {
      abortRef.current?.abort();
    };
  }, [isOpen, test]);

  const fetchInsight = async () => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      setLoading(true);
      setError(null);
      setInsight(null);

      const prompt = `Analyze this medical test pricing data and provide a structured insight.

Test: ${test.test_name}
Category: ${test.category}
City: ${test.city}
ES Healthcare Price: ₹${test.es_price}
Market Average: ₹${test.market_average}
Lowest Price: ₹${test.lowest_price}
Highest Price: ₹${test.highest_price}
Difference: ${test.difference_pct}%
Status: ${test.status}
Current Recommendation: ${test.recommendation}

Please respond with ONLY a JSON object (no markdown, no code blocks) with exactly these keys:
{
  "summary": "2-3 sentence AI summary of the pricing situation",
  "recommendation": "Specific pricing recommendation",
  "businessInsight": "Business insight about market positioning",
  "suggestedPrice": "Suggested optimal price as a number with ₹ symbol",
  "riskLevel": "Low or Medium or High",
  "action": "One-line recommended next action"
}`;

      const response = await sendChatMessage(prompt, [], controller.signal);
      if (controller.signal.aborted) return;

      // Read the streaming response
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

      // Try to parse JSON from the response
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

  /**
   * Parse AI response — attempts to extract JSON from the text.
   * Falls back to a structured response using the raw text.
   */
  const parseAiResponse = (text: string): AiInsightData => {
    // Try to extract JSON from the response
    try {
      // Remove markdown code block wrappers if present
      const cleaned = text.replace(/```json\s*/g, "").replace(/```\s*/g, "").trim();
      const jsonMatch = cleaned.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0]);
        return {
          summary: parsed.summary || "No summary available.",
          recommendation: parsed.recommendation || "No recommendation.",
          businessInsight: parsed.businessInsight || parsed.business_insight || "No business insight.",
          suggestedPrice: parsed.suggestedPrice || parsed.suggested_price || "N/A",
          riskLevel: (["Low", "Medium", "High"].includes(parsed.riskLevel || parsed.risk_level) ? (parsed.riskLevel || parsed.risk_level) : "Medium") as "Low" | "Medium" | "High",
          action: parsed.action || "Review pricing strategy.",
        };
      }
    } catch {
      // JSON parsing failed, fall through to fallback
    }

    // Fallback: use the raw text as summary
    return {
      summary: text.slice(0, 300) || "AI analysis completed.",
      recommendation: test.recommendation || "Review pricing strategy.",
      businessInsight: `ES Healthcare price is ${test.difference_pct > 0 ? "above" : "below"} market average by ${Math.abs(test.difference_pct)}%.`,
      suggestedPrice: formatPrice(Math.round(test.market_average)),
      riskLevel: Math.abs(test.difference_pct) > 15 ? "High" : Math.abs(test.difference_pct) > 5 ? "Medium" : "Low",
      action: test.recommendation,
    };
  };

  if (!test) return null;

  const riskColors = {
    Low: { bg: "bg-emerald-50", text: "text-emerald-700", border: "border-emerald-200", icon: Shield },
    Medium: { bg: "bg-yellow-50", text: "text-yellow-700", border: "border-yellow-200", icon: AlertTriangle },
    High: { bg: "bg-red-50", text: "text-red-700", border: "border-red-200", icon: AlertTriangle },
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="AI Pricing Insight"
      subtitle={`${test.test_name} — ${test.city}`}
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
                <p className="text-sm font-bold text-slate-800">Analyzing pricing data...</p>
                <p className="text-xs text-slate-500 mt-0.5">AI is reviewing market data and competitor pricing</p>
              </div>
            </div>
            <LoadingState message="Generating insight..." rows={4} />
          </div>
        ) : error ? (
          <ErrorState message={error} onRetry={fetchInsight} />
        ) : insight ? (
          <div className="space-y-5">
            {/* AI Summary */}
            <div className="p-5 bg-gradient-to-br from-primary/5 to-blue-50/50 border border-primary/15 rounded-2xl">
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

            {/* Pricing Recommendation */}
            <div className="p-4 bg-slate-50 border border-slate-100 rounded-xl">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-slate-200/60 flex items-center justify-center flex-shrink-0">
                  <TrendingUp className="w-4 h-4 text-slate-600" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Pricing Recommendation</h3>
                  <p className="text-sm font-semibold text-slate-800">{insight.recommendation}</p>
                </div>
              </div>
            </div>

            {/* Business Insight */}
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

            {/* Suggested Price + Risk Level */}
            <div className="grid grid-cols-2 gap-3">
              <div className="p-4 bg-slate-50 border border-slate-100 rounded-xl">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-slate-200/60 flex items-center justify-center flex-shrink-0">
                    <DollarSign className="w-4 h-4 text-slate-600" />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-1">Suggested Price</h3>
                    <p className="text-lg font-black text-slate-800">{insight.suggestedPrice}</p>
                  </div>
                </div>
              </div>

              <div className={`p-4 ${riskColors[insight.riskLevel].bg} border ${riskColors[insight.riskLevel].border} rounded-xl`}>
                <div className="flex items-start gap-3">
                  <div className={`w-8 h-8 rounded-lg bg-white/60 flex items-center justify-center flex-shrink-0`}>
                    {React.createElement(riskColors[insight.riskLevel].icon, {
                      className: `w-4 h-4 ${riskColors[insight.riskLevel].text}`,
                    })}
                  </div>
                  <div>
                    <h3 className={`text-xs font-bold ${riskColors[insight.riskLevel].text} uppercase tracking-wider mb-1`}>Risk Level</h3>
                    <p className={`text-lg font-black ${riskColors[insight.riskLevel].text}`}>{insight.riskLevel}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Recommended Action */}
            <div className="p-4 bg-slate-800 text-white rounded-xl">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center flex-shrink-0">
                  <BarChart3 className="w-4 h-4 text-white" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Recommended Action</h3>
                  <p className="text-sm font-semibold">{insight.action}</p>
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </Modal>
  );
}
