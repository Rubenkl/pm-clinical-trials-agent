
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { AlertTriangle, FileText, Eye, CheckCircle } from "lucide-react";
import { Discrepancy } from "@/services";

interface DiscrepanciesPanelProps {
  subjectId: string;
  discrepancies: Discrepancy[];
}

export function DiscrepanciesPanel({ subjectId, discrepancies }: DiscrepanciesPanelProps) {
  const [severityFilter, setSeverityFilter] = useState("all");
  const [typeFilter, setTypeFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");

  // Mock discrepancies if none provided (for demo purposes)
  const mockDiscrepancies: Discrepancy[] = [
    {
      field: "adverse_events",
      edc_value: [],
      source_value: ["mild rash on arms"],
      discrepancy_type: "missing",
      severity: "critical",
      status: "open"
    },
    {
      field: "vital_signs.systolic_bp",
      edc_value: 147.5,
      source_value: null,
      discrepancy_type: "missing",
      severity: "major",
      status: "open"
    },
    {
      field: "laboratory.bnp",
      edc_value: 319.57,
      source_value: null,
      discrepancy_type: "missing",
      severity: "major",
      status: "open"
    },
    {
      field: "demographics.weight",
      edc_value: 67.0,
      source_value: 67.5,
      discrepancy_type: "mismatch",
      severity: "minor",
      status: "pending"
    },
    {
      field: "visit_date",
      edc_value: "2025-06-15",
      source_value: "15-Jun-2025",
      discrepancy_type: "format_error",
      severity: "minor",
      status: "resolved"
    }
  ];

  const displayDiscrepancies = discrepancies.length > 0 ? discrepancies : mockDiscrepancies;

  const filteredDiscrepancies = displayDiscrepancies.filter(disc => {
    const matchesSeverity = severityFilter === "all" || disc.severity === severityFilter;
    const matchesType = typeFilter === "all" || disc.discrepancy_type === typeFilter;
    const matchesStatus = statusFilter === "all" || disc.status === statusFilter;
    
    return matchesSeverity && matchesType && matchesStatus;
  });

  const getSeverityBadge = (severity: string) => {
    const variants = {
      "critical": "bg-red-100 text-red-800 border-red-200",
      "major": "bg-amber-100 text-amber-800 border-amber-200",
      "minor": "bg-blue-100 text-blue-800 border-blue-200"
    } as const;
    
    return (
      <Badge className={variants[severity as keyof typeof variants] || "bg-slate-100 text-slate-800"}>
        {severity.charAt(0).toUpperCase() + severity.slice(1)}
      </Badge>
    );
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      "open": "bg-red-100 text-red-800",
      "pending": "bg-amber-100 text-amber-800",
      "resolved": "bg-green-100 text-green-800"
    } as const;
    
    return (
      <Badge className={variants[status as keyof typeof variants] || "bg-slate-100 text-slate-800"}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "critical":
        return "🔴";
      case "major":
        return "⚠️";
      case "minor":
        return "🟡";
      default:
        return "ℹ️";
    }
  };

  const formatFieldName = (field: string) => {
    return field
      .split(/[._]/)
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  const formatValue = (value: any) => {
    if (value === null || value === undefined) return "null";
    if (Array.isArray(value)) {
      return value.length === 0 ? "[]" : `[${value.join(", ")}]`;
    }
    return String(value);
  };

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Total Discrepancies</p>
                <p className="text-2xl font-bold">{displayDiscrepancies.length}</p>
              </div>
              <FileText className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Critical</p>
                <p className="text-2xl font-bold text-red-600">
                  {displayDiscrepancies.filter(d => d.severity === 'critical').length}
                </p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Open</p>
                <p className="text-2xl font-bold text-amber-600">
                  {displayDiscrepancies.filter(d => d.status === 'open').length}
                </p>
              </div>
              <Eye className="h-8 w-8 text-amber-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Resolved</p>
                <p className="text-2xl font-bold text-green-600">
                  {displayDiscrepancies.filter(d => d.status === 'resolved').length}
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Discrepancy List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5" />
            Data Discrepancies - {subjectId}
          </CardTitle>
          
          {/* Filters */}
          <div className="flex gap-4">
            <Select value={severityFilter} onValueChange={setSeverityFilter}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Severity" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Severities</SelectItem>
                <SelectItem value="critical">Critical</SelectItem>
                <SelectItem value="major">Major</SelectItem>
                <SelectItem value="minor">Minor</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="open">Open</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="resolved">Resolved</SelectItem>
              </SelectContent>
            </Select>
            
            <Button variant="outline">
              Export Report
            </Button>
          </div>
        </CardHeader>
        
        <CardContent>
          {filteredDiscrepancies.length === 0 ? (
            <div className="text-center py-8 text-slate-500">
              No discrepancies found matching your filters.
            </div>
          ) : (
            <div className="space-y-4">
              {filteredDiscrepancies.map((discrepancy, index) => (
                <div
                  key={index}
                  className={`p-4 border rounded-lg ${
                    discrepancy.severity === 'critical' ? 'border-red-200 bg-red-50' :
                    discrepancy.severity === 'major' ? 'border-amber-200 bg-amber-50' :
                    'border-blue-200 bg-blue-50'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <span className="text-lg">
                        {getSeverityIcon(discrepancy.severity)}
                      </span>
                      <div>
                        <h4 className="font-medium text-slate-900">
                          {formatFieldName(discrepancy.field)}
                        </h4>
                        <p className="text-sm text-slate-600">
                          Type: {discrepancy.discrepancy_type.replace('_', ' ')}
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      {getSeverityBadge(discrepancy.severity)}
                      {getStatusBadge(discrepancy.status)}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm font-medium text-slate-700 mb-1">EDC Value:</p>
                      <p className="text-sm bg-white p-2 rounded border">
                        {formatValue(discrepancy.edc_value)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-700 mb-1">Source Document:</p>
                      <p className="text-sm bg-white p-2 rounded border">
                        {formatValue(discrepancy.source_value)}
                      </p>
                    </div>
                  </div>

                  {/* AI Assessment for critical discrepancies */}
                  {discrepancy.severity === 'critical' && (
                    <div className="mb-4 p-3 bg-white rounded border-l-4 border-red-500">
                      <h5 className="font-medium text-red-900 mb-1">AI Assessment:</h5>
                      <p className="text-sm text-red-800">
                        Missing adverse event in EDC - regulatory reporting requirement not met. 
                        Requires immediate data correction and safety evaluation.
                      </p>
                    </div>
                  )}

                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" className="h-8 text-xs">
                      View Details
                    </Button>
                    <Button size="sm" variant="outline" className="h-8 text-xs">
                      Create Query
                    </Button>
                    {discrepancy.severity === 'critical' && (
                      <Button size="sm" className="h-8 text-xs bg-red-600 hover:bg-red-700">
                        Escalate to Medical Monitor
                      </Button>
                    )}
                    {discrepancy.status === 'open' && (
                      <Button size="sm" variant="outline" className="h-8 text-xs">
                        Mark Resolved
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {displayDiscrepancies.length > 0 && (
            <div className="mt-6 p-4 bg-slate-50 rounded-lg">
              <p className="text-sm text-slate-600 mb-2">
                <strong>AI Analysis Summary:</strong> {displayDiscrepancies.filter(d => d.severity === 'critical').length} critical discrepancy requires immediate attention. 
                Automated discrepancy detection identified {displayDiscrepancies.length} total issues between EDC and source documents.
              </p>
              <div className="flex gap-2">
                <Button size="sm" variant="outline">
                  Generate Bulk Query
                </Button>
                <Button size="sm" variant="outline">
                  Export Audit Report
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
