import {
  Box, Button, Flex, Heading,
} from '@radix-ui/themes';
import { TbArrowLeft } from 'react-icons/tb';
import { useNavigate } from 'react-router';

export default function CreateTicket() {
  const navigate = useNavigate();
  return (
    <Flex gap="3" direction="column">
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
      <Heading size="7">Create a New Support Ticket</Heading>
      <div>Chat box goes here with submit button</div>
    </Flex>
  );
}
