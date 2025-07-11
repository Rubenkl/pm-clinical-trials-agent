import { BaseApiService } from './baseApiService';

export class QueryService extends BaseApiService {
  // Query Management - Use AI-powered endpoints with limits
  async getQueries(params?: {
    skip?: number;
    limit?: number;
    severity?: string[];
    status?: string[];
    site_id?: string;
    subject_id?: string;
  }): Promise<any> {
    try {
      const queryParams = new URLSearchParams();
      // Default to limit 10 for demo to reduce costs
      queryParams.append('skip', (params?.skip || 0).toString());
      queryParams.append('limit', (params?.limit || 10).toString());
      
      if (params?.severity) params.severity.forEach(s => queryParams.append('severity', s));
      if (params?.status) params.status.forEach(s => queryParams.append('status', s));
      if (params?.site_id) queryParams.append('site_id', params.site_id);
      if (params?.subject_id) queryParams.append('subject_id', params.subject_id);
      
      const endpoint = `/test-data/queries?${queryParams.toString()}`;
      return await this.fetchApi(endpoint);
    } catch (error) {
      console.warn('Failed to fetch queries from API, using test data endpoint');
      return await this.fetchApi('/test-data/queries');
    }
  }

  async getQueryStats(): Promise<any> {
    try {
      return await this.fetchApi('/dashboard/metrics/queries');
    } catch (error) {
      console.warn('Failed to fetch query stats, using test data');
      return await this.fetchApi('/test-data/queries');
    }
  }

  async analyzeQuery(data: {
    subject_id: string;
    site_id: string;
    visit: string;
    field_name: string;
    field_value: string;
    expected_value?: string;
    form_name: string;
    context?: any;
  }): Promise<any> {
    try {
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
      console.warn('Query analysis failed:', error);
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