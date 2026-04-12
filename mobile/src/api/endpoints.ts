/**
 * Typed endpoint wrappers — one function per API route.
 */
import { api } from './client';

// ── Users ────────────────────────────────────────────────────────────────────

export interface UserProfile {
  id: string;
  device_id: string;
  display_name: string | null;
  notification_interval_min: number;
  quiet_hours_start: string | null;
  quiet_hours_end: string | null;
  paused: boolean;
}

export const ensureUser = () => api.post<UserProfile>('/api/v1/users/ensure');
export const updateUser = (body: Partial<UserProfile>) =>
  api.patch<UserProfile>('/api/v1/users/me', body);

// ── Decks ────────────────────────────────────────────────────────────────────

export interface Deck {
  id: string;
  owner_id: string;
  title: string;
  description: string | null;
  source_type: 'manual' | 'csv' | 'anki_import';
  created_at: string;
  card_count: number;
}

export const listDecks = () => api.get<Deck[]>('/api/v1/decks');
export const createDeck = (body: { title: string; description?: string }) =>
  api.post<Deck>('/api/v1/decks', body);
export const getDeck = (id: string) => api.get<Deck>(`/api/v1/decks/${id}`);
export const updateDeck = (id: string, body: { title?: string; description?: string }) =>
  api.patch<Deck>(`/api/v1/decks/${id}`, body);
export const deleteDeck = (id: string) => api.delete(`/api/v1/decks/${id}`);

// ── Cards ────────────────────────────────────────────────────────────────────

export interface Card {
  id: string;
  deck_id: string;
  front: string;
  back: string;
  system_tag: string | null;
  topic_tag: string | null;
  difficulty: number;
  created_at: string;
}

export const listCards = (deckId: string) =>
  api.get<Card[]>(`/api/v1/decks/${deckId}/cards`);
export const addCard = (deckId: string, body: Omit<Card, 'id' | 'deck_id' | 'created_at'>) =>
  api.post<Card>(`/api/v1/decks/${deckId}/cards`, body);
export const updateCard = (id: string, body: Partial<Card>) =>
  api.patch<Card>(`/api/v1/cards/${id}`, body);
export const deleteCard = (id: string) => api.delete(`/api/v1/cards/${id}`);

// ── Study ────────────────────────────────────────────────────────────────────

export interface NextQuestion {
  generated_question_id: string;
  card_id: string;
  attending_question: string;
  system_tag: string | null;
  topic_tag: string | null;
  high_yield_takeaway: string;
}

export interface TypedAnswerResponse {
  attempt_id: string;
  mcq_options: string[];
}

export interface ExplanationResponse {
  attempt_id: string;
  attending_question: string;
  typed_answer_raw: string;
  typed_answer_score: number;
  mcq_selected_index: number;
  mcq_correct: boolean;
  correct_answer: string;
  step_by_step_explanation: string;
  wrong_answer_analysis: string[];
  high_yield_takeaway: string;
  follow_up_questions: string[];
  mastery_level: 'weak' | 'fragile' | 'developing' | 'strong';
  recall_gap: 'both' | 'recognition_only' | 'recall_only' | 'neither';
  system_tag: string | null;
  topic_tag: string | null;
}

export const getNextQuestion = (force = false) =>
  api.get<NextQuestion>(`/api/v1/study/next${force ? '?force=true' : ''}`);
export const submitTypedAnswer = (body: {
  generated_question_id: string;
  typed_answer: string;
  response_time_ms?: number;
}) => api.post<TypedAnswerResponse>('/api/v1/study/attempts/typed', body);
export const submitMCQ = (body: {
  attempt_id: string;
  mcq_selected_index: number;
  response_time_ms?: number;
}) => api.post<ExplanationResponse>('/api/v1/study/attempts/mcq', body);

// ── Dashboard ────────────────────────────────────────────────────────────────

export interface Dashboard {
  total_attempts: number;
  mastery_distribution: {
    weak: number;
    fragile: number;
    developing: number;
    strong: number;
  };
  weakest_systems: { system_tag: string; total_attempts: number; avg_typed_score: number; recall_gap_count: number }[];
  weakest_topics: string[];
  recognition_only_count: number;
  strong_mastery_count: number;
  cards_studied: number;
  cards_total: number;
}

export const getDashboard = () => api.get<Dashboard>('/api/v1/dashboard');
