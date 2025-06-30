import {
  Badge, Box, Button, Card, Flex, Heading, Separator, Text,
} from '@radix-ui/themes';
import { TbArrowLeft } from 'react-icons/tb';
import { useNavigate } from 'react-router';

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
        <Box maxWidth="200px">
          <Button
            onClick={resolveTicket}
          >
            Mark Ticket as Resolved
          </Button>
        </Box>
        <Heading size="7">Ticket Detail</Heading>
        <div>Chat box goes here with submit button</div>
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
