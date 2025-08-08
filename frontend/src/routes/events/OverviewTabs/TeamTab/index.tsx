import { useMemo } from 'react';
import { Flex, Table, Text } from '@radix-ui/themes';
import {
  filter,
  find,
  isUndefined,
  map,
} from 'lodash';
import { useParams } from 'react-router';
import { useCurrentUser } from '@/hooks/users';
import { useMyTeam, useMyTeamMembers } from '@/hooks/events';
import AddMemberModal from './AddMemberModal';
import AssignCaptainModal from './AssignCaptainModal';
import EditTeamName from './EditTeamName';
import LeaveTeamModal from './LeaveTeamModal';
import RemovePlayerModal from './RemovePlayerModal';
import TransferTeamModal from './TransferTeamModal';

export default function TeamManagement() {
  const { data : currentUser } = useCurrentUser();

  const { idEvent } = useParams<{idEvent: string}>();
  const { data : team, error : teamError } = useMyTeam(Number(idEvent));

  const { data : fullMembersList, error : fullMembersError } = useMyTeamMembers(team?.event_id);

  const membersList = useMemo(() => filter(fullMembersList, (member) => member.id !== currentUser?.id), [ fullMembersList, currentUser ]);

  const userIsCaptain = useMemo(() => !!find(fullMembersList, (member) => {
    if (member.id === currentUser?.id) {
      return member.role === 'captain';
    }
    return false;
  }), [ fullMembersList, currentUser ]);

  if (isUndefined(team) || teamError || isUndefined(fullMembersList) || fullMembersError) {
    return (
      <>
        <Text as="p">Oops, something went wrong.</Text>
        <Text as="p">{String(teamError)}</Text>
        <Text as="p">{String(fullMembersError)}</Text>
      </>
    );
  }

  const { event_id : eventId, name : teamName } = team;

  return (
    <>
      <Flex gap="4" direction="column">
        {
          (userIsCaptain && !team.locked)
            ? <EditTeamName eventId={eventId} defaultTeamName={teamName} />
            : <Text className="pr-4">{`Team Name: ${teamName}`}</Text>
        }
        {!isUndefined(team.invite_code) && userIsCaptain && !team.locked
          && <AddMemberModal inviteCode={team.invite_code} />}
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
              <Table.Cell>{role}</Table.Cell>
              <Table.Cell>
                <Flex as="span" align="center" gap="2">
                  {
                    userIsCaptain && !team.locked && (
                      <>
                        {id !== currentUser?.id ? (
                          <RemovePlayerModal
                            eventId={eventId}
                            userId={id}
                            name={name}
                          />
                        ) : (
                          <>
                            <LeaveTeamModal
                              eventId={eventId}
                              transferCaptain={userIsCaptain}
                              membersList={membersList}
                            />
                            <TransferTeamModal
                              eventId={eventId}
                              transferCaptain={userIsCaptain}
                              membersList={membersList}
                            />
                          </>
                        )}
                        {id !== currentUser?.id && (
                          <AssignCaptainModal
                            eventId={eventId}
                            userId={id}
                            name={name}
                          />
                        )}

                      </>
                    )
                  }
                  { !userIsCaptain && !team.locked && id === currentUser?.id && (
                    <>
                      <LeaveTeamModal
                        eventId={eventId}
                        transferCaptain={userIsCaptain}
                        membersList={membersList}
                      />
                      <TransferTeamModal
                        eventId={eventId}
                        transferCaptain={userIsCaptain}
                        membersList={membersList}
                      />
                    </>
                  )}
                </Flex>
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>
    </>
  );
}
