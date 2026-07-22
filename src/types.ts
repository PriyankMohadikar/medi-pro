/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

// ── Test pricing row from PostgreSQL ──────────────────────────
export interface TestItem {
  pricing_id: number;
  test_name: string;
  category: string;
  price: number | null;
  provider_name: string;
  provider_type: string;
  city: string;
}

// ── Package from PostgreSQL ───────────────────────────────────
export interface PackageItem {
  package_id: number;
  package_name: string;
  package_price: number | null;
  provider_name: string;
  provider_type: string;
  city: string;
  tests_included: string[];
}

// ── Provider from PostgreSQL ──────────────────────────────────
export interface ProviderItem {
  provider_id: number;
  provider_name: string;
  provider_type: string;
  city: string;
}

// ── Dashboard stats from /api/stats ───────────────────────────
export interface StatsData {
  total_tests: number;
  total_providers: number;
  total_packages: number;
  average_price: number;
  cities: string[];
  categories: string[];
  test_names?: string[];
}

// ── Chat message (AI Assistant) ───────────────────────────────
export interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  text: string;
  timestamp: string;
  visualization?: {
    type: "comparison" | "suggestion" | "trends";
    data?: any;
  };
}

// ── Custom Package (user-created) ─────────────────────────────
export interface CustomPackageTestData {
  id?: number;
  test_name: string;
  individual_price: number | null;
  display_order?: number;
}

export interface CustomPackageData {
  package_id: number;
  package_name: string;
  total_tests: number;
  individual_total_price: number | null;
  discount_percentage: number | null;
  suggested_package_price: number | null;
  market_average_price: number | null;
  expected_customer_savings: number | null;
  created_at: string | null;
  updated_at: string | null;
  tests: CustomPackageTestData[];
}

// ── Navigation ────────────────────────────────────────────────
export type ActiveScreen =
  | "dashboard"
  | "test-pricing"
  | "package-intelligence"
  | "competitor-intelligence"
  | "custom-package-builder"
  | "create-package"
  | "saved-packages"
  | "ai-assistant"
  | "reports"
  | "settings";

// ── Pricing Status ────────────────────────────────────────────
export type PricingStatus = "Competitive" | "Needs Review" | "Overpriced";

// ── Test Analysis (computed on client) ────────────────────────
export interface TestAnalysis {
  test_name: string;
  category: string;
  city: string;
  es_price: number | null;
  lowest_price: number | null;
  highest_price: number | null;
  market_average: number | null;
  difference_pct: number | null;
  status: PricingStatus;
  recommendation: string;
}

// ── Competitor Ranking ────────────────────────────────────────
export interface CompetitorRanking {
  provider_name: string;
  avg_price: number;
  cities_covered: string[];
  test_count: number;
  diff_vs_es: number | null;
  market_position: string;
}

// ── (FilterState is defined in hooks/useFilters.ts) ──────────

// ── ES Provider Name Constant ─────────────────────────────────
export const ES_PROVIDER_NAME = "ES Healthcare";
