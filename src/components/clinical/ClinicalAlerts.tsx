
import { AlertTriangle, Clock, TrendingUp } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface ClinicalAlert {
  severity: "Critical" | "Major" | "Minor";
  message: string;
  description: string;
}

interface ClinicalAlertsProps {
  alerts: ClinicalAlert[];
}

export function ClinicalAlerts({ alerts }: ClinicalAlertsProps) {
  if (alerts.length === 0) {
    return (
      <div className="text-center py-8">
        <TrendingUp className="h-12 w-12 text-green-500 mx-auto mb-4" />
        <p className="text-green-600 font-medium">No active clinical alerts</p>
        <p className="text-sm text-slate-500 mt-1">All parameters within acceptable ranges</p>
      </div>
    );
  }

  const getSeverityStyles = (severity: string) => {
    switch (severity) {
      case "Critical":
        return {
          badge: "bg-red-100 text-red-800 border-red-200",
          container: "border-red-200 bg-red-50",
          icon: "text-red-600"
        };
      case "Major":
        return {
          badge: "bg-amber-100 text-amber-800 border-amber-200",
          container: "border-amber-200 bg-amber-50",
          icon: "text-amber-600"
        };
      case "Minor":
        return {
          badge: "bg-blue-100 text-blue-800 border-blue-200",
          container: "border-blue-200 bg-blue-50",
          icon: "text-blue-600"
        };
      default:
        return {
          badge: "bg-slate-100 text-slate-800 border-slate-200",
          container: "border-slate-200 bg-slate-50",
          icon: "text-slate-600"
        };
    }
  };

  return (
    <div className="space-y-3">
      {alerts.map((alert, index) => {
        const styles = getSeverityStyles(alert.severity);
        
        return (
          <div key={index} className={`p-4 border rounded-lg ${styles.container}`}>
            <div className="flex items-start gap-3">
              <AlertTriangle className={`h-5 w-5 ${styles.icon} mt-0.5 flex-shrink-0`} />
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <h4 className="font-medium text-slate-900">{alert.message}</h4>
                  <Badge className={styles.badge}>
                    {alert.severity}
                  </Badge>
                </div>
                
                <p className="text-sm text-slate-700 mb-3">
                  {alert.description}
                </p>
                
                <div className="flex items-center gap-2 text-xs text-slate-500 mb-3">
                  <Clock className="h-3 w-3" />
                  <span>Detected: Just now</span>
                </div>
                
                <div className="flex gap-2">
                  <Button 
                    size="sm" 
                    variant="outline" 
                    className="h-8 text-xs border-current"
                  >
                    View Details
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline" 
                    className="h-8 text-xs border-current"
                  >
                    Create Query
                  </Button>
                  {alert.severity === "Critical" && (
                    <Button 
                      size="sm" 
                      className="h-8 text-xs bg-red-600 hover:bg-red-700"
                    >
                      Escalate
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </div>
        );
      })}
      
      <div className="pt-3 border-t">
        <p className="text-xs text-slate-500 mb-2">
          Clinical recommendations based on latest values and medical guidelines
        </p>
        <Button variant="outline" className="w-full text-sm">
          Generate Clinical Report
        </Button>
      </div>
    </div>
  );
}
