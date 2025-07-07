import {
  Callout, Card, Grid, Heading,
} from '@radix-ui/themes';
import { TbInfoCircle } from 'react-icons/tb';

/**
 * Provides admins with more detailed reports, along with CSV exports.
 */
export default function AdminReports() {
  return (
    <Grid columns={{ initial : '1', md : '2', xl : '3' }} gap="4">
      <Card>
        <Heading>Report 1</Heading>
        <Callout.Root
          color="jade"
          variant="surface"
        >
          <Callout.Icon>
            <TbInfoCircle />
          </Callout.Icon>
          <Callout.Text>
            Graph or table showing at-a-glance data, with option to download.
          </Callout.Text>
        </Callout.Root>
      </Card>
      <Card>
        <Heading>Report 2</Heading>
        <Callout.Root
          color="jade"
          variant="surface"
        >
          <Callout.Icon>
            <TbInfoCircle />
          </Callout.Icon>
          <Callout.Text>
            Graph or table showing at-a-glance data, with option to download.
          </Callout.Text>
        </Callout.Root>
      </Card>
      <Card>
        <Heading>Report 3</Heading>
        <Callout.Root
          color="jade"
          variant="surface"
        >
          <Callout.Icon>
            <TbInfoCircle />
          </Callout.Icon>
          <Callout.Text>
            Graph or table showing at-a-glance data, with option to download.
          </Callout.Text>
        </Callout.Root>
      </Card>
      <Card>
        <Heading>Report 4</Heading>
        <Callout.Root
          color="jade"
          variant="surface"
        >
          <Callout.Icon>
            <TbInfoCircle />
          </Callout.Icon>
          <Callout.Text>
            Graph or table showing at-a-glance data, with option to download.
          </Callout.Text>
        </Callout.Root>
      </Card>
    </Grid>
  );
}
