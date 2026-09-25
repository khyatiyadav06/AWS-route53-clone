"use client";
import { Bell, ChevronDown, HelpCircle, Search, UserCircle } from "lucide-react";
import { useRouter } from "next/navigation";
import { api } from "../../lib/api";
import { useEffect, useState } from "react";
import type { User } from "../../types";

export default function TopBar() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [menu, setMenu] = useState(false);
  useEffect(() => {
    try { setUser(JSON.parse(localStorage.getItem("route53_user") || "null")); } catch { setUser(null); }
  }, []);
  async function logout() { await api.logout(); router.replace("/login"); }
  return <header className="aws-topbar">
    <div className="aws-brand"><span className="aws-logo">aws</span><span className="console-label">Management Console</span></div>
    <div className="top-search"><Search size={17}/><input aria-label="Search AWS services" placeholder="Search"/><kbd>Alt</kbd><kbd>/</kbd></div>
    <div className="top-actions">
      <button className="top-action" type="button"><span>Region</span><b>Global</b><ChevronDown size={14}/></button>
      <div className="service-indicator">Route 53</div>
      <button className="icon-action" type="button" aria-label="Help"><HelpCircle size={18}/></button>
      <button className="icon-action" type="button" aria-label="Notifications"><Bell size={18}/></button>
      <div className="relative">
        <button className="account-button" type="button" onClick={() => setMenu(v => !v)} aria-haspopup="menu" aria-expanded={menu}>
          <UserCircle size={20}/><span>{user?.name || "Demo User"}</span><ChevronDown size={14}/>
        </button>
        {menu && <div className="account-menu" role="menu">
          <div className="px-4 py-3 border-b border-[#eaeded]"><div className="font-semibold text-sm">{user?.name || "Demo User"}</div><div className="text-xs text-gray-500 mt-1">{user?.email || "demo@route53.local"}</div></div>
          <button type="button" onClick={logout} className="w-full text-left px-4 py-3 text-sm hover:bg-gray-50">Sign out</button>
        </div>}
      </div>
    </div>
  </header>;
}
