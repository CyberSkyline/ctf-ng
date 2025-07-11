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
