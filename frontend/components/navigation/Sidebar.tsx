"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BarChart3, Globe2, Network, ShieldCheck, Route, Users, ChevronDown, Star, Settings } from "lucide-react";
const items=[['Dashboard','/dashboard',BarChart3],['Hosted zones','/hosted-zones',Globe2],['Traffic policies','/traffic-policies',Route],['Health checks','/health-checks',ShieldCheck],['Resolver','/resolver',Network],['Profiles','/profiles',Users]] as const;
export default function Sidebar(){
 const path=usePathname();
 return <aside className="aws-sidebar">
   <div className="sidebar-service"><div className="service-title"><Globe2 size={19}/> Route 53</div><ChevronDown size={15}/></div>
   <div className="sidebar-section-label">Route 53</div>
   {items.map(([name,href,Icon])=>{const active=path===href||path.startsWith(href+'/');return <Link key={href} href={href} className={`sidebar-item ${active?'active':''}`}><Icon size={17}/><span>{name}</span></Link>})}
   <div className="sidebar-divider"/>
   <div className="sidebar-section-label">Shortcuts</div>
   <button className="sidebar-item"><Star size={17}/><span>Favorites</span></button>
   <button className="sidebar-item"><Settings size={17}/><span>Settings</span></button>
   <div className="sidebar-footer">© AWS-style demo console<br/>Route 53 Clone</div>
 </aside>
}
