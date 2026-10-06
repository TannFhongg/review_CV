import { create } from 'zustand';
import type { AnalysisResult, CVSuggestion } from '@/lib/types';

type AnalysisStatus = 'idle' | 'uploading' | 'extracting' | 'parsing_jd' | 'parsing_cv' | 'matching' | 'generating' | 'done' | 'error';

interface AnalysisState {
  // Input
  jdFile: File | null;
  cvFile: File | null;
  jdText: string;
  cvText: string;

  // Status
  status: AnalysisStatus;
  errorMessage: string | null;

  // Result
  result: AnalysisResult | null;

  // Suggestions state
  currentSuggestionIndex: number;

  // Actions
  setJdFile: (file: File | null) => void;
  setCvFile: (file: File | null) => void;
  setJdText: (text: string) => void;
  setCvText: (text: string) => void;
  setStatus: (status: AnalysisStatus) => void;
  setError: (message: string) => void;
  setResult: (result: AnalysisResult) => void;
  acceptSuggestion: (index: number) => void;
  rejectSuggestion: (index: number) => void;
  setCurrentSuggestionIndex: (index: number) => void;
  reset: () => void;
}

const initialState = {
  jdFile: null,
  cvFile: null,
  jdText: '',
  cvText: '',
  status: 'idle' as AnalysisStatus,
  errorMessage: null,
  result: null,
  currentSuggestionIndex: 0,
};

export const useAnalysisStore = create<AnalysisState>((set) => ({
  ...initialState,

  setJdFile: (file) => set({ jdFile: file }),
  setCvFile: (file) => set({ cvFile: file }),
  setJdText: (text) => set({ jdText: text }),
  setCvText: (text) => set({ cvText: text }),
  setStatus: (status) => set({ status, errorMessage: null }),
  setError: (message) => set({ status: 'error', errorMessage: message }),
  setResult: (result) => set({ result, status: 'done' }),

  acceptSuggestion: (index) =>
    set((state) => {
      if (!state.result) return state;
      const suggestions = [...state.result.suggestions];
      suggestions[index] = { ...suggestions[index], accepted: true };
      return { result: { ...state.result, suggestions } };
    }),

  rejectSuggestion: (index) =>
    set((state) => {
      if (!state.result) return state;
      const suggestions = [...state.result.suggestions];
      suggestions[index] = { ...suggestions[index], accepted: false };
      return { result: { ...state.result, suggestions } };
    }),

  setCurrentSuggestionIndex: (index) => set({ currentSuggestionIndex: index }),

  reset: () => set(initialState),
}));
