import {
  Card, Grid, Heading,
} from '@radix-ui/themes';
import { InfoCallout } from 'components/Callouts';

/**
 * Provides admins with more detailed reports, along with CSV exports.
 */
export default function AdminReports() {
  return (
    <Grid columns={{ initial : '1', md : '2', xl : '3' }} gap="4">
      <Card>
        <Heading>Report 1</Heading>
        <InfoCallout>Graph or table showing at-a-glance data, with option to download.</InfoCallout>
      </Card>
      <Card>
        <Heading>Report 2</Heading>
        <InfoCallout>Graph or table showing at-a-glance data, with option to download.</InfoCallout>
      </Card>
      <Card>
        <Heading>Report 3</Heading>
        <InfoCallout>Graph or table showing at-a-glance data, with option to download.</InfoCallout>
      </Card>
      <Card>
        <Heading>Report 4</Heading>
        <InfoCallout>Graph or table showing at-a-glance data, with option to download.</InfoCallout>
      </Card>
    </Grid>
  );
}
