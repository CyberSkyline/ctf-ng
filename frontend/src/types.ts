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
  roles: string[];
  registered_at: Date;
}

export interface Team {
  id: number;
  name: string;
  event_id: number;
  event_name?: string;
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
  user_name?: string;
  team_name?: string;
  challenge_name?: string;
  question_name?: string;
}

export interface HintRedemption {
  id: number;
  user_id: number;
  team_id: number;
  score_event_id?: number;
  timestamp: Date;
  points: number;
  user_name?: string;
  team_name?: string;
  hint_preview?: string;
  challenge_id: number;
  challenge_name?: string;
  event_id?: number;
  event_name?: string;
}

export interface ManualPointAward {
  id: number;
  admin_id: number;
  team_id: number;
  score_event_id: number;
  timestamp: Date;
  points: number;
  reason: string;
  admin_name?: string;
  team_name?: string;
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
  team_name: string;
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
  event_name?: string;
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
  author_id: number;
  author_name: string;
  status: string;
  opened_timestamp: Date;
  last_updated: Date;
  event_id?: number;
  event_name?: string;
  team_id?: number;
  team_name?: string;
  challenge_id?: number;
  challenge_name?: string;
  message_count: number;
}

export interface TicketTag {
  id: number;
  name: string;
  color?: string;
  description?: string;
  ticket_count: number;
}

export interface AdminTicket extends Ticket {
  assigned_to?: number;
  assigned_to_name?: string;
  muted: boolean;
  closed_timestamp?: Date;
  tags: TicketTag[];
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
