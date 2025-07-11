import { BaseApiService } from './baseApiService';

export class ComplianceService extends BaseApiService {
  // Protocol Compliance - AI Powered
  async getProtocolDeviations(): Promise<any> {
    try {
      return await this.fetchApi('/test-data/protocol/deviations');
    } catch (error) {
      console.warn('Failed to fetch protocol deviations');
      throw error;
    }
  }

  async getDeviationStats(): Promise<any> {
    try {
      return await this.fetchApi('/dashboard/metrics/compliance');
    } catch (error) {
      console.warn('Failed to fetch deviation stats, using test data');
      return await this.fetchApi('/test-data/protocol/deviations');
    }
  }

  async detectProtocolDeviations(data: {
    subject_id: string;
    site_id: string;
    visit: string;
    protocol_data: any;
    actual_data: any;
  }): Promise<any> {
    try {
      return await this.fetchApi('/clinical/detect-deviations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject_id: data.subject_id,
          visit_data: {
            visit_date: new Date().toISOString().split('T')[0],
            scheduled_date: new Date(Date.now() - 86400000).toISOString().split('T')[0], // 1 day ago
            procedures_completed: data.actual_data.procedures || [],
            medications: data.actual_data.medications || []
          },
          protocol_requirements: {
            visit_window_days: data.protocol_data.visit_window_days || 3,
            required_procedures: data.protocol_data.required_procedures || [],
            prohibited_medications: data.protocol_data.prohibited_medications || []
          }
        })
      });
    } catch (error) {
      console.warn('Protocol deviation detection failed:', error);
      throw error;
    }
  }

  async getProtocolMonitoring(): Promise<any> {
    try {
      return await this.fetchApi('/test-data/protocol/monitoring');
    } catch (error) {
      console.warn('Failed to fetch protocol monitoring');
      throw error;
    }
  }
}