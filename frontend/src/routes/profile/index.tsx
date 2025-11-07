import { useState } from "react";
import { useSponsors } from "@/hooks/sponsors"
import { useMySponsor, setMySponsor } from "@/hooks/users";
import { Button, Card, Container, Flex, Heading, Grid, Text } from "@radix-ui/themes"
import { isNil, isNull, map } from 'lodash'
import { ErrorCallout } from "components/Callouts";

export default function Profile() {
  const [ isEditing, setIsEditing ] = useState<boolean>(false);
  const [ newSponsorError, setNewSponsorError ] = useState<string | null>(null);
  const { data: allSponsors, error } = useSponsors();
  const { data: mySponsor, error: mySponsorError, isLoading } = useMySponsor();

  const selectSponsor = (id: number) => {
    setNewSponsorError(null);

    setMySponsor(id)
      .then(() => {
        setIsEditing(false)
      })
      .catch((err) => {
        setNewSponsorError(err.message)
      })
  }

  return (
    <>
      <title>Profile</title>
      <Container size='2'>
        <Flex justify='between'>
          <Heading as='h1'>Profile</Heading>
          <Button
            onClick={() => {
              setNewSponsorError(null)
              setIsEditing(!isEditing)
            }}
          >
            {isEditing ? 'Cancel Edit' : 'Edit Sponsor'}
          </Button>
        </Flex>
        <Heading size='4' as='h2' className='pt-4'>{isEditing ? 'All Sponsors:' : 'My Sponsor:'}</Heading>
        {isEditing ? (
          <>
            {!isNull(newSponsorError) && <ErrorCallout>{newSponsorError}</ErrorCallout>}
            <Grid columns='3' gap='1'>
              {map(allSponsors, (sponsor) => (
                <Card
                  key={sponsor.id}
                  asChild
                >
                  <button
                    onClick={() => selectSponsor(sponsor.id)}
                  >
                    <Flex direction='column'>
                      <Text weight='bold' align='center'>{sponsor.name}</Text>
                      {sponsor.logo && <img src={sponsor.logo} alt={sponsor.name} />}
                    </Flex>
                  </button>
                </Card>
              ))}
            </Grid>
          </>
        ) : (
          <>
            {!isNil(mySponsor) && (
              <>
                <p>{mySponsor.name}</p>
                {mySponsor.logo && <img src={mySponsor.logo} alt={mySponsor.name} />}
              </>
            )}
          </>
        )}
      </Container>
    </>
  )
}
