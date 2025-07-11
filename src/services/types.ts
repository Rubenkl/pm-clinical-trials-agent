export interface StudyStatus {
  study_id: string;
  protocol: string;
  phase: string;
  status: string;
  subjects_enrolled: number;
  target_enrollment: number;
  sites_active: number;
  start_date: string;
  estimated_completion: string;
}

export interface ClinicalSubject {
  subject_id: string;
  demographics: {
    age: number;
    gender: "M" | "F";
    race: string;
    weight: number;
    height: number;
    enrollment_date: string;
  };
  clinical_data: {
    vital_signs: VitalSigns[];
    laboratory: LabValues[];
    imaging: ImagingResults[];
    adverse_events: AdverseEvent[];
  };
  study_status: "active" | "withdrawn" | "completed";
  site_id: string;
}

export interface VitalSigns {
  visit: string;
  systolic_bp: number;
  diastolic_bp: number;
  heart_rate: number;
  weight: number;
  date: string;
}

export interface LabValues {
  visit: string;
  bnp: number;
  creatinine: number;
  troponin: number;
  date: string;
}

export interface ImagingResults {
  visit: string;
  lvef: number;
  date: string;
  findings?: string;
}

export interface AdverseEvent {
  event: string;
  severity: "Mild" | "Moderate" | "Severe";
  relationship: string;
  date: string;
}

export interface Discrepancy {
  field: string;
  edc_value: any;
  source_value: any;
  discrepancy_type: "missing" | "mismatch" | "format_error";
  severity: "critical" | "major" | "minor";
  status: "open" | "resolved" | "pending";
}

export interface AIResponse {
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