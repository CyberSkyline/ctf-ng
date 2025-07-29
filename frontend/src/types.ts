export interface Event {
  id: number;
  name: string;
  description?: string | null;
  max_team_size: number;
  start_time?: Date;
  end_time?: Date;
  locked: boolean;
  public: boolean;
  registration_open: boolean;
  registration_start_date?: Date;
  registration_end_date?: Date;
}

export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  registered_at: Date;
}

export interface Team {
  id: number;
  name: string;
  event_id: number;
  member_count: number;
  ranked: boolean;
  locked: boolean;
  invite_code?: string;
}

export interface TeamMember {
  id: number;
  user_id: number;
  user_name: string;
  team_id: number;
  event_id: number;
  joined_at: Date;
  role: 'member' | 'captain';
}

export interface Challenge {
  id: number;
  name: string;
  description: string;
  icon: string;
  summary: string;
  total_questions: number;
  total_points: number;
}

export interface MeChallenge {
  challenge_id: number;
  total_points_available: number;
  total_points_scored: number;
  num_questions_solved: number;
  num_questions_available: number;
  num_attempts_made: number;
}

export interface Question {
  id: number;
  name: string;
  body: string;
  placeholder: string;
  points: number;
  max_attempts: number;
  challenge_id: number;
}

export interface Hint {
  id: number;
  challenge_id: number;
  preview: string;
  body: string | null; // Null if hint has not been redeemed, string if it has.
  deduction: number;
}

export interface Attempt {
  id: number;
  question_id: number;
  event_id: number;
  submission: string;
  correct: boolean;
  created_at: Date;
  team_id: number;
  user_id: number;
}
