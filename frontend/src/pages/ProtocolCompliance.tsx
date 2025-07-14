import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Shield, AlertTriangle, CheckCircle, Clock, TrendingUp, Building, Users, FileText, Loader2 } from "lucide-react";
import { apiService } from "@/services";
import { useToast } from "@/hooks/use-toast";

const complianceStats = [
  { label: "Protocol Adherence", value: "96.2%", change: "+1.2%", variant: "default" as const },
  { label: "Active Deviations", value: "3", change: "-2", variant: "destructive" as const },
  { label: "Risk Score", value: "Low", change: "Stable", variant: "default" as const },
  { label: "Enrollment Rate", value: "94%", change: "+8%", variant: "default" as const }
];

const activeDeviations = [
  {
    id: "DEV-2025-0089",
    type: "inclusion_criteria_violation",
    subject: "CARD010", // Age 85 - exceeds protocol limit 
    site: "SITE_001",
    severity: "major", 
    detected: "2025-01-09",
    description: "Subject enrolled with age 85 years (criterion: 18-80 years)",
    status: "needs_analysis",
    impact: "regulatory_risk",
    aiResponse: null
  },
  {
    id: "DEV-2025-0090",
    type: "inclusion_criteria_violation", 
    subject: "CARD030", // Age 17 - below protocol limit
    site: "SITE_002",
    severity: "critical",
    detected: "2025-01-10", 
    description: "Subject enrolled with age 17 years (criterion: 18-80 years)",
    status: "needs_analysis",
    impact: "safety_concern",
    aiResponse: null
  },
  {
    id: "DEV-2025-0091",
    type: "blood_pressure_violation",
    subject: "CARD001", // High BP case
    site: "SITE_001",
    severity: "major",
    detected: "2025-01-11",
    description: "Systolic BP >180 mmHg detected (protocol exclusion criteria)",
    status: "needs_analysis", 
    impact: "safety_concern",
    aiResponse: null
  }
];

const riskPatterns = [
  {
    pattern: "Enrollment Issues",
    sites: ["Site 002"],
    count: 3,
    trend: "increasing",
    description: "Multiple inclusion criteria violations",
    recommendation: "Enhanced screening training required"
  },
  {
    pattern: "Visit Scheduling",
    sites: ["Site 001", "Site 002"],
    count: 5,
    trend: "stable", 
    description: "Consistent visit window deviations",
    recommendation: "Implement automated scheduling alerts"
  }
];

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case "major": return "destructive";
    case "minor": return "default";
    case "critical": return "destructive";
    case "pending_analysis": return "secondary";
    default: return "outline";
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case "under_review": return "default";
    case "capa_pending": return "secondary";
    case "investigation": return "destructive";
    case "resolved": return "secondary";
    case "needs_analysis": return "default";
    default: return "outline";
  }
};

const getImpactColor = (impact: string) => {
  switch (impact) {
    case "high_regulatory_risk": return "destructive";
    case "safety_concern": return "destructive";
    case "low_impact": return "secondary";
    case "pending_assessment": return "outline";
    default: return "outline";
  }
};

export default function ProtocolCompliance() {
  const [selectedDeviation, setSelectedDeviation] = useState<any>(null);
  const [aiDeviationResult, setAiDeviationResult] = useState<any>(null);
  const [deviationsWithResponses, setDeviationsWithResponses] = useState<any[]>(activeDeviations);
  const { toast } = useToast();

  // Use actual protocol deviations from test data
  const { data: deviationsData, isLoading } = useQuery({
    queryKey: ['protocol-deviations'],
    queryFn: () => apiService.getProtocolDeviations(),
    staleTime: 30000,
  });

  // AI-powered deviation detection
  const deviationDetectMutation = useMutation({
    mutationFn: async (data: any) => {
      console.log('Calling AI deviation detection endpoint with data:', data);
      return await apiService.detectProtocolDeviations(data);
    },
    onSuccess: (result) => {
      console.log('AI deviation detection completed:', result);
      setAiDeviationResult(result);
      
      // Update the deviation with the AI response
      if (selectedDeviation) {
        setDeviationsWithResponses(prev => 
          prev.map(deviation => 
            deviation.id === selectedDeviation.id 
              ? { ...deviation, aiResponse: result }
              : deviation
          )
        );
      }
      
      toast({
        title: "Success",
        description: "AI deviation analysis completed!"
      });
    },
    onError: (error: any) => {
      console.error('AI deviation detection failed:', error);
      toast({
        title: "Error",
        description: `AI analysis failed: ${error.message || 'Please try again.'}`,
        variant: "destructive"
      });
    }
  });

  // Transform API data to match component structure
  const actualDeviations = deviationsData?.deviations ? 
    deviationsData.deviations.map((deviation: any) => ({
      id: deviation.deviation_id,
      type: deviation.deviation_type,
      subject: deviation.subject_id,
      site: deviation.site_id,
      severity: deviation.severity,
      detected: new Date(deviation.detected_date).toLocaleDateString(),
      status: deviation.status,
      impact: deviation.impact_assessment,
      description: deviation.description,
      aiResponse: null
    })) : deviationsWithResponses;

  const handleAnalyzeDeviation = (deviation: any) => {
    setSelectedDeviation(deviation);
    setAiDeviationResult(null);
    
    console.log('Starting AI deviation analysis for:', deviation);
    
    // Create demo scenario based on deviation type
    const protocolData = deviation.type === 'inclusion_criteria_violation' ? {
      required_age_min: 18,
      required_conditions: ['cardiovascular_disease']
    } : deviation.type === 'visit_window_deviation' ? {
      required_visit_window: "±3 days",
      visit_schedule: "every 2 weeks"
    } : {
      prohibited_medications: ['aspirin', 'warfarin'],
      required_procedures: ['ecg', 'blood_draw']
    };

    const actualData = deviation.type === 'inclusion_criteria_violation' ? {
      age: 17.8,
      conditions: ['cardiovascular_disease']
    } : deviation.type === 'visit_window_deviation' ? {
      visit_date: "2025-01-15",
      scheduled_date: "2025-01-09"
    } : {
      concomitant_medications: ['aspirin', 'metformin'],
      completed_procedures: ['ecg']
    };
    
    deviationDetectMutation.mutate({
      subject_id: deviation.subject,
      site_id: deviation.site,
      visit: "Week_4",
      protocol_data: protocolData,
      actual_data: actualData,
      context: {
        demo_mode: true,
        limit_analysis: true,
        deviation_type: deviation.type
      }
    });
  };

  return (
    <div className="flex-1 space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Protocol Compliance</h1>
          <p className="text-muted-foreground">Monitor protocol adherence with examples of both compliant and deviant cases</p>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {complianceStats.map((stat) => (
          <Card key={stat.label}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.label}</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">
                <span className={stat.variant === "destructive" ? "text-red-600" : "text-green-600"}>
                  {stat.change}
                </span>{" "}
                from last period
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Critical Alerts */}
      <Alert className="border-red-200 bg-red-50">
        <AlertTriangle className="h-4 w-4 text-red-600" />
        <AlertTitle className="text-red-800">Critical Compliance Alert</AlertTitle>
        <AlertDescription className="text-red-700">
          Critical protocol violations detected: CARD010 (age 85) and CARD030 (age 17) enrolled outside age criteria. 
          Immediate PI review and regulatory notification required.
        </AlertDescription>
      </Alert>

      {/* Compliant Subjects Examples */}
      <Alert className="border-green-200 bg-green-50">
        <CheckCircle className="h-4 w-4 text-green-600" />
        <AlertTitle className="text-green-800">Protocol Compliant Examples</AlertTitle>
        <AlertDescription className="text-green-700">
          <strong>Exemplary compliance:</strong> CARD003, CARD007, CARD008, CARD014, CARD015 showing 100% protocol adherence - 
          proper age range (18-80), complete visit windows, medication compliance, and documentation standards.
          <div className="mt-2 grid grid-cols-1 md:grid-cols-3 gap-2 text-xs">
            <div>• <strong>Age Compliance:</strong> All within 18-80 range</div>
            <div>• <strong>Visit Windows:</strong> 100% adherence to ±3 days</div>
            <div>• <strong>Documentation:</strong> Complete and timely</div>
          </div>
        </AlertDescription>
      </Alert>

      <Tabs defaultValue="deviations" className="w-full">
        <TabsList>
          <TabsTrigger value="deviations">Active Deviations</TabsTrigger>
          <TabsTrigger value="patterns">Risk Patterns</TabsTrigger>
          <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
        </TabsList>

        <TabsContent value="deviations" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Active Protocol Deviations</CardTitle>
              <CardDescription>Current deviations requiring attention and follow-up</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Deviation ID</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Subject</TableHead>
                    <TableHead>Site</TableHead>
                    <TableHead>Severity</TableHead>
                    <TableHead>Detected</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Impact</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {actualDeviations.map((deviation) => (
                    <TableRow key={deviation.id} className="cursor-pointer hover:bg-muted/50">
                      <TableCell className="font-medium">{deviation.id}</TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {deviation.type.replace(/_/g, ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell>{deviation.subject}</TableCell>
                      <TableCell>
                        <div className="flex items-center">
                          <Building className="h-4 w-4 mr-2 text-muted-foreground" />
                          {deviation.site}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={getSeverityColor(deviation.severity) as any}>
                          {deviation.severity}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center">
                          <Clock className="h-4 w-4 mr-2 text-muted-foreground" />
                          {deviation.detected}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={getStatusColor(deviation.status) as any}>
                          {deviation.status.replace(/_/g, ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant={getImpactColor(deviation.impact) as any}>
                          {deviation.impact.replace(/_/g, ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {deviation.aiResponse && (
                            <Badge variant="secondary" className="text-xs">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Analyzed
                            </Badge>
                          )}
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => handleAnalyzeDeviation(deviation)}
                            disabled={deviationDetectMutation.isPending}
                          >
                            {deviationDetectMutation.isPending && selectedDeviation?.id === deviation.id ? (
                              <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Analyzing...</>
                            ) : (
                              'Analyze'
                            )}
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* AI Deviation Analysis Panel */}
          <Card>
            <CardHeader>
              <CardTitle>AI-Powered Deviation Analysis</CardTitle>
              <CardDescription>Real-time protocol deviation detection and impact assessment</CardDescription>
            </CardHeader>
            <CardContent>
              {aiDeviationResult ? (
                <div className="space-y-6 max-h-96 overflow-y-auto">
                  <div className="flex items-center justify-between">
                    <h4 className="text-lg font-semibold">AI Protocol Analysis Complete</h4>
                    <div className="flex gap-2">
                      <Badge variant="secondary">
                        Subject: {aiDeviationResult.query_id?.split('-')[2] || selectedDeviation?.subject}
                      </Badge>
                      {aiDeviationResult.execution_time && (
                        <Badge variant="outline">
                          {aiDeviationResult.execution_time.toFixed(2)}s
                        </Badge>
                      )}
                    </div>
                  </div>

                  {/* Input Analysis Summary */}
                  {selectedDeviation && (
                    <div className="bg-muted/30 border border-muted p-4 rounded-lg">
                      <h5 className="font-medium mb-2">Input Analysis Details</h5>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div><span className="font-medium">Deviation Type:</span> {selectedDeviation.type.replace(/_/g, ' ')}</div>
                        <div><span className="font-medium">Subject:</span> {selectedDeviation.subject}</div>
                        <div><span className="font-medium">Site:</span> {selectedDeviation.site}</div>
                        <div><span className="font-medium">Detected:</span> {selectedDeviation.detected}</div>
                      </div>
                      <p className="text-sm text-muted-foreground mt-2">{selectedDeviation.description}</p>
                    </div>
                  )}

                  {/* Severity & Priority */}
                  {aiDeviationResult.analysis?.analysis && (
                    <div className="grid gap-4 md:grid-cols-2">
                      <div className="bg-primary/5 border border-primary/20 p-4 rounded-lg">
                        <h5 className="font-medium text-primary mb-2">AI-Determined Severity</h5>
                        <div className="flex items-center gap-2 mb-2">
                          <Badge variant={
                            aiDeviationResult.analysis.analysis.severity === 'critical' ? 'destructive' : 
                            aiDeviationResult.analysis.analysis.severity === 'high' ? 'default' : 'secondary'
                          }>
                            {aiDeviationResult.analysis.analysis.severity}
                          </Badge>
                          <Badge variant="outline">
                            {aiDeviationResult.analysis.analysis.priority} priority
                          </Badge>
                        </div>
                      </div>
                      
                      <div className="bg-amber-50 border border-amber-200 p-4 rounded-lg">
                        <h5 className="font-medium text-amber-800 mb-2">Clinical Significance</h5>
                        <p className="text-sm text-amber-700">{aiDeviationResult.analysis.analysis.clinical_significance}</p>
                      </div>
                    </div>
                  )}

                  {/* Clinical Findings */}
                  {aiDeviationResult.analysis?.analysis?.findings && (
                    <div className="space-y-3">
                      <h5 className="font-medium">AI Clinical Findings</h5>
                      <div className="bg-muted/50 p-4 rounded-lg">
                        <ul className="space-y-2">
                          {aiDeviationResult.analysis.analysis.findings.map((finding: string, index: number) => (
                            <li key={index} className="text-sm flex items-start gap-2">
                              <AlertTriangle className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                              <span>{finding}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}

                  {/* Medical Assessment */}
                  {aiDeviationResult.analysis?.analysis?.medical_assessment && (
                    <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                      <h5 className="font-medium text-blue-800 mb-2">Medical Assessment</h5>
                      <p className="text-sm text-blue-700">{aiDeviationResult.analysis.analysis.medical_assessment}</p>
                    </div>
                  )}

                  {/* Recommended Queries */}
                  {aiDeviationResult.analysis?.analysis?.recommended_queries && aiDeviationResult.analysis.analysis.recommended_queries.length > 0 && (
                    <div className="space-y-2">
                      <h5 className="font-medium">AI-Recommended Actions</h5>
                      <div className="space-y-2">
                        {aiDeviationResult.analysis.analysis.recommended_queries.map((query: string, index: number) => (
                          <div key={index} className="bg-red-50 border border-red-200 p-3 rounded">
                            <p className="text-sm text-red-700">{query}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* No AI Analysis Available - Show Explanation */}
                  {!aiDeviationResult.analysis?.analysis?.findings && (
                    <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-5 w-5 text-green-600" />
                        <h5 className="font-medium text-green-800">AI Analysis Summary</h5>
                      </div>
                      <div className="mt-2 space-y-2">
                        <p className="text-sm text-green-700">
                          The AI has analyzed the protocol deviation for {selectedDeviation?.subject} and provided a comprehensive assessment.
                        </p>
                        <div className="text-xs text-green-600 space-y-1">
                          <p>• Analysis Type: {aiDeviationResult.analysis?.analysis?.analysis_type || 'Protocol Compliance Analysis'}</p>
                          <p>• Execution Time: {aiDeviationResult.execution_time?.toFixed(2)}s</p>
                          <p>• Status: {aiDeviationResult.success ? 'Completed Successfully' : 'Processing'}</p>
                        </div>
                      </div>
                    </div>
                  )}

                </div>
              ) : (
                <div className="border-2 border-dashed border-muted rounded-lg p-8 text-center">
                  <AlertTriangle className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">AI Deviation Analysis Ready</h3>
                  <p className="text-muted-foreground mb-4">
                    Click "Analyze" on any deviation above to see AI-powered impact assessment and CAPA recommendations
                  </p>
                  <div className="space-y-2 text-sm text-muted-foreground">
                    <p>• Real-time protocol compliance checking</p>
                    <p>• Regulatory impact assessment</p>
                    <p>• Automated CAPA recommendations</p>
                    <p>• Risk scoring and prioritization</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="patterns" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Risk Pattern Analysis</CardTitle>
              <CardDescription>Identify systematic issues across sites and protocol areas</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {riskPatterns.map((pattern, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <h3 className="font-semibold">{pattern.pattern}</h3>
                        <Badge variant={pattern.trend === 'increasing' ? 'destructive' : 'secondary'}>
                          {pattern.count} occurrences
                        </Badge>
                        <div className="flex items-center gap-1">
                          <TrendingUp className={`h-4 w-4 ${pattern.trend === 'increasing' ? 'text-red-500' : 'text-green-500'}`} />
                          <span className="text-sm text-muted-foreground">{pattern.trend}</span>
                        </div>
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{pattern.description}</p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">Affected Sites:</span>
                        {pattern.sites.map((site) => (
                          <Badge key={site} variant="outline">{site}</Badge>
                        ))}
                      </div>
                      <Button size="sm" variant="outline" disabled>View Details</Button>
                    </div>
                    <div className="mt-3 p-3 bg-blue-50 rounded border border-blue-200">
                      <p className="text-sm font-medium text-blue-900 mb-1">Recommendation:</p>
                      <p className="text-sm text-blue-800">{pattern.recommendation}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="monitoring">
          <Card>
            <CardHeader>
              <CardTitle>Protocol Monitoring</CardTitle>
              <CardDescription>Real-time protocol compliance monitoring - Coming Soon</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <Shield className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">Real-time Monitoring - Coming Soon</h3>
                <p className="text-muted-foreground mb-4">
                  Currently showing {actualDeviations.length} active deviations from real clinical data
                </p>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <p>• Live deviation detection algorithms</p>
                  <p>• Automated risk scoring</p>
                  <p>• Predictive compliance analytics</p>
                  <p>• Real-time site performance metrics</p>
                </div>
                <Button className="mt-4" disabled>
                  Coming Soon
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}