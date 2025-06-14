import { map } from 'lodash';
import { Flex, Table } from '@radix-ui/themes';
import EditTeamName from './EditTeamName';
import AddMemberModal from './AddMemberModal';
import RemovePlayerModal from './RemovePlayerModal';
import LeaveTeamModal from './LeaveTeamModal';
import TransferTeamModal from './TransferTeamModal';
import AssignCaptainModal from './AssignCaptainModal';

export default function TeamManagement() {
  const selfId = '1'; // its a me, Mario
  const inviteCode = 'httptempcode';
  const membersList = [
    { id: '1', name: 'cj', role: 'captain' },
    { id: '2', name: 'md', role: 'captain' },
  ];

  const transferCaptain = true;

  return (
    <>
      <Flex gap="4" direction="column">
        <EditTeamName />
        <AddMemberModal
          inviteCode={inviteCode}
        />
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
          {map(membersList, (member) => (
            <Table.Row key={member.id}>
              <Table.RowHeaderCell>{member.name}</Table.RowHeaderCell>
              <Table.Cell>{member.role}</Table.Cell>
              <Table.Cell>
                <Flex as="span" align="center" gap="2">
                  {member.id === selfId ? (
                    <>
                      <LeaveTeamModal
                        transferCaptain={transferCaptain}
                        membersList={membersList}
                      />
                      <TransferTeamModal
                        transferCaptain={transferCaptain}
                        membersList={membersList}
                      />
                    </>
                  ) : (
                    <>
                      <RemovePlayerModal
                        id={member.id}
                        name={member.name}
                      />
                      <AssignCaptainModal
                        id={member.id}
                        name={member.name}
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
