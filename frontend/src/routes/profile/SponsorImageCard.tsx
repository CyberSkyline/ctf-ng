import type { Sponsor } from '@/types';
import { Card, Flex, Text } from '@radix-ui/themes';
import { useFileUrl } from '@/hooks/fileuploads';

export default function SponsorImageCard({ sponsor, selectSponsor }: {sponsor: Sponsor, selectSponsor: (id: number) => void}) {
  const { id, name, logo } = sponsor;
  const { data } = useFileUrl('sponsor-logos', logo);

  return (
    <Card
      key={id}
      asChild
    >
      <button
        type="button"
        onClick={() => selectSponsor(id)}
        aria-label={name}
      >
        <Flex direction="column">
          <Text weight="bold" align="center">{name}</Text>

          <img src={data?.url} alt={data?.filename} />

        </Flex>
      </button>
    </Card>
  );
}
