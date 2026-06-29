import axios from 'axios';

// Use same-origin /api (proxied by Next.js) — avoids Windows localhost/IPv6 issues
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

export function getApiErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    if (err.code === 'ECONNABORTED') {
      return 'API request timed out. The backend may still be loading data — wait a moment and refresh.';
    }
    if (!err.response) {
      return (
        'Cannot reach the backend API. Start it in a terminal: ' +
        'cd backend → venv\\Scripts\\activate → python main.py ' +
        '(then restart the frontend with npm run dev)'
      );
    }
    const detail = err.response.data?.detail;
    return `API error ${err.response.status}${detail ? `: ${detail}` : ''}`;
  }
  if (err instanceof Error) {
    return err.message;
  }
  return 'Unknown API error';
}

export interface StudentProfile {
  rank: number;
  category: string;
  preferred_locations?: string[];
  preferred_streams?: string[];
}

export interface ChoiceNode {
  priority_number: number;
  college_code: string;
  course_code: string;
  college_name: string;
  course_name: string;
  location: string;
  chancing: { round_1: string; round_2: string; round_3: string };
}

export interface PredictionResponse {
  status: string;
  student_rank: number;
  category: string;
  total_matches: number;
  total_choices: number;
  dream_count: number;
  target_count: number;
  safety_count: number;
  choices: ChoiceNode[];
}

export const kcetAPI = {
  // Fetch all categories
  getCategories: async () => {
    const response = await apiClient.get('/categories');
    return response.data;
  },

  // Fetch all colleges
  getColleges: async () => {
    const response = await apiClient.get('/colleges');
    return response.data;
  },

  // Fetch all courses
  getCourses: async () => {
    const response = await apiClient.get('/courses');
    return response.data;
  },

  // Fetch all locations
  getLocations: async () => {
    const response = await apiClient.get('/locations');
    return response.data;
  },

  // Generate prediction and optimized choice list
  predictColleges: async (profile: StudentProfile): Promise<PredictionResponse> => {
    const response = await apiClient.post('/predict', profile);
    return response.data;
  },

  // Evaluate chancing for a specific entry
  evaluateChance: async (rank: number, cutoffRank: number, roundNo: number = 2) => {
    const response = await apiClient.post('/evaluate-chance', null, {
      params: {
        rank,
        cutoff_rank: cutoffRank,
        round_no: roundNo,
      },
    });
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};

export default kcetAPI;
