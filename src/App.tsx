/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, useMemo } from "react";
import { fetchTests, fetchPackages, fetchStats, fetchProviders } from "./api";
import { TestItem, PackageItem, ProviderItem, StatsData, ActiveScreen, CustomPackageData } from "./types";

// Page views
import { Suspense, lazy } from "react";

// Lazy load views to reduce initial bundle size and memory usage
const DashboardView = lazy(() => import("./components/DashboardView"));
const TestPricingView = lazy(() => import("./components/TestPricingView"));
const PackageIntelligenceView = lazy(() => import("./components/PackageIntelligenceView"));
const CompetitorIntelligenceView = lazy(() => import("./components/CompetitorIntelligenceView"));
const PackageBuilderView = lazy(() => import("./components/PackageBuilderView"));
const SavedPackagesView = lazy(() => import("./components/SavedPackagesView"));
const AiAssistantView = lazy(() => import("./components/AiAssistantView"));
const ReportsView = lazy(() => import("./components/ReportsView"));
const SettingsView = lazy(() => import("./components/SettingsView"));

import {
  LayoutDashboard,
  TestTubeDiagonal,
  Package,
  Users,
  Hammer,
  Sparkles,
  FileBarChart,
  Settings,
  Loader2,
  AlertCircle,
  ChevronRight,
  ChevronDown,
  PlusCircle,
  FolderOpen,
} from "lucide-react";

export default function App() {
  const [tests, setTests] = useState<TestItem[]>([]);
  const [packages, setPackages] = useState<PackageItem[]>([]);
  const [providers, setProviders] = useState<ProviderItem[]>([]);
  const [stats, setStats] = useState<StatsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [dataLoaded, setDataLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeScreen, setActiveScreen] = useState<ActiveScreen>("ai-assistant");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [packageBuilderOpen, setPackageBuilderOpen] = useState(false);
  const [editingPackage, setEditingPackage] = useState<CustomPackageData | null>(null);

  // ── Fetch all data only when needed ──────────────────────────────
  useEffect(() => {
    // If the active screen is AI Assistant or Settings, we don't need the massive DB load yet
    if (activeScreen === "ai-assistant" || activeScreen === "settings") {
      return;
    }
    
    // Only load once
    if (dataLoaded) return;

    async function loadData() {
      try {
        setLoading(true);
        setError(null);
        const [testsData, packagesData, statsData, providersData] = await Promise.all([
          fetchTests(),
          fetchPackages(),
          fetchStats(),
          fetchProviders(),
        ]);
        setTests(testsData);
        setPackages(packagesData);
        setStats(statsData);
        setProviders(providersData);
        setDataLoaded(true);
      } catch (err: any) {
        console.error("Failed to load data:", err);
        setError("Could not connect to the API. Make sure the FastAPI server is running on port 8000.");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [activeScreen, dataLoaded]);

  const formatPrice = (val: number | null) => {
    if (val === null || val === undefined) return "N/A";
    return `₹${val.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
  };

  // Handle edit from Saved Packages → navigate to Create with pre-populated data
  const handleEditPackage = (pkg: CustomPackageData) => {
    setEditingPackage(pkg);
    setActiveScreen("create-package");
  };

  const handleCancelEdit = () => {
    setEditingPackage(null);
  };

  const handleSaveSuccess = () => {
    setEditingPackage(null);
  };

  // Sidebar navigation structure
  const navSections = [
    {
      label: "Analytics",
      items: [
        { id: "dashboard" as ActiveScreen, label: "Dashboard", icon: LayoutDashboard },
        { id: "test-pricing" as ActiveScreen, label: "Test Pricing Analysis", icon: TestTubeDiagonal },
        { id: "package-intelligence" as ActiveScreen, label: "Package Intelligence", icon: Package },
        { id: "competitor-intelligence" as ActiveScreen, label: "Competitor Intelligence", icon: Users },
      ],
    },
    {
      label: "Tools",
      items: [
        {
          id: "custom-package-builder" as ActiveScreen,
          label: "Custom Package Builder",
          icon: Hammer,
          isSubmenu: true,
          subItems: [
            { id: "create-package" as ActiveScreen, label: "Create Package", icon: PlusCircle },
            { id: "saved-packages" as ActiveScreen, label: "Saved Packages", icon: FolderOpen },
          ],
        },
        { id: "ai-assistant" as ActiveScreen, label: "AI Pricing Assistant", icon: Sparkles },
      ],
    },
  ];

  const screenTitles: Record<ActiveScreen, string> = {
    dashboard: "Executive Dashboard",
    "test-pricing": "Test Pricing Analysis",
    "package-intelligence": "Package Intelligence",
    "competitor-intelligence": "Competitor Intelligence",
    "custom-package-builder": "Custom Package Builder",
    "create-package": "Create Package",
    "saved-packages": "Saved Packages",
    "ai-assistant": "AI Pricing Assistant",
    reports: "Reports",
    settings: "Settings",
  };

  const sidebarWidth = sidebarCollapsed ? "w-[68px]" : "w-[260px]";
  const mainPadding = sidebarCollapsed ? "pl-[68px]" : "pl-[260px]";

  // Check if a submenu item is active
  const isPackageBuilderActive = activeScreen === "create-package" || activeScreen === "saved-packages" || activeScreen === "custom-package-builder";

  // Auto-expand submenu when navigating to a child
  useEffect(() => {
    if (isPackageBuilderActive) {
      setPackageBuilderOpen(true);
    }
  }, [isPackageBuilderActive]);

  // ── Loading state ──────────────────────────────────────────
  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="bg-white p-10 rounded-2xl card-shadow text-center space-y-4 max-w-sm border border-slate-100">
          <Loader2 className="w-10 h-10 text-primary animate-spin mx-auto" />
          <div>
            <h2 className="font-display text-lg font-bold text-slate-800">Loading ESHPrice Pro</h2>
            <p className="text-sm text-slate-400 mt-1">Connecting to database...</p>
          </div>
        </div>
      </div>
    );
  }

  // ── Error state ────────────────────────────────────────────
  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="bg-white border border-red-100 p-10 rounded-2xl card-shadow text-center space-y-4 max-w-md">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto bg-red-50 p-2.5 rounded-full" />
          <h2 className="font-display text-xl font-bold text-slate-800">Connection Error</h2>
          <p className="text-sm text-slate-500">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-6 py-2.5 bg-primary text-white font-semibold rounded-xl hover:bg-primary-dark transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-on-background font-sans flex antialiased">
      {/* ── SIDEBAR ─────────────────────────────────────────── */}
      <aside
        className={`${sidebarWidth} bg-white border-r border-slate-200/80 fixed h-full z-50 flex flex-col transition-all duration-300 ease-in-out`}
      >
        {/* Brand */}
        <div className={`py-5 flex items-center border-b border-slate-100 transition-all duration-300 ${sidebarCollapsed ? 'justify-center px-2' : 'px-6 gap-3'}`}>
          <img 
            src="/logo.png" 
            alt="ES Healthcare" 
            className={`object-contain mix-blend-multiply transition-all duration-300 ${sidebarCollapsed ? 'h-8 w-auto' : 'h-10 w-auto'}`} 
          />
          {!sidebarCollapsed && (
            <div className="flex flex-col text-left animate-fadeInUp">
              <h1 className="text-[16px] font-display font-bold text-slate-800 leading-tight tracking-tight">ESHPrice Pro</h1>
              <p className="text-[10px] font-bold text-primary/80 uppercase tracking-wider">Pricing Intelligence</p>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-5">
          {navSections.map((section) => (
            <div key={section.label}>
              {!sidebarCollapsed && (
                <span className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider px-3 block mb-2">
                  {section.label}
                </span>
              )}
              <div className="space-y-0.5">
                {section.items.map((item) => {
                  const Icon = item.icon;
                  const hasSubmenu = 'isSubmenu' in item && item.isSubmenu;

                  if (hasSubmenu && 'subItems' in item) {
                    // Collapsible submenu item
                    return (
                      <div key={item.id}>
                        <button
                          onClick={() => {
                            if (sidebarCollapsed) {
                              setActiveScreen("create-package");
                            } else {
                              setPackageBuilderOpen(!packageBuilderOpen);
                            }
                          }}
                          title={sidebarCollapsed ? item.label : undefined}
                          className={`w-full flex items-center gap-3 px-3 py-2.5 transition-all text-left text-[13px] font-medium rounded-xl ${
                            isPackageBuilderActive
                              ? "bg-primary/10 text-primary"
                              : "text-slate-500 hover:bg-slate-50 hover:text-slate-700"
                          }`}
                        >
                          <Icon className={`w-[18px] h-[18px] flex-shrink-0 ${isPackageBuilderActive ? "text-primary" : "text-slate-400"}`} />
                          {!sidebarCollapsed && (
                            <>
                              <span className="truncate flex-1">{item.label}</span>
                              <ChevronDown
                                className={`w-3.5 h-3.5 transition-transform duration-200 ${
                                  packageBuilderOpen ? "rotate-0" : "-rotate-90"
                                } ${isPackageBuilderActive ? "text-primary" : "text-slate-400"}`}
                              />
                            </>
                          )}
                        </button>
                        {/* Sub-items */}
                        {!sidebarCollapsed && packageBuilderOpen && (
                          <div className="ml-5 mt-0.5 pl-3 border-l-2 border-slate-100 space-y-0.5">
                            {item.subItems.map((sub) => {
                              const SubIcon = sub.icon;
                              const isSubActive = activeScreen === sub.id;
                              return (
                                <button
                                  key={sub.id}
                                  onClick={() => {
                                    setActiveScreen(sub.id);
                                    if (sub.id === "create-package") {
                                      setEditingPackage(null);
                                    }
                                  }}
                                  className={`w-full flex items-center gap-2.5 px-3 py-2 transition-all text-left text-[12px] font-medium rounded-lg ${
                                    isSubActive
                                      ? "bg-primary text-white shadow-sm"
                                      : "text-slate-500 hover:bg-slate-50 hover:text-slate-700"
                                  }`}
                                >
                                  <SubIcon className={`w-[15px] h-[15px] flex-shrink-0 ${isSubActive ? "text-white" : "text-slate-400"}`} />
                                  <span className="truncate">{sub.label}</span>
                                </button>
                              );
                            })}
                          </div>
                        )}
                      </div>
                    );
                  }

                  // Regular nav item
                  const isActive = activeScreen === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => setActiveScreen(item.id)}
                      title={sidebarCollapsed ? item.label : undefined}
                      className={`w-full flex items-center gap-3 px-3 py-2.5 transition-all text-left text-[13px] font-medium rounded-xl ${
                        isActive
                          ? "bg-primary text-white shadow-sm"
                          : "text-slate-500 hover:bg-slate-50 hover:text-slate-700"
                      }`}
                    >
                      <Icon className={`w-[18px] h-[18px] flex-shrink-0 ${isActive ? "text-white" : "text-slate-400"}`} />
                      {!sidebarCollapsed && <span className="truncate">{item.label}</span>}
                      {!sidebarCollapsed && item.id === "ai-assistant" && (
                        <span className={`ml-auto text-[9px] px-1.5 py-0.5 rounded-md font-bold tracking-wide ${isActive ? "bg-white/20 text-white" : "bg-primary text-white"}`}>
                          AI
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Bottom: DB Status */}
        {/* <div className="p-3 border-t border-slate-100">
          <div className={`bg-slate-50 rounded-xl p-3 border border-slate-100 ${sidebarCollapsed ? "text-center" : ""}`}>
            <div className="flex items-center gap-2 mb-1">
              <span className="flex h-2 w-2 relative flex-shrink-0">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
              </span>
              {!sidebarCollapsed && <span className="text-[11px] font-semibold text-slate-600">PostgreSQL</span>}
            </div>
            {!sidebarCollapsed && (
              <p className="text-[10px] text-slate-400 font-medium">
                {stats?.total_tests ?? 0} tests · {stats?.total_providers ?? 0} providers
              </p>
            )}
          </div>
        </div> */}
      </aside>

      {/* ── MAIN CONTENT ─────────────────────────────────────── */}
      <div className={`${mainPadding} flex-1 flex flex-col ${activeScreen === "ai-assistant" ? "h-screen overflow-hidden" : "min-h-screen"} transition-all duration-300`}>
        {/* Top Bar */}
        <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-slate-100 px-8 py-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors text-slate-400 hover:text-slate-600"
            >
              <ChevronRight className={`w-4 h-4 transition-transform duration-300 ${sidebarCollapsed ? "" : "rotate-180"}`} />
            </button>
            <div>
              <h2 className="font-display text-lg font-bold text-slate-800">
                {screenTitles[activeScreen]}
              </h2>
              <p className="text-[11px] text-slate-400 font-medium">
                ES Healthcare · Pricing Decision Support
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right hidden md:block">
              <p className="text-xs font-semibold text-slate-600">Admin User</p>
              <p className="text-[10px] text-slate-400">ES Healthcare</p>
            </div>
            <div className="w-8 h-8 rounded-full bg-primary text-white flex items-center justify-center font-display font-bold text-xs">
              ES
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className={`${activeScreen === "ai-assistant" ? "flex-1 p-0 overflow-hidden" : "flex-grow p-8"}`}>
          <Suspense fallback={
            <div className="flex items-center justify-center h-64">
              <Loader2 className="w-8 h-8 text-primary animate-spin" />
            </div>
          }>
            {activeScreen === "dashboard" && (
              <DashboardView
                tests={tests}
                packages={packages}
                stats={stats}
                formatPrice={formatPrice}
                onNavigateToScreen={(screen) => setActiveScreen(screen)}
              />
            )}
            {activeScreen === "test-pricing" && (
              <TestPricingView
                tests={tests}
                stats={stats}
                formatPrice={formatPrice}
              />
            )}
            {activeScreen === "package-intelligence" && (
              <PackageIntelligenceView
                tests={tests}
                packages={packages}
                stats={stats}
                formatPrice={formatPrice}
              />
            )}
            {activeScreen === "competitor-intelligence" && (
              <CompetitorIntelligenceView
                tests={tests}
                packages={packages}
                stats={stats}
                formatPrice={formatPrice}
              />
            )}
            {(activeScreen === "custom-package-builder" || activeScreen === "create-package") && (
              <PackageBuilderView
                tests={tests}
                packages={packages}
                stats={stats}
                formatPrice={formatPrice}
                editingPackage={editingPackage}
                onSaveSuccess={handleSaveSuccess}
                onCancelEdit={handleCancelEdit}
              />
            )}
            {activeScreen === "saved-packages" && (
              <SavedPackagesView
                formatPrice={formatPrice}
                onEditPackage={handleEditPackage}
              />
            )}
            {activeScreen === "ai-assistant" && (
              <AiAssistantView
                currency="INR"
              />
            )}
            {activeScreen === "reports" && (
              <ReportsView
                tests={tests}
                packages={packages}
                stats={stats}
                formatPrice={formatPrice}
              />
            )}
            {activeScreen === "settings" && (
              <SettingsView stats={stats} />
            )}
          </Suspense>
        </main>
      </div>
    </div>
  );
}
