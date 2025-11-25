export interface Event {
  id: number;
  name: string;
  description?: string | null;
  image?: string | null;
  max_team_size: number;
  start_time?: Date;
  end_time?: Date;
  locked: boolean;
  public: boolean;
  registration_open: boolean;
  registration_start_date?: Date;
  registration_end_date?: Date;
  hints_enabled: boolean;
  time_limit_minutes: number | null;
}

export interface Sponsor {
  id: number;
  name: string;
  logo?: string;
}

export interface UploadedFile {
  filename: string,
  folder: string,
  last_modified?: Date,
  url?: string,
}

export interface User {
  id: number;
  name: string;
  email: string;
  roles: string[];
  registered_at: Date;
  affiliation: Sponsor | null;
}

export interface Team {
  id: number;
  name: string;
  event_id: number;
  event_name?: string;
  member_count: number;
  ranked: boolean;
  invite_code?: string;
  start_timestamp: Date | null;
  end_time: Date | null;
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
  num_questions: number;
  total_points: number;
  event_name?: string;
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

export interface AdminQuestion extends Question {
  answer: string;
}

export interface Hint {
  id: number;
  challenge_id: number;
  name: string;
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
  team_id: number;
  challenge_name: string;
  team_name: string;
  challenge_id: number;
  containers: number;
  event_id: number;
  event_name?: string;
}

export interface ContainerBlueprint {
  id: number;
  name: string;
  image: string;
  hostname: string;
  stdin_open: boolean;
  tty: boolean;
  command: string[];
  entrypoint: string[];
  environment: Record<string, string>;
  networks: string[];
  cap_add: string[];
  mem_limit: string;
  memswap_limit: string;
  cpus: number;
  user: string;
  challenge_id: number;
}

export interface ContainerInstance {
  id: number;
  blueprint: number;
  team_id: number;
  hostip: string;
  dockerid: string;
}

export interface ContainerStatus {
  id: number;
  name: string;
  image: string;
  docker_id: string;
  status: 'created' | 'running' | 'paused' | 'restarting' | 'exited' | 'removing' | 'dead';
  env: string[];
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

export interface Notification {
  id: number;
  type: string;
  title: string;
  message: string;
  recipient_id: number;
  created_at: Date;
  sender_id?: number;
  read_at?: Date;
  expires_at?: Date;
  ticket_id?: number;
  team_id?: number;
  event_id?: number;
  challenge_id?: number;
  recipient_name?: string;
  sender_name?: string;
  ticket_subject?: string;
  team_name?: string;
  event_name?: string;
}

export interface Announcement {
  id: number;
  title: string;
  message: string;
  created_at: Date;
  expires_at: Date;
  sender_id: number;
  sender_name: string;
  type: string;
}

export interface Workspace {
  id : number;
  hostip : string;
  dockerid : string;
  user : number;
}

export interface ChallengeVariable {
  id: number;
  name: string;
  default: string;
  template: string;
}
