import type { accentColors } from '@radix-ui/themes/props';
import type { IconType } from 'react-icons';
import {
  TbCalendarEvent,
  TbCube,
  TbGhost,
  TbLifebuoy,
  TbPackages,
  TbSpeakerphone,
  TbStarFilled,
  TbTools,
  TbUser,
  TbUsersGroup,
} from 'react-icons/tb';

export type AccentColor = (typeof accentColors)[number];

export const ROUTEPREFIX: string = BASE_PATH;
export const APIPREFIX: string = `${ROUTEPREFIX}/ng`;
export const SSO_LOGIN_PATH: string = `/ng/authenticate/okta/login`;
export const SSO_REGISTRATION_PATH: string = `/ng/authenticate/okta/register`;

// Semantic icons used throughout the UI, defined here for consistency
export const EventIcon = TbCalendarEvent;
export const UserIcon = TbUser;
export const TeamIcon = TbUsersGroup;
export const ChallengeIcon = TbCube;
export const DeploymentIcon = TbPackages;
export const AnnouncementIcon = TbSpeakerphone;
export const ImpersonateIcon = TbGhost;

// Semantic colors for UI.
// Use instead of default accent for things that carry semantic meaning.

/** Use for controls that confirm a positive action - creating/adding, registration, applying changes to settings, etc. */
export const COLOR_POSITIVE: AccentColor = 'lime';
/** Use for controls that signal warning/privilege or have notable (but not destructive) effects - changes in privilege, scores, availability, etc. */
export const COLOR_WARNING: AccentColor = 'orange';
/** Use for actions that have destructive effects - deletion, leaving teams, etc. */
export const COLOR_NEGATIVE: AccentColor = 'red';
/** Use for informational messages or controls that provide additional context without changing state. */
export const COLOR_INFO: AccentColor = 'teal';

/**
 * Accent color used for question input fields. Should usually match the global accent,
 * but may need to change for disambiguation if the global accent is green/red.
 */
export const COLOR_QUESTION: AccentColor = 'teal';

/** Use for controls related to hints, remote access, god mode, etc. */
export const COLOR_HINT: AccentColor = 'violet';

// Colors/icons used for displaying User and TeamMember roles.
// Will fall back to generic gray badges if a role is not specified here.
export const ROLES: Record<string, { color: AccentColor; icon: IconType }> = {
  admin : {
    color : COLOR_NEGATIVE,
    icon : TbTools,
  },
  support : {
    color : COLOR_HINT,
    icon : TbLifebuoy,
  },
  captain : {
    color : COLOR_WARNING,
    icon : TbStarFilled,
  },
  member : {
    color : 'gray',
    icon : UserIcon,
  },
};

/* Find these const defined in NotificationType.py */
export const NOTIF_TYPE = {
  TICKETS : [
    'ticket_create',
    'ticket_message',
    'ticket_status_change',
    'ticket_assigned',
  ],
};

export const OTHER_TAXONOMY = 'Tags';

export const PC_YEAR = '8'; // PC8
