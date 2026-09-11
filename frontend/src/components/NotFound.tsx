import { Button } from '@radix-ui/themes';
import { TbMapSearch } from 'react-icons/tb';
import { Link } from 'react-router';
import ErrorDisplay from './ErrorDisplay';

export default function NotFound() {
  return (
    <ErrorDisplay
      status={404}
      color="gray"
      icon={TbMapSearch}
      title="We couldn't find that page"
      description="The page you were looking for doesn't exist, or it may have been moved."
      actions={(
        <Button asChild size="3">
          <Link to="/">Go to dashboard</Link>
        </Button>
      )}
    />
  );
}
