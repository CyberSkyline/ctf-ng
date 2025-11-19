import { useMyTeam, useMyTeamMembers } from '@/hooks/events';
import { useCurrentUser } from '@/hooks/users';
import { Container, Flex, Table } from '@radix-ui/themes';
import { ErrorCallout } from 'components/Callouts';
import RequireEventPermission from 'components/RequireEventPermission';
import RoleBadge from 'components/RoleBadge';
import Statistic from 'components/Statistic';
import { isUndefined, map } from 'lodash';
import { useParams } from 'react-router';
import AddMemberModal from './AddMemberModal';
import AssignCaptainModal from './AssignCaptainModal';
import RemovePlayerModal from './RemovePlayerModal';

export default function TeamManagement() {
  const { data : currentUser } = useCurrentUser();

  const { idEvent } = useParams<{idEvent: string}>();
  const { data : team, error : teamError } = useMyTeam(Number(idEvent));

  const { data : fullMembersList, error : fullMembersError } = useMyTeamMembers(team?.event_id);

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
      <Flex gap="3" direction="row" justify="between" align="center" mb="3">
        <Statistic label="Your Team" value={teamName} />
        <RequireEventPermission
          permission="CAN_EDIT_TEAM"
          eventId={eventId}
          permissionDeniedPlaceholder={null}
        >
          {!isUndefined(team.invite_code) && <AddMemberModal inviteCode={team.invite_code} eventId={eventId} />}
        </RequireEventPermission>
      </Flex>

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
                      <RemovePlayerModal
                        eventId={eventId}
                        userId={id}
                        name={name}
                      />
                    )}
                    {role !== 'captain' && (
                      <AssignCaptainModal
                        eventId={eventId}
                        userId={id}
                        name={name}
                      />
                    )}
                  </RequireEventPermission>
                </Flex>
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>
    </Container>
  );
}
