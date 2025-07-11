import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Progress } from "@/components/ui/progress";
import { Bot, Activity, Zap, Settings, TrendingUp, Clock, CheckCircle, AlertTriangle } from "lucide-react";

const agentStats = [
  { label: "Active Agents", value: "5", change: "+0", variant: "default" as const },
  { label: "Tasks Completed", value: "127", change: "+23", variant: "default" as const },
  { label: "Avg Response Time", value: "8.2s", change: "-1.3s", variant: "default" as const },
  { label: "Success Rate", value: "96.8%", change: "+2.1%", variant: "default" as const }
];

const agents = [
  {
    id: "portfolio_manager",
    name: "Portfolio Manager",
    description: "Clinical analysis orchestration and medical recommendations",
    status: "active",
    performance: 96,
    tasksToday: 45,
    avgResponseTime: "8.2s",
    confidence: 85,
    accuracy: 94.5,
    lastActivity: "2 minutes ago",
    capabilities: ["Clinical Analysis", "Workflow Orchestration", "Medical Recommendations"]
  },
  {
    id: "query_analyzer", 
    name: "Query Analyzer",
    description: "Data query generation and clinical context analysis",
    status: "active",
    performance: 94,
    tasksToday: 32,
    avgResponseTime: "5.1s",
    confidence: 90,
    accuracy: 96.2,
    lastActivity: "5 minutes ago",
    capabilities: ["Query Generation", "Data Analysis", "Clinical Context"]
  },
  {
    id: "data_verifier",
    name: "Data Verifier", 
    description: "Source data verification and discrepancy detection",
    status: "active",
    performance: 98,
    tasksToday: 18,
    avgResponseTime: "12.5s",
    confidence: 95,
    accuracy: 98.1,
    lastActivity: "1 minute ago",
    capabilities: ["SDV Processing", "Discrepancy Detection", "Data Quality"]
  },
  {
    id: "query_tracker",
    name: "Query Tracker",
    description: "Query lifecycle management and resolution tracking",
    status: "active", 
    performance: 92,
    tasksToday: 28,
    avgResponseTime: "6.8s",
    confidence: 88,
    accuracy: 93.7,
    lastActivity: "3 minutes ago",
    capabilities: ["Query Tracking", "Resolution Monitoring", "Workflow Management"]
  },
  {
    id: "protocol_monitor",
    name: "Protocol Monitor",
    description: "Protocol compliance monitoring and deviation detection",
    status: "maintenance",
    performance: 89,
    tasksToday: 0,
    avgResponseTime: "N/A",
    confidence: 80,
    accuracy: 91.3,
    lastActivity: "2 hours ago",
    capabilities: ["Compliance Monitoring", "Deviation Detection", "Risk Assessment"]
  }
];

const recentActivity = [
  {
    agent: "Portfolio Manager",
    action: "Detected severe anemia in CARD001 (Hgb 8.5 g/dL)",
    time: "2 minutes ago",
    status: "completed", 
    duration: "4.2s"
  },
  {
    agent: "Data Verifier",
    action: "Completed SDV for Site 003 subjects",
    time: "5 minutes ago", 
    status: "completed",
    duration: "18.7s"
  },
  {
    agent: "Query Analyzer",
    action: "Generated query for hemoglobin discrepancy",
    time: "8 minutes ago",
    status: "completed",
    duration: "5.9s"
  },
  {
    agent: "Query Tracker", 
    action: "Updated resolution status for Q-2025-001234",
    time: "12 minutes ago",
    status: "completed",
    duration: "3.2s"
  }
];

const getStatusColor = (status: string) => {
  switch (status) {
    case "active": return "default";
    case "maintenance": return "secondary";
    case "inactive": return "destructive";
    default: return "outline";
  }
};

export default function AIAgentsHub() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  return (
    <div className="flex-1 space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Agents Hub</h1>
          <p className="text-muted-foreground">Monitor AI agents for clinical trial automation</p>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {agentStats.map((stat) => (
          <Card key={stat.label}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{stat.label}</CardTitle>
              <Bot className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">
                <span className="text-green-600">{stat.change}</span> today
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <Tabs defaultValue="agents" className="w-full">
        <TabsList>
          <TabsTrigger value="agents">Active Agents</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="activity">Activity Feed</TabsTrigger>
          <TabsTrigger value="configuration">Configuration</TabsTrigger>
        </TabsList>

        <TabsContent value="agents" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {agents.map((agent) => (
              <Card key={agent.id} className="cursor-pointer hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Bot className="h-8 w-8 text-primary" />
                      <div>
                        <CardTitle className="text-lg">{agent.name}</CardTitle>
                        <Badge variant={getStatusColor(agent.status) as any}>
                          {agent.status}
                        </Badge>
                      </div>
                    </div>
                    <Switch checked={agent.status === "active"} disabled />
                  </div>
                  <CardDescription>{agent.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Performance</span>
                        <span>{agent.performance}%</span>
                      </div>
                      <Progress value={agent.performance} className="w-full" />
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <div className="text-muted-foreground">Tasks Today</div>
                        <div className="font-semibold">{agent.tasksToday}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Avg Response</div>
                        <div className="font-semibold">{agent.avgResponseTime}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Accuracy</div>
                        <div className="font-semibold">{agent.accuracy}%</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Last Active</div>
                        <div className="font-semibold">{agent.lastActivity}</div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="text-sm font-medium">Capabilities</div>
                      <div className="flex flex-wrap gap-1">
                        {agent.capabilities.map((capability) => (
                          <Badge key={capability} variant="outline" className="text-xs">
                            {capability}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="performance">
          <Card>
            <CardHeader>
              <CardTitle>Agent Performance Metrics</CardTitle>
              <CardDescription>Detailed performance analytics for all AI agents</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Agent</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Performance</TableHead>
                    <TableHead>Tasks Today</TableHead>
                    <TableHead>Avg Response</TableHead>
                    <TableHead>Accuracy</TableHead>
                    <TableHead>Confidence</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {agents.map((agent) => (
                    <TableRow key={agent.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <Bot className="h-5 w-5 text-primary" />
                          <div>
                            <div className="font-medium">{agent.name}</div>
                            <div className="text-xs text-muted-foreground">{agent.id}</div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={getStatusColor(agent.status) as any}>
                          {agent.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Progress value={agent.performance} className="w-16" />
                          <span className="text-sm">{agent.performance}%</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Activity className="h-4 w-4 text-muted-foreground" />
                          {agent.tasksToday}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Clock className="h-4 w-4 text-muted-foreground" />
                          {agent.avgResponseTime}
                        </div>
                      </TableCell>
                      <TableCell>{agent.accuracy}%</TableCell>
                      <TableCell>{agent.confidence}%</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="cursor-default">
                          View Only
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="activity">
          <Card>
            <CardHeader>
              <CardTitle>Recent Agent Activity</CardTitle>
              <CardDescription>Real-time feed of agent actions and tasks</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentActivity.map((activity, index) => (
                  <div key={index} className="flex items-center gap-4 p-4 border rounded-lg">
                    <div className="flex-shrink-0">
                      <Bot className="h-8 w-8 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium">{activity.agent}</span>
                        <Badge variant={activity.status === "completed" ? "secondary" : "default"}>
                          {activity.status}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">{activity.action}</p>
                    </div>
                    <div className="flex flex-col items-end text-sm text-muted-foreground">
                      <span>{activity.time}</span>
                      <span className="text-xs">Duration: {activity.duration}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="configuration">
          <Card>
            <CardHeader>
              <CardTitle>Agent Configuration</CardTitle>
              <CardDescription>Configure agent behavior and performance parameters</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <Settings className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">Agent Configuration Panel</h3>
                <p className="text-muted-foreground mb-4">
                  Advanced configuration options for AI agent behavior and performance tuning
                </p>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <p>• Confidence threshold adjustment</p>
                  <p>• Response time optimization</p>
                  <p>• Task prioritization settings</p>
                  <p>• Integration endpoint configuration</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}