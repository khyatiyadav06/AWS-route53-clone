import "./globals.css";
import {ReactNode} from "react";
export const metadata={title:"Route 53 Clone",description:"AWS Route 53 experience clone"};
export default function RootLayout({children}:{children:ReactNode}){return <html lang="en"><body>{children}</body></html>}
