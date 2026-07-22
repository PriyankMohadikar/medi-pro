/**
 * API service layer for MediPrice Pro.
 * All fetch calls to the FastAPI backend (/api/*).
 * Vite proxy forwards these to http://localhost:8000.
 */

import type { TestItem, PackageItem, ProviderItem, StatsData, CustomPackageData } from "./types";

const API_BASE = "/api";

// ── Test Pricing ──────────────────────────────────────────────
export async function fetchTests(filters?: {
  city?: string;
  provider?: string;
  category?: string;
}): Promise<TestItem[]> {
  const params = new URLSearchParams();
  if (filters?.city) params.set("city", filters.city);
  if (filters?.provider) params.set("provider", filters.provider);
  if (filters?.category) params.set("category", filters.category);

  const url = `${API_BASE}/tests${params.toString() ? `?${params}` : ""}`;
  const res = await fetch(url, { headers: { 'Cache-Control': 'no-cache' } });
  if (!res.ok) throw new Error("Failed to fetch tests");
  return res.json();
}

export async function fetchAnalyzedTests(filters?: {
  city?: string;
  category?: string;
  search?: string;
  status?: string;
  recommendation?: string;
  sort_by?: string;
  sort_dir?: string;
  page?: number;
  page_size?: number;
}, signal?: AbortSignal): Promise<any> {
  const params = new URLSearchParams();
  if (filters?.city) params.set("city", filters.city);
  if (filters?.category) params.set("category", filters.category);
  if (filters?.search) params.set("search", filters.search);
  if (filters?.status) params.set("status", filters.status);
  if (filters?.recommendation) params.set("recommendation", filters.recommendation);
  if (filters?.sort_by) params.set("sort_by", filters.sort_by);
  if (filters?.sort_dir) params.set("sort_dir", filters.sort_dir);
  if (filters?.page) params.set("page", filters.page.toString());
  if (filters?.page_size) params.set("page_size", filters.page_size.toString());

  const url = `${API_BASE}/analyzed-tests${params.toString() ? `?${params}` : ""}`;
  const res = await fetch(url, { 
    headers: { 'Cache-Control': 'no-cache' },
    signal
  });
  if (!res.ok) throw new Error("Failed to fetch analyzed tests");
  return res.json();
}

export async function exportAnalyzedTests(filters?: {
  city?: string;
  category?: string;
  status?: string;
  recommendation?: string;
  search?: string;
}): Promise<any> {
  const params = new URLSearchParams();
  if (filters?.city) params.set("city", filters.city);
  if (filters?.category) params.set("category", filters.category);
  if (filters?.status) params.set("status", filters.status);
  if (filters?.recommendation) params.set("recommendation", filters.recommendation);
  if (filters?.search) params.set("search", filters.search);

  const url = `${API_BASE}/export-analyzed-tests${params.toString() ? `?${params}` : ""}`;
  const res = await fetch(url, { headers: { 'Cache-Control': 'no-cache' } });
  if (!res.ok) throw new Error("Failed to export analyzed tests");
  return res.json();
}

// ── Packages ──────────────────────────────────────────────────
export async function fetchPackages(filters?: {
  city?: string;
  provider?: string;
}): Promise<PackageItem[]> {
  const params = new URLSearchParams();
  if (filters?.city) params.set("city", filters.city);
  if (filters?.provider) params.set("provider", filters.provider);

  const url = `${API_BASE}/packages${params.toString() ? `?${params}` : ""}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch packages");
  return res.json();
}

// ── Providers ─────────────────────────────────────────────────
export async function fetchProviders(city?: string): Promise<ProviderItem[]> {
  const params = city ? `?city=${encodeURIComponent(city)}` : "";
  const res = await fetch(`${API_BASE}/providers${params}`);
  if (!res.ok) throw new Error("Failed to fetch providers");
  return res.json();
}

// ── Stats ─────────────────────────────────────────────────────
export async function fetchStats(): Promise<StatsData> {
  const res = await fetch(`${API_BASE}/stats`);
  if (!res.ok) throw new Error("Failed to fetch stats");
  return res.json();
}

// ── Health ────────────────────────────────────────────────────
export async function fetchHealth(): Promise<{
  status: string;
  database: string;
  rows: { providers: number; test_pricing: number; package_pricing: number };
}> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error("API unreachable");
  return res.json();
}

// ── Chat ──────────────────────────────────────────────────────
export async function sendChatMessage(
  message: string,
  history: { role: string; content: string }[] = [],
  signal?: AbortSignal,
  provider?: string
): Promise<Response> {
  const payload: any = { message, history };
  if (provider) {
    payload.provider = provider;
  }
  
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
    signal,
  });
  if (!res.ok) {
    let errMsg = "Chat request failed";
    try {
      const errData = await res.json();
      if (errData && errData.detail) {
        errMsg = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
      } else if (errData && errData.error) {
        errMsg = typeof errData.error === 'string' ? errData.error : JSON.stringify(errData.error);
      }
    } catch (e) {
      // Ignore JSON parse errors
    }
    throw new Error(errMsg);
  }
  return res;
}

export async function checkAiHealth(provider: string): Promise<{ status: string; provider: string }> {
  const res = await fetch(`${API_BASE}/chat/health?provider=${encodeURIComponent(provider)}`);
  if (!res.ok) {
    throw new Error("Provider health check failed");
  }
  return res.json();
}

// ── Custom Packages ───────────────────────────────────────────

export async function fetchCustomPackages(
  search?: string,
  sortBy?: string,
  sortOrder?: string
): Promise<CustomPackageData[]> {
  const params = new URLSearchParams();
  if (search) params.set("search", search);
  if (sortBy) params.set("sort_by", sortBy);
  if (sortOrder) params.set("sort_order", sortOrder);

  const url = `${API_BASE}/custom-packages${params.toString() ? `?${params}` : ""}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error("Failed to fetch custom packages");
  return res.json();
}

export async function fetchCustomPackage(id: number): Promise<CustomPackageData> {
  const res = await fetch(`${API_BASE}/custom-packages/${id}`);
  if (!res.ok) throw new Error("Failed to fetch custom package");
  return res.json();
}

export async function createCustomPackage(data: {
  package_name: string;
  total_tests?: number;
  individual_total_price?: number;
  discount_percentage?: number;
  suggested_package_price?: number;
  market_average_price?: number;
  expected_customer_savings?: number;
  tests: { test_name: string; individual_price?: number; display_order?: number }[];
}): Promise<CustomPackageData> {
  const res = await fetch(`${API_BASE}/custom-packages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to create package" }));
    throw new Error(err.detail || "Failed to create package");
  }
  return res.json();
}

export async function updateCustomPackage(
  id: number,
  data: {
    package_name: string;
    total_tests?: number;
    individual_total_price?: number;
    discount_percentage?: number;
    suggested_package_price?: number;
    market_average_price?: number;
    expected_customer_savings?: number;
    tests: { test_name: string; individual_price?: number; display_order?: number }[];
  }
): Promise<CustomPackageData> {
  const res = await fetch(`${API_BASE}/custom-packages/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to update package" }));
    throw new Error(err.detail || "Failed to update package");
  }
  return res.json();
}

export async function duplicateCustomPackage(id: number): Promise<CustomPackageData> {
  const res = await fetch(`${API_BASE}/custom-packages/${id}/duplicate`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to duplicate package");
  return res.json();
}

export async function deleteCustomPackage(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/custom-packages/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete package");
}

