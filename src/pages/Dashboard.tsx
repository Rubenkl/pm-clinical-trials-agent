
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  Users, 
  AlertTriangle, 
  MessageSquare, 
  Activity, 
  TrendingUp,
  Shield
} from "lucide-react";
import { ClinicalMetricsCard } from "@/components/dashboard/ClinicalMetricsCard";
import { StudyProgressChart } from "@/components/dashboard/StudyProgressChart";
import { RecentAnalysisTable } from "@/components/dashboard/RecentAnalysisTable";
import { CriticalAlertsPanel } from "@/components/dashboard/CriticalAlertsPanel";
import { apiService } from "@/services";

export default function Dashboard() {
  // Use demo data for comprehensive statistics 
  const { data: studyStatus, isLoading } = useQuery({
    queryKey: ['demo-study-status'],
    queryFn: () => apiService.getDashboardAnalytics(),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-slate-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-32 bg-slate-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Clinical Dashboard</h1>
          <p className="text-slate-600 mt-1">
            Protocol CARD-2025-001 • Cardiovascular Phase II Study
          </p>
        </div>
        <div className="text-right text-sm text-slate-500">
          Last updated: {new Date().toLocaleString()}
        </div>
      </div>

      {/* Critical Alerts Banner */}
      <Alert className="border-red-200 bg-red-50">
        <AlertTriangle className="h-4 w-4 text-red-600" />
        <AlertDescription className="text-red-800">
          <strong>3 Critical Clinical Alerts</strong> require immediate attention: CARD001 (severe anemia), CARD010 (age violation), CARD030 (age violation).
          <a href="/discrepancies" className="underline ml-2">View Details →</a>
        </AlertDescription>
      </Alert>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ClinicalMetricsCard
          title="Active Subjects"
          value="20/50"
          subtitle="40% enrollment (demo subset)"
          icon={Users}
          trend="+4 problem subjects analyzed"
          trendUp={true}
        />
        <ClinicalMetricsCard
          title="Critical Alerts"
          value="3"
          subtitle="Safety & compliance concerns"
          icon={AlertTriangle}
          trend="CARD001, CARD010, CARD030"
          trendUp={false}
          alertLevel="critical"
        />
        <ClinicalMetricsCard
          title="Open Queries"
          value="52"
          subtitle="From problem subjects"
          icon={MessageSquare}
          trend="12+13+13+14 discrepancies"
          trendUp={false}
        />
        <ClinicalMetricsCard
          title="AI Analysis"
          value="100%"
          subtitle="Real test data accuracy"
          icon={Activity}
          trend="Live demo ready"
          trendUp={true}
        />
        <ClinicalMetricsCard
          title="Clean Subjects"
          value="60%"
          subtitle="Zero discrepancies found" 
          icon={TrendingUp}
          trend="CARD003, 007, 008, 014+"
          trendUp={true}
        />
        <ClinicalMetricsCard
          title="Protocol Compliance"
          value="85%"
          subtitle="Age violations detected"
          icon={Shield}
          trend="2 critical deviations"
          trendUp={false}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Study Progress */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Study Progress & Enrollment
            </CardTitle>
          </CardHeader>
          <CardContent>
            <StudyProgressChart />
          </CardContent>
        </Card>

        {/* Critical Alerts */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-700">
              <AlertTriangle className="h-5 w-5" />
              Critical Alerts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <CriticalAlertsPanel />
          </CardContent>
        </Card>
      </div>

      {/* Recent AI Analysis */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Recent AI Clinical Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <RecentAnalysisTable />
        </CardContent>
      </Card>
    </div>
  );
}
