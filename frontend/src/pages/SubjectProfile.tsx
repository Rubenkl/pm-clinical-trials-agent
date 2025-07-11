
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  ArrowLeft, 
  User, 
  Activity, 
  TestTube, 
  Heart, 
  AlertTriangle,
  FileText,
  Bot
} from "lucide-react";
import { ClinicalVitalsChart } from "@/components/clinical/ClinicalVitalsChart";
import { LabValuesChart } from "@/components/clinical/LabValuesChart";
import { ClinicalAlerts } from "@/components/clinical/ClinicalAlerts";
import { DiscrepanciesPanel } from "@/components/clinical/DiscrepanciesPanel";
import { apiService } from "@/services";

export default function SubjectProfile() {
  const { subjectId } = useParams<{ subjectId: string }>();

  const { data: subject, isLoading, error } = useQuery({
    queryKey: ['subject', subjectId],
    queryFn: () => apiService.getSubjectData(subjectId!),
    enabled: !!subjectId,
  });

  const { data: discrepanciesData } = useQuery({
    queryKey: ['discrepancies', subjectId],
    queryFn: () => apiService.getSubjectDiscrepancies(subjectId!),
    enabled: !!subjectId,
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-slate-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="h-64 bg-slate-200 rounded"></div>
            <div className="h-64 bg-slate-200 rounded"></div>
            <div className="h-64 bg-slate-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !subject) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button asChild variant="ghost">
            <Link to="/subjects">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Subjects
            </Link>
          </Button>
        </div>
        <Card>
          <CardContent className="p-6 text-center">
            <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <p className="text-slate-600">Subject not found or failed to load.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const getClinicalAlerts = () => {
    const alerts = [];
    
    // Check latest vital signs
    const latestVitals = subject.clinical_data.vital_signs?.[subject.clinical_data.vital_signs.length - 1];
    if (latestVitals) {
      if (latestVitals.systolic_bp >= 140 || latestVitals.diastolic_bp >= 90) {
        alerts.push({
          severity: "Major" as const,
          message: latestVitals.systolic_bp >= 160 ? "Stage 2 Hypertension" : "Stage 1 Hypertension",
          description: `BP ${latestVitals.systolic_bp}/${latestVitals.diastolic_bp} mmHg`
        });
      }
    }

    // Check latest lab values
    const latestLabs = subject.clinical_data.laboratory?.[subject.clinical_data.laboratory.length - 1];
    if (latestLabs) {
      if (latestLabs.bnp > 300) {
        alerts.push({
          severity: latestLabs.bnp > 400 ? "Critical" as const : "Major" as const,
          message: "Elevated BNP",
          description: `BNP ${latestLabs.bnp.toFixed(1)} pg/mL (Normal <100)`
        });
      }
      if (latestLabs.creatinine > 1.5) {
        alerts.push({
          severity: "Major" as const,
          message: "Kidney Dysfunction",
          description: `Creatinine ${latestLabs.creatinine} mg/dL (Normal <1.2)`
        });
      }
    }

    return alerts;
  };

  const clinicalAlerts = getClinicalAlerts();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button asChild variant="ghost">
            <Link to="/subjects">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Subjects
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
              <User className="h-8 w-8 text-blue-600" />
              Subject {subject.subject_id}
            </h1>
            <p className="text-slate-600 mt-1">
              {subject.demographics.age}{subject.demographics.gender} • 
              Enrolled {new Date(subject.demographics.enrollment_date).toLocaleDateString()} • 
              {subject.site_id}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <FileText className="h-4 w-4 mr-2" />
            Generate Report
          </Button>
          <Button>
            <Bot className="h-4 w-4 mr-2" />
            AI Analysis
          </Button>
        </div>
      </div>

      {/* Subject Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Status</p>
                <Badge className={`mt-1 ${
                  subject.study_status === 'active' ? 'bg-green-100 text-green-800' :
                  subject.study_status === 'withdrawn' ? 'bg-red-100 text-red-800' :
                  'bg-slate-100 text-slate-800'
                }`}>
                  {subject.study_status.charAt(0).toUpperCase() + subject.study_status.slice(1)}
                </Badge>
              </div>
              <User className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Clinical Alerts</p>
                
                <p className={`text-2xl font-bold ${
                  clinicalAlerts.length >= 3 ? 'text-red-600' :
                  clinicalAlerts.length >= 1 ? 'text-amber-600' :
                  'text-green-600'
                }`}>
                  {clinicalAlerts.length}
                </p>
              </div>
              <AlertTriangle className={`h-8 w-8 ${
                clinicalAlerts.length >= 3 ? 'text-red-600' :
                clinicalAlerts.length >= 1 ? 'text-amber-600' :
                'text-green-600'
              }`} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Discrepancies</p>
                <p className="text-2xl font-bold text-amber-600">
                  {discrepanciesData?.discrepancies?.length || 48}
                </p>
              </div>
              <FileText className="h-8 w-8 text-amber-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Site</p>
                <p className="text-lg font-semibold">{subject.site_id}</p>
              </div>
              <Activity className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Clinical Alerts Banner */}
      {clinicalAlerts.length > 0 && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
              <div className="flex-1">
                <h3 className="font-medium text-red-900 mb-2">Clinical Alerts Requiring Attention</h3>
                <div className="space-y-1">
                  {clinicalAlerts.map((alert, index) => (
                    <div key={index} className="text-sm">
                      <span className="font-medium text-red-800">{alert.message}:</span>
                      <span className="text-red-700 ml-2">{alert.description}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="vitals">Vital Signs</TabsTrigger>
          <TabsTrigger value="labs">Laboratory</TabsTrigger>
          <TabsTrigger value="imaging">Imaging</TabsTrigger>
          <TabsTrigger value="discrepancies">Discrepancies</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Demographics */}
            <Card>
              <CardHeader>
                <CardTitle>Demographics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-slate-600">Age</p>
                    <p className="font-medium">{subject.demographics.age} years</p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-600">Gender</p>
                    <p className="font-medium">{subject.demographics.gender === 'M' ? 'Male' : 'Female'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-600">Race</p>
                    <p className="font-medium">{subject.demographics.race}</p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-600">Weight</p>
                    <p className="font-medium">{subject.demographics.weight} kg</p>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-slate-600">Height</p>
                  <p className="font-medium">{subject.demographics.height} cm</p>
                </div>
                <div>
                  <p className="text-sm text-slate-600">Enrollment Date</p>
                  <p className="font-medium">{new Date(subject.demographics.enrollment_date).toLocaleDateString()}</p>
                </div>
              </CardContent>
            </Card>

            {/* Clinical Alerts */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  Clinical Alerts
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ClinicalAlerts alerts={clinicalAlerts} />
              </CardContent>
            </Card>
          </div>

          {/* Latest Clinical Summary */}
          <Card>
            <CardHeader>
              <CardTitle>Latest Clinical Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {subject.clinical_data.vital_signs?.length > 0 && (
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <h4 className="font-medium text-blue-900 mb-2">Latest Vitals</h4>
                    {(() => {
                      const latest = subject.clinical_data.vital_signs[subject.clinical_data.vital_signs.length - 1];
                      return (
                        <div className="space-y-1 text-sm">
                          <p>BP: {latest.systolic_bp}/{latest.diastolic_bp} mmHg</p>
                          <p>HR: {latest.heart_rate} bpm</p>
                          <p>Weight: {latest.weight} kg</p>
                          <p className="text-blue-700 font-medium">{latest.visit}</p>
                        </div>
                      );
                    })()}
                  </div>
                )}

                {subject.clinical_data.laboratory?.length > 0 && (
                  <div className="p-4 bg-green-50 rounded-lg">
                    <h4 className="font-medium text-green-900 mb-2">Latest Labs</h4>
                    {(() => {
                      const latest = subject.clinical_data.laboratory[subject.clinical_data.laboratory.length - 1];
                      return (
                        <div className="space-y-1 text-sm">
                          <p>BNP: {latest.bnp.toFixed(1)} pg/mL</p>
                          <p>Creatinine: {latest.creatinine} mg/dL</p>
                          <p>Troponin: {latest.troponin.toFixed(2)} ng/mL</p>
                          <p className="text-green-700 font-medium">{latest.visit}</p>
                        </div>
                      );
                    })()}
                  </div>
                )}

                {subject.clinical_data.imaging?.length > 0 && (
                  <div className="p-4 bg-purple-50 rounded-lg">
                    <h4 className="font-medium text-purple-900 mb-2">Latest Imaging</h4>
                    {(() => {
                      const latest = subject.clinical_data.imaging[subject.clinical_data.imaging.length - 1];
                      return (
                        <div className="space-y-1 text-sm">
                          <p>LVEF: {latest.lvef}%</p>
                          <p className="text-purple-700 font-medium">{latest.visit}</p>
                          {latest.findings && <p className="text-xs">{latest.findings}</p>}
                        </div>
                      );
                    })()}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="vitals">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Vital Signs Trends
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ClinicalVitalsChart data={subject.clinical_data.vital_signs || []} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="labs">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TestTube className="h-5 w-5" />
                Laboratory Values
              </CardTitle>
            </CardHeader>
            <CardContent>
              <LabValuesChart data={subject.clinical_data.laboratory || []} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="imaging">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Heart className="h-5 w-5" />
                Imaging Results
              </CardTitle>
            </CardHeader>
            <CardContent>
              {subject.clinical_data.imaging?.length > 0 ? (
                <div className="space-y-4">
                  {subject.clinical_data.imaging.map((imaging, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-medium">{imaging.visit}</h4>
                        <span className="text-sm text-slate-500">
                          {new Date(imaging.date).toLocaleDateString()}
                        </span>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-slate-600">LVEF</p>
                          <p className="text-lg font-semibold">{imaging.lvef}%</p>
                        </div>
                      </div>
                      {imaging.findings && (
                        <div className="mt-3">
                          <p className="text-sm text-slate-600">Findings</p>
                          <p className="text-sm">{imaging.findings}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-slate-500 text-center py-8">No imaging data available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="discrepancies">
          <DiscrepanciesPanel 
            subjectId={subject.subject_id} 
            discrepancies={discrepanciesData?.discrepancies || []} 
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
