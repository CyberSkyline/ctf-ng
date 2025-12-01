import { useAdminSponsors } from '@/hooks/sponsors';
import AdminGrid from 'components/AdminGrid';
import { ErrorCallout } from 'components/Callouts';
import type { ColDef } from 'ag-grid-community';
import type { Sponsor } from '@/types';
import { Flex } from '@radix-ui/themes';
import SponsorSidebar from './SponsorSidebar';
import SponsorModal from './SponsorModal';

const colDefs: ColDef<Sponsor>[] = [
  {
    field : 'id',
    headerName : 'ID',
  },
  {
    field : 'name',
    headerName : 'Name',
    filter : true,
  },
  {
    field : 'logo',
    headerName : 'Logo URL',
    width : 500,
  },
];

export default function AdminSponsors() {
  const { data, error, isLoading } = useAdminSponsors();

  if (error) {
    return <ErrorCallout>{error.message}</ErrorCallout>;
  }

  return (
    <>
      <title>Admin Sponsors</title>
      <AdminGrid
        rowData={data || []}
        columnDefs={colDefs}
        loading={isLoading}
        getRowId={(params) => params.data.id.toString()}
        sidebarComponent={SponsorSidebar}
        toolbar={(
          <Flex direction="row" justify="start">
            <SponsorModal />
          </Flex>
        )}
      />
    </>
  );
}
