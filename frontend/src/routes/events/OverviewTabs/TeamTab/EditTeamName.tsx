import {
  Box,
  Button,
  Text,
  TextField,
} from '@radix-ui/themes';
import { Form } from 'radix-ui';
import { useState } from 'react';
import { TbPencil } from 'react-icons/tb';
import { updateTeamName } from '@/hooks/events';
import type { Team } from '@/types';

export default function EditTeamName(team: Team) {
  const { name : defaultTeamName, event_id : eventId} = team
  const [ isEditing, setIsEditing ] = useState<boolean>(false);
  const [ formData, setFormData ] = useState({
    teamName : defaultTeamName,
  });
  const [ loading, setLoading ] = useState<boolean>(false);
  const [ error, setError ] = useState<string | null>(null);

  const updateName = (e) => {
    e.preventDefault();

    const newTeam = { ...team, name : formData.teamName as string };
    updateTeamName(eventId, newTeam)
      .then(() => {
        setIsEditing(false);
      })
      .catch((err) => {
        setError(err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name] : value,
    }));
  };

  return (
    <Box maxWidth="280px">
      {
        isEditing ? (
          <Form.Root
            onSubmit={updateName}
          >
            <Form.Field name="teamName">
              <Form.Control
                asChild
              >
                <TextField.Root
                  value={formData.teamName}
                  onChange={handleChange}
                  required
                >
                  <TextField.Slot side="right">
                    <Button
                      variant="solid"
                      color="gray"
                      size="1"
                      onClick={() => {
                        setIsEditing(false);
                        setFormData({ teamName : defaultTeamName });
                      }}
                    >
                      Cancel
                    </Button>
                    <Form.Submit asChild>
                      <Button
                        type="submit"
                        size="1"
                      >
                        Save
                      </Button>
                    </Form.Submit>
                  </TextField.Slot>
                </TextField.Root>
              </Form.Control>
              <Form.Message match="valueMissing">
                Please enter a team name.
              </Form.Message>
            </Form.Field>
          </Form.Root>
        ) : (
          <>
            <Text
              className="pr-4"
            >
              Team Name:
            </Text>
            <Button
              className="!mt-0"
              variant="ghost"
              onClick={() => setIsEditing(true)}
            >
              {formData.teamName}
              <TbPencil />
            </Button>
          </>
        )
      }
    </Box>
  );
}
