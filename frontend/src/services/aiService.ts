import { BaseApiService } from './baseApiService';
import { AIResponse } from './types';

export class AIService extends BaseApiService {
  // AI Agent interactions
  async sendChatMessage(message: string): Promise<AIResponse> {
    try {
      console.log('🔍 Sending chat message with correct API format...');
      
      const requestBody = {
        workflow_type: 'comprehensive_analysis',
        subject_id: 'CARD001',
        input_data: {
          request: `Get test data for subject CARD001 and analyze: ${message}`
        }
      };
      
      console.log('📤 Request body:', requestBody);
      
      const response = await fetch(`https://pm-clinical-trials-agent-production.up.railway.app/api/v1/clinical/execute-workflow`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      console.log('📡 Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('📡 Error response:', errorText);
        throw new Error(`Chat API failed: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log('✅ Chat response:', data);
      
      // Transform response to match our interface
      return {
        success: true,
        response: data.results ? JSON.stringify(data.results, null, 2) : data.message || 'Analysis completed',
        agent_id: data.workflow_type || 'comprehensive-analysis',
        execution_time: data.execution_time || 0,
        metadata: {
          clinical_analysis: true,
          tools_used: true,
          workflow_executed: true
        }
      };
    } catch (error) {
      console.warn('Using mock AI response');
      return {
        success: true,
        response: `🤖 **Mock Clinical Analysis** (Backend unavailable)\n\nI understand you're asking: "${message}"\n\nThis would normally connect to our production Clinical Trials AI system to provide real clinical analysis. When the backend is available, I can:\n\n• Analyze real clinical data from 50 cardiology subjects\n• Provide medical interpretations of BP, BNP, creatinine values\n• Generate clinical recommendations and safety alerts\n• Execute multi-agent workflows for complex queries\n\nThe system is designed to showcase genuine clinical intelligence with proper medical expertise.`,
        agent_id: 'mock-portfolio-manager',
        execution_time: 1.5,
        metadata: {
          clinical_analysis: true,
          tools_used: false,
          workflow_executed: false
        }
      };
    }
  }

  async executeWorkflow(workflowType: string, inputData: any): Promise<any> {
    try {
      return await this.fetchApi('/clinical/execute-workflow', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow_type: workflowType,
          subject_id: inputData.subject_id || 'CARD001',
          input_data: inputData
        })
      });
    } catch (error) {
      console.warn('Workflow execution failed:', error);
      throw error;
    }
  }

  async getAgentStatus(): Promise<any> {
    try {
      return await this.fetchApi('/clinical/health');
    } catch (error) {
      console.warn('Using mock agent status');
      return { status: 'mock', agents: ['portfolio-manager'] };
    }
  }
}