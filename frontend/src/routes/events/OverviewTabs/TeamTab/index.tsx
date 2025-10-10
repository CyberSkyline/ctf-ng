import { useMyTeam, useMyTeamMembers } from '@/hooks/events';
import { useCurrentUser } from '@/hooks/users';
import {
  Container,
  Flex,
  Table,
  Text,
} from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import RequireEventPermission from 'components/RequireEventPermission';
import RoleBadge from 'components/RoleBadge';
import { find, isUndefined, map } from 'lodash';
import { useMemo } from 'react';
import { useParams } from 'react-router';
import AddMemberModal from './AddMemberModal';
import AssignCaptainModal from './AssignCaptainModal';
import EditTeamName from './EditTeamName';
import LeaveTeamModal from './LeaveTeamModal';
import RemovePlayerModal from './RemovePlayerModal';

export default function TeamManagement() {
  const { data : currentUser } = useCurrentUser();

  const { idEvent } = useParams<{idEvent: string}>();
  const { data : team, error : teamError } = useMyTeam(Number(idEvent));

  const { data : fullMembersList, error : fullMembersError } = useMyTeamMembers(team?.event_id);

  const userIsCaptain = useMemo(() => !!find(fullMembersList, (member) => {
    if (member.user_id === currentUser?.id) {
      return member.role === 'captain';
    }
    return false;
  }), [ fullMembersList, currentUser ]);

  if (teamError || fullMembersError) {
    return (
      <Container size="4">
        {teamError && <ErrorCallout>{teamError.message}</ErrorCallout>}
        {fullMembersError && <ErrorCallout>{fullMembersError.message}</ErrorCallout>}
      </Container>
    );
  }

  if (!team) {
    // if team is still loading, show nothing
    return null;
  }

  const { event_id : eventId, name : teamName } = team;

  return (
    <Container size="4">

      <RequireEventPermission
        permission="CAN_EDIT_TEAM"
        eventId={eventId}
        permissionDeniedPlaceholder={<Text>{`Team Name: ${teamName}`}</Text>}
      >
        <Flex gap="3" direction="row" justify="between">
          <EditTeamName eventId={eventId} defaultTeamName={teamName} />
          {!isUndefined(team.invite_code) && <AddMemberModal inviteCode={team.invite_code} eventId={eventId} />}
        </Flex>
      </RequireEventPermission>

      <Table.Root>
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeaderCell>Name</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Role</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Actions</Table.ColumnHeaderCell>
          </Table.Row>
        </Table.Header>

        <Table.Body>
          {map(fullMembersList, ({
            user_name : name,
            user_id : id,
            role,
          }) => (
            <Table.Row key={id}>
              <Table.RowHeaderCell>
                {
                  id === currentUser?.id ? `${name} (you)` : name
                }
              </Table.RowHeaderCell>
              <Table.Cell><RoleBadge value={role} /></Table.Cell>
              <Table.Cell>
                <Flex as="span" align="center" gap="2">
                  <RequireEventPermission
                    permission="CAN_EDIT_TEAM"
                    eventId={eventId}
                    permissionDeniedPlaceholder={null}
                  >
                    {id !== currentUser?.id && (
                      <>
                        <RemovePlayerModal
                          eventId={eventId}
                          userId={id}
                          name={name}
                        />
                        <AssignCaptainModal
                          eventId={eventId}
                          userId={id}
                          name={name}
                        />
                      </>
                    )}
                  </RequireEventPermission>
                  { !team.locked && id === currentUser?.id && (
                    <LeaveTeamModal
                      eventId={eventId}
                      transferCaptain={userIsCaptain && team.member_count !== 1}
                    />
                  )}
                </Flex>
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>
    </Container>
  );
}
