import type { IconType } from 'react-icons';
import {
  TbCalendarEvent,
  TbCube,
  TbLifebuoy,
  TbStarFilled,
  TbTools,
  TbUser,
  TbUsersGroup,
} from 'react-icons/tb';
import type { accentColors } from '@radix-ui/themes/props';

export const ROUTEPREFIX: string = '/hello';
export const APIPREFIX: string = '/ng';

// Semantic icons used throughout the UI, defined here for consistency
export const EventIcon = TbCalendarEvent;
export const UserIcon = TbUser;
export const TeamIcon = TbUsersGroup;
export const ChallengeIcon = TbCube;

// Colors/icons used for displaying User and TeamMember roles.
// Will fall back to generic gray badges if a role is not specified here.
export const ROLES: Record<string, { color: (typeof accentColors)[number]; icon: IconType }> = {
  admin : {
    color : 'red',
    icon : TbTools,
  },
  support : {
    color : 'jade',
    icon : TbLifebuoy,
  },
  captain : {
    color : 'amber',
    icon : TbStarFilled,
  },
  member : {
    color : 'gray',
    icon : UserIcon,
  },
};

export const DATEFORMAT = {
  range : {
    year : 'numeric',
    month : 'long',
    day : 'numeric',
  },
};
