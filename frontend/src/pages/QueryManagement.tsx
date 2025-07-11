import { useState, useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Separator } from "@/components/ui/separator";
import { AlertCircle, Clock, CheckCircle, User, Building, Play, Loader2, Brain, FileText } from "lucide-react";
import { apiService } from "@/services";
import { toast } from "sonner";

export default function QueryManagement() {
  const [selectedDemo, setSelectedDemo] = useState<any>(null);
  const [aiAnalysisResult, setAiAnalysisResult] = useState<any>(null);

  // Fetch demo test data (limited to 10 for cost efficiency)
  const { data: queries, isLoading } = useQuery({
    queryKey: ['demo-queries'],
    queryFn: () => apiService.getDemoQueries(10),
  });

  // AI Query Analysis Mutation - Call REAL AI endpoint
  const analyzeQueryMutation = useMutation({
    mutationFn: async (data: any) => {
      console.log('Calling AI analysis endpoint with data:', data);
      // Use the direct query service analyze method which calls /api/v1/queries/analyze
      return await apiService.analyzeQuery(data);
    },
    onSuccess: (result) => {
      console.log('AI analysis completed:', result);
      setAiAnalysisResult(result);
      
      // Update the scenario with the AI response
      if (selectedDemo) {
        setScenariosWithResponses(prev => 
          prev.map(scenario => 
            scenario.id === selectedDemo.id 
              ? { ...scenario, aiResponse: result }
              : scenario
          )
        );
      }
      
      toast.success("AI analysis completed!");
    },
    onError: (error) => {
      console.error('AI analysis failed:', error);
      toast.error(`AI analysis failed: ${error.message || 'Please try again.'}`);
    }
  });

  // Demo data scenarios for AI analysis
  const demoScenarios = [
    {
      id: 1,
      title: "Critical Lab Value: Severe Anemia",
      subject_id: "CARD001",
      site_id: "SITE_001", 
      visit: "Week_4",
      field_name: "hemoglobin",
      field_value: "8.5",
      expected_value: "12.5",
      form_name: "Laboratory Results",
      description: "Hemoglobin dropped from 12.5 to 8.5 g/dL",
      aiResponse: null
    },
    {
      id: 2,
      title: "Blood Pressure Discrepancy",
      subject_id: "CARD002",
      site_id: "SITE_002",
      visit: "Week_4", 
      field_name: "systolic_bp",
      field_value: "185",
      expected_value: "140",
      form_name: "Vital Signs",
      description: "Systolic BP elevated to 185 mmHg",
      aiResponse: null
    },
    {
      id: 3,
      title: "Cardiac Function Alert",
      subject_id: "CARD003",
      site_id: "SITE_001",
      visit: "Week_16",
      field_name: "lvef",
      field_value: "35",
      expected_value: "55", 
      form_name: "Echocardiogram",
      description: "LVEF decreased from 55% to 35%",
      aiResponse: null
    }
  ];

  const [scenariosWithResponses, setScenariosWithResponses] = useState<any[]>(demoScenarios);

  const handleRunAIAnalysis = (scenario: any) => {
    setSelectedDemo(scenario);
    setAiAnalysisResult(null);
    
    console.log('Starting AI analysis for scenario:', scenario);
    
    analyzeQueryMutation.mutate({
      subject_id: scenario.subject_id,
      site_id: scenario.site_id,
      visit: scenario.visit,
      field_name: scenario.field_name,
      field_value: scenario.field_value,
      expected_value: scenario.expected_value,
      form_name: scenario.form_name,
      context: {
        demo_mode: true,
        limit_analysis: true,
        initials: "DEMO",
        site_name: `Site ${scenario.site_id}`
      }
    });
  };

  if (isLoading) {
    return (
      <div className="flex-1 space-y-6 p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <Loader2 className="h-12 w-12 mx-auto text-muted-foreground mb-4 animate-spin" />
            <p className="text-muted-foreground">Loading demo data...</p>
          </div>
        </div>
      </div>
    );
  }
  return (
    <div className="flex-1 space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Query Analysis Demo</h1>
          <p className="text-muted-foreground">
            Demonstrating AI-powered clinical query analysis with real test data (limited to 10 samples for cost efficiency)
          </p>
        </div>
      </div>

      {/* Demo Statistics */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Test Data Queries</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{queries?.length || 0}</div>
            <p className="text-xs text-muted-foreground">Limited for demo</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">AI Scenarios</CardTitle>
            <Brain className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{scenariosWithResponses.filter(s => s.aiResponse).length}/{demoScenarios.length}</div>
            <p className="text-xs text-muted-foreground">Ready for analysis</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">LLM Cost Control</CardTitle>
            <AlertCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">ON</div>
            <p className="text-xs text-muted-foreground">10 sample limit</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Demo Mode</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">ACTIVE</div>
            <p className="text-xs text-muted-foreground">Limited analysis</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Test Data Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Demo Input Scenarios
            </CardTitle>
            <CardDescription>
              Select a clinical scenario to send to AI agents for analysis
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {scenariosWithResponses.map((scenario) => (
              <div key={scenario.id} className="border rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">{scenario.title}</h4>
                  <div className="flex items-center gap-2">
                    {scenario.aiResponse && (
                      <Badge variant="secondary" className="text-xs">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Analyzed
                      </Badge>
                    )}
                    <Button 
                      size="sm" 
                      onClick={() => handleRunAIAnalysis(scenario)}
                      disabled={analyzeQueryMutation.isPending}
                      className="flex items-center gap-2"
                    >
                      {analyzeQueryMutation.isPending ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Play className="h-4 w-4" />
                      )}
                      Analyze
                    </Button>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-muted-foreground">Subject:</span> {scenario.subject_id}
                  </div>
                  <div>
                    <span className="text-muted-foreground">Visit:</span> {scenario.visit}
                  </div>
                  <div>
                    <span className="text-muted-foreground">Field:</span> {scenario.field_name}
                  </div>
                  <div>
                    <span className="text-muted-foreground">Value:</span> {scenario.field_value}
                  </div>
                </div>
                <p className="text-sm text-muted-foreground">{scenario.description}</p>
                
                {scenario.aiResponse && (
                  <div className="mt-3 p-3 bg-muted/30 rounded border-l-2 border-primary">
                    <div className="text-xs text-muted-foreground mb-1">Latest AI Analysis:</div>
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant={
                        scenario.aiResponse.analysis?.severity === 'critical' ? 'destructive' : 
                        scenario.aiResponse.analysis?.severity === 'major' ? 'default' : 'secondary'
                      }>
                        {scenario.aiResponse.analysis?.severity || 'analyzed'}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        {scenario.aiResponse.analysis?.priority || 'standard'}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {scenario.aiResponse.analysis?.clinical_significance || 'Analysis completed'}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </CardContent>
        </Card>

        {/* AI Analysis Results Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              AI Agent Response
            </CardTitle>
            <CardDescription>
              Medical intelligence analysis from AI agents
            </CardDescription>
          </CardHeader>
          <CardContent>
            {analyzeQueryMutation.isPending ? (
              <div className="flex items-center justify-center h-48">
                <div className="text-center space-y-4">
                  <Loader2 className="h-8 w-8 mx-auto animate-spin text-primary" />
                  <p className="text-sm text-muted-foreground">AI agents analyzing clinical data...</p>
                </div>
              </div>
            ) : aiAnalysisResult ? (
              <div className="space-y-4 max-h-96 overflow-y-auto">
                <div className="border-l-4 border-primary pl-4">
                  <h4 className="font-medium text-primary">Analysis Complete</h4>
                  <p className="text-sm text-muted-foreground">Query ID: {aiAnalysisResult.query_id}</p>
                  {aiAnalysisResult.execution_time && (
                    <p className="text-xs text-muted-foreground">Execution time: {aiAnalysisResult.execution_time.toFixed(2)}s</p>
                  )}
                </div>

                {/* Clinical Significance & Severity */}
                {aiAnalysisResult.analysis && (
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="bg-primary/5 border border-primary/20 p-4 rounded-lg">
                      <h5 className="font-medium text-primary mb-2">Severity & Priority</h5>
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant={
                          aiAnalysisResult.analysis.severity === 'critical' ? 'destructive' : 
                          aiAnalysisResult.analysis.severity === 'major' ? 'default' : 'secondary'
                        }>
                          {aiAnalysisResult.analysis.severity}
                        </Badge>
                        <Badge variant="outline">
                          {aiAnalysisResult.analysis.priority} priority
                        </Badge>
                      </div>
                    </div>
                    
                    <div className="bg-amber-50 border border-amber-200 p-4 rounded-lg">
                      <h5 className="font-medium text-amber-800 mb-2">Clinical Significance</h5>
                      <p className="text-sm text-amber-700">{aiAnalysisResult.analysis.clinical_significance}</p>
                    </div>
                  </div>
                )}
                
                {/* Clinical Findings */}
                {aiAnalysisResult.analysis?.findings && (
                  <div className="space-y-3">
                    <h5 className="font-medium">Clinical Findings</h5>
                    <div className="bg-muted/50 p-4 rounded-lg">
                      <ul className="space-y-2">
                        {aiAnalysisResult.analysis.findings.map((finding: string, index: number) => (
                          <li key={index} className="text-sm flex items-start gap-2">
                            <AlertCircle className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                            <span>{finding}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Medical Assessment */}
                {aiAnalysisResult.analysis?.medical_assessment && (
                  <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg">
                    <h5 className="font-medium text-blue-800 mb-2">Medical Assessment</h5>
                    <p className="text-sm text-blue-700">{aiAnalysisResult.analysis.medical_assessment}</p>
                  </div>
                )}

                {/* Recommended Queries */}
                {aiAnalysisResult.analysis?.recommended_queries && aiAnalysisResult.analysis.recommended_queries.length > 0 && (
                  <div className="space-y-2">
                    <h5 className="font-medium">Recommended Queries</h5>
                    <div className="space-y-2">
                      {aiAnalysisResult.analysis.recommended_queries.map((query: string, index: number) => (
                        <div key={index} className="bg-red-50 border border-red-200 p-3 rounded">
                          <p className="text-sm text-red-700">{query}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : selectedDemo ? (
              <div className="flex items-center justify-center h-48">
                <div className="text-center space-y-4">
                  <AlertCircle className="h-8 w-8 mx-auto text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">
                    Click "Analyze" to see AI agent analysis
                  </p>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-48">
                <div className="text-center space-y-4">
                  <Brain className="h-8 w-8 mx-auto text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">
                    Select a scenario to begin AI analysis
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* API Test Data Section */}
      {queries && queries.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Live API Test Data</CardTitle>
            <CardDescription>
              Actual queries from {queries.length} test data samples (limited for demo cost efficiency)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Query ID</TableHead>
                  <TableHead>Subject</TableHead>
                  <TableHead>Field</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Description</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {queries.slice(0, 5).map((query: any) => (
                  <TableRow key={query.query_id}>
                    <TableCell className="font-mono text-sm">{query.query_id}</TableCell>
                    <TableCell>{query.subject_id}</TableCell>
                    <TableCell>{query.field}</TableCell>
                    <TableCell>
                      <Badge variant={
                        query.severity === 'critical' ? 'destructive' : 
                        query.severity === 'major' ? 'default' : 'secondary'
                      }>
                        {query.severity}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{query.status}</Badge>
                    </TableCell>
                    <TableCell className="max-w-xs truncate">{query.description}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            {queries.length > 5 && (
              <p className="text-sm text-muted-foreground mt-4">
                Showing 5 of {queries.length} total queries (limited for demo)
              </p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}