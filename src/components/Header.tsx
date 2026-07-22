/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from "react";
import { Search, Bell, Database, Globe, User, Check, Settings, LogOut } from "lucide-react";

interface HeaderProps {
  currency: string;
  setCurrency: (curr: string) => void;
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  activeScreen: string;
}

export default function Header({
  searchTerm,
  setSearchTerm,
  activeScreen
}: HeaderProps) {
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  const formatScreenTitle = (screen: string) => {
    return screen
      .split("-")
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  const notifications = [
    { id: 1, text: "Apollo Labs updated CBC cost by +12% in Mumbai", time: "2h ago", unread: true },
    { id: 2, text: "AI Assistant suggested a price optimization for LFT", time: "5h ago", unread: true },
    { id: 3, text: "Wellness Gold package was approved for national catalog", time: "1d ago", unread: false }
  ];

  return (
    <header className="fixed top-0 right-0 w-[calc(100%-280px)] h-16 bg-white border-b glass-border flex justify-between items-center px-md z-40">
      {/* Left: Dynamic Search */}
      <div className="flex items-center gap-md flex-1 max-w-lg">
        <div className="relative w-full group">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-primary transition-colors" />
          <input
            type="text"
            className="w-full bg-slate-50/50 border border-slate-200 rounded-full py-2 pl-10 pr-4 focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary font-sans text-sm text-slate-700 placeholder-slate-400 transition-all"
            placeholder={`Search tests, packages, or insights in ${formatScreenTitle(activeScreen)}...`}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* Right: Notifications, Profile */}
      <div className="flex items-center gap-4">
        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => {
              setShowNotifications(!showNotifications);
              setShowProfileMenu(false);
            }}
            className="p-2 hover:bg-slate-100 rounded-full transition-all relative text-slate-500 hover:text-slate-700"
            title="Notifications"
          >
            <Bell className="w-5 h-5" />
            {notifications.some(n => n.unread) && (
              <span className="absolute top-2 right-2.5 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white"></span>
            )}
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 bg-white border border-slate-200 rounded-xl soft-shadow p-sm space-y-3 text-sm z-50 animate-in fade-in slide-in-from-top-2 duration-200">
              <div className="flex justify-between items-center border-b border-slate-100 pb-2">
                <h4 className="font-display font-semibold text-slate-800">Notifications</h4>
                <span className="text-[10px] bg-primary/10 text-primary px-2 py-0.5 rounded-full font-medium">
                  {notifications.filter(n => n.unread).length} New
                </span>
              </div>
              <div className="space-y-1 max-h-64 overflow-y-auto">
                {notifications.map(n => (
                  <div key={n.id} className={`p-2 rounded-lg cursor-pointer transition-colors ${n.unread ? "bg-slate-50" : "hover:bg-slate-50"}`}>
                    <div className="flex justify-between items-start">
                      <p className={`text-xs ${n.unread ? "font-semibold text-slate-800" : "text-slate-600"}`}>
                        {n.text}
                      </p>
                      {n.unread && <span className="w-1.5 h-1.5 bg-primary rounded-full mt-1.5 flex-shrink-0 ml-2"></span>}
                    </div>
                    <span className="text-[10px] text-slate-400 mt-1 block font-medium">{n.time}</span>
                  </div>
                ))}
              </div>
              <button
                className="w-full py-1.5 text-xs text-primary font-medium hover:bg-primary/5 rounded-lg transition-colors"
                onClick={() => setShowNotifications(false)}
              >
                Mark all as read
              </button>
            </div>
          )}
        </div>

        <div className="h-6 w-px bg-slate-200"></div>

        {/* User Profile */}
        <div className="relative">
          <button
            onClick={() => {
              setShowProfileMenu(!showProfileMenu);
              setShowNotifications(false);
            }}
            className="flex items-center gap-2 p-1.5 hover:bg-slate-100 rounded-full transition-all pl-3"
          >
            <div className="flex flex-col items-end">
              <span className="font-display text-sm font-semibold text-slate-700 leading-none">Admin User</span>
              <span className="font-sans text-[10px] text-slate-500 font-medium mt-0.5">ES Healthcare</span>
            </div>
            <div className="w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center border border-primary/20 font-display font-semibold text-sm">
              AD
            </div>
          </button>

          {showProfileMenu && (
            <div className="absolute right-0 mt-2 w-56 bg-white border border-slate-200 rounded-xl soft-shadow p-2 text-sm z-50 animate-in fade-in slide-in-from-top-2 duration-200">
              <div className="p-2 border-b border-slate-100 mb-1">
                <p className="font-display font-semibold text-slate-800">Admin User</p>
                <p className="text-xs text-slate-500">admin@eshealthcare.com</p>
              </div>
              
              <button className="w-full flex items-center gap-2 p-2 hover:bg-slate-50 rounded-lg text-slate-600 transition-colors">
                <User className="w-4 h-4" /> My Profile
              </button>
              <button className="w-full flex items-center gap-2 p-2 hover:bg-slate-50 rounded-lg text-slate-600 transition-colors">
                <Settings className="w-4 h-4" /> Preferences
              </button>
              <div className="h-px bg-slate-100 my-1"></div>
              <button className="w-full flex items-center gap-2 p-2 hover:bg-red-50 text-red-600 rounded-lg transition-colors">
                <LogOut className="w-4 h-4" /> Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
