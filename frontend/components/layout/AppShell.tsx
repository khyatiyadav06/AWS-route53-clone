import {ReactNode} from "react";
import TopBar from "./TopBar";
import Sidebar from "../navigation/Sidebar";
export default function AppShell({children}:{children:ReactNode}){return <div className="min-h-screen bg-[#f7f8f8]"><TopBar/><div className="flex"><Sidebar/><main className="flex-1 min-w-0 px-8 py-7">{children}</main></div></div>}
