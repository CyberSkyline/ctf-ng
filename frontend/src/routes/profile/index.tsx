import { useState } from 'react';
import { useSponsors } from '@/hooks/sponsors';
import { useMySponsor, setMySponsor } from '@/hooks/users';
import {
  Box,
  Button,
  Container,
  Flex,
  Grid,
  Heading,
} from '@radix-ui/themes';
import {
  isNil,
  isNull,
  isUndefined,
  map,
} from 'lodash';
import { ErrorCallout, WarningCallout } from 'components/Callouts';
import { useFileUrl } from '@/hooks/fileuploads';
import SponsorImageCard from './SponsorImageCard';

export default function Profile() {
  const [ isEditing, setIsEditing ] = useState<boolean>(false);
  const [ newSponsorError, setNewSponsorError ] = useState<string | null>(null);
  const { data : allSponsors, error } = useSponsors();
  const { data : mySponsor, error : mySponsorError } = useMySponsor();
  const { data : image } = useFileUrl('sponsor-logos', mySponsor?.logo);

  const selectSponsor = (id: number) => {
    setNewSponsorError(null);

    setMySponsor(id)
      .then(() => {
        setIsEditing(false);
      })
      .catch((err) => {
        setNewSponsorError(err.message);
      });
  };

  if (mySponsorError) {
    return <ErrorCallout>{mySponsorError.message}</ErrorCallout>;
  }

  return (
    <>
      <title>Profile</title>
      <Container size="2">
        <Flex justify="between">
          <Heading as="h1">Profile</Heading>
          <Button
            onClick={() => {
              setNewSponsorError(null);
              setIsEditing(!isEditing);
            }}
          >
            {isEditing ? 'Cancel Edit' : 'Edit Sponsor'}
          </Button>
        </Flex>
        {isNil(mySponsor) && <WarningCallout className="mt-4">You must select a sponsor prior to registering for events.</WarningCallout>}
        <Heading size="4" as="h2" className="pt-4">{isEditing ? 'All Sponsors:' : 'My Sponsor:'}</Heading>
        {isEditing ? (
          <>
            {!isNull(newSponsorError) && <ErrorCallout>{newSponsorError}</ErrorCallout>}
            {!isUndefined(error) && <ErrorCallout>{error.message}</ErrorCallout>}
            <Grid columns="3" gap="1">
              {map(allSponsors, (sponsor) => (
                <SponsorImageCard
                  sponsor={sponsor}
                  selectSponsor={selectSponsor}
                />
              ))}
            </Grid>
          </>
        ) : (
          !isNil(mySponsor) && (
            <>
              <p>{mySponsor.name}</p>
              {image?.url && (
                <Box maxHeight="500px">
                  <img src={image?.url} alt="" />
                </Box>
              )}
            </>
          )
        )}
      </Container>
    </>
  );
}
