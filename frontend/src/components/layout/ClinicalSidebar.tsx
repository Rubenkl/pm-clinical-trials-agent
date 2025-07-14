
import { useState } from "react";
import { 
  LayoutDashboard, 
  Users, 
  Bot, 
  AlertTriangle, 
  FileText, 
  Settings,
  Search,
  FileCheck,
  Shield,
  Building2,
  TrendingUp,
  ClipboardList
} from "lucide-react";
import { NavLink, useLocation } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
  useSidebar,
} from "@/components/ui/sidebar";

interface NavigationItem {
  title: string;
  url: string;
  icon: any;
  badge?: string;
  description?: string;
}

interface NavigationSection {
  title: string;
  items: NavigationItem[];
}

const navigationSections: NavigationSection[] = [
  {
    title: "Overview",
    items: [
      { title: "Dashboard", url: "/", icon: LayoutDashboard }
    ]
  },
  {
    title: "Core Workflows", 
    items: [
      { title: "Query Management", url: "/queries", icon: Search },
      { title: "Source Data Verification", url: "/sdv", icon: FileCheck },
      { title: "Protocol Compliance", url: "/compliance", icon: Shield }
    ]
  },
  {
    title: "Data Management",
    items: [
      { title: "Subjects", url: "/subjects", icon: Users },
      { title: "Discrepancies", url: "/discrepancies", icon: AlertTriangle }
    ]
  },
  {
    title: "AI Intelligence",
    items: [
      { title: "Clinical Analysis", url: "/ai-chat", icon: ClipboardList }
    ]
  }
];

export function ClinicalSidebar() {
  const { state } = useSidebar();
  const location = useLocation();
  const currentPath = location.pathname;
  const collapsed = state === "collapsed";

  const isActive = (path: string) => {
    if (path === "/") return currentPath === "/";
    return currentPath.startsWith(path);
  };

  const getNavClass = (path: string) => {
    return isActive(path) 
      ? "bg-blue-100 text-blue-900 font-medium border-r-2 border-blue-600" 
      : "hover:bg-slate-100 text-slate-700";
  };

  return (
    <Sidebar
      className={`border-r border-slate-200 bg-white ${collapsed ? "w-14" : "w-64"}`}
      collapsible="icon"
    >
      <div className="p-4 border-b border-slate-200">
        {!collapsed && (
          <div>
            <h2 className="text-lg font-bold text-slate-900">Clinical Trials AI</h2>
            <p className="text-sm text-slate-600">CARD-2025-001</p>
          </div>
        )}
        {collapsed && (
          <div className="text-center">
            <div className="w-8 h-8 bg-blue-600 rounded text-white flex items-center justify-center text-sm font-bold">
              CT
            </div>
          </div>
        )}
      </div>

      <SidebarContent className="p-2">
        {navigationSections.map((section) => (
          <SidebarGroup key={section.title}>
            <SidebarGroupLabel className={collapsed ? "sr-only" : "text-xs font-medium text-slate-500 uppercase tracking-wider mb-2"}>
              {section.title}
            </SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {section.items.map((item) => (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton asChild>
                      <NavLink 
                        to={item.url} 
                        className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${getNavClass(item.url)} relative`}
                      >
                        <item.icon className="h-4 w-4 flex-shrink-0" />
                        {!collapsed && (
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <span className="truncate">{item.title}</span>
                              {item.badge && (
                                <Badge variant="secondary" className="ml-2 text-xs">
                                  {item.badge}
                                </Badge>
                              )}
                            </div>
                          </div>
                        )}
                        {collapsed && item.badge && (
                          <Badge variant="secondary" className="absolute -top-1 -right-1 text-xs min-w-[18px] h-4 px-1">
                            {item.badge}
                          </Badge>
                        )}
                      </NavLink>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        ))}
      </SidebarContent>
    </Sidebar>
  );
}
