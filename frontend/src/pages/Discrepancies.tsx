
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { AlertTriangle, Search, FileText, Eye, CheckCircle, Clock } from "lucide-react";
import { Link } from "react-router-dom";
import { apiService } from "@/services";

export default function Discrepancies() {
  const [searchTerm, setSearchTerm] = useState("");
  const [severityFilter, setSeverityFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");

  // Fetch real subjects data
  const { data: subjects, isLoading } = useQuery({
    queryKey: ['subjects'],
    queryFn: () => apiService.getSubjects()
  });

  // Get discrepancies for all subjects
  const { data: allDiscrepancies, isLoading: discrepanciesLoading } = useQuery({
    queryKey: ['all-discrepancies'],
    queryFn: async () => {
      if (!subjects) return [];
      const discrepancyData = await Promise.all(
        subjects.map(async (subject: any) => {
          try {
            const result = await apiService.getSubjectDiscrepancies(subject.subject_id);
            return {
              subject_id: subject.subject_id,
              discrepancies: result.discrepancies || [],
              total_discrepancies: result.discrepancies?.length || 0,
              critical: result.discrepancies?.filter((d: any) => d.severity === 'critical').length || 0,
              major: result.discrepancies?.filter((d: any) => d.severity === 'major').length || 0,
              minor: result.discrepancies?.filter((d: any) => d.severity === 'minor').length || 0,
              open: result.discrepancies?.filter((d: any) => d.status === 'open').length || 0,
              pending: result.discrepancies?.filter((d: any) => d.status === 'pending').length || 0,
              resolved: result.discrepancies?.filter((d: any) => d.status === 'resolved').length || 0,
              last_updated: result.discrepancies?.[0]?.last_updated || 'N/A'
            };
          } catch (error) {
            console.warn(`Failed to fetch discrepancies for ${subject.subject_id}`);
            return {
              subject_id: subject.subject_id,
              discrepancies: [],
              total_discrepancies: 0,
              critical: 0,
              major: 0,
              minor: 0,
              open: 0,
              pending: 0,
              resolved: 0,
              last_updated: 'N/A'
            };
          }
        })
      );
      return discrepancyData;
    },
    enabled: !!subjects
  });

  const isLoadingData = isLoading || discrepanciesLoading;

  const filteredDiscrepancies = allDiscrepancies?.filter((item: any) => {
    const matchesSearch = item.subject_id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSeverity = severityFilter === "all" || 
      (severityFilter === "critical" && item.critical > 0) ||
      (severityFilter === "major" && item.major > 0) ||
      (severityFilter === "minor" && item.minor > 0);
    const matchesStatus = statusFilter === "all" ||
      (statusFilter === "open" && item.open > 0) ||
      (statusFilter === "pending" && item.pending > 0) ||
      (statusFilter === "resolved" && item.resolved > 0);
    
    return matchesSearch && matchesSeverity && matchesStatus;
  }) || [];

  const totalDiscrepancies = allDiscrepancies?.reduce((sum: number, item: any) => sum + item.total_discrepancies, 0) || 0;
  const totalCritical = allDiscrepancies?.reduce((sum: number, item: any) => sum + item.critical, 0) || 0;
  const totalOpen = allDiscrepancies?.reduce((sum: number, item: any) => sum + item.open, 0) || 0;
  const totalResolved = allDiscrepancies?.reduce((sum: number, item: any) => sum + item.resolved, 0) || 0;

  if (isLoadingData) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
              <AlertTriangle className="h-8 w-8 text-amber-600" />
              Discrepancy Management
            </h1>
            <p className="text-slate-600 mt-1">
              EDC vs Source Document Analysis • CARD-2025-001
            </p>
          </div>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="text-lg font-medium text-slate-600 mb-2">Loading discrepancy data...</div>
            <div className="text-sm text-slate-500">Analyzing subject records</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
            <AlertTriangle className="h-8 w-8 text-amber-600" />
            Discrepancy Management
          </h1>
          <p className="text-slate-600 mt-1">
            EDC vs Source Document Analysis • CARD-2025-001
          </p>
        </div>
        <Button>
          <FileText className="h-4 w-4 mr-2" />
          Export All Reports
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Total Discrepancies</p>
                <p className="text-2xl font-bold">{totalDiscrepancies}</p>
                <p className="text-xs text-slate-500">Across 50 subjects</p>
              </div>
              <FileText className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Critical Issues</p>
                <p className="text-2xl font-bold text-red-600">{totalCritical}</p>
                <p className="text-xs text-red-500">Require immediate attention</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Open Issues</p>
                <p className="text-2xl font-bold text-amber-600">{totalOpen}</p>
                <p className="text-xs text-amber-500">Pending resolution</p>
              </div>
              <Clock className="h-8 w-8 text-amber-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Resolution Rate</p>
                <p className="text-2xl font-bold text-green-600">
                  {totalDiscrepancies > 0 ? Math.round((totalResolved / totalDiscrepancies) * 100) : 0}%
                </p>
                <p className="text-xs text-green-500">{totalResolved} resolved</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Critical Alerts Banner */}
      {totalCritical > 0 && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
              <div className="flex-1">
                <h3 className="font-medium text-red-900 mb-2">Critical Discrepancies Requiring Immediate Action</h3>
                <div className="space-y-1 text-sm text-red-800">
                  <p>• {totalCritical} critical discrepancies identified across subjects</p>
                  <p>• Review subject profiles for detailed analysis</p>
                  <p>• Safety interventions may be required</p>
                </div>
                <div className="mt-3 flex gap-2">
                  <Button size="sm" className="bg-red-600 hover:bg-red-700">
                    Escalate All Critical
                  </Button>
                  <Button size="sm" variant="outline" className="border-red-200 text-red-700">
                    Generate Safety Report
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Discrepancy Table */}
      <Card>
        <CardHeader>
          <CardTitle>Subject Discrepancy Summary</CardTitle>
          
          {/* Filters */}
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search by subject ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={severityFilter} onValueChange={setSeverityFilter}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Severity" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Severities</SelectItem>
                <SelectItem value="critical">Has Critical</SelectItem>
                <SelectItem value="major">Has Major</SelectItem>
                <SelectItem value="minor">Has Minor</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="open">Has Open</SelectItem>
                <SelectItem value="pending">Has Pending</SelectItem>
                <SelectItem value="resolved">Has Resolved</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Subject ID</TableHead>
                  <TableHead>Total Issues</TableHead>
                  <TableHead>Critical</TableHead>
                  <TableHead>Major</TableHead>
                  <TableHead>Minor</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Last Updated</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredDiscrepancies.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8 text-slate-500">
                      No discrepancies found matching your criteria.
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredDiscrepancies.map((item) => (
                    <TableRow key={item.subject_id}>
                      <TableCell className="font-medium">
                        <Link 
                          to={`/subjects/${item.subject_id}?tab=discrepancies`}
                          className="text-blue-600 hover:text-blue-800 hover:underline"
                        >
                          {item.subject_id}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <span className="font-medium">{item.total_discrepancies}</span>
                      </TableCell>
                      <TableCell>
                        {item.critical > 0 ? (
                          <Badge className="bg-red-100 text-red-800">
                            {item.critical}
                          </Badge>
                        ) : (
                          <span className="text-slate-400">0</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {item.major > 0 ? (
                          <Badge className="bg-amber-100 text-amber-800">
                            {item.major}
                          </Badge>
                        ) : (
                          <span className="text-slate-400">0</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {item.minor > 0 ? (
                          <Badge className="bg-blue-100 text-blue-800">
                            {item.minor}
                          </Badge>
                        ) : (
                          <span className="text-slate-400">0</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          {item.open > 0 && (
                            <Badge variant="destructive" className="text-xs">
                              {item.open} Open
                            </Badge>
                          )}
                          {item.pending > 0 && (
                            <Badge variant="secondary" className="text-xs">
                              {item.pending} Pending
                            </Badge>
                          )}
                          {item.resolved > 0 && (
                            <Badge variant="default" className="text-xs bg-green-100 text-green-800">
                              {item.resolved} Resolved
                            </Badge>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="text-sm text-slate-500">
                        {item.last_updated}
                      </TableCell>
                      <TableCell>
                        <div className="flex space-x-1">
                          <Button asChild variant="ghost" size="sm">
                            <Link to={`/subjects/${item.subject_id}?tab=discrepancies`}>
                              <Eye className="h-4 w-4" />
                            </Link>
                          </Button>
                          <Button variant="ghost" size="sm">
                            <FileText className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

    </div>
  );
}
