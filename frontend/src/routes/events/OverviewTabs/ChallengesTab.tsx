import { Container, TextField, Grid } from '@radix-ui/themes';
import ChallengeCard from 'components/event/ChallengeCard';
import { TbCode, TbSearch } from 'react-icons/tb';

export default function ChallengesTab() {
  return (
    <>
      <Container size="2" mb="4">
        <TextField.Root placeholder="Search challenges...">
          <TextField.Slot>
            <TbSearch height="16" width="16" />
          </TextField.Slot>
        </TextField.Root>
      </Container>
      <Container size="4">
        <Grid columns={{ xs: '1', sm: '2', md: '3' }} gap="4">
          {/* Placeholder challenges to demo UI */}
          {[...Array(8)].map((_, index) => (
            <ChallengeCard
              id={index.toString()}
              name="Challenge Name"
              description="Lorem ipsum dolor sit amet, consectetur adipiscing elit."
              icon={TbCode}
              points={1000}
              completed={index % 2 === 0} // Example completion status
                  // using index as key for test data. replace with unique id once present
                  // eslint-disable-next-line react/no-array-index-key
              key={index}
            />
          ))}
        </Grid>
      </Container>
    </>
  );
}
