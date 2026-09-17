import type { AccentColor } from '@/constants';
import {
  COLOR_NEGATIVE,
  COLOR_WARNING,
  SSO_CARD_REGISTRATION_PATH,
  SSO_LOGIN_PATH,
  SUPPORT_EMAIL,
  TOC_EMAIL,
  TOC_PHONE,
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

function TocContact() {
  return (
    <>
      {`If you continue to experience difficulties accessing your account, please email the CISA Technical Operations Center at `}
      <RadixLink asChild>
        <Link to={`mailto:${TOC_EMAIL}`}>{TOC_EMAIL}</Link>
      </RadixLink>
      {` or call `}
      <b>{TOC_PHONE}</b>
      .
    </>
  );
}

function SsoActions() {
  return (
    <>
      <Button asChild size="3">
        <Link to={SSO_LOGIN_PATH} reloadDocument>Try logging in again</Link>
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
    title : 'Your login attempt expired',
    description : `We could not identify your current single sign-on session. This usually happens
      when the login page is left open too long, or when cookies are blocked. `,
    color : COLOR_WARNING,
    icon : TbLockExclamation,
    actions : <SsoActions />,
  },
  sso_state_mismatch : {
    title : 'Your single sign-on session could not be verified',
    description : `The response from your identity provider did not match the attempt we started. `,
    color : COLOR_WARNING,
    icon : TbLockExclamation,
    actions : <SsoActions />,
  },
  sso_no_code : {
    title : 'Your login attempt was not completed',
    description : `Your identity provider did not send back an authorization code, so there was
      nothing for us to verify. `,
    color : COLOR_WARNING,
    icon : TbLockExclamation,
    actions : <SsoActions />,
  },
  sso_generic_error : {
    title : 'Your identity provider rejected the login attempt',
    description : (
      <>
        {`Your identity provider returned an error instead of authenticating you in. `}
        <TocContact />
      </>
    ),
    icon : TbPlugConnectedX,
    actions : <SsoActions />,
  },
  sso_card_error : {
    title : 'Your PIV/CAC card is required to log in',
    description : (
      <>
        {`Please go to `}
        <RadixLink asChild>
          <Link to={SSO_CARD_REGISTRATION_PATH} target="_blank" rel="noopener noreferrer">
            this link
          </Link>
        </RadixLink>
        {` to update your PIV/CAC information in CISA's Registration Portal. 
        When prompted, use your current password + MFA or Login.gov credentials to log in.
        You will be able to log in after updating that information in the CISA Registration Portal.`}
      </>
    ),
    icon : TbIdBadge2,
    actions : <SsoActions />,
  },
  sso_auth_failed : {
    title : 'We could not log you in',
    description : (
      <>
        {`Your identity provider authenticated you in but did not share the details we need to match you to an account. `}
        <TocContact />
      </>
    ),
    icon : TbLockExclamation,
    actions : <SsoActions />,
  },
  sso_unexpected : {
    title : 'Something went wrong while logging you in',
    description : `An unexpected error interrupted your login. The problem has been recorded. Please
      try again, and quote the reference below if you need to contact support.`,
    icon : TbServerBolt,
    actions : <SupportActions />,
  },
  sso_registration_unavailable : {
    title : 'Account registration is unavailable',
    description : (
      <>
        {`Single sign-on registration has not been set up for this site, so there is nowhere to
          send you. If you need an account, please `}
        <Link to={`mailto:${SUPPORT_EMAIL}`}>Email support</Link>
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
