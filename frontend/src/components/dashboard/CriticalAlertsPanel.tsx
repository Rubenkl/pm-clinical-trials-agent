
import { AlertTriangle, Clock, User } from "lucide-react";
import { Button } from "@/components/ui/button";

// Critical alerts based on actual test data patterns
const criticalAlerts = [
  {
    id: 1,
    subject: "CARD001",
    alert: "Severe Anemia",
    severity: "Critical",
    time: "2 hours ago",
    description: "Hemoglobin 8.5 g/dL - significant safety concern"
  },
  {
    id: 2,
    subject: "CARD002",
    alert: "Blood Pressure Discrepancy",
    severity: "Major",
    time: "4 hours ago", 
    description: "Systolic BP 145 vs 155 mmHg - 10 mmHg difference"
  },
  {
    id: 3,
    subject: "CARD005",
    alert: "Multiple Discrepancies",
    severity: "Major",
    time: "6 hours ago",
    description: "13 discrepancies detected across cardiovascular markers"
  }
];

export function CriticalAlertsPanel() {
  return (
    <div className="space-y-3">
      {criticalAlerts.map((alert) => (
        <div key={alert.id} className="p-3 border rounded-lg border-red-200 bg-red-50">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-2">
              <AlertTriangle className="h-4 w-4 text-red-600 mt-0.5" />
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <span className="font-medium text-red-900">{alert.subject}</span>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    alert.severity === 'Critical' 
                      ? 'bg-red-100 text-red-800' 
                      : 'bg-amber-100 text-amber-800'
                  }`}>
                    {alert.severity}
                  </span>
                </div>
                <p className="text-sm font-medium text-red-800 mt-1">{alert.alert}</p>
                <p className="text-xs text-red-600 mt-1">{alert.description}</p>
                <div className="flex items-center text-xs text-red-600 mt-2">
                  <Clock className="h-3 w-3 mr-1" />
                  {alert.time}
                </div>
              </div>
            </div>
          </div>
          <div className="mt-3 flex space-x-2">
            <Button size="sm" variant="outline" className="h-7 text-xs border-red-200 text-red-700 hover:bg-red-100">
              View Details
            </Button>
            <Button size="sm" variant="outline" className="h-7 text-xs border-red-200 text-red-700 hover:bg-red-100">
              Escalate
            </Button>
          </div>
        </div>
      ))}
      
      <Button variant="outline" className="w-full text-sm">
        View All Alerts
      </Button>
    </div>
  );
}
