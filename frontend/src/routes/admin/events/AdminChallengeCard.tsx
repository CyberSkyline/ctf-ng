import { COLOR_INFO, DeploymentIcon } from '@/constants';
import type { Challenge } from '@/types';
import {
  Box,
  Button,
  Card,
  Flex,
  Heading,
  Text,
} from '@radix-ui/themes';
import ChallengeIcon from 'components/ChallengeIcon';
import { TbPackages } from 'react-icons/tb';
import { Link } from 'react-router';

export default function AdminChallengeCard({ challenge }: { challenge: Challenge }) {
  return (
    <Card>
      <Flex direction="row" align="center" justify="between" gap="2">
        <Box>
          <Flex direction="row" align="center" gap="1">
            <ChallengeIcon icon={challenge.icon} />
            <Heading size="3">
              {challenge.name}
            </Heading>
          </Flex>
          <Text color="gray">
            {challenge.summary}
          </Text>
        </Box>
        <Flex direction="row" align="center" gap="2">
          <Button variant="ghost" color={COLOR_INFO} asChild className="!m-0">
            <Link
              to={`/admin/deployments/?filter=${btoa(JSON.stringify({ challenge_name : { filterType : 'text', type : 'equals', filter : challenge.name } }))}`}
            >
              <DeploymentIcon />
              Deployments
            </Link>
          </Button>
        </Flex>
      </Flex>
    </Card>
  );
}
