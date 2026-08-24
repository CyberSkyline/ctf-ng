import { useCurrentUser } from '@/hooks/users';
import {
  Container,
  Flex,
  Heading,
  Skeleton,
  Text,
} from '@radix-ui/themes';
import HeaderContainer from 'components/HeaderContainer';
import EmailPreferences from './EmailPreferences';
import NotificationPreferences from './NotificationPreferences';
import SponsorInfo from './SponsorInfo';
import WorkspaceRestartModal from './WorkspaceRestartModal';

export default function Profile() {
  const { data : currentUser } = useCurrentUser();

  return (
    <>
      <title>Profile</title>

      <HeaderContainer>
        <Skeleton loading={!currentUser}>
          <Heading size="8" className="w-fit" aria-label={`Profile for ${currentUser?.name}`}>{currentUser?.name || 'Loading'}</Heading>
        </Skeleton>
        <Skeleton loading={!currentUser}>
          <Text color="gray">{currentUser?.email || 'loading@loading.com'}</Text>
        </Skeleton>
        <SponsorInfo />
      </HeaderContainer>

      <Container size="2" my="8">
        <Flex direction="column" gap="8">
          <EmailPreferences />
          <NotificationPreferences />
          <WorkspaceRestartModal />
        </Flex>
      </Container>
    </>
  );
}
