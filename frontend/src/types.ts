export type Event = {
  id: number;
  name: string;
  description?: string | null;
  max_team_size: number;
  start_time?: string;
  end_time?: string;
  locked: boolean;
  team_count: number;
  total_members: number;
};

export type User = {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'user';
  registered_at: string;
  team_count: number;
}

export type Team = {
  id: number;
  name: string;
  event_id: number;
  event_name: string;
  member_count: number;
  max_team_size: number;
  is_full: boolean;
  invite_code: string;
  ranked: boolean;
}

export type TeamMember = {
  user_id: number;
  joined_at: string;
  role: 'member' | 'captain';
}
