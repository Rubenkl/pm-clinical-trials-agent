import { BaseApiService } from './baseApiService';

export class SDVService extends BaseApiService {
  // Source Data Verification - AI Powered
  async getSDVSessions(): Promise<any> {
    try {
      return await this.fetchApi('/test-data/sdv/sessions');
    } catch (error) {
      console.warn('Failed to fetch SDV sessions');
      throw error;
    }
  }

  async getSDVStats(): Promise<any> {
    try {
      return await this.fetchApi('/dashboard/metrics/sdv');
    } catch (error) {
      console.warn('Failed to fetch SDV stats, using test data');
      return await this.fetchApi('/test-data/sdv/sessions');
    }
  }

  async verifySourceData(data: {
    subject_id: string;
    site_id: string;
    visit: string;
    edc_data: any;
    source_data: any;
    monitor_id: string;
  }): Promise<any> {
    try {
      return await this.fetchApi('/clinical/verify-data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject_id: data.subject_id,
          visit: data.visit,
          edc_data: data.edc_data,
          source_data: data.source_data
        })
      });
    } catch (error) {
      console.warn('SDV verification failed:', error);
      throw error;
    }
  }
}