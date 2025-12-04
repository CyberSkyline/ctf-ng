import { useFileUrl } from '@/hooks/fileuploads';
import type { Sponsor } from '@/types';
import { Box, DataList } from '@radix-ui/themes';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { ErrorCallout, WarningCallout } from 'components/Callouts';
import { useId } from 'react';
import SponsorModal from './SponsorModal';

export default function SponsorSidebar({ entity }: {entity: Sponsor}) {
  const { data, error } = useFileUrl('sponsor-logos', entity.logo);
  const headerId = useId();

  return (
    <AdminSidebar labelId={headerId}>
      <AdminSidebarHeader title={entity.name} id={headerId}>
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
