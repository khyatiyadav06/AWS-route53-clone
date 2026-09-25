"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Edit, Eye, MoreVertical, Plus, Search, Trash2 } from "lucide-react";
import AppShell from "../../components/layout/AppShell";
import Modal from "../../components/ui/Modal";
import Toast from "../../components/ui/Toast";
import Pagination from "../../components/tables/Pagination";
import ActionMenu from "../../components/ui/ActionMenu";
import { api } from "../../lib/api";
import type { Page, Zone } from "../../types";

export default function HostedZones() {
  const [data, setData] = useState<Page<Zone> | null>(null);
  const [search, setSearch] = useState(""); const [page, setPage] = useState(1);
  const [modal, setModal] = useState<"create" | "edit" | "delete" | null>(null);
  const [selected, setSelected] = useState<Zone | null>(null); const [toast, setToast] = useState("");
  const [error, setError] = useState(""); const [loading, setLoading] = useState(true);

  async function load() { setLoading(true); try { setData(await api.zones(page, search)); setError(""); } catch (e) { setError(e instanceof Error ? e.message : "Unable to load hosted zones"); } finally { setLoading(false); } }
  useEffect(() => { void load(); }, [page, search]);
  const open = (next: "create" | "edit" | "delete", zone?: Zone) => { setSelected(zone || null); setModal(next); };

  return <AppShell><div className="max-w-[1400px]">
    <nav className="breadcrumb mb-4" aria-label="Breadcrumb"><Link href="/dashboard">AWS Management Console</Link><span className="mx-2">›</span><span>Route 53</span><span className="mx-2">›</span><span>Hosted zones</span></nav>
    <div className="flex flex-wrap justify-between items-end gap-4 mb-5"><div><h1 className="page-title">Hosted zones</h1><p className="subtle mt-2">Create and manage public and private DNS hosted zones.</p></div><button className="btn btn-primary flex items-center gap-2" onClick={() => open("create")}><Plus size={17}/> Create hosted zone</button></div>
    <div className="action-bar"><ActionMenu items={[{label:"Create hosted zone", onClick:()=>open("create")}, {label:"Refresh", onClick:()=>void load()}]}/><span className="subtle text-sm">Hosted zones</span></div>
    <div className="console-panel">
      <div className="p-4 border-b border-[#eaeded] flex flex-wrap items-center gap-3"><div className="relative max-w-xl w-full"><Search className="absolute left-3 top-2.5 text-gray-400" size={17}/><input className="aws-input pl-9" aria-label="Search hosted zones" placeholder="Find hosted zones by domain name, zone ID, or description" value={search} onChange={e=>{setPage(1);setSearch(e.target.value)}}/></div><span className="text-sm subtle">{data?.total ?? 0} hosted zones</span></div>
      {error && <div className="m-4 aws-alert-error" role="alert">{error}<button className="aws-link ml-3" onClick={()=>void load()}>Retry</button></div>}
      {loading ? <div className="empty-state" aria-live="polite">Loading hosted zones…</div> : !data?.items.length ? <div className="empty-state"><h2 className="font-semibold text-[#161e2d]">No hosted zones found</h2><p className="mt-2">Try a different search or create a hosted zone.</p><button className="btn btn-primary mt-5" onClick={()=>open("create")}>Create hosted zone</button></div> : <>
        <div className="overflow-x-auto"><table className="w-full text-sm aws-table"><thead><tr><th className="p-4 text-left">Domain name</th><th className="p-4 text-left">Hosted zone ID</th><th className="p-4 text-left">Type</th><th className="p-4 text-left">Record count</th><th className="p-4 text-left">Description</th><th className="p-4 text-left">Created</th><th className="p-4 text-left">Actions</th></tr></thead><tbody>{data.items.map(z=><tr key={z.id}>
          <td className="p-4"><Link className="aws-link font-semibold" href={`/hosted-zones/${z.id}`}>{z.name}</Link></td><td className="p-4 font-mono text-xs">{z.zone_id}</td><td className="p-4">{z.zone_type}</td><td className="p-4">{z.record_count}</td><td className="p-4 max-w-sm truncate">{z.description || "—"}</td><td className="p-4">{new Date(z.created_at).toLocaleDateString()}</td>
          <td className="p-4"><div className="flex items-center gap-1"><button className="icon-button" title="View details" aria-label={`View ${z.name}`} onClick={()=>location.assign(`/hosted-zones/${z.id}`)}><Eye size={16}/></button><ActionMenu items={[{label:"View details",onClick:()=>location.assign(`/hosted-zones/${z.id}`)},{label:"Edit",onClick:()=>open("edit",z)},{label:"Delete",danger:true,onClick:()=>open("delete",z)}]}/><MoreVertical size={16} className="text-gray-400"/></div></td>
        </tr>)}</tbody></table></div><div className="p-4 border-t border-[#eaeded]"><Pagination page={data.page} pages={data.pages} onChange={setPage}/></div></>}
    </div>
  </div>{modal && <ZoneModal mode={modal} zone={selected || undefined} close={()=>setModal(null)} refresh={load} toast={setToast}/>} {toast && <Toast message={toast} onClose={()=>setToast("")}/>}</AppShell>;
}

function ZoneModal({mode, zone, close, refresh, toast}:{mode:"create"|"edit"|"delete";zone?:Zone;close:()=>void;refresh:()=>Promise<void>;toast:(s:string)=>void}) {
  const [name,setName]=useState(zone?.name||""); const [description,setDescription]=useState(zone?.description||""); const [zoneType,setZoneType]=useState(zone?.zone_type||"Public"); const [busy,setBusy]=useState(false); const [error,setError]=useState("");
  async function save(){setBusy(true);setError("");try{if(mode==="delete"){await api.deleteZone(zone!.id);toast("Hosted zone deleted successfully.")}else if(mode==="create"){await api.createZone({name,description,zone_type:zoneType});toast("Hosted zone created successfully.")}else{await api.updateZone(zone!.id,{name,description,zone_type:zoneType});toast("Hosted zone updated successfully.")}close();await refresh();}catch(e){setError(e instanceof Error?e.message:"Request failed");}finally{setBusy(false)}}
  return <Modal title={mode==='delete'?'Delete hosted zone':mode==='create'?'Create hosted zone':'Edit hosted zone'} onClose={close}>{mode==='delete'?<><p className="text-gray-700">Are you sure you want to delete <strong>{zone?.name}</strong>? All associated DNS records will also be deleted.</p>{error&&<div className="aws-alert-error mt-4">{error}</div>}<div className="flex justify-end gap-3 mt-7"><button className="btn" onClick={close}>Cancel</button><button className="btn bg-[#d91515] text-white border-[#d91515]" disabled={busy} onClick={()=>void save()}>{busy?'Deleting…':'Delete'}</button></div></>:<div className="space-y-5"><label className="aws-label">Domain name *<input required className="aws-input mt-1" value={name} onChange={e=>setName(e.target.value)} placeholder="example.com"/></label><label className="aws-label">Description<input className="aws-input mt-1" value={description} onChange={e=>setDescription(e.target.value)}/></label><label className="aws-label">Zone type<select className="aws-input mt-1" value={zoneType} onChange={e=>setZoneType(e.target.value)}><option>Public</option><option>Private</option></select></label>{error&&<div className="aws-alert-error" role="alert">{error}</div>}<div className="flex justify-end gap-3"><button className="btn" onClick={close}>Cancel</button><button className="btn btn-primary" disabled={busy||!name.trim()} onClick={()=>void save()}>{busy?'Saving…':mode==='create'?'Create hosted zone':'Save changes'}</button></div></div>}</Modal>;
}
