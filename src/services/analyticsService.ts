import { BaseApiService } from './baseApiService';

export class AnalyticsService extends BaseApiService {
  // Analytics Dashboard - AI Powered
  async getDashboardAnalytics(): Promise<any> {
    try {
      return await this.fetchApi('/test-data/analytics/dashboard');
    } catch (error) {
      console.warn('Failed to fetch dashboard analytics');
      throw error;
    }
  }
}