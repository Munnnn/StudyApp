/**
 * Global Zustand store.
 * - deviceId: persisted once per install
 * - user: server-returned profile
 * - settings: local notification config
 * - currentAttempt: ephemeral, cleared after explanation screen
 */
import { create } from 'zustand';

export interface UserProfile {
  id: string;
  device_id: string;
  display_name: string | null;
  notification_interval_min: number;
  quiet_hours_start: string | null;
  quiet_hours_end: string | null;
  paused: boolean;
}

export interface CurrentAttempt {
  attempt_id: string;
  generated_question_id: string;
  attending_question: string;
  mcq_options: string[];
  typed_answer: string;
}

interface AppState {
  deviceId: string | null;
  user: UserProfile | null;
  currentAttempt: CurrentAttempt | null;
  setDeviceId: (id: string) => void;
  setUser: (user: UserProfile) => void;
  setCurrentAttempt: (a: CurrentAttempt | null) => void;
  clearAttempt: () => void;
}

export const useStore = create<AppState>((set) => ({
  deviceId: null,
  user: null,
  currentAttempt: null,
  setDeviceId: (id) => set({ deviceId: id }),
  setUser: (user) => set({ user }),
  setCurrentAttempt: (currentAttempt) => set({ currentAttempt }),
  clearAttempt: () => set({ currentAttempt: null }),
}));
