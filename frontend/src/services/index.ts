import { StudyService } from './studyService';
import { QueryService } from './queryService';
import { SDVService } from './sdvService';
import { ComplianceService } from './complianceService';
import { AnalyticsService } from './analyticsService';
import { DemoDataService } from './demoDataService';

import { AIService } from './aiService';

// Combined API Service that includes all domain services
class ApiService extends StudyService {
  private queryService = new QueryService();
  private sdvService = new SDVService();
  private complianceService = new ComplianceService();
  private analyticsService = new AnalyticsService();
  private aiService = new AIService();
  private demoService = new DemoDataService();

  // Query Management methods
  getQueries = this.queryService.getQueries.bind(this.queryService);
  getQueryStats = this.queryService.getQueryStats.bind(this.queryService);
  analyzeQuery = this.queryService.analyzeQuery.bind(this.queryService);

  // SDV methods
  getSDVSessions = this.sdvService.getSDVSessions.bind(this.sdvService);
  getSDVStats = this.sdvService.getSDVStats.bind(this.sdvService);
  verifySourceData = this.sdvService.verifySourceData.bind(this.sdvService);

  // Compliance methods
  getProtocolDeviations = this.complianceService.getProtocolDeviations.bind(this.complianceService);
  getDeviationStats = this.complianceService.getDeviationStats.bind(this.complianceService);
  detectProtocolDeviations = this.complianceService.detectProtocolDeviations.bind(this.complianceService);
  getProtocolMonitoring = this.complianceService.getProtocolMonitoring.bind(this.complianceService);

  // Analytics methods
  // getDashboardAnalytics = this.analyticsService.getDashboardAnalytics.bind(this.analyticsService);

  // AI methods
  sendChatMessage = this.aiService.sendChatMessage.bind(this.aiService);
  getAgentStatus = this.aiService.getAgentStatus.bind(this.aiService);
  executeWorkflow = this.aiService.executeWorkflow.bind(this.aiService);

  // Demo methods with limited data
  getDemoQueries = this.demoService.getDemoQueries.bind(this.demoService);
  getDemoSDVSessions = this.demoService.getDemoSDVSessions.bind(this.demoService);
  getDemoProtocolDeviations = this.demoService.getDemoProtocolDeviations.bind(this.demoService);
  getDemoSubjects = this.demoService.getDemoSubjects.bind(this.demoService);
  analyzeQueryDemo = this.demoService.analyzeQueryDemo.bind(this.demoService);
}

export const apiService = new ApiService();

// Export types for use in components
export * from './types';