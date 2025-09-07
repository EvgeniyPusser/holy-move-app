import { create } from 'zustand';

interface MovingState {
  fromZip: string;
  toZip: string;
  rooms: number;
  moveDate: string;
  results: { price: number; truckType: string; helpersCount: number } | null;
  setForm: (data: Partial<MovingState>) => void;
  setResults: (results: MovingState['results']) => void;
  reset: () => void;
}

export const useMovingStore = create<MovingState>((set) => ({
  fromZip: '',
  toZip: '',
  rooms: 1,
  moveDate: '',
  results: null,
  setForm: (data) => set((state) => ({ ...state, ...data })),
  setResults: (results) => set({ results }),
  reset: () => set({ fromZip: '', toZip: '', rooms: 1, moveDate: '', results: null }),
}));
