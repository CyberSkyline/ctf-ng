import { useAdminChallengeHints, useAdminChallengeQuestions, useAdminChallengeVariables } from '@/hooks/challenge';
import type { Challenge } from '@/types';
import { tagComparator } from '@/util';
import {
  Badge,
  Code,
  Flex,
  Table,
} from '@radix-ui/themes';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { ErrorCallout, InfoCallout } from 'components/Callouts';
import RadixMarkdown from 'components/RadixMarkdown';
import { TbVariable } from 'react-icons/tb';

export default function ChallengeDetailsTab({ challenge }: {challenge: Challenge}) {
  const { data : questions, error : questionsError } = useAdminChallengeQuestions(challenge.id);
  const { data : hints, error : hintsError } = useAdminChallengeHints(challenge.id);
  const { data : variables, error : varsError } = useAdminChallengeVariables(challenge.id);

  const sortedTags = [ ...challenge.tags ].sort(tagComparator);

  return (
    <>
      <AdminSidebarHeader title="Description" />
      <RadixMarkdown>
        {challenge.description}
      </RadixMarkdown>

      <AdminSidebarHeader title="Tags" />
      {sortedTags.length === 0
        ? <InfoCallout>This challenge does not have any tags.</InfoCallout>
        : (
          <Flex direction="row" gap="1" wrap="wrap">
            {sortedTags.map((tag) => (
              <Badge key={tag} color="gray" radius="full">
                {tag}
              </Badge>
            ))}
          </Flex>
        )}

      <AdminSidebarHeader title="Questions" />
      {questionsError && <ErrorCallout>{questionsError.message}</ErrorCallout> }
      {questions && questions.length === 0 && <InfoCallout>This challenge does not have any questions.</InfoCallout>}
      {questions && questions.length > 0
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
                <Table.Cell>
                  {q.answer.startsWith('"') ? null : <TbVariable className="inline me-1 opacity-50" aria-label="Variable" />}
                  {q.answer.replace(/^"(.*)"$/, '$1')}
                </Table.Cell>
                <Table.Cell>{q.max_attempts}</Table.Cell>
                <Table.Cell>{q.points}</Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table.Root>
        )}

      <AdminSidebarHeader title="Hints" />
      {hintsError && <ErrorCallout>{hintsError.message}</ErrorCallout> }
      {hints && hints.length === 0 && <InfoCallout>This challenge does not have any hints.</InfoCallout>}
      {hints && hints.length > 0
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

      <AdminSidebarHeader title="Variables" />
      {varsError && <ErrorCallout>{varsError.message}</ErrorCallout> }
      {variables && variables.length === 0 && <InfoCallout>This challenge does not have any variables.</InfoCallout>}
      {variables && variables.length > 0
        && (
        <Table.Root>
          <Table.Header>
            <Table.Row>
              <Table.ColumnHeaderCell>Name</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Default</Table.ColumnHeaderCell>
              <Table.ColumnHeaderCell>Template</Table.ColumnHeaderCell>
            </Table.Row>
          </Table.Header>
          <Table.Body>
            {variables?.map((v) => (
              <Table.Row key={v.id}>
                <Table.Cell>
                  <TbVariable className="inline me-1 opacity-50" aria-label="Variable" />
                  {v.name}
                </Table.Cell>
                <Table.Cell>{v.default}</Table.Cell>
                <Table.Cell><Code color="gray">{v.template}</Code></Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table.Root>
        )}
    </>
  );
}
