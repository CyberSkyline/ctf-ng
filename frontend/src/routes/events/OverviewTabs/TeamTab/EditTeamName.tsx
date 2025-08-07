import {
  Box,
  Button,
  Text,
  TextField,
} from '@radix-ui/themes';
import { Form } from 'radix-ui';
import { useEffect, useState } from 'react';
import { TbPencil } from 'react-icons/tb';
import { ErrorCallout } from 'components/Callouts';
import { updateTeamName } from '@/hooks/events';
import type { Team } from '@/types';

export default function EditTeamName(
  { eventId, defaultTeamName } :
  { eventId: Team['event_id'], defaultTeamName: Team['name'] },
) {
  const [ isEditing, setIsEditing ] = useState<boolean>(false);
  const [ formData, setFormData ] = useState({
    teamName : defaultTeamName,
  });
  const [ loading, setLoading ] = useState<boolean>(false);
  const [ error, setError ] = useState<string | null>(null);

  useEffect(() => {
    if (!isEditing) {
      setError(null);
      setLoading(false);
    }
  }, [ isEditing ]);

  const updateName = (e) => {
    e.preventDefault();
    setLoading(true);

    updateTeamName(eventId, formData.teamName)
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
    <Box maxWidth="380px">
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
                        loading={loading}
                        disabled={loading}
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
              {error && (
                <ErrorCallout className="mt-2">
                  {error}
                </ErrorCallout>
              )}
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
