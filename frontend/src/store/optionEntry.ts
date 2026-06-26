import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ChoiceNode {
  priorityNumber: number;
  collegeCode: string;
  courseCode: string;
  collegeName: string;
  courseName: string;
  location: string;
  chancing: { round_1: string; round_2: string; round_3: string };
}

interface StudentProfile {
  rank: number;
  category: string;
  preferredLocations?: string[];
  preferredStreams?: string[];
}

interface OptionEntryState {
  // Profile state
  studentProfile: StudentProfile | null;
  setStudentProfile: (profile: StudentProfile) => void;
  
  // Choices state
  choices: ChoiceNode[];
  addChoice: (node: Omit<ChoiceNode, 'priorityNumber'>) => void;
  removeChoice: (collegeCode: string, courseCode: string) => void;
  reorderChoices: (startIndex: number, endIndex: number) => void;
  clearList: () => void;
  setChoices: (choices: ChoiceNode[]) => void;
  
  // Metadata
  totalMatches: number;
  setTotalMatches: (count: number) => void;
  dreamCount: number;
  setDreamCount: (count: number) => void;
  targetCount: number;
  setTargetCount: (count: number) => void;
  safetyCount: number;
  setSafetyCount: (count: number) => void;
}

export const useOptionEntryStore = create<OptionEntryState>()(
  persist(
    (set) => ({
      // Profile state
      studentProfile: null,
      setStudentProfile: (profile) => set({ studentProfile: profile }),
      
      // Choices state
      choices: [],
      
      addChoice: (node) => set((state) => {
        // Block duplicate entries
        if (state.choices.some(c => c.collegeCode === node.collegeCode && c.courseCode === node.courseCode)) {
          return state;
        }
        const updated = [...state.choices, { ...node, priorityNumber: state.choices.length + 1 }];
        return { choices: updated };
      }),
      
      removeChoice: (collegeCode, courseCode) => set((state) => {
        const filtered = state.choices.filter(c => !(c.collegeCode === collegeCode && c.courseCode === courseCode));
        const reindexed = filtered.map((c, index) => ({ ...c, priorityNumber: index + 1 }));
        return { choices: reindexed };
      }),
      
      reorderChoices: (startIndex, endIndex) => set((state) => {
        const result = Array.from(state.choices);
        const [removed] = result.splice(startIndex, 1);
        result.splice(endIndex, 0, removed);
        const reindexed = result.map((c, index) => ({ ...c, priorityNumber: index + 1 }));
        return { choices: reindexed };
      }),
      
      clearList: () => set({ choices: [] }),
      
      setChoices: (choices) => set({ choices }),
      
      // Metadata
      totalMatches: 0,
      setTotalMatches: (count) => set({ totalMatches: count }),
      
      dreamCount: 0,
      setDreamCount: (count) => set({ dreamCount: count }),
      
      targetCount: 0,
      setTargetCount: (count) => set({ targetCount: count }),
      
      safetyCount: 0,
      setSafetyCount: (count) => set({ safetyCount: count }),
    }),
    {
      name: 'kcet-2026-choice-workspace',
    }
  )
);
