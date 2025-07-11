import { BaseApiService } from './baseApiService';
import { StudyStatus, ClinicalSubject, Discrepancy } from './types';

export class StudyService extends BaseApiService {
  // Study and overview data
  async getStudyStatus(): Promise<StudyStatus> {
    try {
      return await this.fetchApi<StudyStatus>('/test-data/status');
    } catch (error) {
      console.warn('Using mock study status data due to API failure');
      return {
        study_id: 'CARD-2025-001',
        protocol: 'Cardiovascular Phase 2 Clinical Trial',
        phase: 'Phase II',
        status: 'Active',
        subjects_enrolled: 50,
        target_enrollment: 60,
        sites_active: 3,
        start_date: '2025-03-01',
        estimated_completion: '2025-12-31'
      };
    }
  }

  // Subject data - Limited to 10 for demo
  async getSubjects(): Promise<ClinicalSubject[]> {
    try {
      // Fetch only first 10 subjects for demo to reduce LLM costs
      const subjects: ClinicalSubject[] = [];
      for (let i = 1; i <= 10; i++) {
        const subjectId = `CARD${i.toString().padStart(3, '0')}`;
        try {
          const subject = await this.getSubjectData(subjectId);
          subjects.push(subject);
        } catch (error) {
          console.warn(`Failed to fetch subject ${subjectId}:`, error);
        }
      }
      
      // If we got some subjects, return them, otherwise use limited mock
      if (subjects.length > 0) {
        return subjects;
      } else {
        throw new Error('No subjects fetched from API');
      }
    } catch (error) {
      console.warn('Using limited mock subjects data (10 subjects for demo)');
      return this.getMockSubjects().slice(0, 10); // Limit to 10 for demo
    }
  }

  async getSubjectData(subjectId: string): Promise<ClinicalSubject> {
    try {
      const apiResponse = await this.fetchApi<any>(`/test-data/subjects/${subjectId}`);
      
      // Transform API response to match our interface
      if (apiResponse.data && apiResponse.data.subject_info) {
        const subjectInfo = apiResponse.data.subject_info;
        const visitData = apiResponse.data.visit_data;
        
        // Get the latest visit data (Week_4 or most recent)
        const latestVisit = visitData.Week_4 || visitData.Baseline || visitData.Screening;
        
        return {
          subject_id: subjectInfo.subject_id,
          demographics: {
            age: subjectInfo.demographics.age,
            gender: subjectInfo.demographics.gender as "M" | "F",
            race: subjectInfo.demographics.race,
            weight: subjectInfo.demographics.weight,
            height: subjectInfo.demographics.height,
            enrollment_date: subjectInfo.demographics.enrollment_date
          },
          clinical_data: {
            vital_signs: latestVisit ? [{
              visit: "Week_4",
              systolic_bp: latestVisit.vital_signs.systolic_bp,
              diastolic_bp: latestVisit.vital_signs.diastolic_bp,
              heart_rate: latestVisit.vital_signs.heart_rate,
              weight: subjectInfo.demographics.weight,
              date: new Date().toISOString().split('T')[0]
            }] : [],
            laboratory: latestVisit ? [{
              visit: "Week_4",
              bnp: latestVisit.laboratory.bnp,
              creatinine: latestVisit.laboratory.creatinine,
              troponin: latestVisit.laboratory.troponin,
              date: new Date().toISOString().split('T')[0]
            }] : [],
            imaging: latestVisit ? [{
              visit: "Week_4",
              lvef: latestVisit.imaging.lvef,
              date: new Date().toISOString().split('T')[0],
              findings: latestVisit.imaging.wall_motion || "Normal"
            }] : [],
            adverse_events: latestVisit?.adverse_events?.map((ae: any) => ({
              event: ae.term,
              severity: ae.severity as "Mild" | "Moderate" | "Severe",
              relationship: "Possibly related",
              date: ae.start_date
            })) || []
          },
          study_status: "active" as const,
          site_id: subjectInfo.site_id
        };
      }
      
      // Fallback to original response if structure is different
      return apiResponse;
    } catch (error) {
      console.warn(`Using mock data for ${subjectId}`);
      return this.getMockSubject(subjectId);
    }
  }

  private getMockSubjects(): ClinicalSubject[] {
    // Limited to 10 subjects for demo to reduce LLM processing costs
    const subjects: ClinicalSubject[] = [];
    for (let i = 1; i <= 10; i++) {
      const subjectId = `CARD${i.toString().padStart(3, '0')}`;
      subjects.push(this.getMockSubject(subjectId));
    }
    return subjects;
  }

  private getMockSubject(subjectId: string): ClinicalSubject {
    const num = parseInt(subjectId.replace('CARD', ''));
    const isCard001 = subjectId === 'CARD001';
    
    return {
      subject_id: subjectId,
      demographics: {
        age: isCard001 ? 43 : 35 + (num % 40),
        gender: (num % 2 === 0) ? "M" : "F" as "M" | "F",
        race: ["White", "Black", "Hispanic", "Asian"][num % 4],
        weight: isCard001 ? 67.0 : 60 + (num % 30),
        height: isCard001 ? 154.6 : 150 + (num % 25),
        enrollment_date: "2025-05-08"
      },
      clinical_data: {
        vital_signs: [{
          visit: "Week_4",
          systolic_bp: isCard001 ? 147.5 : 120 + (num % 30),
          diastolic_bp: isCard001 ? 79.6 : 70 + (num % 20),
          heart_rate: isCard001 ? 97.3 : 70 + (num % 30),
          weight: isCard001 ? 67.0 : 60 + (num % 30),
          date: "2025-06-05"
        }],
        laboratory: [{
          visit: "Week_4",
          bnp: isCard001 ? 319.57 : 100 + (num % 300),
          creatinine: isCard001 ? 1.84 : 0.8 + (num % 1.0),
          troponin: isCard001 ? 0.08 : 0.01 + (num % 0.1),
          date: "2025-06-05"
        }],
        imaging: [{
          visit: "Week_4",
          lvef: isCard001 ? 50.6 : 50 + (num % 20),
          date: "2025-06-05",
          findings: isCard001 ? "Normal cardiac function" : "Within normal limits"
        }],
        adverse_events: isCard001 ? [{
          event: "Mild rash",
          severity: "Mild" as const,
          relationship: "Possibly related",
          date: "2025-05-20"
        }] : []
      },
      study_status: (num % 10 === 0) ? "withdrawn" : "active" as const,
      site_id: `SITE_00${(num % 3) + 1}`
    };
  }

  async getSubjectDiscrepancies(subjectId: string): Promise<{ discrepancies: Discrepancy[] }> {
    try {
      return await this.fetchApi<{ discrepancies: Discrepancy[] }>(`/test-data/subjects/${subjectId}/discrepancies`);
    } catch (error) {
      console.warn(`Using mock discrepancies for ${subjectId}`);
      return { discrepancies: this.getMockDiscrepancies(subjectId) };
    }
  }

  private getMockDiscrepancies(subjectId: string): Discrepancy[] {
    const isCard001 = subjectId === 'CARD001';
    if (!isCard001) return [];
    
    return [
      {
        field: "adverse_events",
        edc_value: [],
        source_value: ["rash"],
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
      }
    ];
  }

  // Site performance
  async getSitePerformance(): Promise<any> {
    try {
      return await this.fetchApi('/test-data/sites/performance');
    } catch (error) {
      console.warn('Using mock site performance data');
      return {
        sites: [
          { site_id: 'SITE_001', enrollment: 20, data_quality: 94.2 },
          { site_id: 'SITE_002', enrollment: 15, data_quality: 91.7 },
          { site_id: 'SITE_003', enrollment: 15, data_quality: 96.8 }
        ]
      };
    }
  }
}