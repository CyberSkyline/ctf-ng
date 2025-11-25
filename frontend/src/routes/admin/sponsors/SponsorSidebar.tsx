import type { Sponsor } from '@/types';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { ErrorCallout, WarningCallout } from 'components/Callouts';
import { useFileUrl } from '@/hooks/fileuploads';
import { Box, DataList } from '@radix-ui/themes';
import SponsorModal from './SponsorModal';

export default function SponsorSidebar({ entity }: {entity: Sponsor}) {
  const { data, error } = useFileUrl('sponsor-logos', entity.logo);

  return (
    <AdminSidebar>
      <AdminSidebarHeader title={entity.name}>
        <SponsorModal sponsor={entity} />
      </AdminSidebarHeader>
      <DataList.Root>
        <DataList.Item>
          <DataList.Label>Name</DataList.Label>
          <DataList.Value>{entity.name}</DataList.Value>
        </DataList.Item>
        <DataList.Item>
          <DataList.Label>Filename</DataList.Label>
          <DataList.Value>{entity.logo}</DataList.Value>
        </DataList.Item>
      </DataList.Root>
      {entity.logo ? (
        <Box maxHeight="500px">
          <img src={data?.url} alt={data?.filename} />
        </Box>
      ) : <WarningCallout>No logo is associated with this sponsor</WarningCallout>}
      {error && <ErrorCallout>{error.message}</ErrorCallout>}
    </AdminSidebar>
  );
}
