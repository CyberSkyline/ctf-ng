import { useNotificationSoundEnabled } from '@/hooks/notifications';
import {
  Box,
  Flex,
  Heading,
  IconButton,
  Switch,
  Text,
} from '@radix-ui/themes';
import ding from 'assets/audio/ding.mp3';
import { useId, useRef } from 'react';
import { TbPlayerPlayFilled } from 'react-icons/tb';

export default function NotificationPreferences() {
  const [ soundEnabled, setNotificationSoundEnabled ] = useNotificationSoundEnabled();
  const profileAudioRef = useRef<HTMLAudioElement>(new Audio(ding));
  const switchId = useId();

  return (
    <Flex direction="column" gap="4">
      <Box>
        <Heading as="h2">Notifications</Heading>
        <Text color="gray" trim="end">Manage your in-platform notification settings.</Text>
      </Box>
      {/* No-op form used here to ensure fields follow global form styling. */}
      <form onSubmit={(e) => e.preventDefault()}>
        <Flex align="center" gap="2">
          <Switch
            id={switchId}
            checked={soundEnabled}
            onCheckedChange={(checked) => {
              setNotificationSoundEnabled(checked);
            }}
            name="Notification Sound"
            size="3"
          />
          <Text as="label" htmlFor={switchId}>Notification Sound</Text>
          <IconButton
            aria-label="Play Notification Sound"
            radius="full"
            size="1"
            variant="surface"
            onClick={() => {
              profileAudioRef.current.currentTime = 0;
              profileAudioRef.current.play().catch(() => {
                // throw away the error intentionally
              });
            }}
          >
            <TbPlayerPlayFilled className="text-xs" />
          </IconButton>
        </Flex>
      </form>
    </Flex>
  );
}
