import { useState } from 'react';
import {
  Box,
  Button,
  Text,
  TextField,
} from '@radix-ui/themes';
import { TbPencil } from 'react-icons/tb';

export default function EditTeamName() {
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [teamName, setTeamName] = useState<string>('blah');

  function updateName() {
    // api call here
    setIsEditing(false);
  }

  return (
    <Box maxWidth="280px">
      {
        isEditing ? (
          <TextField.Root
            value={teamName}
            onChange={(e) => setTeamName(e.target.value)}
          >
            <TextField.Slot side="right">
              <Button
                variant="solid"
                color="gray"
                size="1"
                onClick={() => setIsEditing(false)}
              >
                Cancel
              </Button>
              <Button
                size="1"
                onClick={updateName}
              >
                Save
              </Button>
            </TextField.Slot>
          </TextField.Root>
        ) : (
          <>
            <Text
              className="pr-4"
            >
              Team Name:
            </Text>
            <Button
              className="!mt-0"
              color="lime"
              variant="ghost"
              onClick={() => setIsEditing(true)}
            >
              {teamName}
              <TbPencil />
            </Button>
          </>
        )
      }
    </Box>
  );
}
