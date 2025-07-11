
import { ReactNode } from "react";
import { ClinicalSidebar } from "./ClinicalSidebar";
import { ClinicalHeader } from "./ClinicalHeader";

interface ClinicalLayoutProps {
  children: ReactNode;
}

export function ClinicalLayout({ children }: ClinicalLayoutProps) {
  return (
    <>
      <ClinicalSidebar />
      <div className="flex-1 flex flex-col">
        <ClinicalHeader />
        <main className="flex-1 p-6 bg-slate-50">
          {children}
        </main>
      </div>
    </>
  );
}
