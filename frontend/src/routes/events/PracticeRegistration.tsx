import { registerMyPracticeEvent, useMyEligibility } from '@/hooks/events';
import { useCurrentUser, useRegistration } from '@/hooks/users';
import type { Event } from '@/types';
import { ErrorCallout, WarningCallout } from 'components/Callouts';
import { useEffect, useRef, useState } from 'react';
import { Link as RadixLink } from '@radix-ui/themes';
import { Link } from 'react-router';

export default function PracticeRegistration({ event }: {event: Event}) {
  const { data : user } = useCurrentUser();
  const { isUnregistered } = useRegistration(event.id);
  const { data : eligible, error : eligibilityError } = useMyEligibility(isUnregistered ? event.id : null); // only check eligibility if unregistered

  const mySponsor = user?.affiliation;

  // Handling for implicit registration to practice events
  const hasAttemptedRegistration = useRef(false); // ensures that registration is only attempted once in strict mode
  const [ implicitRegistrationFailed, setImplicitRegistrationFailed ] = useState(false);
  useEffect(() => {
    if (mySponsor && eligible && event.practice && !hasAttemptedRegistration.current) {
      hasAttemptedRegistration.current = true;
      registerMyPracticeEvent(event.id).catch(() => {
        setImplicitRegistrationFailed(true);
      });
    }
  }, [ event, mySponsor, eligible ]);

  return (
    <>
      {user && !mySponsor && (
        <WarningCallout>
          You must select a sponsor on the
          {' '}
          <RadixLink asChild>
            <Link to="/profile?sponsor=1">profile page</Link>
          </RadixLink>
          {' '}
          prior to participating.
        </WarningCallout>
      )}
      {eligibilityError && (
        <ErrorCallout>
          {eligibilityError.message}
        </ErrorCallout>
      )}
      {implicitRegistrationFailed && (
        <ErrorCallout>
          Failed to add your user to this practice event. Please
          {' '}
          <RadixLink asChild>
            <Link to="/support">contact support</Link>
          </RadixLink>
          .
        </ErrorCallout>
      )}
    </>
  );
}
