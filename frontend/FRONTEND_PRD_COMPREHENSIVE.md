# Product Requirements Document (PRD)
## Clinical Trials AI Agent Frontend - React Dashboard & Interface

**Version:** 1.0  
**Date:** January 2025  
**Product Owner:** Director of AI Innovation  
**Status:** Ready for Development  
**Backend Integration:** Production-Ready Clinical Intelligence System

---

## 🎯 Executive Summary

This PRD defines the requirements for building a comprehensive React frontend that showcases our **production-ready clinical trials AI agent system**. The frontend will demonstrate real clinical intelligence through an intuitive interface that connects clinical trial stakeholders with our multi-agent AI system analyzing **actual cardiology study data** from 50 subjects.

### Key Differentiators
- **Real Clinical Data**: 50 cardiology subjects with complete clinical profiles (not mock data)
- **Genuine AI Intelligence**: OpenAI Agents SDK analyzing actual BP readings, BNP levels, imaging results
- **Clinical Expertise**: Proper medical interpretation and recommendations for real patient scenarios
- **Multi-Agent Orchestration**: Portfolio Manager coordinating 5 specialized clinical agents

---

## 📊 Product Overview

### 2.1 Problem Statement
Current clinical trial management systems lack:
- **Real-time AI-powered clinical analysis** of subject data
- **Intelligent discrepancy detection** between EDC and source documents  
- **AI-assisted query generation** based on medical expertise
- **Integrated workflow orchestration** for complex clinical processes
- **Clinical decision support** for trial monitoring and safety

### 2.2 Solution Overview
A comprehensive React dashboard that:
- **Showcases Real Clinical Intelligence**: Analyzes actual cardiology study data from CARD001-CARD050
- **Provides Multi-Agent AI Interface**: Chat with Portfolio Manager for clinical analysis and recommendations
- **Visualizes Clinical Data**: Subject profiles, vital signs trends, lab values, imaging results
- **Manages Clinical Workflows**: Query resolution, discrepancy tracking, workflow orchestration
- **Demonstrates Medical Expertise**: Proper interpretation of cardiovascular and renal markers

### 2.3 Backend Integration Capabilities
Our backend provides **production-ready clinical intelligence**:
- **50 Cardiology Subjects**: Complete clinical profiles with demographics, vital signs, labs, imaging
- **Real Clinical Analysis**: BP interpretation (Stage 1/2 HTN), cardiac markers (BNP, troponin), kidney function
- **48 Discrepancies per Subject**: Actual EDC vs source document differences
- **5 AI Agents**: Portfolio Manager, Query Analyzer, Data Verifier, Query Generator, Query Tracker
- **Clinical Recommendations**: Cardiology/nephrology consultations, safety monitoring

---

## 👥 User Personas & Stakeholders

### 3.1 Primary Users

#### Clinical Research Associates (CRA)
**Role**: Site monitoring and data verification  
**Needs**: 
- Subject overview dashboards with clinical alerts
- Discrepancy reports and resolution tracking
- AI-assisted query generation and management
- Site performance analytics and trends

#### Clinical Data Managers (CDM)
**Role**: Data quality and database management  
**Needs**: 
- Data quality dashboards with AI insights
- Automated discrepancy detection and categorization
- Query workflow optimization and tracking
- Cross-system data verification tools

#### Clinical Research Coordinators (CRC)
**Role**: Site-level trial coordination  
**Needs**: 
- Subject enrollment and visit scheduling
- Clinical alert notifications and follow-up
- Protocol compliance monitoring
- Communication with medical monitors

#### Principal Investigators (PI)
**Role**: Medical oversight and decision making  
**Needs**: 
- Clinical summary dashboards with medical insights
- Safety signal detection and escalation
- AI-powered clinical recommendations
- Regulatory compliance tracking

### 3.2 Secondary Users

#### Medical Monitors
- Clinical safety oversight
- Adverse event assessment
- Protocol deviation review

#### Regulatory Affairs
- Compliance tracking
- Audit trail management
- Regulatory submission support

---

## 🏗️ Technical Architecture & Framework Requirements

### 4.1 Frontend Technology Stack
```
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite for fast development and building
- **UI Framework**: Tailwind CSS for consistent styling
- **State Management**: Redux Toolkit or Zustand
- **Data Fetching**: React Query (TanStack Query) 
- **Charts & Visualization**: Chart.js or D3.js for clinical data
- **Component Library**: Headless UI or Shadcn/ui
- **Testing**: Jest + React Testing Library
- **Deployment**: Railway or Vercel
```

### 4.2 Backend Integration
```
Base URL: https://pm-clinical-trials-agent-production.up.railway.app
Local Dev: http://localhost:8000

Key Endpoints:
- POST /api/v1/agents/chat - AI agent interaction
- GET /api/v1/test-data/status - Study overview
- GET /api/v1/test-data/subjects/{id} - Subject clinical data
- GET /api/v1/test-data/subjects/{id}/discrepancies - Data discrepancies
- GET /api/v1/test-data/sites/performance - Site analytics
- GET /api/v1/agents/status - Agent system health
```

### 4.3 Real Data Integration
The frontend will showcase **actual clinical intelligence** by integrating with:
- **50 Cardiology Subjects**: CARD001-CARD050 with complete profiles
- **Protocol CARD-2025-001**: Cardiovascular Phase 2 study across 3 sites
- **Real Clinical Values**: BP readings, BNP levels, creatinine, LVEF, demographics
- **Actual Discrepancies**: 48 EDC vs source document differences per subject

---

## 🎨 User Interface Requirements

### 5.1 Dashboard Layout & Navigation

#### Primary Navigation Structure
```
📊 Dashboard (Home)
├── 👥 Subjects (50 cardiology patients)
│   ├── Subject List (CARD001-CARD050)
│   ├── Subject Profile (Clinical data, vitals, labs)
│   └── Clinical Analysis (AI insights, recommendations)
├── 🤖 AI Agents
│   ├── Portfolio Manager Chat
│   ├── Agent Status & Health
│   └── Workflow Orchestration
├── 📋 Discrepancies
│   ├── Critical Issues (Safety alerts)
│   ├── Data Quality (EDC vs Source)
│   └── Resolution Tracking
├── 📊 Study Management
│   ├── Protocol CARD-2025-001 Overview
│   ├── Site Performance (3 sites)
│   └── Enrollment & Timeline
└── ⚙️ Settings
    ├── User Preferences
    └── System Configuration
```

#### Responsive Design Requirements
- **Desktop First**: Primary interface for clinical workstations
- **Tablet Support**: Site coordinators using iPads
- **Mobile Responsive**: Basic functionality for on-the-go access
- **Print Friendly**: Clinical reports and regulatory documentation

### 5.2 Core Interface Components

#### 5.2.1 Dashboard Overview (Landing Page)
**Purpose**: High-level system overview and quick access to key functions

**Key Metrics Cards**:
```
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Active Subjects │ │ Critical Alerts │ │ Open Queries    │
│      47/50      │ │       3         │ │      142        │
└─────────────────┘ └─────────────────┘ └─────────────────┘

┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ AI Analysis     │ │ Data Quality    │ │ Site Performance│
│   98.5% Acc     │ │     94.2%       │ │    87.3% Avg    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

**Recent AI Analysis Section**:
- Last 5 clinical analyses with subject ID and findings
- Clinical alerts requiring attention
- Quick access to Portfolio Manager chat

**Study Progress Visualization**:
- Enrollment timeline (target vs actual)
- Visit completion rates by site
- Protocol milestone tracking

#### 5.2.2 AI Agent Chat Interface
**Purpose**: Interactive chat with Portfolio Manager for clinical analysis

**Chat Interface Design**:
```
┌─────────────────────────────────────────────────────────┐
│ 🤖 Clinical Portfolio Manager                          │
├─────────────────────────────────────────────────────────┤
│ User: Analyze CARD001 clinical data                    │
│                                                         │
│ 🤖 AI: CLINICAL FINDING: BP 147.5/79.6 mmHg = Stage 1 │
│ Hypertension (normal <120/80)                          │
│                                                         │
│ CLINICAL SIGNIFICANCE: Elevated BNP (319.57 pg/mL)     │
│ indicates potential heart failure. Creatinine (1.84)   │
│ shows kidney dysfunction requiring monitoring.          │
│                                                         │
│ RECOMMENDED ACTION: Cardiology consultation for HTN    │
│ management, nephrology evaluation for renal function.  │
│                                                         │
│ [View Full Analysis] [Generate Query] [Save Report]    │
├─────────────────────────────────────────────────────────┤
│ Type your clinical question...                   [Send]│
└─────────────────────────────────────────────────────────┘
```

**Pre-defined Clinical Queries**:
- "Analyze subject CARD001 vital signs and lab values"
- "Check discrepancies for CARD002"
- "Generate safety report for subjects with elevated BNP"
- "Review site performance for SITE_001"

**AI Response Features**:
- **Clinical Findings**: Highlighted medical interpretations
- **Medical Recommendations**: Actionable clinical advice
- **Tool Output Display**: JSON results from function tools
- **Export Options**: PDF reports, clinical summaries

#### 5.2.3 Subject Management Dashboard
**Purpose**: Comprehensive view of all 50 cardiology subjects

**Subject List View**:
```
┌────────────────────────────────────────────────────────────┐
│ CARD-2025-001 Subjects (50 enrolled)         [+ Add Subject]│
├────────────────────────────────────────────────────────────┤
│ Search: [_______________] Filter: [All Sites ▼] [Status ▼] │
├────────────────────────────────────────────────────────────┤
│ ID     │ Age │ Gender │ Site │ Status    │ Alerts │ Last Visit│
├────────────────────────────────────────────────────────────┤
│ CARD001│ 43  │ F      │ S001 │ Active    │ ⚠️ 3   │ Week 4    │
│ CARD002│ 58  │ M      │ S001 │ Active    │ ⚠️ 1   │ Week 6    │
│ CARD003│ 67  │ F      │ S002 │ Withdrawn │ -      │ Week 2    │
│ CARD004│ 45  │ M      │ S001 │ Active    │ 🔴 2   │ Screening │
│ ...    │ ... │ ...    │ ...  │ ...       │ ...    │ ...       │
└────────────────────────────────────────────────────────────┘
```

**Alert Icons Legend**:
- 🔴 Critical (Safety concerns, SAEs)
- ⚠️ Major (Protocol deviations, missing data)
- 🟡 Minor (Administrative issues)

**Subject Profile View** (Individual Subject Detail):
```
┌─────────────────────────────────────────────────────────────┐
│ Subject CARD001 - 43F, Enrolled 2025-05-08    [AI Analysis]│
├─────────────────────────────────────────────────────────────┤
│ Demographics    │ Clinical Status    │ Study Progress       │
│ Age: 43         │ Status: Active     │ Visits: 4/8 Complete│
│ Gender: Female  │ Site: SITE_001     │ Next: Week 6 (Due)  │
│ Race: White     │ Enrolled: 05/08/25 │ Compliance: 94%     │
│ Weight: 67.0 kg │ Last Visit: Week 4 │ Queries: 12 Open    │
│ Height: 154.6cm │ Protocol: CARD-001 │ Discrepancies: 48   │
├─────────────────────────────────────────────────────────────┤
│ 📊 Vital Signs Trends          │ 🧪 Laboratory Values    │
│ ┌─────────────────────────────┐ │ Latest Results (Week 4): │
│ │ BP: 147/80 ↗ (Stage 1 HTN) │ │ BNP: 319.57 ↑ (H)      │
│ │ HR: 97 → (Normal)          │ │ Creatinine: 1.84 ↑ (H) │
│ │ Wt: 67.0 → (Stable)       │ │ Troponin: 0.08 → (N)   │
│ └─────────────────────────────┘ │ LVEF: 50.6% → (Normal)  │
├─────────────────────────────────────────────────────────────┤
│ 🔍 Clinical Alerts & Recommendations                        │
│ ⚠️ Stage 1 Hypertension - Consider antihypertensive therapy │
│ ⚠️ Elevated BNP - Cardiology consultation recommended       │
│ ⚠️ Kidney dysfunction - Nephrology evaluation needed        │
├─────────────────────────────────────────────────────────────┤
│ [Generate Clinical Report] [AI Analysis] [Create Query]     │
└─────────────────────────────────────────────────────────────┘
```

#### 5.2.4 Clinical Data Visualization
**Purpose**: Visual representation of clinical data trends and patterns

**Vital Signs Dashboard**:
```
Blood Pressure Trends (CARD001)
┌─────────────────────────────────────────────────────────┐
│ 160 ┤                                              ⚠️   │
│ 150 ┤                                         ●────●   │
│ 140 ┤                                    ●────●         │
│ 130 ┤                               ●────●              │
│ 120 ┤ ────────────────────────────────● Normal Limit   │
│ 110 ┤                                                   │
│ 100 ┤                                                   │
│     └─────────────────────────────────────────────────┤
│      Screen  Week1   Week2   Week4   Week6   Week8     │
└─────────────────────────────────────────────────────────┘
Systolic: 147.5 mmHg ↗ | Diastolic: 79.6 mmHg →
Clinical Interpretation: Stage 1 Hypertension
```

**Laboratory Values Grid**:
```
┌──────────────────────────────────────────────────────────┐
│ Laboratory Trends - Last 4 Visits                       │
├──────────────────────────────────────────────────────────┤
│ Parameter    │ Screen│ Week1 │ Week2 │ Week4 │ Trend│ Flag│
├──────────────────────────────────────────────────────────┤
│ BNP (pg/mL)  │ 319.6 │ 325.1 │ 298.4 │ 342.2 │  ↗   │ H  │
│ Creatinine   │ 1.84  │ 1.79  │ 1.88  │ 1.91  │  ↗   │ H  │
│ Troponin     │ 0.08  │ 0.06  │ 0.05  │ 0.10  │  ↗   │ N  │
│ LVEF (%)     │ 50.6  │ 52.1  │ 49.8  │ 47.5  │  ↘   │ ⚠️  │
└──────────────────────────────────────────────────────────┘
H = High, N = Normal, ⚠️ = Concerning trend
```

#### 5.2.5 Discrepancy Management Interface
**Purpose**: Track and resolve EDC vs source document differences

**Discrepancy Dashboard**:
```
┌─────────────────────────────────────────────────────────────┐
│ Data Discrepancies - CARD001 (48 total)      [Export Report]│
├─────────────────────────────────────────────────────────────┤
│ Priority Filter: [All] [Critical] [Major] [Minor]          │
│ Field Filter: [All Fields] [Vitals] [Labs] [Adverse Events]│
├─────────────────────────────────────────────────────────────┤
│ Field                │ EDC Value │ Source │ Type    │ Status │
├─────────────────────────────────────────────────────────────┤
│ 🔴 adverse_events    │ []        │ [rash] │ Missing │ Open   │
│ ⚠️ vital_signs.sys_bp │ 147.5     │ null   │ Missing │ Open   │
│ ⚠️ laboratory.bnp    │ 319.57    │ null   │ Missing │ Open   │
│ ⚠️ laboratory.creat  │ 1.84      │ null   │ Missing │ Open   │
│ 🟡 imaging.lvef      │ 50.6      │ null   │ Missing │ Open   │
├─────────────────────────────────────────────────────────────┤
│ AI Analysis: 1 critical discrepancy requires immediate     │
│ attention - adverse event not captured in EDC system.      │
│ [Generate Query] [Escalate] [Mark Reviewed]                │
└─────────────────────────────────────────────────────────────┘
```

**Discrepancy Detail View**:
```
┌─────────────────────────────────────────────────────────────┐
│ Discrepancy Detail - CARD001                               │
├─────────────────────────────────────────────────────────────┤
│ Field: adverse_events                     Severity: Critical│
│ Visit: Week 2                            Detected: AI Agent │
├─────────────────────────────────────────────────────────────┤
│ EDC Data:                                                   │
│ No adverse events recorded                                  │
│                                                             │
│ Source Document:                                            │
│ "Patient reported mild rash on arms starting Day 12,       │
│ resolved with topical treatment"                            │
├─────────────────────────────────────────────────────────────┤
│ AI Assessment:                                              │
│ Missing adverse event in EDC - regulatory reporting        │
│ requirement not met. Requires immediate data correction    │
│ and safety evaluation.                                      │
├─────────────────────────────────────────────────────────────┤
│ Recommended Actions:                                        │
│ 1. Add adverse event to EDC system                         │
│ 2. Assess causality relationship to study drug             │
│ 3. Update safety monitoring log                             │
│ 4. Notify medical monitor                                   │
├─────────────────────────────────────────────────────────────┤
│ [Create Query] [Escalate to Medical Monitor] [Update EDC]  │
└─────────────────────────────────────────────────────────────┘
```

#### 5.2.6 Study Management Overview
**Purpose**: High-level study metrics and site performance

**Protocol Overview**:
```
┌─────────────────────────────────────────────────────────────┐
│ Protocol CARD-2025-001: Cardiovascular Phase 2 Study      │
├─────────────────────────────────────────────────────────────┤
│ Study Status: Active          │ Enrollment: 50/60 (83%)    │
│ Start Date: 2025-03-01        │ Completion: 2025-12-31     │
│ Phase: II                     │ Primary Endpoint: LVEF     │
│ Therapeutic Area: Cardiology  │ Duration: 24 weeks         │
├─────────────────────────────────────────────────────────────┤
│ Site Performance Summary:                                   │
│                                                             │
│ SITE_001 (New York)     ████████████░░ 20/25 subjects     │
│ ├─ Enrollment Rate: 4.2/month ↗                           │
│ ├─ Data Quality: 94.2% ↗                                  │
│ └─ Query Rate: 2.1/subject ↘                              │
│                                                             │
│ SITE_002 (Boston)       ████████░░░░░░ 15/20 subjects     │
│ ├─ Enrollment Rate: 3.8/month →                           │
│ ├─ Data Quality: 91.7% →                                  │
│ └─ Query Rate: 3.2/subject ↗                              │
│                                                             │
│ SITE_003 (Chicago)      ██████████░░░░ 15/15 subjects     │
│ ├─ Enrollment Rate: 5.1/month ↗                           │
│ ├─ Data Quality: 96.8% ↗                                  │
│ └─ Query Rate: 1.8/subject ↘                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Functional Requirements

### 6.1 Core Application Features

#### 6.1.1 Real-Time AI Agent Integration
**Feature**: Interactive chat interface with Portfolio Manager
**Requirements**:
- Real-time messaging with clinical AI agent
- Support for complex clinical queries and analysis
- Display of AI tool outputs (JSON results from function tools)
- Clinical finding interpretation and recommendations
- Export capabilities for AI-generated reports

**Implementation Details**:
```typescript
// AI Agent Chat Service
interface AIAgentService {
  sendMessage(message: string): Promise<AIResponse>;
  getAgentStatus(): Promise<AgentStatus>;
  executeWorkflow(workflowType: string, data: any): Promise<WorkflowResult>;
}

interface AIResponse {
  success: boolean;
  response: string;
  agent_id: string;
  execution_time: number;
  metadata: {
    clinical_analysis?: boolean;
    tools_used?: boolean;
    workflow_executed?: boolean;
  };
}
```

#### 6.1.2 Clinical Data Management
**Feature**: Comprehensive subject data visualization and management
**Requirements**:
- Real-time display of 50 cardiology subjects
- Clinical data visualization (vitals, labs, imaging)
- Medical alert system with severity classification
- Integration with test data service endpoints
- Clinical trend analysis and pattern recognition

**Data Models**:
```typescript
interface ClinicalSubject {
  subject_id: string;          // "CARD001"
  demographics: {
    age: number;               // 43
    gender: "M" | "F";         // "F"
    race: string;              // "White"
    weight: number;            // 67.0
    height: number;            // 154.6
    enrollment_date: string;   // "2025-05-08"
  };
  clinical_data: {
    vital_signs: VitalSigns[];
    laboratory: LabValues[];
    imaging: ImagingResults[];
    adverse_events: AdverseEvent[];
  };
  study_status: "active" | "withdrawn" | "completed";
  site_id: string;             // "SITE_001"
}

interface VitalSigns {
  visit: string;               // "Baseline", "Week_4"
  systolic_bp: number;         // 147.5
  diastolic_bp: number;        // 79.6
  heart_rate: number;          // 97.3
  weight: number;              // 67.0
  date: string;
}

interface LabValues {
  visit: string;
  bnp: number;                 // 319.57
  creatinine: number;          // 1.84
  troponin: number;            // 0.08
  date: string;
}
```

#### 6.1.3 Discrepancy Detection and Management
**Feature**: Automated identification and tracking of data discrepancies
**Requirements**:
- Real-time display of EDC vs source document differences
- Severity classification (Critical, Major, Minor)
- AI-powered discrepancy analysis and recommendations
- Workflow integration for discrepancy resolution
- Audit trail and compliance tracking

#### 6.1.4 Clinical Decision Support
**Feature**: AI-powered clinical insights and recommendations
**Requirements**:
- Medical interpretation of clinical values
- Safety signal detection and alerts
- Treatment recommendation suggestions
- Protocol compliance monitoring
- Regulatory requirement tracking

### 6.2 Advanced Features

#### 6.2.1 Workflow Orchestration Visualization
**Feature**: Visual representation of multi-agent workflows
**Requirements**:
- Real-time workflow execution tracking
- Agent handoff visualization
- Performance metrics and timing
- Error handling and recovery displays

#### 6.2.2 Clinical Reporting System
**Feature**: Automated generation of clinical reports
**Requirements**:
- AI-generated clinical summaries
- Regulatory compliance reports
- Site performance analytics
- Custom report builder interface

#### 6.2.3 Safety Monitoring Dashboard
**Feature**: Real-time safety signal detection and management
**Requirements**:
- Adverse event tracking and analysis
- SAE (Serious Adverse Event) notifications
- Medical monitor escalation workflows
- Regulatory timeline compliance tracking

---

## 🎨 User Experience & Design Requirements

### 7.1 Design Principles

#### Medical-Grade Interface Standards
- **Clinical Clarity**: Clean, uncluttered layouts focusing on critical information
- **Medical Accuracy**: Proper medical terminology and reference ranges
- **Safety First**: Critical alerts and safety information prominently displayed
- **Efficiency**: Streamlined workflows for clinical users
- **Accessibility**: WCAG 2.1 AA compliance for all users

#### Visual Design Language
- **Color Scheme**: 
  - Primary: Medical blue (#2563EB)
  - Success: Clinical green (#059669)
  - Warning: Amber (#D97706)
  - Error: Medical red (#DC2626)
  - Critical: Dark red (#B91C1C)
- **Typography**: Inter or similar medical-grade font
- **Icons**: Lucide React or Heroicons for consistency
- **Spacing**: 8px grid system for precise layouts

### 7.2 Responsive Design Requirements

#### Desktop (Primary Interface)
- **Resolution**: 1920x1080 minimum
- **Layouts**: Multi-column dashboards with sidebar navigation
- **Features**: Full functionality including complex data visualizations

#### Tablet (Field Use)
- **Resolution**: 768px+ width
- **Layouts**: Adaptive layouts with collapsible navigation
- **Features**: Essential functionality for site visits

#### Mobile (Basic Access)
- **Resolution**: 375px+ width
- **Layouts**: Single-column stack layouts
- **Features**: Read-only access and critical alerts

### 7.3 Accessibility Requirements
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Readers**: Proper ARIA labels and descriptions
- **Color Contrast**: WCAG AA contrast ratios
- **Text Scaling**: Support up to 200% zoom
- **Focus Management**: Clear focus indicators

---

## 🔌 API Integration Requirements

### 8.1 Backend Service Integration

#### Primary API Endpoints
```typescript
// Base configuration
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://pm-clinical-trials-agent-production.up.railway.app'
  : 'http://localhost:8000';

// AI Agent Services
POST /api/v1/agents/chat
GET  /api/v1/agents/status
POST /api/v1/agents/workflow
DELETE /api/v1/agents/workflow/{workflow_id}

// Test Data Services
GET /api/v1/test-data/status
GET /api/v1/test-data/subjects/{subject_id}
GET /api/v1/test-data/subjects/{subject_id}/discrepancies
GET /api/v1/test-data/sites/performance
GET /api/v1/test-data/study-info
```

#### Data Fetching Strategy
```typescript
// React Query integration for caching and synchronization
import { useQuery, useMutation } from '@tanstack/react-query';

// Subject data with automatic refetching
const useSubjectData = (subjectId: string) => {
  return useQuery({
    queryKey: ['subject', subjectId],
    queryFn: () => api.getSubjectData(subjectId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 30 * 1000, // 30 seconds for active monitoring
  });
};

// AI agent chat with mutation
const useAIChat = () => {
  return useMutation({
    mutationFn: (message: string) => api.sendAIMessage(message),
    onSuccess: (data) => {
      // Handle AI response
      console.log('AI Response:', data.response);
    },
  });
};
```

### 8.2 Real-Time Data Integration

#### WebSocket Implementation (Future Enhancement)
```typescript
// Real-time updates for critical changes
interface WebSocketService {
  onSubjectAlert: (callback: (alert: ClinicalAlert) => void) => void;
  onDiscrepancyDetected: (callback: (discrepancy: Discrepancy) => void) => void;
  onWorkflowUpdate: (callback: (update: WorkflowUpdate) => void) => void;
}
```

#### Error Handling Strategy
```typescript
// Robust error handling for clinical systems
class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public endpoint: string
  ) {
    super(message);
  }
}

// Retry logic for critical operations
const apiWithRetry = async (operation: () => Promise<any>, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await operation();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await delay(1000 * Math.pow(2, i)); // Exponential backoff
    }
  }
};
```

---

## 📊 Data Models & State Management

### 9.1 Application State Structure

#### Global State Management
```typescript
// Redux Toolkit or Zustand store structure
interface AppState {
  auth: AuthState;
  subjects: SubjectsState;
  aiAgents: AIAgentsState;
  discrepancies: DiscrepanciesState;
  ui: UIState;
}

interface SubjectsState {
  list: ClinicalSubject[];
  selected: string | null;
  filters: SubjectFilters;
  loading: boolean;
  error: string | null;
}

interface AIAgentsState {
  chatHistory: ChatMessage[];
  activeWorkflows: Workflow[];
  agentStatus: AgentStatus;
  isProcessing: boolean;
}

interface DiscrepanciesState {
  bySubject: Record<string, Discrepancy[]>;
  filtered: Discrepancy[];
  filters: DiscrepancyFilters;
  resolutionStatus: Record<string, ResolutionStatus>;
}
```

#### Local Component State
```typescript
// Subject profile component state
interface SubjectProfileState {
  activeTab: 'overview' | 'vitals' | 'labs' | 'discrepancies';
  timeRange: 'all' | '30d' | '7d';
  selectedVisit: string | null;
  isEditing: boolean;
}

// AI chat component state
interface AIChatState {
  message: string;
  isTyping: boolean;
  suggestions: string[];
  selectedSubject: string | null;
}
```

### 9.2 Data Validation & Type Safety

#### Runtime Validation with Zod
```typescript
import { z } from 'zod';

// Subject data validation schema
const SubjectSchema = z.object({
  subject_id: z.string().regex(/^CARD\d{3}$/),
  demographics: z.object({
    age: z.number().min(18).max(100),
    gender: z.enum(['M', 'F']),
    race: z.string(),
    weight: z.number().positive(),
    height: z.number().positive(),
    enrollment_date: z.string().datetime(),
  }),
  study_status: z.enum(['active', 'withdrawn', 'completed']),
  site_id: z.string().regex(/^SITE_\d{3}$/),
});

// API response validation
const validateSubjectData = (data: unknown): ClinicalSubject => {
  return SubjectSchema.parse(data);
};
```

---

## ⚡ Performance Requirements

### 10.1 Performance Benchmarks

#### Load Time Requirements
- **Initial Page Load**: < 2 seconds
- **Subject Data Fetch**: < 1 second
- **AI Agent Response**: < 10 seconds (backend processing)
- **Chart Rendering**: < 500ms
- **Navigation Transitions**: < 200ms

#### Scalability Targets
- **Concurrent Users**: 100+ simultaneous users
- **Data Volume**: 50 subjects × 8 visits × multiple data points
- **API Calls**: Rate limiting and efficient caching
- **Memory Usage**: < 100MB for typical session

### 10.2 Optimization Strategies

#### Code Splitting & Lazy Loading
```typescript
// Route-based code splitting
const SubjectsPage = lazy(() => import('./pages/SubjectsPage'));
const AIChatPage = lazy(() => import('./pages/AIChatPage'));
const DiscrepanciesPage = lazy(() => import('./pages/DiscrepanciesPage'));

// Component-level lazy loading
const ClinicalChart = lazy(() => import('./components/ClinicalChart'));
```

#### Data Optimization
```typescript
// Efficient data fetching with pagination
interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// Virtual scrolling for large datasets
import { FixedSizeList as List } from 'react-window';

const SubjectList = ({ subjects }: { subjects: ClinicalSubject[] }) => (
  <List
    height={600}
    itemCount={subjects.length}
    itemSize={80}
    itemData={subjects}
  >
    {SubjectRow}
  </List>
);
```

#### Caching Strategy
```typescript
// Service Worker for offline capability
const cacheStrategy = {
  // Cache clinical data for offline access
  subjects: 'cache-first',
  // Always fetch fresh AI responses
  aiChat: 'network-first',
  // Cache static assets
  assets: 'cache-first',
};
```

---

## 🔒 Security & Compliance Requirements

### 11.1 Security Implementation

#### Authentication & Authorization
```typescript
// JWT-based authentication
interface AuthToken {
  userId: string;
  role: 'cra' | 'cdm' | 'crc' | 'pi' | 'admin';
  permissions: string[];
  exp: number;
}

// Role-based access control
const usePermissions = () => {
  const { user } = useAuth();
  
  return {
    canViewSubject: (subjectId: string) => 
      user.permissions.includes('view_subjects') || 
      user.assignedSubjects.includes(subjectId),
    canEditData: () => user.permissions.includes('edit_data'),
    canAccessAI: () => user.permissions.includes('ai_access'),
  };
};
```

#### Data Protection
```typescript
// PII data handling
interface SecureDataHandler {
  encryptPII(data: string): string;
  maskPII(data: string): string;
  auditAccess(userId: string, dataAccessed: string): void;
}

// Audit trail implementation
const useAuditTrail = () => {
  const logAccess = (action: string, resource: string) => {
    // Log all user actions for compliance
    auditAPI.log({
      timestamp: new Date().toISOString(),
      userId: getCurrentUser().id,
      action,
      resource,
      ipAddress: getClientIP(),
    });
  };
  
  return { logAccess };
};
```

### 11.2 Regulatory Compliance

#### 21 CFR Part 11 Compliance
- **Electronic Signatures**: Digital signatures for critical actions
- **Audit Trails**: Immutable logs of all system interactions
- **Data Integrity**: Validation and verification of all data
- **Access Controls**: Role-based permissions and authentication

#### HIPAA Compliance
- **PHI Protection**: Encryption of all patient data
- **Access Logging**: Audit trails for PHI access
- **Data Minimization**: Only display necessary patient information
- **Secure Transmission**: HTTPS for all API communications

---

## 🧪 Testing Requirements

### 12.1 Testing Strategy

#### Unit Testing (Jest + React Testing Library)
```typescript
// Component testing example
describe('SubjectProfile', () => {
  it('displays clinical alerts correctly', () => {
    const subject = mockSubjectWithAlerts();
    render(<SubjectProfile subject={subject} />);
    
    expect(screen.getByText('⚠️ Stage 1 Hypertension')).toBeInTheDocument();
    expect(screen.getByText('Elevated BNP')).toBeInTheDocument();
  });
  
  it('calls AI analysis when button clicked', async () => {
    const mockAICall = jest.fn();
    render(<SubjectProfile subject={mockSubject()} onAIAnalysis={mockAICall} />);
    
    await user.click(screen.getByText('AI Analysis'));
    expect(mockAICall).toHaveBeenCalledWith(mockSubject().subject_id);
  });
});
```

#### Integration Testing
```typescript
// API integration testing
describe('AI Agent Integration', () => {
  it('sends clinical analysis request successfully', async () => {
    const mockResponse = {
      success: true,
      response: 'CLINICAL FINDING: BP 147.5/79.6 = Stage 1 HTN',
      execution_time: 8.5,
    };
    
    mockAPI.post('/api/v1/agents/chat').mockResolvedValue(mockResponse);
    
    const result = await aiService.analyzeSubject('CARD001');
    expect(result.response).toContain('Stage 1 HTN');
  });
});
```

#### End-to-End Testing (Playwright or Cypress)
```typescript
// E2E testing example
test('complete clinical workflow', async ({ page }) => {
  await page.goto('/subjects');
  
  // Select subject
  await page.click('[data-testid="subject-CARD001"]');
  
  // Request AI analysis
  await page.click('[data-testid="ai-analysis-button"]');
  
  // Verify clinical findings displayed
  await expect(page.locator('[data-testid="clinical-findings"]'))
    .toContainText('Stage 1 Hypertension');
  
  // Generate clinical report
  await page.click('[data-testid="generate-report"]');
  
  // Verify report generated
  await expect(page.locator('[data-testid="report-status"]'))
    .toContainText('Report generated successfully');
});
```

### 12.2 Performance Testing

#### Load Testing
```typescript
// Performance testing with automated monitoring
const performanceTests = {
  subjectListLoad: {
    target: '< 1 second',
    test: 'Load 50 subjects with clinical data',
  },
  aiResponseTime: {
    target: '< 10 seconds',
    test: 'AI clinical analysis request',
  },
  chartRendering: {
    target: '< 500ms',
    test: 'Render vital signs trends chart',
  },
};
```

#### Accessibility Testing
```typescript
// Automated accessibility testing
import { axe, toHaveNoViolations } from 'jest-axe';

test('dashboard has no accessibility violations', async () => {
  const { container } = render(<Dashboard />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

---

## 🚀 Implementation Plan & Milestones

### 13.1 Development Phases

#### Phase 1: Foundation & Core Infrastructure (Week 1-2)
**Sprint Goals**:
- Set up React + TypeScript + Vite development environment
- Implement basic routing and navigation structure
- Create design system and UI component library
- Set up API integration layer with backend
- Implement authentication and basic security

**Key Deliverables**:
- ✅ Development environment with hot reload
- ✅ Component library with Tailwind CSS
- ✅ API service layer with TypeScript types
- ✅ Basic authentication flow
- ✅ Responsive navigation structure

**Acceptance Criteria**:
- Development environment builds without errors
- Navigation works across all screen sizes
- API integration successfully fetches test data
- Authentication flow prevents unauthorized access

#### Phase 2: Subject Management & Clinical Data (Week 3-4)
**Sprint Goals**:
- Build comprehensive subject dashboard
- Implement clinical data visualization
- Create subject profile pages with medical data
- Integrate with real test data service (50 subjects)
- Add medical alerts and clinical interpretations

**Key Deliverables**:
- ✅ Subject list with search and filtering
- ✅ Individual subject profiles with clinical data
- ✅ Vital signs trends and laboratory value charts
- ✅ Medical alert system with severity indicators
- ✅ Integration with backend test data endpoints

**Acceptance Criteria**:
- All 50 cardiology subjects display correctly
- Clinical data charts render properly
- Medical alerts show appropriate severity levels
- Subject profiles load in < 1 second

#### Phase 3: AI Agent Integration & Chat Interface (Week 5-6)
**Sprint Goals**:
- Build interactive AI agent chat interface
- Implement real-time messaging with Portfolio Manager
- Display AI clinical analysis and recommendations
- Add workflow orchestration visualization
- Create clinical report generation features

**Key Deliverables**:
- ✅ Real-time chat interface with AI agent
- ✅ Clinical analysis display with medical interpretations
- ✅ AI tool output visualization (JSON results)
- ✅ Workflow execution tracking
- ✅ Clinical report export functionality

**Acceptance Criteria**:
- AI agent responds with clinical analysis in < 10 seconds
- Clinical findings display in proper medical format
- Tool outputs show complete JSON results
- Reports generate in PDF format

#### Phase 4: Discrepancy Management & Quality Control (Week 7-8)
**Sprint Goals**:
- Build discrepancy detection and tracking interface
- Implement EDC vs source document comparison
- Add discrepancy resolution workflows
- Create data quality dashboards
- Integrate with AI-powered discrepancy analysis

**Key Deliverables**:
- ✅ Discrepancy dashboard with filtering and sorting
- ✅ Individual discrepancy detail views
- ✅ Resolution workflow tracking
- ✅ AI-powered discrepancy analysis display
- ✅ Data quality metrics and reporting

**Acceptance Criteria**:
- All 48 discrepancies per subject display correctly
- Severity classification works properly
- Resolution tracking updates in real-time
- AI analysis provides actionable recommendations

#### Phase 5: Study Management & Analytics (Week 9-10)
**Sprint Goals**:
- Build study overview and protocol management
- Implement site performance analytics
- Create enrollment tracking and projections
- Add regulatory compliance monitoring
- Build executive dashboard with key metrics

**Key Deliverables**:
- ✅ Protocol CARD-2025-001 overview dashboard
- ✅ Site performance comparison (3 sites)
- ✅ Enrollment tracking and timeline visualization
- ✅ Regulatory compliance checklist
- ✅ Executive summary with KPIs

**Acceptance Criteria**:
- Study metrics update in real-time
- Site performance comparisons are accurate
- Enrollment projections are data-driven
- Compliance tracking shows regulatory status

#### Phase 6: Advanced Features & Polish (Week 11-12)
**Sprint Goals**:
- Implement advanced clinical workflows
- Add safety monitoring and SAE tracking
- Create custom reporting and analytics
- Optimize performance and user experience
- Conduct comprehensive testing and bug fixes

**Key Deliverables**:
- ✅ Safety monitoring dashboard
- ✅ Custom report builder
- ✅ Performance optimizations
- ✅ Comprehensive test coverage
- ✅ Production deployment

**Acceptance Criteria**:
- All performance benchmarks met
- Safety alerts trigger appropriately
- Custom reports generate correctly
- System handles 100+ concurrent users

### 13.2 Technical Milestones

#### Milestone 1: Technical Foundation Complete
**Date**: End of Week 2
**Criteria**: 
- ✅ Development environment fully operational
- ✅ Component library and design system implemented
- ✅ API integration layer with full TypeScript types
- ✅ Authentication and basic security functional

#### Milestone 2: Clinical Data Integration Complete
**Date**: End of Week 4
**Criteria**:
- ✅ All 50 subjects displaying with complete clinical profiles
- ✅ Real-time clinical data visualization working
- ✅ Medical alerts and severity classification functional
- ✅ Performance targets met for data loading

#### Milestone 3: AI Intelligence Showcase Complete
**Date**: End of Week 6
**Criteria**:
- ✅ AI agent providing real clinical analysis
- ✅ Medical recommendations displaying properly
- ✅ Workflow orchestration visible and functional
- ✅ Clinical reports generating automatically

#### Milestone 4: Production-Ready System
**Date**: End of Week 12
**Criteria**:
- ✅ All core features implemented and tested
- ✅ Performance and security requirements met
- ✅ Comprehensive documentation complete
- ✅ Production deployment successful

---

## 📈 Success Metrics & KPIs

### 14.1 User Experience Metrics

#### Usability Metrics
- **Task Completion Rate**: > 95% for core workflows
- **Time to Complete Analysis**: < 2 minutes for subject clinical review
- **User Error Rate**: < 2% for data entry and navigation
- **User Satisfaction Score**: > 4.5/5 for clinical users

#### Performance Metrics
- **Page Load Time**: < 2 seconds for all major pages
- **AI Response Time**: < 10 seconds for clinical analysis
- **System Availability**: > 99.5% uptime
- **Mobile Responsiveness**: 100% feature parity on tablets

### 14.2 Clinical Intelligence Metrics

#### AI Agent Effectiveness
- **Clinical Accuracy**: > 95% for medical interpretations
- **Discrepancy Detection**: > 90% accuracy for identifying data issues
- **Workflow Efficiency**: 8-40x improvement in query resolution time
- **Medical Recommendations**: > 90% clinically appropriate suggestions

#### Data Quality Impact
- **Discrepancy Resolution Time**: < 3 minutes average
- **Data Completeness**: > 98% for critical clinical fields
- **Query Generation Accuracy**: > 95% for AI-generated queries
- **Regulatory Compliance**: 100% audit trail completeness

### 14.3 Business Impact Metrics

#### Operational Efficiency
- **Query Processing Time**: From 30 minutes to < 3 minutes
- **SDV Cost Reduction**: 75% improvement in data verification efficiency
- **Site Monitoring Efficiency**: 50% reduction in monitoring time
- **Training Time**: < 2 hours for new user onboarding

#### Clinical Trial Metrics
- **Protocol Compliance**: > 95% adherence to study protocols
- **Safety Signal Detection**: < 30 minutes for critical findings
- **Data Lock Timeline**: 40% faster database lock
- **Regulatory Submission**: 60% faster preparation time

---

## 🎯 Demo & Showcase Strategy

### 15.1 Clinical Intelligence Demonstration

#### Demo Scenario 1: Real Patient Analysis
**Subject**: CARD001 - 43-year-old female with cardiovascular risks
**Demo Flow**:
1. **Navigate to Subject**: Show subject list, select CARD001
2. **Display Clinical Profile**: Demographics, vital signs, lab values
3. **Identify Clinical Issues**: BP 147.5/79.6 (Stage 1 HTN), elevated BNP (319.57)
4. **AI Analysis**: Chat with Portfolio Manager for clinical interpretation
5. **Medical Recommendations**: Cardiology consultation, nephrology evaluation
6. **Generate Report**: Export clinical summary with AI insights

**Key Highlights**:
- Real clinical data, not mock examples
- Proper medical interpretation with normal ranges
- AI-powered clinical recommendations
- Comprehensive clinical workflow demonstration

#### Demo Scenario 2: Discrepancy Detection & Resolution
**Subject**: CARD001 with 48 actual discrepancies
**Demo Flow**:
1. **Discrepancy Dashboard**: Show 48 EDC vs source differences
2. **Critical Issue**: Missing adverse event in EDC (rash not recorded)
3. **AI Assessment**: Regulatory implications and safety concerns
4. **Resolution Workflow**: Generate query, escalate to medical monitor
5. **Audit Trail**: Track resolution and compliance documentation

**Key Highlights**:
- Real discrepancies from test data
- AI-powered severity assessment
- Regulatory compliance awareness
- Automated workflow orchestration

#### Demo Scenario 3: Study Management Overview
**Protocol**: CARD-2025-001 with 50 subjects across 3 sites
**Demo Flow**:
1. **Study Dashboard**: Protocol overview and enrollment progress
2. **Site Performance**: Compare 3 sites' data quality and efficiency
3. **AI Analytics**: Pattern detection and performance insights
4. **Executive Summary**: Key metrics and ROI demonstration

**Key Highlights**:
- Real study with actual metrics
- Multi-site performance comparison
- AI-driven insights and recommendations
- Executive-level reporting

### 15.2 Stakeholder-Specific Demos

#### For Clinical Research Associates (CRA)
**Focus**: Site monitoring and data verification efficiency
**Demo Elements**:
- Subject monitoring dashboard with clinical alerts
- AI-assisted discrepancy resolution
- Query generation and tracking
- Site performance analytics

#### For Clinical Data Managers (CDM)
**Focus**: Data quality and database management
**Demo Elements**:
- Data quality dashboards with AI insights
- Automated discrepancy detection
- Cross-system data verification
- Query workflow optimization

#### For Principal Investigators (PI)
**Focus**: Clinical oversight and medical decision making
**Demo Elements**:
- Clinical summary dashboards with medical insights
- Safety signal detection and escalation
- AI-powered clinical recommendations
- Regulatory compliance tracking

#### For Executives
**Focus**: ROI and business impact
**Demo Elements**:
- 8-40x efficiency improvements
- Cost reduction metrics (75% SDV savings)
- Quality improvements (95% accuracy)
- Regulatory compliance (100% audit trails)

---

## 🔄 Maintenance & Evolution

### 16.1 Ongoing Development Priorities

#### Short-term Enhancements (3-6 months)
- **Enhanced AI Capabilities**: More sophisticated clinical analysis
- **Advanced Visualizations**: Interactive charts and clinical timelines
- **Mobile App**: Native iOS and Android applications
- **Integration Expansion**: Additional EDC systems and lab interfaces

#### Medium-term Evolution (6-12 months)
- **Predictive Analytics**: ML models for outcome prediction
- **Multi-Study Support**: Handle multiple protocols simultaneously
- **Advanced Workflow**: Complex clinical decision trees
- **API Ecosystem**: Third-party integrations and marketplace

#### Long-term Vision (12+ months)
- **Real-time Collaboration**: Multi-user real-time editing
- **Advanced AI Agents**: Specialized agents for different therapeutic areas
- **Regulatory Intelligence**: Automated regulatory submission preparation
- **Global Deployment**: Multi-region, multi-language support

### 16.2 Success Criteria for MVP

#### Technical Success Criteria
- ✅ All 50 subjects display with complete clinical data
- ✅ AI agent provides medically accurate clinical analysis
- ✅ Discrepancy detection identifies all 48 issues per subject
- ✅ Performance meets all benchmarks (< 2s load times)
- ✅ Security and compliance requirements fully met

#### Business Success Criteria
- ✅ Demonstrates 8-40x efficiency improvements
- ✅ Shows 75% cost reduction potential for SDV
- ✅ Achieves > 95% clinical accuracy in AI analysis
- ✅ Provides 100% audit trail compliance
- ✅ Receives > 90% user satisfaction in testing

#### Clinical Success Criteria
- ✅ Proper medical interpretation of all clinical values
- ✅ Appropriate severity classification for all findings
- ✅ Clinically relevant recommendations for all subjects
- ✅ Regulatory compliance for all workflows
- ✅ Safety signal detection within required timelines

---

## 📋 Appendices

### Appendix A: Technical Specifications

#### Development Environment Setup
```bash
# Frontend setup
npm create vite@latest clinical-trials-frontend -- --template react-ts
cd clinical-trials-frontend
npm install

# Key dependencies
npm install @tanstack/react-query axios
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu
npm install lucide-react clsx tailwind-merge
npm install recharts date-fns
npm install @types/node

# Development tools
npm install -D eslint prettier @types/react @types/react-dom
npm install -D @testing-library/react @testing-library/jest-dom
npm install -D vitest jsdom @vitejs/plugin-react
```

#### Project Structure
```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ui/             # Base UI components (buttons, inputs)
│   │   ├── charts/         # Clinical data visualization
│   │   ├── forms/          # Data entry and editing forms
│   │   └── layout/         # Navigation and layout components
│   ├── pages/              # Route-level page components
│   │   ├── Dashboard.tsx   # Main dashboard
│   │   ├── Subjects/       # Subject management pages
│   │   ├── AIChat/         # AI agent interaction
│   │   ├── Discrepancies/  # Data quality management
│   │   └── Study/          # Study management
│   ├── services/           # API integration and data services
│   │   ├── api.ts          # Base API configuration
│   │   ├── subjects.ts     # Subject data services
│   │   ├── aiAgent.ts      # AI agent communication
│   │   └── testData.ts     # Test data service integration
│   ├── hooks/              # Custom React hooks
│   │   ├── useSubjects.ts  # Subject data management
│   │   ├── useAIChat.ts    # AI agent interaction
│   │   └── useAuth.ts      # Authentication management
│   ├── types/              # TypeScript type definitions
│   │   ├── clinical.ts     # Clinical data types
│   │   ├── api.ts          # API response types
│   │   └── ui.ts           # UI component types
│   ├── utils/              # Utility functions
│   │   ├── clinical.ts     # Clinical calculations and formatting
│   │   ├── formatting.ts   # Data formatting utilities
│   │   └── constants.ts    # Application constants
│   └── styles/             # Global styles and themes
├── public/                 # Static assets
├── tests/                  # Test files
└── docs/                   # Documentation
```

### Appendix B: Component Library Specifications

#### Base UI Components
```typescript
// Button component with clinical styling
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'critical' | 'success';
  size: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  children: React.ReactNode;
}

// Clinical alert component
interface AlertProps {
  severity: 'critical' | 'major' | 'minor' | 'info';
  title: string;
  description?: string;
  dismissible?: boolean;
  actions?: React.ReactNode;
}

// Data table for clinical information
interface DataTableProps<T> {
  data: T[];
  columns: ColumnDef<T>[];
  sorting?: boolean;
  filtering?: boolean;
  pagination?: boolean;
  selection?: boolean;
}
```

### Appendix C: API Integration Examples

#### Subject Data Fetching
```typescript
// Get subject clinical data
const getSubjectData = async (subjectId: string): Promise<ClinicalSubject> => {
  const response = await api.get(`/test-data/subjects/${subjectId}`);
  return validateSubjectData(response.data);
};

// AI agent clinical analysis
const analyzeSubject = async (subjectId: string): Promise<AIAnalysis> => {
  const response = await api.post('/agents/chat', {
    message: `Analyze clinical data for ${subjectId}. Use your get_test_subject_data tool to get their real clinical data, then analyze it.`,
    agent_type: 'portfolio-manager'
  });
  return response.data;
};

// Get discrepancies for subject
const getSubjectDiscrepancies = async (subjectId: string): Promise<Discrepancy[]> => {
  const response = await api.get(`/test-data/subjects/${subjectId}/discrepancies`);
  return response.data.discrepancies;
};
```

### Appendix D: Testing Strategy Details

#### Component Testing Examples
```typescript
// Subject profile component test
describe('SubjectProfile', () => {
  const mockSubject: ClinicalSubject = {
    subject_id: 'CARD001',
    demographics: {
      age: 43,
      gender: 'F',
      race: 'White',
      weight: 67.0,
      height: 154.6,
      enrollment_date: '2025-05-08'
    },
    study_status: 'active',
    site_id: 'SITE_001'
  };

  it('displays subject demographics correctly', () => {
    render(<SubjectProfile subject={mockSubject} />);
    
    expect(screen.getByText('CARD001')).toBeInTheDocument();
    expect(screen.getByText('43F')).toBeInTheDocument();
    expect(screen.getByText('SITE_001')).toBeInTheDocument();
  });
  
  it('shows clinical alerts when present', () => {
    const subjectWithAlerts = {
      ...mockSubject,
      clinical_alerts: [
        { severity: 'major', message: 'Stage 1 Hypertension' }
      ]
    };
    
    render(<SubjectProfile subject={subjectWithAlerts} />);
    expect(screen.getByText('⚠️ Stage 1 Hypertension')).toBeInTheDocument();
  });
});
```

---

## 🎯 Conclusion

This comprehensive PRD provides a complete roadmap for building a world-class clinical trials management frontend that showcases our **production-ready AI intelligence**. The system will demonstrate genuine clinical expertise through real patient data analysis, not mock demonstrations.

### Key Differentiators
- **Real Clinical Intelligence**: Actual analysis of 50 cardiology subjects
- **Medical Expertise**: Proper interpretation of BP, BNP, creatinine, LVEF
- **AI-Powered Workflows**: Multi-agent orchestration for clinical processes
- **Regulatory Compliance**: FDA-ready audit trails and compliance tracking
- **Production Ready**: Live deployment with real-time clinical analysis

The frontend will serve as the perfect demonstration of our clinical AI capabilities, showing stakeholders how artificial intelligence can transform clinical trial operations through genuine medical intelligence and workflow automation.

**Development Timeline**: 12 weeks to full production deployment  
**Success Metrics**: 8-40x efficiency improvements, 95% clinical accuracy, 75% cost reduction  
**Business Impact**: Revolutionary advancement in clinical trial technology with immediate ROI