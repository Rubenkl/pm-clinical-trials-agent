
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { SidebarProvider } from "@/components/ui/sidebar";
import { ClinicalLayout } from "@/components/layout/ClinicalLayout";
import Dashboard from "./pages/Dashboard";
import Subjects from "./pages/Subjects";
import SubjectProfile from "./pages/SubjectProfile";
import AIChat from "./pages/AIChat";
import Discrepancies from "./pages/Discrepancies";
import QueryManagement from "./pages/QueryManagement";
import SourceDataVerification from "./pages/SourceDataVerification";
import ProtocolCompliance from "./pages/ProtocolCompliance";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchInterval: 30 * 1000, // 30 seconds for clinical monitoring
    },
  },
});

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <SidebarProvider>
          <div className="min-h-screen flex w-full bg-slate-50">
            <ClinicalLayout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/queries" element={<QueryManagement />} />
                <Route path="/sdv" element={<SourceDataVerification />} />
                <Route path="/compliance" element={<ProtocolCompliance />} />
                <Route path="/subjects" element={<Subjects />} />
                <Route path="/subjects/:subjectId" element={<SubjectProfile />} />
                <Route path="/discrepancies" element={<Discrepancies />} />
                <Route path="/ai-chat" element={<AIChat />} />
                <Route path="*" element={<NotFound />} />
              </Routes>
            </ClinicalLayout>
          </div>
        </SidebarProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
