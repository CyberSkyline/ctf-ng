export type Event = {
  id: number;
  name: string;
  description?: string | null;
  max_team_size: number;
  start_time?: string;
  end_time?: string;
  locked: boolean;
};
