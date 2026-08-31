import { AnnouncementIcon } from '@/constants';
import type { Announcement } from '@/types';
import { formatDate } from '@/util';
import {
  Box,
  Flex,
  Grid,
  Text,
} from '@radix-ui/themes';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import AnnouncementTypeBadge from 'components/AnnouncementTypeBadge';
import RadixMarkdown from 'components/RadixMarkdown';
import Statistic from 'components/Statistic';
import { useId } from 'react';
import DeleteAnnouncementModal from './DeleteAnnouncementModal';

export default function AnnouncementSidebar({ entity }: {entity: Announcement}) {
  const headerId = useId();

  return (
    <AdminSidebar labelId={headerId}>
      <AdminSidebarHeader title={entity.title} icon={<AnnouncementIcon />} id={headerId}>
        <DeleteAnnouncementModal id={entity.id} />
      </AdminSidebarHeader>

      <Grid columns="2" gap="4" align="center" justify="between">
        <Statistic
          label="Created"
          value={formatDate(entity.created_at)}
          size="5"
        />
        <Statistic
          label="Expires"
          value={formatDate(entity.expires_at) || 'Never'}
          size="5"
        />

        <Statistic
          label="Sender"
          value={entity.sender_name ?? `UNKNOWN (${entity.sender_id})`}
          size="5"
        />
        <Box>
          <Text size="2" color="gray">Type</Text>
          <Flex direction="row">
            <AnnouncementTypeBadge type={entity.type} size="2" />
          </Flex>
        </Box>
      </Grid>

      <AdminSidebarHeader title="Message" />
      <RadixMarkdown>{entity.message}</RadixMarkdown>
    </AdminSidebar>
  );
}
