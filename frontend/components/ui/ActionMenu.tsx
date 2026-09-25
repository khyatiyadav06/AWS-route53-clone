"use client";
import { useEffect, useRef, useState } from "react";
import { ChevronDown } from "lucide-react";

export type ActionItem = { label: string; onClick: () => void; danger?: boolean; disabled?: boolean };

export default function ActionMenu({ items, label = "Actions" }: { items: ActionItem[]; label?: string }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const close = (event: MouseEvent) => { if (ref.current && !ref.current.contains(event.target as Node)) setOpen(false); };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);
  return <div className="relative" ref={ref}>
    <button type="button" className="btn flex items-center gap-2" aria-haspopup="menu" aria-expanded={open} onClick={() => setOpen(v => !v)}>
      {label}<ChevronDown size={14}/>
    </button>
    {open && <div className="absolute left-0 top-full mt-1 z-30 min-w-[180px] bg-white border border-[#aab7b8] shadow-lg py-1" role="menu">
      {items.map((item) => <button key={item.label} type="button" role="menuitem" disabled={item.disabled} onClick={() => { item.onClick(); setOpen(false); }} className={`w-full text-left px-3 py-2 text-sm hover:bg-[#f2f3f3] disabled:opacity-40 disabled:cursor-not-allowed ${item.danger ? "text-[#d91515]" : "text-[#161e2d]"}`}>{item.label}</button>)}
    </div>}
  </div>;
}
