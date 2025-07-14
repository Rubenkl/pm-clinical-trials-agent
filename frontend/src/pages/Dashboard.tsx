
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
  // Fetch real data from available endpoints
  const { data: subjects, isLoading: subjectsLoading } = useQuery({
    queryKey: ['subjects'],
    queryFn: () => apiService.getSubjects(),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  const { data: studyStatus, isLoading: statusLoading } = useQuery({
    queryKey: ['study-status'],
    queryFn: () => apiService.getStudyStatus(),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  const isLoading = subjectsLoading || statusLoading;

  // Calculate metrics from real data
  const activeSubjects = subjects?.filter((s: any) => s.study_status === 'active').length || 0;
  const totalSubjects = subjects?.length || 0;
  const completedSubjects = subjects?.filter((s: any) => s.study_status === 'completed').length || 0;
  const enrollmentPercentage = totalSubjects > 0 ? Math.round((totalSubjects / 50) * 100) : 0;

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

      {/* Study Status Info */}
      <Alert className="border-blue-200 bg-blue-50">
        <Activity className="h-4 w-4 text-blue-600" />
        <AlertDescription className="text-blue-800">
          <strong>{studyStatus?.protocol || "Clinical Trial"}</strong> • {studyStatus?.phase || "Phase II"} • 
          Status: {studyStatus?.status || "Active"} • {studyStatus?.subjects_enrolled || totalSubjects} subjects enrolled
          <a href="/subjects" className="underline ml-2">View Subjects →</a>
        </AlertDescription>
      </Alert>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ClinicalMetricsCard
          title="Total Subjects"
          value={`${totalSubjects}/50`}
          subtitle={`${enrollmentPercentage}% enrollment`}
          icon={Users}
          trend={`${activeSubjects} active, ${completedSubjects} completed`}
          trendUp={true}
        />
        <ClinicalMetricsCard
          title="Study Status"
          value={studyStatus?.status || "Active"}
          subtitle={studyStatus?.phase || "Phase II"}
          icon={Activity}
          trend={`Started: ${studyStatus?.start_date || "2025-03-01"}`}
          trendUp={true}
        />
        <ClinicalMetricsCard
          title="Enrollment Progress"
          value={`${studyStatus?.subjects_enrolled || totalSubjects}/${studyStatus?.target_enrollment || 60}`}
          subtitle="Target enrollment"
          icon={TrendingUp}
          trend={`${Math.round(((studyStatus?.subjects_enrolled || totalSubjects) / (studyStatus?.target_enrollment || 60)) * 100)}% complete`}
          trendUp={true}
        />
        <ClinicalMetricsCard
          title="Active Sites"
          value={studyStatus?.sites_active?.toString() || "3"}
          subtitle="Research sites"
          icon={Shield}
          trend="All sites active"
          trendUp={true}
        />
        <ClinicalMetricsCard
          title="Study Timeline"
          value={studyStatus?.estimated_completion ? new Date(studyStatus.estimated_completion).toLocaleDateString() : "Dec 2025"}
          subtitle="Estimated completion"
          icon={MessageSquare}
          trend={studyStatus?.status === "Active" ? "On track" : "In progress"}
          trendUp={true}
        />
        <ClinicalMetricsCard
          title="Protocol"
          value={studyStatus?.study_id || "CARD-2025-001"}
          subtitle="Study identifier"
          icon={AlertTriangle}
          trend={studyStatus?.protocol || "Cardiovascular Phase 2"}
          trendUp={true}
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
