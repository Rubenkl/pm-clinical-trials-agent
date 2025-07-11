
import { Card, CardContent } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface ClinicalMetricsCardProps {
  title: string;
  value: string;
  subtitle: string;
  icon: LucideIcon;
  trend?: string;
  trendUp?: boolean;
  alertLevel?: "normal" | "warning" | "critical";
}

export function ClinicalMetricsCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  trendUp,
  alertLevel = "normal"
}: ClinicalMetricsCardProps) {
  const getCardStyles = () => {
    switch (alertLevel) {
      case "critical":
        return "border-red-200 bg-red-50";
      case "warning":
        return "border-amber-200 bg-amber-50";
      default:
        return "border-slate-200 bg-white";
    }
  };

  const getIconStyles = () => {
    switch (alertLevel) {
      case "critical":
        return "text-red-600";
      case "warning":
        return "text-amber-600";
      default:
        return "text-blue-600";
    }
  };

  return (
    <Card className={cn("transition-all hover:shadow-md", getCardStyles())}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-600">{title}</p>
            <p className="text-3xl font-bold text-slate-900">{value}</p>
            <p className="text-sm text-slate-500">{subtitle}</p>
            {trend && (
              <p className={cn(
                "text-xs font-medium",
                trendUp ? "text-green-600" : "text-slate-600"
              )}>
                {trend}
              </p>
            )}
          </div>
          <div className={cn(
            "h-12 w-12 rounded-lg flex items-center justify-center",
            alertLevel === "critical" ? "bg-red-100" : 
            alertLevel === "warning" ? "bg-amber-100" : "bg-blue-100"
          )}>
            <Icon className={cn("h-6 w-6", getIconStyles())} />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
