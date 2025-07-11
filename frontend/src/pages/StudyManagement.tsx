
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { 
  FileText, 
  Users, 
  MapPin, 
  Calendar, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  Clock
} from "lucide-react";
import { StudyProgressChart } from "@/components/dashboard/StudyProgressChart";

const siteData = [
  {
    id: "SITE_001",
    name: "New York Medical Center",
    location: "New York, NY",
    enrollment: { current: 20, target: 25 },
    enrollment_rate: 4.2,
    data_quality: 94.2,
    query_rate: 2.1,
    status: "active",
    principal_investigator: "Dr. Sarah Johnson",
    coordinator: "Jennifer Smith, CRC"
  },
  {
    id: "SITE_002", 
    name: "Boston General Hospital",
    location: "Boston, MA",
    enrollment: { current: 15, target: 20 },
    enrollment_rate: 3.8,
    data_quality: 91.7,
    query_rate: 3.2,
    status: "active",
    principal_investigator: "Dr. Michael Chen",
    coordinator: "Lisa Rodriguez, CRC"
  },
  {
    id: "SITE_003",
    name: "Chicago Research Institute", 
    location: "Chicago, IL",
    enrollment: { current: 15, target: 15 },
    enrollment_rate: 5.1,
    data_quality: 96.8,
    query_rate: 1.8,
    status: "completed",
    principal_investigator: "Dr. Robert Davis",
    coordinator: "Amanda Wilson, CRC"
  }
];

const milestones = [
  { name: "First Patient In", date: "2025-03-01", status: "completed" },
  { name: "50% Enrollment", date: "2025-05-15", status: "completed" },
  { name: "Last Patient In", date: "2025-07-30", status: "on-track" },
  { name: "Database Lock", date: "2025-10-31", status: "upcoming" },
  { name: "Final Report", date: "2025-12-31", status: "upcoming" }
];

export default function StudyManagement() {
  const totalEnrolled = siteData.reduce((sum, site) => sum + site.enrollment.current, 0);
  const totalTarget = siteData.reduce((sum, site) => sum + site.enrollment.target, 0);
  const enrollmentPercentage = Math.round((totalEnrolled / totalTarget) * 100);
  const avgDataQuality = Math.round(siteData.reduce((sum, site) => sum + site.data_quality, 0) / siteData.length * 10) / 10;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
            <FileText className="h-8 w-8 text-blue-600" />
            Study Management
          </h1>
          <p className="text-slate-600 mt-1">
            Protocol CARD-2025-001 • Cardiovascular Phase II Study
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <FileText className="h-4 w-4 mr-2" />
            Protocol Document
          </Button>
          <Button>
            <TrendingUp className="h-4 w-4 mr-2" />
            Study Report
          </Button>
        </div>
      </div>

      {/* Protocol Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Protocol Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div>
              <p className="text-sm text-slate-600">Study Status</p>
              <Badge className="mt-1 bg-green-100 text-green-800">Active</Badge>
              <p className="text-xs text-slate-500 mt-1">Enrolling patients</p>
            </div>
            <div>
              <p className="text-sm text-slate-600">Phase</p>
              <p className="text-lg font-semibold">Phase II</p>
              <p className="text-xs text-slate-500">Cardiovascular</p>
            </div>
            <div>
              <p className="text-sm text-slate-600">Study Duration</p>
              <p className="text-lg font-semibold">24 weeks</p>
              <p className="text-xs text-slate-500">Per subject</p>
            </div>
            <div>
              <p className="text-sm text-slate-600">Primary Endpoint</p>
              <p className="text-lg font-semibold">LVEF Change</p>
              <p className="text-xs text-slate-500">Left ventricular ejection fraction</p>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-slate-50 rounded-lg">
            <h4 className="font-medium mb-2">Study Objectives</h4>
            <p className="text-sm text-slate-600">
              To evaluate the efficacy and safety of investigational therapy in patients with cardiovascular disease. 
              Primary objective is to assess the change in left ventricular ejection fraction (LVEF) from baseline to Week 24.
              Secondary objectives include assessment of cardiovascular biomarkers, quality of life measures, and safety parameters.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Key Metrics Dashboard */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Enrollment</p>
                <p className="text-2xl font-bold text-green-600">{totalEnrolled}/{totalTarget}</p>
                <p className="text-xs text-green-500">{enrollmentPercentage}% complete</p>
              </div>
              <Users className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Active Sites</p>
                <p className="text-2xl font-bold text-blue-600">3</p>
                <p className="text-xs text-blue-500">All performing well</p>
              </div>
              <MapPin className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Data Quality</p>
                <p className="text-2xl font-bold text-emerald-600">{avgDataQuality}%</p>
                <p className="text-xs text-emerald-500">Above target (90%)</p>
              </div>
              <CheckCircle className="h-8 w-8 text-emerald-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Timeline</p>
                <p className="text-2xl font-bold text-amber-600">On Track</p>
                <p className="text-xs text-amber-500">5 months remaining</p>
              </div>
              <Calendar className="h-8 w-8 text-amber-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs for detailed views */}
      <Tabs defaultValue="sites" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="sites">Site Performance</TabsTrigger>
          <TabsTrigger value="enrollment">Enrollment</TabsTrigger>
          <TabsTrigger value="milestones">Milestones</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
        </TabsList>

        <TabsContent value="sites" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Site Performance Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {siteData.map((site) => (
                  <div key={site.id} className="p-4 border rounded-lg">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-lg font-semibold">{site.name}</h3>
                        <p className="text-slate-600">{site.location} • {site.id}</p>
                        <div className="mt-2 space-y-1 text-sm text-slate-500">
                          <p>PI: {site.principal_investigator}</p>
                          <p>Coordinator: {site.coordinator}</p>
                        </div>
                      </div>
                      <Badge className={
                        site.status === 'active' ? 'bg-green-100 text-green-800' :
                        site.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                        'bg-slate-100 text-slate-800'
                      }>
                        {site.status.charAt(0).toUpperCase() + site.status.slice(1)}
                      </Badge>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <p className="text-sm text-slate-600">Enrollment</p>
                        <div className="flex items-center gap-2">
                          <Progress 
                            value={(site.enrollment.current / site.enrollment.target) * 100} 
                            className="flex-1"
                          />
                          <span className="text-sm font-medium">
                            {site.enrollment.current}/{site.enrollment.target}
                          </span>
                        </div>
                        <p className="text-xs text-slate-500 mt-1">
                          {site.enrollment_rate}/month rate
                        </p>
                      </div>

                      <div>
                        <p className="text-sm text-slate-600">Data Quality</p>
                        <p className="text-xl font-semibold text-green-600">
                          {site.data_quality}%
                        </p>
                        <p className={`text-xs ${
                          site.data_quality >= 95 ? 'text-green-500' :
                          site.data_quality >= 90 ? 'text-amber-500' :
                          'text-red-500'
                        }`}>
                          {site.data_quality >= 95 ? 'Excellent' :
                           site.data_quality >= 90 ? 'Good' : 'Needs Improvement'}
                        </p>
                      </div>

                      <div>
                        <p className="text-sm text-slate-600">Query Rate</p>
                        <p className="text-xl font-semibold">
                          {site.query_rate}
                        </p>
                        <p className="text-xs text-slate-500">queries/subject</p>
                      </div>

                      <div className="flex gap-2">
                        <Button size="sm" variant="outline">
                          View Details
                        </Button>
                        <Button size="sm" variant="outline">
                          Contact Site
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="enrollment">
          <Card>
            <CardHeader>
              <CardTitle>Enrollment Progress</CardTitle>
            </CardHeader>
            <CardContent>
              <StudyProgressChart />
              
              <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-blue-50 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-2">Current Status</h4>
                  <p className="text-2xl font-bold text-blue-700">{totalEnrolled}/60</p>
                  <p className="text-sm text-blue-600">Subjects enrolled</p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <h4 className="font-medium text-green-900 mb-2">Completion Rate</h4>
                  <p className="text-2xl font-bold text-green-700">{enrollmentPercentage}%</p>
                  <p className="text-sm text-green-600">of target reached</p>
                </div>
                <div className="p-4 bg-amber-50 rounded-lg">
                  <h4 className="font-medium text-amber-900 mb-2">Projected Timeline</h4>
                  <p className="text-2xl font-bold text-amber-700">Aug 2025</p>
                  <p className="text-sm text-amber-600">Last patient in</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="milestones">
          <Card>
            <CardHeader>
              <CardTitle>Study Milestones</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {milestones.map((milestone, index) => (
                  <div key={index} className="flex items-center gap-4 p-4 border rounded-lg">
                    <div className={`w-3 h-3 rounded-full ${
                      milestone.status === 'completed' ? 'bg-green-500' :
                      milestone.status === 'on-track' ? 'bg-blue-500' :
                      'bg-slate-300'
                    }`} />
                    
                    <div className="flex-1">
                      <h4 className="font-medium">{milestone.name}</h4>
                      <p className="text-sm text-slate-600">{milestone.date}</p>
                    </div>
                    
                    <Badge className={
                      milestone.status === 'completed' ? 'bg-green-100 text-green-800' :
                      milestone.status === 'on-track' ? 'bg-blue-100 text-blue-800' :
                      'bg-slate-100 text-slate-800'
                    }>
                      {milestone.status === 'on-track' ? 'On Track' : milestone.status.charAt(0).toUpperCase() + milestone.status.slice(1)}
                    </Badge>
                  </div>
                ))}
              </div>
              
              <div className="mt-6 p-4 bg-slate-50 rounded-lg">
                <h4 className="font-medium mb-2">Timeline Status</h4>
                <p className="text-sm text-slate-600">
                  Study is progressing according to planned timeline. All major milestones are on track 
                  with no anticipated delays to database lock or final report submission.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="compliance">
          <Card>
            <CardHeader>
              <CardTitle>Regulatory Compliance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-4">GCP Compliance</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Site Training Complete</span>
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Protocol Deviations</span>
                      <Badge className="bg-amber-100 text-amber-800">3 Minor</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Audit Trail Complete</span>
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">SAE Reporting</span>
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-4">Data Integrity</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Source Data Verification</span>
                      <span className="text-sm font-medium">94.2%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Query Resolution Rate</span>
                      <span className="text-sm font-medium">87.3%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Data Lock Readiness</span>
                      <Badge className="bg-blue-100 text-blue-800">On Track</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">CDISC Compliance</span>
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-6 p-4 border-l-4 border-green-500 bg-green-50">
                <h4 className="font-medium text-green-900 mb-2">Compliance Status: Excellent</h4>
                <p className="text-sm text-green-800">
                  Study maintains full regulatory compliance with all GCP guidelines. 
                  Minor protocol deviations have been documented and reported appropriately. 
                  All sites are audit-ready with complete documentation.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
