import { API_CONFIG } from '../config/api';

// API utility functions
const API_BASE_URL = API_CONFIG.baseUrl;

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export async function apiCall<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  // Debug logging
  console.log(`API Call: ${options.method || 'GET'} ${url}`);
  
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.timeout);
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      signal: controller.signal,
      ...options,
    });
    
    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || errorMessage;
      } catch {
        // If response is not JSON, use the status text
      }
      
      throw new ApiError(response.status, errorMessage);
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    } else {
      throw new Error('Expected JSON response but received: ' + contentType);
    }
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    
    // Handle abort errors
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error(`Request timeout: ${endpoint}`);
    }
    
    // Network or other errors
    console.error('API call failed:', error);
    console.error('URL:', url);
    console.error('Options:', options);
    
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error(`Network error: Unable to connect to API at ${url}. Please check if the backend is running.`);
    }
    
    throw new Error(`Failed to fetch from ${endpoint}: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

// Health check function
export const checkApiHealth = async (): Promise<boolean> => {
  try {
    await apiCall<any>('/health');
    return true;
  } catch (error) {
    console.error('API health check failed:', error);
    return false;
  }
};

// Specific API functions
export const api = {
  getRepositories: () => apiCall<any[]>('/api/repos'),
  getRepository: (id: number) => apiCall<any>(`/api/repos/${id}`),
  getRepositoryBranches: (id: number, limit = 50) => apiCall<any[]>(`/api/repos/${id}/branches?limit=${limit}`),
  getRepositoryPulls: (id: number, state = 'open', limit = 50) => apiCall<any[]>(`/api/repos/${id}/pulls?state=${state}&limit=${limit}`),
  getRepositoryIssues: (id: number, state = 'open', limit = 50) => apiCall<any[]>(`/api/repos/${id}/issues?state=${state}&limit=${limit}`),
  getRepositoryCIRuns: (id: number, limit = 50) => apiCall<any[]>(`/api/repos/${id}/ci-runs?limit=${limit}`),
  getEvents: (params: { repo?: string; event_type?: string; limit?: number } = {}) => {
    const searchParams = new URLSearchParams();
    if (params.repo) searchParams.set('repo', params.repo);
    if (params.event_type) searchParams.set('event_type', params.event_type);
    if (params.limit) searchParams.set('limit', params.limit.toString());
    
    const query = searchParams.toString();
    return apiCall<any[]>(`/api/events${query ? '?' + query : ''}`);
  },
  getStats: () => apiCall<any>('/api/stats'),
  syncGitHub: () => apiCall<any>('/api/sync/github', { method: 'POST' }),
  sendDiscordNotification: (message: string, webhookUrl?: string) => 
    apiCall<any>('/api/discord/notify', {
      method: 'POST',
      body: JSON.stringify({ message, webhook_url: webhookUrl }),
    }),
};