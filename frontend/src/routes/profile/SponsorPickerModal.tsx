import { useFileList } from '@/hooks/fileuploads';
import { useSponsors } from '@/hooks/sponsors';
import { setMySponsor } from '@/hooks/users';
import type { Sponsor } from '@/types';
import { ErrorCallout } from 'components/Callouts';
import FormSearchField from 'components/FormSearchField';
import Modal from 'components/Modal';
import { isNil, keyBy } from 'lodash';
import { useCallback, type ReactNode } from 'react';
import type { UseFormReturn } from 'react-hook-form';
import { TbInfoCircle } from 'react-icons/tb';

type SponsorPickerFields = { sponsorId: number | null };

// Inner component used here so that hooks only activate when modal is open.
function SponsorPickerForm({
  rhf,
}: {
  rhf: UseFormReturn<SponsorPickerFields>,
}) {
  const { control, formState : { errors } } = rhf;

  const { data : sponsors, error : sponsorsError } = useSponsors();
  const { data : logoList } = useFileList('sponsor-logos', true);
  const logoLookup = keyBy(logoList?.files, 'filename');

  const getSponsorIcon = useCallback((sponsor: Sponsor) => {
    const url = logoLookup[sponsor.logo ?? '']?.download_url;

    // search logos are accompanied by name, so alt text isn't needed
    return url
      ? <img src={url} alt="" className="h-4 w-4 object-cover" />
      : <TbInfoCircle className="h-4 w-4" />;
  }, [ logoLookup ]);

  return (
    <>
      {sponsorsError && <ErrorCallout className="mb-3">{sponsorsError.message}</ErrorCallout>}
      <FormSearchField
        control={control}
        name="sponsorId"
        label="New Sponsor"
        datasource={(sponsors ?? []) as (Sponsor & Record<string, unknown>)[]}
        valueKey="id"
        labelKey="name"
        getIcon={getSponsorIcon}
        openOnFocus
        rules={{ required : 'Sponsor is required' }}
        error={errors.sponsorId}
      />
    </>
  );
}

export default function SponsorPickerModal({
  trigger,
}: {
  trigger: ReactNode,
}) {
  return (
    <Modal<SponsorPickerFields>
      title="Change Sponsor"
      description="Your sponsor is the organization you represent in events."
      submitVerb="Save"
      defaultValues={{ sponsorId : null }}
      onSubmit={async ({ sponsorId }) => {
        if (!isNil(sponsorId)) {
          await setMySponsor(sponsorId);
        }
      }}
      trigger={trigger}
    >
      {(rhf) => <SponsorPickerForm rhf={rhf} />}
    </Modal>
  );
}
