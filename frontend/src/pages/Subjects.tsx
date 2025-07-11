
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search, Filter, Users, Eye, AlertTriangle, TrendingUp } from "lucide-react";
import { apiService } from "@/services";

export default function Subjects() {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [siteFilter, setSiteFilter] = useState("all");

  // Use demo subjects for realistic showcase
  const { data: subjects, isLoading, error } = useQuery({
    queryKey: ['demo-subjects'],
    queryFn: () => apiService.getDemoSubjects(20), // Mix of clean and problem subjects
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const filteredSubjects = subjects?.filter(subject => {
    const subjectInfo = subject.data?.subject_info;
    if (!subjectInfo?.demographics) return false;
    
    const matchesSearch = subject.subject_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         subjectInfo.demographics.age.toString().includes(searchTerm) ||
                         subjectInfo.demographics.gender.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === "all" || (subjectInfo.overall_status || 'active') === statusFilter;
    const matchesSite = siteFilter === "all" || subjectInfo.site_id === siteFilter;
    
    return matchesSearch && matchesStatus && matchesSite;
  }) || [];

  const getStatusBadge = (status: string) => {
    const variants = {
      "active": "default",
      "withdrawn": "secondary",
      "completed": "outline"
    } as const;
    
    return <Badge variant={variants[status as keyof typeof variants] || "default"}>{status}</Badge>;
  };

  const getAlertCount = (subjectId: string) => {
    // Alert counts based on actual test data patterns
    const alertCounts: Record<string, number> = {
      // Problem subjects with 12-18 discrepancies
      "CARD001": 3,
      "CARD002": 2,
      "CARD005": 4,
      "CARD006": 3,
      // Protocol violation subjects
      "CARD010": 2, // age 85
      "CARD030": 1, // age 17
      // Some clean subjects with minor alerts
      "CARD015": 1,
      "CARD027": 1
    };
    return alertCounts[subjectId] || 0;
  };

  const getAlertIcon = (count: number) => {
    if (count >= 3) return <span className="text-red-600">🔴 {count}</span>;
    if (count >= 1) return <span className="text-amber-600">⚠️ {count}</span>;
    return <span className="text-slate-400">-</span>;
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-slate-200 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-slate-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-slate-900">Subject Management</h1>
        <Card>
          <CardContent className="p-6 text-center">
            <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <p className="text-slate-600">Failed to load subjects. Please try again.</p>
            <Button className="mt-4" onClick={() => window.location.reload()}>
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
            <Users className="h-8 w-8 text-blue-600" />
            Subject Management
          </h1>
          <p className="text-slate-600 mt-1">
            CARD-2025-001 • {subjects?.length || 0} subjects enrolled
          </p>
        </div>
        <Button>
          <Users className="h-4 w-4 mr-2" />
          Add Subject
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Total Subjects</p>
                <p className="text-2xl font-bold">{subjects?.length || 0}/50</p>
              </div>
              <Users className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Active</p>
                <p className="text-2xl font-bold text-green-600">
                  {subjects?.filter(s => (s.data?.subject_info?.overall_status || 'active') === 'active').length || 0}
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Withdrawn</p>
                <p className="text-2xl font-bold text-amber-600">
                  {subjects?.filter(s => (s.data?.subject_info?.overall_status || 'active') === 'withdrawn').length || 0}
                </p>
              </div>
              <AlertTriangle className="h-8 w-8 text-amber-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">With Alerts</p>
                <p className="text-2xl font-bold text-red-600">8</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Subject List</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search subjects by ID, age, or gender..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="withdrawn">Withdrawn</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
              </SelectContent>
            </Select>
            <Select value={siteFilter} onValueChange={setSiteFilter}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Site" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Sites</SelectItem>
                <SelectItem value="SITE_001">SITE_001</SelectItem>
                <SelectItem value="SITE_002">SITE_002</SelectItem>
                <SelectItem value="SITE_003">SITE_003</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Subject Table */}
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Subject ID</TableHead>
                  <TableHead>Demographics</TableHead>
                  <TableHead>Site</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Alerts</TableHead>
                  <TableHead>Enrollment</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredSubjects.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-8 text-slate-500">
                      No subjects found matching your criteria.
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredSubjects.map((subject) => {
                    const subjectInfo = subject.data?.subject_info;
                    const demographics = subjectInfo?.demographics;
                    
                    return (
                      <TableRow key={subject.subject_id}>
                        <TableCell className="font-medium">
                          <Link 
                            to={`/subjects/${subject.subject_id}`}
                            className="text-blue-600 hover:text-blue-800 hover:underline"
                          >
                            {subject.subject_id}
                          </Link>
                        </TableCell>
                        <TableCell>
                          <div>
                            <div className="font-medium">
                              {demographics?.age}y, {demographics?.gender}
                            </div>
                            <div className="text-sm text-slate-500">
                              {demographics?.race} • {demographics?.weight}kg
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>{subjectInfo?.site_id}</TableCell>
                        <TableCell>{getStatusBadge(subjectInfo?.overall_status || 'active')}</TableCell>
                        <TableCell>{getAlertIcon(getAlertCount(subject.subject_id))}</TableCell>
                        <TableCell className="text-sm text-slate-500">
                          {demographics?.enrollment_date ? new Date(demographics.enrollment_date).toLocaleDateString() : '-'}
                        </TableCell>
                        <TableCell>
                          <div className="flex space-x-1">
                            <Button asChild variant="ghost" size="sm">
                              <Link to={`/subjects/${subject.subject_id}`}>
                                <Eye className="h-4 w-4" />
                              </Link>
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
