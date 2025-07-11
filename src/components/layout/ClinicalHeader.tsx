
import { Bell, Search, User } from "lucide-react";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function ClinicalHeader() {
  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <SidebarTrigger className="text-slate-600 hover:text-slate-900" />
        <div className="text-sm text-slate-600">
          Protocol CARD-2025-001 • Phase II Cardiovascular Study
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input 
            placeholder="Search subjects, data..." 
            className="pl-10 w-80 bg-slate-50 border-slate-200"
          />
        </div>
        
        <Button variant="ghost" size="sm" className="relative">
          <Bell className="h-4 w-4" />
          <span className="absolute -top-1 -right-1 h-2 w-2 bg-red-500 rounded-full"></span>
        </Button>
        
        <Button variant="ghost" size="sm">
          <User className="h-4 w-4" />
          <span className="ml-2 hidden sm:inline">Dr. Smith</span>
        </Button>
      </div>
    </header>
  );
}
