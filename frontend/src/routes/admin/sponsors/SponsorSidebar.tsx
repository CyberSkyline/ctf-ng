import type { Sponsor } from '@/types';
import AdminSidebar from 'components/AdminSidebar';
import AdminSidebarHeader from 'components/AdminSidebarHeader';
import { WarningCallout } from 'components/Callouts';
import SponsorModal from './SponsorModal';

export default function SponsorSidebar({ entity }: {entity: Sponsor}) {
  return (
    <AdminSidebar>
      <AdminSidebarHeader title={entity.name}>
        <SponsorModal sponsor={entity} />
      </AdminSidebarHeader>
      {entity.logo ? (
        <>
          <p>{entity.logo}</p>
          <img src={entity.logo} alt={entity.name} />
        </>
      ) : <WarningCallout>No logo is associated with this sponsor</WarningCallout>}
    </AdminSidebar>
  );
}
