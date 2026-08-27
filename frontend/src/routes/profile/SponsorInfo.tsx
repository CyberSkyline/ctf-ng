import { useFileUrl } from '@/hooks/fileuploads';
import { useMySponsor } from '@/hooks/users';
import {
  Card,
  Flex,
  IconButton,
  Link as RadixLink,
  Skeleton,
} from '@radix-ui/themes';
import { ErrorCallout, WarningCallout } from 'components/Callouts';
import Statistic from 'components/Statistic';
import { isNil } from 'lodash';
import { TbInfoCircle, TbPencil } from 'react-icons/tb';
import SponsorPickerModal from './SponsorPickerModal';

export default function SponsorInfo() {
  const { data : mySponsor, isLoading, error } = useMySponsor();
  const { data : image } = useFileUrl('sponsor-logos', mySponsor?.logo);

  if (error) {
    return <ErrorCallout className="mt-4">{error.message}</ErrorCallout>;
  }

  if (!isLoading && isNil(mySponsor)) {
    return (
      <WarningCallout className="mt-4">
        You must
        {' '}
        <SponsorPickerModal
          trigger={(
            <RadixLink asChild>
              <button type="button">select a sponsor</button>
            </RadixLink>
          )}
        />
        {' '}
        prior to registering for events.
      </WarningCallout>
    );
  }

  return (
    <Skeleton loading={isLoading}>
      <Card mt="4" className="w-fit">
        <Flex align="center" gap="2">
          {image?.download_url ? (
            <img src={image.download_url} alt="" height="48" width="48" className="shrink-0" />
          ) : (
            <TbInfoCircle size="48" className="shrink-0" />
          )}
          <Statistic label="Your Sponsor" value={mySponsor?.name ?? 'Loading'} size="4" />
          {!isLoading && (
            <SponsorPickerModal
              trigger={(
                <IconButton size="1" ml="2" variant="ghost" aria-label="Change sponsor">
                  <TbPencil />
                </IconButton>
              )}
            />
          )}
        </Flex>
      </Card>
    </Skeleton>
  );
}
