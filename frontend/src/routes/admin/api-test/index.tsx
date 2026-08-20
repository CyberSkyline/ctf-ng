import { apiMutation } from '@/fetchers';
import {
  Box,
  Container,
  Flex,
  TextField,
  TextArea,
  Button,
  Select,
} from '@radix-ui/themes';
import { ErrorCallout, InfoCallout } from 'components/Callouts';
import { useState } from 'react';
import { Link } from 'react-router';
import { COLOR_POSITIVE } from '@/constants';
import { TbExternalLink } from 'react-icons/tb';

/**
 * API test page for development.
 */
export default function AdminApiTest() {
  const [ method, setMethod ] = useState<'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'>('GET');
  const [ route, setRoute ] = useState('');
  const [ body, setBody ] = useState('');
  const [ response, setResponse ] = useState<string | null>(null);
  const [ error, setError ] = useState<string | null>(null);

  return (
    <Container size="4">
      <Flex direction="column" gap="4">
        <Box>
          <Button color={COLOR_POSITIVE} asChild>
            <Link to="/ng/docs" target="_blank">
              API Documentation
              <TbExternalLink />
            </Link>
          </Button>
        </Box>

        <Flex direction="row" gap="4">
          <Select.Root
            onValueChange={(value) => {
              setMethod(value as 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE');
            }}
            defaultValue={method}
          >
            <Select.Trigger className="!w-64" />
            <Select.Content>
              <Select.Item value="GET">GET</Select.Item>
              <Select.Item value="POST">POST</Select.Item>
              <Select.Item value="PUT">PUT</Select.Item>
              <Select.Item value="PATCH">PATCH</Select.Item>
              <Select.Item value="DELETE">DELETE</Select.Item>
            </Select.Content>
          </Select.Root>

          <TextField.Root
            placeholder="/route"
            value={route}
            onChange={(event) => setRoute(event.target.value)}
            className="grow"
          >
            <TextField.Slot>
              /ng
            </TextField.Slot>
          </TextField.Root>
        </Flex>

        {method !== 'GET' && (
          <TextArea
            placeholder="body"
            value={body}
            onChange={(event) => setBody(event.target.value)}
          />
        )}

        <Button onClick={() => {
          apiMutation(
            route,
            (method !== 'GET' && body) ? JSON.parse(body) : undefined,
            {
              method,
            },
          ).then((r) => {
            setError(null);
            setResponse(JSON.stringify(r, null, 2));
          }).catch((err) => {
            setResponse(null);
            setError(err.message);
          });
        }}
        >
          Send
        </Button>
        {response && (
          <InfoCallout>
            {response}
          </InfoCallout>
        )}
        {error && (
          <ErrorCallout>
            {error}
          </ErrorCallout>
        )}
      </Flex>
    </Container>
  );
}
