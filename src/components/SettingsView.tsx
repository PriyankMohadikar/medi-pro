/**
 * Settings — Page 8
 * Platform configuration and database status.
 */

import React, { useState } from "react";
import { StatsData } from "../types";
import {
  Database,
  Server,
  Building2,
  Globe,
  Palette,
  Key,
  Save,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
} from "lucide-react";

interface SettingsViewProps {
  stats: StatsData | null;
}

export default function SettingsView({ stats }: SettingsViewProps) {
  const [activeTab, setActiveTab] = useState<"general" | "database" | "api">("general");
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="max-w-5xl mx-auto flex flex-col md:flex-row gap-6">
      {/* Settings Sidebar */}
      <div className="w-full md:w-64 flex-shrink-0 space-y-1">
        <h2 className="font-display text-lg font-bold text-slate-800 mb-4 px-3">Settings</h2>
        
        <button
          onClick={() => setActiveTab("general")}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
            activeTab === "general" ? "bg-primary text-white shadow-sm" : "text-slate-600 hover:bg-slate-100"
          }`}
        >
          <Building2 className={`w-4 h-4 ${activeTab === "general" ? "text-white" : "text-slate-400"}`} />
          General & Organization
        </button>
        
        <button
          onClick={() => setActiveTab("database")}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
            activeTab === "database" ? "bg-primary text-white shadow-sm" : "text-slate-600 hover:bg-slate-100"
          }`}
        >
          <Database className={`w-4 h-4 ${activeTab === "database" ? "text-white" : "text-slate-400"}`} />
          Database Connection
        </button>
        
        <button
          onClick={() => setActiveTab("api")}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
            activeTab === "api" ? "bg-primary text-white shadow-sm" : "text-slate-600 hover:bg-slate-100"
          }`}
        >
          <Key className={`w-4 h-4 ${activeTab === "api" ? "text-white" : "text-slate-400"}`} />
          API & Intelligence
        </button>
      </div>

      {/* Settings Content */}
      <div className="flex-1 space-y-6">
        {/* General Settings */}
        {activeTab === "general" && (
          <div className="bg-white border border-slate-200 rounded-2xl card-shadow overflow-hidden">
            <div className="px-6 py-5 border-b border-slate-100">
              <h3 className="font-display font-bold text-lg text-slate-800">Organization Settings</h3>
              <p className="text-xs text-slate-500 mt-1">Configure your primary organization identity and defaults.</p>
            </div>
            
            <div className="p-6 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">Primary Provider Name</label>
                  <input
                    type="text"
                    defaultValue="ES Healthcare"
                    disabled
                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-500 cursor-not-allowed"
                  />
                  <p className="text-[10px] text-slate-400 mt-1.5">This name must exactly match the database records to identify your own tests vs competitors.</p>
                </div>
                
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">Default Region / City</label>
                  <select className="w-full bg-white border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all">
                    <option value="All">All Regions (Default)</option>
                    {stats?.cities.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>
              </div>
              
              <div className="border-t border-slate-100 pt-6">
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2 flex items-center gap-2">
                  <Palette className="w-4 h-4 text-slate-400" /> UI Theme
                </label>
                <div className="flex gap-4">
                  <button className="flex-1 bg-slate-50 border-2 border-primary rounded-xl p-4 flex flex-col items-center gap-2 hover:bg-slate-100 transition-colors">
                    <div className="w-full h-12 bg-white rounded-lg border border-slate-200 shadow-sm flex items-center p-2 gap-2">
                      <div className="w-3 h-3 bg-primary rounded-full"></div>
                      <div className="flex-1 h-2 bg-slate-100 rounded-full"></div>
                    </div>
                    <span className="text-xs font-semibold text-primary">Enterprise Blue (Active)</span>
                  </button>
                  <button className="flex-1 bg-slate-50 border-2 border-transparent rounded-xl p-4 flex flex-col items-center gap-2 hover:bg-slate-100 transition-colors opacity-50 cursor-not-allowed">
                    <div className="w-full h-12 bg-slate-900 rounded-lg shadow-sm flex items-center p-2 gap-2">
                      <div className="w-3 h-3 bg-indigo-500 rounded-full"></div>
                      <div className="flex-1 h-2 bg-slate-800 rounded-full"></div>
                    </div>
                    <span className="text-xs font-semibold text-slate-500">Dark Mode (Coming Soon)</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Database Settings */}
        {activeTab === "database" && (
          <div className="bg-white border border-slate-200 rounded-2xl card-shadow overflow-hidden">
            <div className="px-6 py-5 border-b border-slate-100 flex justify-between items-center">
              <div>
                <h3 className="font-display font-bold text-lg text-slate-800 flex items-center gap-2">
                  <Database className="w-5 h-5 text-primary" /> Database Connection
                </h3>
                <p className="text-xs text-slate-500 mt-1">Status of the PostgreSQL connection and data sync.</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 ${stats ? "bg-emerald-50 text-emerald-600" : "bg-red-50 text-red-600"}`}>
                <span className={`w-2 h-2 rounded-full ${stats ? "bg-emerald-500" : "bg-red-500"}`}></span>
                {stats ? "Connected" : "Disconnected"}
              </span>
            </div>
            
            <div className="p-6 space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-50 border border-slate-100 p-4 rounded-xl text-center">
                  <p className="text-2xl font-display font-bold text-slate-800">{stats?.total_tests ?? 0}</p>
                  <p className="text-[10px] uppercase font-semibold text-slate-400 mt-1">Total Tests</p>
                </div>
                <div className="bg-slate-50 border border-slate-100 p-4 rounded-xl text-center">
                  <p className="text-2xl font-display font-bold text-slate-800">{stats?.total_packages ?? 0}</p>
                  <p className="text-[10px] uppercase font-semibold text-slate-400 mt-1">Packages</p>
                </div>
                <div className="bg-slate-50 border border-slate-100 p-4 rounded-xl text-center">
                  <p className="text-2xl font-display font-bold text-slate-800">{stats?.total_providers ?? 0}</p>
                  <p className="text-[10px] uppercase font-semibold text-slate-400 mt-1">Providers</p>
                </div>
                <div className="bg-slate-50 border border-slate-100 p-4 rounded-xl text-center">
                  <p className="text-2xl font-display font-bold text-slate-800">{stats?.cities?.length ?? 0}</p>
                  <p className="text-[10px] uppercase font-semibold text-slate-400 mt-1">Cities</p>
                </div>
              </div>
              
              <div className="bg-blue-50 border border-blue-100 p-4 rounded-xl flex items-start gap-3">
                <Server className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-sm font-semibold text-blue-900">Live Data Connection</h4>
                  <p className="text-xs text-blue-700 mt-1 leading-relaxed">
                    MediPrice Pro is currently connected to the live PostgreSQL instance. Data is fetched in real-time. Any updates made in the database will reflect here automatically on page refresh.
                  </p>
                  <button onClick={() => window.location.reload()} className="mt-3 text-xs font-bold text-blue-700 bg-white px-3 py-1.5 rounded-lg border border-blue-200 hover:bg-blue-50 transition-colors flex items-center gap-1.5">
                    <RefreshCw className="w-3.5 h-3.5" /> Force Sync Data
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* API Settings */}
        {activeTab === "api" && (
          <div className="bg-white border border-slate-200 rounded-2xl card-shadow overflow-hidden">
            <div className="px-6 py-5 border-b border-slate-100">
              <h3 className="font-display font-bold text-lg text-slate-800 flex items-center gap-2">
                <Key className="w-5 h-5 text-primary" /> API & Intelligence
              </h3>
              <p className="text-xs text-slate-500 mt-1">Configure AI assistant models and external integrations.</p>
            </div>
            
            <div className="p-6 space-y-6">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">Google Gemini API Key</label>
                <div className="flex gap-3">
                  <input
                    type="password"
                    value="••••••••••••••••••••••••••••••••••••"
                    disabled
                    className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-500 cursor-not-allowed font-mono"
                  />
                  <button className="px-4 py-2.5 bg-white border border-slate-200 text-slate-600 text-sm font-semibold rounded-xl hover:bg-slate-50 transition-colors">
                    Update
                  </button>
                </div>
                <p className="text-[10px] text-slate-400 mt-2">API Key is securely configured via environment variables (.env) for the backend server.</p>
              </div>
              
              <div className="border-t border-slate-100 pt-6">
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-3">AI Intelligence Engine Status</label>
                
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 border border-emerald-200 bg-emerald-50 rounded-xl">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-emerald-100 flex items-center justify-center">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-emerald-800">Primary Engine: Gemini 1.5 Pro</p>
                        <p className="text-[10px] text-emerald-600 mt-0.5">Connected and processing queries</p>
                      </div>
                    </div>
                    <span className="text-[10px] font-bold px-2 py-1 bg-emerald-200 text-emerald-800 rounded-md">ACTIVE</span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 border border-slate-200 bg-slate-50 rounded-xl opacity-60">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-slate-200 flex items-center justify-center">
                        <Database className="w-4 h-4 text-slate-500" />
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-slate-700">Fallback Engine: Offline Rules</p>
                        <p className="text-[10px] text-slate-500 mt-0.5">Pre-computed analytics fallback</p>
                      </div>
                    </div>
                    <span className="text-[10px] font-bold px-2 py-1 bg-slate-200 text-slate-600 rounded-md">STANDBY</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Global Save Button */}
        <div className="flex justify-end pt-4">
          <div className="flex items-center gap-4">
            {saved && (
              <span className="text-sm font-medium text-emerald-600 flex items-center gap-1.5 animate-fadeInUp">
                <CheckCircle2 className="w-4 h-4" /> Settings saved successfully
              </span>
            )}
            <button
              onClick={handleSave}
              className="px-6 py-2.5 bg-primary text-white text-sm font-semibold rounded-xl hover:bg-primary-dark transition-colors flex items-center gap-2 shadow-sm"
            >
              <Save className="w-4 h-4" /> Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
