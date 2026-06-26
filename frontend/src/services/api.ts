import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

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
