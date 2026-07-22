/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

// ── AI Assistant suggested queries & history ──────────────────
// These are kept as static constants since they are UI-only prompts.

export const SUGGESTED_QUERIES = [
  "Compare CBC price across all cities",
  "Which provider is cheapest for Lipid Profile in Ahmedabad?",
  "Show me all test prices in Surat",
  "What is the average HbA1c price?",
  "Suggest a health package under ₹3000"
];

export const RECENT_HISTORY = [
  { text: "Lipid Profile comparison Ahmedabad", time: "2h ago" },
  { text: "Ahmedabad Lab Trends Analysis", time: "Yesterday" },
  { text: "Vitamin D Pricing across cities", time: "3 days ago" },
  { text: "ES Healthcare vs competitors", time: "Last week" }
];
