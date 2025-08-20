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
  event_id: number;
  name: string;
  description: string;
  icon: string;
  summary: string;
  total_questions: number;
  total_points: number;
}

export interface MeChallenge {
  challenge_id: number;
  challenge_name: string;
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
  user_id: number;
  team_id: number;
  event_id: number;
  challenge_id: number;
  question_id: number;
  score_event_id?: number;
  timestamp: Date;
  points: number;
  submission: string;
  is_correct: boolean;
}

export interface Score {
   id: number;
   team_id: number;
   event_id: number;
   points: number;
   last_update: Date;
   team_name: string | null;
}

export interface ScoreEvent {
  id: number;
  score_id: number;
  team_id: number;
  points: number;
  timestamp: Date;
}

export interface Deployment {
  id: number;
  blueprint: number;
  team: number;
  challenge_name: string;
  team_name: string;
  challenge_id: number;
  containers: number;
  event_id: number;
}

export interface ContainerInstance {
  id: number;
  blueprint: number;
  team: number;
  hostip: string;
  dockerid: string;
}

export interface ContainerStatus {
  id: number;
  name: string;
  image: string;
  docker_id: string;
  status: 'created' | 'running' | 'paused' | 'restarting' | 'exited' | 'removing' | 'dead';
}

export interface Ticket {
  id: number;
  subject: string;
  event_id?: number;
  event_name?: string;
  team_id?: number;
  team_name?: string;
  challenge_id?: number;
  challenge_name?: string;
  status: 'open' | 'closed' | 'inprogress';
  last_updated: Date;
  opened_timestamp: Date;
  author_id: number;
  message_count: number;
  tags: string[]
}

export interface TicketMessage {
  author_id: number;
  author_name: string;
  author_type: string;
  created_at: Date;
  id: number;
  text: string;
  ticket_id: number
}
