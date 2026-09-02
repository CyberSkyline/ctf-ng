import type { AccentColor } from '@/constants';
import { COLOR_NEGATIVE } from '@/constants';
import {
  Badge,
  Card,
  Code,
  DataList,
  Flex,
  Heading,
  IconButton,
  Text,
  Tooltip,
} from '@radix-ui/themes';
import Accordion from 'components/Accordion';
import type { ReactNode } from 'react';
import { useState } from 'react';
import type { IconType } from 'react-icons';
import { TbAlertTriangle, TbCheck, TbCopy } from 'react-icons/tb';

interface ErrorDisplayProps {
  /** Short, plain-language summary of what went wrong. */
  title: string;
  /** What the user should understand or do about it. */
  description: ReactNode;
  /** HTTP-style status shown above the title. Omitted for errors without one. */
  status?: number | string;
  /** Semantic accent for the icon and status badge. */
  color?: AccentColor;
  icon?: IconType;
  /** Buttons offering the user a way forward. Rendered full-width, stacked. */
  actions?: ReactNode;
  /** Stable machine-readable identifier for the failure, e.g. `sso_state_mismatch`. */
  code?: string;
  /** Log correlation id. Users quote this in support tickets. */
  reference?: string;
  /** Internal specifics. Only present when the backend runs in debug mode. */
  detail?: string;
}

function CopyButton({ value }: { value: string }) {
  const [ copied, setCopied ] = useState(false);

  const copy = () => {
    navigator.clipboard.writeText(value).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    }, () => { /* clipboard unavailable - the value is selectable either way */ });
  };

  return (
    <Tooltip content={copied ? 'Copied' : 'Copy'}>
      <IconButton
        size="1"
        variant="ghost"
        color="gray"
        aria-label={`Copy ${value}`}
        onClick={copy}
      >
        {copied ? <TbCheck aria-hidden /> : <TbCopy aria-hidden />}
      </IconButton>
    </Tooltip>
  );
}

/**
 * Full-page treatment for a request that could not be completed.
 *
 * Leads with plain language and a way forward; the machine-readable code,
 * reference id and any debug detail are tucked into a collapsed section so
 * they stay available for support without shouting at the user.
 */
export default function ErrorDisplay({
  title,
  description,
  status,
  color = COLOR_NEGATIVE,
  icon : Icon = TbAlertTriangle,
  actions,
  code,
  reference,
  detail,
}: ErrorDisplayProps) {
  const hasDetails = Boolean(code || reference || detail);

  return (
    <Flex
      className="min-h-[calc(100vh-var(--NavBarHeight)-var(--FooterBarHeight))] -m-3 bg-dots-1"
      align="center"
      justify="center"
      direction="column"
      p="3"
    >
      <title>{title}</title>
      <Card size="3" className="w-full max-w-lg">
        <Flex direction="column" align="center" gap="4" px="2" py="4">
          <Flex
            align="center"
            justify="center"
            className="size-16 shrink-0 rounded-full"
            style={{
              backgroundColor : `var(--${color}-a3)`,
              color : `var(--${color}-11)`,
            }}
          >
            <Icon size={30} aria-hidden />
          </Flex>

          <Flex direction="column" align="center" gap="2">
            {status !== undefined && (
              <Badge color={color} variant="soft" radius="full" className="tabular-nums">
                {status}
              </Badge>
            )}
            <Heading size="6" align="center" wrap="balance">
              {title}
            </Heading>
            <Text as="p" color="gray" align="center" wrap="pretty">
              {description}
            </Text>
          </Flex>

          {actions && (
            <Flex direction="column" gap="2" width="100%" mt="1">
              {actions}
            </Flex>
          )}

          {hasDetails && (
            <Accordion.Root type="single" collapsible className="w-full">
              <Accordion.Item value="details">
                <Accordion.Header>
                  <Accordion.Trigger color="gray">
                    <Text size="2">Technical details</Text>
                  </Accordion.Trigger>
                </Accordion.Header>
                <Accordion.Content>
                  <DataList.Root size="1" orientation="vertical">
                    {code && (
                      <DataList.Item>
                        <DataList.Label>Error code</DataList.Label>
                        <DataList.Value>
                          <Code variant="ghost" size="2">{code}</Code>
                        </DataList.Value>
                      </DataList.Item>
                    )}
                    {reference && (
                      <DataList.Item>
                        <DataList.Label>Reference</DataList.Label>
                        <DataList.Value>
                          <Flex align="center" gap="2">
                            <Code variant="ghost" size="2" className="ss02">{reference}</Code>
                            <CopyButton value={reference} />
                          </Flex>
                        </DataList.Value>
                      </DataList.Item>
                    )}
                    {detail && (
                      <DataList.Item>
                        <DataList.Label>Detail</DataList.Label>
                        <DataList.Value>
                          <Code
                            variant="ghost"
                            size="2"
                            className="block whitespace-pre-wrap break-words max-h-48 overflow-y-auto"
                          >
                            {detail}
                          </Code>
                        </DataList.Value>
                      </DataList.Item>
                    )}
                  </DataList.Root>
                </Accordion.Content>
              </Accordion.Item>
            </Accordion.Root>
          )}
        </Flex>
      </Card>
    </Flex>
  );
}
