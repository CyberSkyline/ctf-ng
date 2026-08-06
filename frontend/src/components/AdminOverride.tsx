import { COLOR_WARNING } from '@/constants';
import { Box, Badge, Callout } from '@radix-ui/themes';
import type { ComponentProps } from 'react';
import { TbAlertTriangle } from 'react-icons/tb';

type Props =
  | ({ type: 'callout' } & ComponentProps<typeof Callout.Root>)
  | ({ type: 'badge' } & ComponentProps<typeof Badge>);

export default function AdminOverride(props: Props) {
  // eslint-disable-next-line react/destructuring-assignment
  if (props.type === 'callout') {
    const { children, ...calloutProps } = props;

    return (
      <Callout.Root
        variant="surface"
        color={COLOR_WARNING}
        {...calloutProps}
      >
        <Callout.Icon>
          <TbAlertTriangle aria-label="Warning" />
        </Callout.Icon>

        <Callout.Text className="whitespace-pre-wrap">
          {children}
        </Callout.Text>
      </Callout.Root>
    );
  }

  const { children, ...badgeProps } = props;

  return (
    <Box>
      <Badge
        color={COLOR_WARNING}
        size="3"
        radius="full"
        {...badgeProps}
      >
        {children}
      </Badge>
    </Box>
  );
}
