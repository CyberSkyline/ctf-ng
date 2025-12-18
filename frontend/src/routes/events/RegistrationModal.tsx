import { COLOR_POSITIVE } from '@/constants';
import { registerMyEvent, registerMyEventTeamJoin } from '@/hooks/events';
import type { Event } from '@/types';
import { Button } from '@radix-ui/themes';
import Modal from 'components/Modal';
import { isUndefined } from 'lodash';
import { TbDoorEnter } from 'react-icons/tb';
import { useNavigate, useParams } from 'react-router';
import RegistrationDataForm from './RegistrationDataForm';

export default function RegistrationModal({ eventId, eventName, isTeamGame }: {eventId : Event['id'], eventName: string, isTeamGame: boolean}) {
  const { inviteCode, idEvent } = useParams();
  const joinWithCode = !!(eventId === Number(idEvent) && !isUndefined(inviteCode));

  const navigate = useNavigate();

  const handleRegister = async (data: { leaderboardName: string; joinCode: string; termsConditions: boolean, selectedOption: string }) => {
    const { leaderboardName, selectedOption } = data;

    if (selectedOption === 'join-team') {
      // Allow user to input invite code or invite url
      let { joinCode } = data;
      joinCode = joinCode.indexOf('/') > -1 ? joinCode.substring(joinCode.lastIndexOf('/') + 1) : joinCode;

      return registerMyEventTeamJoin(eventId, joinCode).then(() => {
        navigate(`/events/${eventId}`);
      });
    }

    return registerMyEvent(eventId, leaderboardName).then(() => {
      navigate(`/events/${eventId}`);
    });
  };

  return (
    <Modal
      title={`Register for ${eventName}`}
      trigger={(
        <Button color={COLOR_POSITIVE}>
          <TbDoorEnter />
          Register
        </Button>
      )}
      onSubmit={handleRegister}
      submitVerb="Register"
      defaultOpen={joinWithCode}
      defaultValues={{
        leaderboardName : '',
        termsConditions : false,
        selectedOption : joinWithCode ? 'join-team' : 'create-team',
      }}
      onOpenChange={(open) => {
        if (!open && joinWithCode) {
          // If the user closes the modal while registering via an invite link, take them back to the event detail page
          navigate(`/events/${eventId}`);
        }
      }}
    >
      {(rhf) => (
        <RegistrationDataForm
          rhf={rhf}
          isTeamGame={isTeamGame}
          joinWithCode={joinWithCode}
          eventId={eventId}
        />
      )}
    </Modal>
  );
}
