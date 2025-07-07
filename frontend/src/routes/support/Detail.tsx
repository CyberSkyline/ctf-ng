import {
  Badge, Box, Button, Card, Flex, Heading, Separator, Text,
} from '@radix-ui/themes';
import { TbArrowLeft } from 'react-icons/tb';
import { useNavigate } from 'react-router';
// import Editor from 'components/Editor'; //milkdown
import { map } from 'lodash';
/* import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import rehypeRaw from 'rehype-raw';
import rehypeSanitize from 'rehype-sanitize'; */

function StatusBadge(status: string) {
  switch (status) {
    case 'closed': return <Badge color="jade">Closed</Badge>;
    case 'inprogress': return <Badge color="blue">In Progress</Badge>;
    default: return <Badge color="orange">Open</Badge>;
  }
}

export default function Detail() {
  const status = 'inprogress';
  const event = 'blah event';
  const challenge = 'blah challenge';
  const repliesArray = [
    { user : 'user1', timestamp : '2025-11-1', text : 'blah' },
    { user : 'user2', timestamp : '2025-11-1', text : 'blah' },
    { user : 'user3', timestamp : '2025-11-1', text : 'blah' },
    { user : 'user4', timestamp : '2025-11-1', text : 'blah' },
  ];

  const navigate = useNavigate();

  function resolveTicket() {
    // do server call to resolve ticket
    console.log('Resolved Ticket');
    // onSuccess go back to details page
    navigate('/support');
  }

  return (
    <Flex direction="row" gap="4">
      <Flex gap="3" direction="column" className="w-4/5">
        <Box maxWidth="200px">
          <Button
            variant="ghost"
            color="lime"
            onClick={() => { navigate('/support'); }}
          >
            <TbArrowLeft />
            {' '}
            Support
          </Button>
        </Box>
        <Heading size="7">Ticket Detail</Heading>
        <Box maxWidth="200px">
          <Button
            onClick={resolveTicket}
          >
            Mark Ticket as Resolved
          </Button>
        </Box>
        <div>
          {map(repliesArray, ({ user, timestamp, text }) => (
            <Card className="pt-8">
              <Text>{user}</Text>
              <Text>{timestamp}</Text>
              <div className="pb-4">
                {text}
                markdownreact here
              </div>
            </Card>
          ))}
        </div>
        <div>
          {/* <Editor
            value={value}
            onChange={handleOnChange}
          /> */}
        </div>
      </Flex>

      <Card size="3" className="w-1/5">
        <Flex direction="column" gap="4">
          <div>
            Event
            <Separator size="4" />
            <Text>{event}</Text>
          </div>
          <div>
            Challenge
            <Separator size="4" />
            <Text>{challenge}</Text>
          </div>
          <div>
            Status
            <Separator size="4" />
            {StatusBadge(status)}
          </div>
        </Flex>
      </Card>
    </Flex>
  );
}
