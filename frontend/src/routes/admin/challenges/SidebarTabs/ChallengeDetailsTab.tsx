import { useAdminChallengeHints, useAdminChallengeQuestions } from '@/hooks/challenge';
import type { Challenge } from '@/types';
import { Table } from '@radix-ui/themes';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { ErrorCallout } from 'components/Callouts';
import RadixMarkdown from 'components/RadixMarkdown';

export default function ChallengeDetailsTab({ challenge }: {challenge: Challenge}) {
  const { data : questions, error : questionsError } = useAdminChallengeQuestions(challenge.id);
  const { data : hints, error : hintsError } = useAdminChallengeHints(challenge.id);

  return (
    <>
      <AdminSidebarHeader title="Description" />
      <RadixMarkdown>
        {challenge.description}
      </RadixMarkdown>

      <AdminSidebarHeader title="Questions" />
      {questionsError && <ErrorCallout>{questionsError.message}</ErrorCallout> }
      {questions
        && (
        <Table.Root>
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeaderCell>Name</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Body</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Answer</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Attempts</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Points</Table.ColumnHeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {questions?.map((q) => (
              <Table.Row key={q.id}>
                <Table.Cell>{q.name}</Table.Cell>
                <Table.Cell>{q.body}</Table.Cell>
                <Table.Cell>{q.answer}</Table.Cell>
                <Table.Cell>{q.max_attempts}</Table.Cell>
                <Table.Cell>{q.points}</Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table.Root>
        )}

      <AdminSidebarHeader title="Hints" />
      {hintsError && <ErrorCallout>{hintsError.message}</ErrorCallout> }
      {hints
        && (
        <Table.Root>
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeaderCell>Name</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Preview</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Body</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Deduction</Table.ColumnHeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {hints?.map((h) => (
              <Table.Row key={h.id}>
                <Table.Cell>{h.name}</Table.Cell>
                <Table.Cell>{h.preview}</Table.Cell>
                <Table.Cell>{h.body}</Table.Cell>
                <Table.Cell>{h.deduction}</Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table.Root>
        )}
    </>
  );
}
