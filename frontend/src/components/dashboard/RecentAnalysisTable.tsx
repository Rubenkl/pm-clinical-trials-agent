
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Eye, FileText } from "lucide-react";

// Recent analyses based on actual test data patterns  
const recentAnalyses = [
  {
    subject: "CARD001",
    analysis: "Critical Anemia Detection",
    findings: "Hemoglobin 8.5 g/dL vs expected 12.5 g/dL",
    recommendation: "Verify hemoglobin level and assess for interventions",
    timestamp: "10 minutes ago",
    severity: "Critical"
  },
  {
    subject: "CARD002",
    analysis: "Blood Pressure Discrepancy Analysis",
    findings: "Systolic BP: 145 mmHg vs 155 mmHg (10 mmHg difference)",
    recommendation: "Confirm source document accuracy for systolic BP",
    timestamp: "25 minutes ago",
    severity: "Major"
  },
  {
    subject: "CARD003",
    analysis: "Data Quality Verification",
    findings: "No discrepancies detected - clean subject profile",
    recommendation: "Continue routine monitoring",
    timestamp: "1 hour ago",
    severity: "Normal"
  },
  {
    subject: "CARD007",
    analysis: "Source Data Verification",
    findings: "All data points verified - 100% accuracy",
    recommendation: "No action required",
    timestamp: "2 hours ago",
    severity: "Normal"
  },
  {
    subject: "CARD010", 
    analysis: "Protocol Violation Assessment",
    findings: "Subject age 85 exceeds protocol limit (18-80)",
    recommendation: "Review inclusion criteria compliance",
    timestamp: "3 hours ago",
    severity: "Major"
  }
];

export function RecentAnalysisTable() {
  const getSeverityBadge = (severity: string) => {
    const variants = {
      "Critical": "destructive",
      "Major": "secondary",
      "Minor": "outline",
      "Normal": "default"
    } as const;
    
    return <Badge variant={variants[severity as keyof typeof variants] || "default"}>{severity}</Badge>;
  };

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Subject</TableHead>
            <TableHead>Analysis Type</TableHead>
            <TableHead>Key Findings</TableHead>
            <TableHead>Recommendation</TableHead>
            <TableHead>Severity</TableHead>
            <TableHead>Time</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {recentAnalyses.map((analysis, index) => (
            <TableRow key={index}>
              <TableCell className="font-medium">{analysis.subject}</TableCell>
              <TableCell>{analysis.analysis}</TableCell>
              <TableCell className="max-w-xs truncate" title={analysis.findings}>
                {analysis.findings}
              </TableCell>
              <TableCell className="max-w-xs truncate" title={analysis.recommendation}>
                {analysis.recommendation}
              </TableCell>
              <TableCell>{getSeverityBadge(analysis.severity)}</TableCell>
              <TableCell className="text-sm text-slate-500">{analysis.timestamp}</TableCell>
              <TableCell>
                <div className="flex space-x-1">
                  <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
                    <Eye className="h-3 w-3" />
                  </Button>
                  <Button variant="ghost" size="sm" className="h-7 w-7 p-0">
                    <FileText className="h-3 w-3" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
