import type { AccentColor } from '@/constants';
import {
  COLOR_NEGATIVE,
  COLOR_WARNING,
  SSO_CARD_REGISTRATION_PATH,
  SSO_LOGIN_PATH,
} from '@/constants';
import { useAuth } from '@/hooks/users';
import { Button, Link as RadixLink } from '@radix-ui/themes';
import type { ReactNode } from 'react';
import type { IconType } from 'react-icons';
import {
  TbIdBadge2,
  TbLifebuoy,
  TbLockExclamation,
  TbPlugConnectedX,
  TbServerBolt,
} from 'react-icons/tb';
import { Link } from 'react-router';
import ErrorDisplay from './ErrorDisplay';

const SUPPORT_EMAIL = 'presidentscup@cisa.dhs.gov';
const TOC_EMAIL = 'TOC@mail.cisa.dhs.gov';
const TOC_PHONE = '202-771-CISA(2472)';

/** How to reach a human. The only route open to someone without an account. */
function TocContact() {
  return (
    <>
      {`please email the CISA Technical Operations Center at `}
      <RadixLink asChild>
        <Link to={`mailto:${TOC_EMAIL}`}>{TOC_EMAIL}</Link>
      </RadixLink>
      {` or call `}
      <b>{TOC_PHONE}</b>
    </>
  );
}

/** Retry sign-in, then fall back to the login page. */
function SsoActions() {
  return (
    <>
      <Button asChild size="3">
        <Link to={SSO_LOGIN_PATH} reloadDocument>Try signing in again</Link>
      </Button>
      <Button asChild size="3" variant="soft" color="gray">
        <Link to="/login">Back to login</Link>
      </Button>
    </>
  );
}

function SupportActions() {
  const { isAuthenticated } = useAuth();

  return (
    <>
      <Button asChild size="3">
        <Link to="/">Go to dashboard</Link>
      </Button>
      <Button asChild size="3" variant="soft" color="gray">
        {isAuthenticated
          ? <Link to="/support/createTicket">Contact support</Link>
          : <Link to={`mailto:${SUPPORT_EMAIL}`}>Email support</Link>}
      </Button>
    </>
  );
}

interface ErrorContent {
  title: string;
  description: ReactNode;
  color?: AccentColor;
  icon?: IconType;
  actions?: ReactNode;
}

/**
 * Copy for each error the backend can render this page with.
 *
 * Keys must match the codes passed to `render_error_page` in
 * `backend/ng/core/utils/error_page.py`. The server sends only a code, so
 * everything a visitor reads is authored here rather than echoed back from the
 * server's response.
 */
const ERRORS: Record<string, ErrorContent> = {
  sso_state_missing : {
    title : 'Your sign-in session expired',
    description : `We could not match this sign-in to a session we started. This usually happens
      when a login is left open too long, or when cookies are blocked. Starting over should fix it.`,
    color : COLOR_WARNING,
    icon : TbLockExclamation,
    actions : <SsoActions />,
  },
  sso_state_mismatch : {
    title : 'Your sign-in could not be verified',
    description : `The response from your identity provider did not match the sign-in we started,
      so we stopped it. Start a fresh sign-in from this device to continue.`,
    color : COLOR_WARNING,
    icon : TbLockExclamation,
    actions : <SsoActions />,
  },
  sso_no_code : {
    title : 'Your sign-in was not completed',
    description : `Your identity provider did not send back an authorization code, so there was
      nothing for us to verify. This usually means the sign-in was cancelled or interrupted.`,
    color : COLOR_WARNING,
    icon : TbLockExclamation,
    actions : <SsoActions />,
  },
  sso_generic_error : {
    title : 'Your identity provider rejected the sign-in',
    description : (
      <>
        {`Your identity provider returned an error instead of signing you in. `}
        {`If you continue to experience difficulties accessing your account, `}
        <TocContact />
        .
      </>
    ),
    icon : TbPlugConnectedX,
    actions : <SsoActions />,
  },
  sso_card_error : {
    title : 'Your PIV/CAC card is required to log in',
    description : (
      <>
        {`This application requires you to use your PIV/CAC card to log in. Please use `}
        <RadixLink asChild>
          <Link to={SSO_CARD_REGISTRATION_PATH} target="_blank" rel="noopener noreferrer">
            this link
          </Link>
        </RadixLink>
        {` to update your PIV/CAC UPN information in CISA's Registration Portal. `}
        {`Use your current password + MFA or Login.gov credentials to log in to the Registration Portal. `}
        You will be able to use your PIV/CAC to login after updating that information in the CISA Registration Portal.
      </>
    ),
    icon : TbIdBadge2,
    actions : <SsoActions />,
  },
  sso_auth_failed : {
    title : 'We could not sign you in',
    description : `Your identity provider signed you in but did not share the details we need to
      match you to an account. Trying again will often resolve it; if not, please contact support.`,
    icon : TbLockExclamation,
    actions : <SsoActions />,
  },
  sso_unexpected : {
    title : 'Something went wrong while signing you in',
    description : `An unexpected error interrupted your sign-in. The problem has been logged. Please
      try again, and quote the reference below if you need to contact support.`,
    icon : TbServerBolt,
    actions : <SsoActions />,
  },
  sso_registration_unavailable : {
    title : 'Account registration is unavailable',
    description : (
      <>
        {`Single sign-on registration has not been set up for this site, so there is nowhere to
          send you. If you need an account, `}
        <TocContact />
        .
      </>
    ),
    color : COLOR_WARNING,
    icon : TbLifebuoy,
    actions : <SupportActions />,
  },
};

const FALLBACK: ErrorContent = {
  title : 'Something went wrong',
  description : `We hit an error while handling your request. The problem has been logged. Please
    try again, and quote the reference below if you need to contact support.`,
  icon : TbServerBolt,
  actions : <SupportActions />,
};

/**
 * Error page shown in place of the routed page.
 *
 * Non-API routes that a browser navigates to directly - OAuth callbacks and
 * the like - serve the app with the failure attached to `window.init.error`,
 * rather than returning a JSON body the user has to read raw.
 */
export default function ErrorPage({ error }: { error: InitError }) {
  const {
    code, status, reference, detail,
  } = error;

  const content = ERRORS[code] ?? FALLBACK;

  return (
    <ErrorDisplay
      title={content.title}
      description={content.description}
      color={content.color ?? COLOR_NEGATIVE}
      icon={content.icon}
      actions={content.actions}
      status={status}
      code={code}
      reference={reference}
      detail={detail}
    />
  );
}
