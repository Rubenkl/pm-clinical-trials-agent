import { BaseApiService } from './baseApiService';

export class DemoDataService extends BaseApiService {
  // Recommended subject pools for realistic demos
  private cleanSubjects = ['CARD003', 'CARD004', 'CARD007', 'CARD008', 'CARD010', 'CARD014', 'CARD015', 'CARD027'];
  private problemSubjects = ['CARD001', 'CARD002', 'CARD005', 'CARD006'];
  private protocolViolationSubjects = ['CARD010', 'CARD030']; // age violations
  
  async getDemoQueries(limit: number = 10): Promise<any> {
    try {
      return await this.fetchApi(`/test-data/queries?limit=${limit}`);
    } catch (error) {
      console.warn('Failed to fetch demo queries');
      throw error;
    }
  }

  async getDemoSDVSessions(limit: number = 10): Promise<any> {
    try {
      return await this.fetchApi(`/test-data/sdv/sessions?limit=${limit}`);
    } catch (error) {
      console.warn('Failed to fetch demo SDV sessions');
      throw error;
    }
  }

  async getDemoProtocolDeviations(limit: number = 10): Promise<any> {
    try {
      return await this.fetchApi(`/test-data/protocol/deviations?limit=${limit}`);
    } catch (error) {
      console.warn('Failed to fetch demo protocol deviations');
      throw error;
    }
  }

  async getDemoSubjects(limit: number = 10): Promise<any> {
    try {
      // Mix of clean and problem subjects for realistic demo scenarios
      const selectedSubjects = [
        ...this.problemSubjects.slice(0, Math.ceil(limit * 0.3)), // 30% problem subjects
        ...this.cleanSubjects.slice(0, Math.floor(limit * 0.7))    // 70% clean subjects
      ].slice(0, limit);

      const subjects = [];
      for (const subjectId of selectedSubjects) {
        try {
          const subject = await this.fetchApi(`/test-data/subjects/${subjectId}`);
          subjects.push(subject);
        } catch (error) {
          console.warn(`Failed to fetch demo subject ${subjectId}`);
        }
      }
      return subjects;
    } catch (error) {
      console.warn('Failed to fetch demo subjects');
      throw error;
    }
  }

  // Get subjects by scenario type
  async getCleanSubjects(limit: number = 5): Promise<any> {
    return this.getSubjectsByType(this.cleanSubjects.slice(0, limit));
  }

  async getProblemSubjects(limit: number = 4): Promise<any> {
    return this.getSubjectsByType(this.problemSubjects.slice(0, limit));
  }

  async getProtocolViolationSubjects(limit: number = 2): Promise<any> {
    return this.getSubjectsByType(this.protocolViolationSubjects.slice(0, limit));
  }

  private async getSubjectsByType(subjectIds: string[]): Promise<any> {
    const subjects = [];
    for (const subjectId of subjectIds) {
      try {
        const subject = await this.fetchApi(`/test-data/subjects/${subjectId}`);
        subjects.push(subject);
      } catch (error) {
        console.warn(`Failed to fetch subject ${subjectId}`);
      }
    }
    return subjects;
  }

  // Analyze with limited context to reduce LLM costs
  async analyzeQueryDemo(data: {
    subject_id: string;
    site_id: string;
    visit: string;
    field_name: string;
    field_value: string;
    expected_value?: string;
    form_name: string;
    context?: {
      demo_mode: boolean;
      limit_analysis: boolean;
    };
  }): Promise<any> {
    try {
      // Add demo context to reduce LLM processing
      const demoData = {
        ...data,
        context: {
          ...data.context,
          demo_mode: true,
          limit_analysis: true,
          sample_size: 10
        }
      };
      
      return await this.fetchApi('/clinical/analyze-query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query_id: `QRY-${Date.now()}-${data.subject_id}`,
          subject_id: data.subject_id,
          query_text: `${data.field_name}: ${data.field_value}${data.expected_value ? ` (expected: ${data.expected_value})` : ''}`,
          data_points: [{
            field: data.field_name,
            value: data.field_value,
            unit: this.getUnitForField(data.field_name)
          }]
        })
      });
    } catch (error) {
      console.warn('Demo query analysis failed:', error);
      throw error;
    }
  }

  private getUnitForField(fieldName: string): string {
    const unitMap: Record<string, string> = {
      'hemoglobin': 'g/dL',
      'systolic_bp': 'mmHg',
      'diastolic_bp': 'mmHg',
      'heart_rate': 'bpm',
      'lvef': '%',
      'bnp': 'pg/mL',
      'creatinine': 'mg/dL',
      'troponin': 'ng/mL'
    };
    return unitMap[fieldName] || '';
  }
}