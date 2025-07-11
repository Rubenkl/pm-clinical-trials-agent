// Force production URL for the Clinical Trials AI backend
const API_BASE_URL = 'https://pm-clinical-trials-agent-production.up.railway.app/api/v1';

export class BaseApiService {
  protected async fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const fullUrl = `${API_BASE_URL}${endpoint}`;
    
    try {
      console.log(`🚀 API Request Details:`);
      console.log(`- URL: ${fullUrl}`);
      console.log(`- Method: ${options?.method || 'GET'}`);
      console.log(`- Origin: ${window.location.origin}`);
      console.log(`- Headers:`, options?.headers);
      
      const requestOptions: RequestInit = {
        ...options,
        headers: {
          ...options?.headers,
        }
      };

      const response = await fetch(fullUrl, requestOptions);

      console.log(`✅ Response Status: ${response.status}`);
      console.log(`✅ Response OK: ${response.ok}`);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`❌ Response Error Body:`, errorText);
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
      }

      const data = await response.json();
      console.log(`✅ Response Data:`, data);
      return data;
    } catch (error) {
      console.error(`❌ Fetch Error for ${endpoint}:`, error);
      console.error(`❌ Full URL attempted: ${fullUrl}`);
      
      // Check if it's a network error
      if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
        console.error(`🌐 Network Error - Backend might be down or unreachable`);
        console.error(`🔍 Check: Is ${API_BASE_URL} responding?`);
      }
      
      throw error;
    }
  }

  // Health check
  async checkHealth(): Promise<any> {
    try {
      return await this.fetchApi('/health');
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }
}