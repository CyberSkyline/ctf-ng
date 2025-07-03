import ReactMarkdown, { type Components } from 'react-markdown';
import {
  Text, Heading, Link, Table, Code, Em, Strong, Blockquote,
} from '@radix-ui/themes';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';

/**
 * Mapping of html elements to their themed Radix UI counterparts to use when rendering markdown.
 */
const Components: Components = {
  // @ts-expect-error - ReactMarkdown types broken under React 19
  p : ({ children }) => <Text as="p" color="gray" mb="2">{children}</Text>,
  // @ts-expect-error - ReactMarkdown types broken under React 19
  em : ({ children }) => <Em>{children}</Em>,
  // @ts-expect-error - ReactMarkdown types broken under React 19
  strong : ({ children }) => <Strong>{children}</Strong>,
  // @ts-expect-error - ReactMarkdown types broken under React 19
  code : ({ children }) => <Code color="lime">{children}</Code>,
  // @ts-expect-error - ReactMarkdown types broken under React 19
  blockquote : ({ children }) => <Blockquote>{children}</Blockquote>,
  // @ts-expect-error - ReactMarkdown types broken under React 19
  a : ({ href, children }) => <Link href={href} color="lime" target="_blank" rel="noopener noreferrer">{children}</Link>,
  // @ts-expect-error - ReactMarkdown types broken under React 19
  h1 : ({ children }) => <Heading size="6" as="h1">{children}</Heading>,
  // @ts-expect-error - ReactMarkdown types broken under React 19
  h2 : ({ children }) => <Heading size="5" as="h2">{children}</Heading>,
  // @ts-expect-error - ReactMarkdown types broken under React 19
  h3 : ({ children }) => <Heading size="4" as="h3">{children}</Heading>,
  // @ts-expect-error - ReactMarkdown types broken under React 19
  h4 : ({ children }) => <Heading size="3" as="h4">{children}</Heading>,
  // @ts-expect-error - ReactMarkdown types broken under React 19
  h5 : ({ children }) => <Heading size="2" as="h5">{children}</Heading>,
  // @ts-expect-error - ReactMarkdown types broken under React 19
  h6 : ({ children }) => <Heading size="1" as="h6">{children}</Heading>,
  // @ts-expect-error - ReactMarkdown types broken under React 19
  ul : ({ children }) => <ul className="list-disc list-inside mb-2">{children}</ul>,
  // @ts-expect-error - ReactMarkdown types broken under React 19
  ol : ({ children }) => <ol className="list-decimal list-inside mb-2">{children}</ol>,
  // @ts-expect-error - ReactMarkdown types broken under React 19
  li : ({ children }) => <Text asChild color="gray" mb="1"><li>{children}</li></Text>,
  // @ts-expect-error - ReactMarkdown types broken under React 19
  table : ({ children }) => <Table.Root className="w-fit max-w-full mb-2">{children}</Table.Root>,
  // @ts-expect-error - ReactMarkdown types broken under React 19
  thead : ({ children }) => <Table.Header>{children}</Table.Header>,
  // @ts-expect-error - ReactMarkdown types broken under React 19
  tbody : ({ children }) => <Table.Body>{children}</Table.Body>,
  // @ts-expect-error - ReactMarkdown types broken under React 19
  tr : ({ children }) => <Table.Row>{children}</Table.Row>,
  // @ts-expect-error - ReactMarkdown types broken under React 19
  th : ({ children }) => <Table.ColumnHeaderCell>{children}</Table.ColumnHeaderCell>,
  // @ts-expect-error - ReactMarkdown types broken under React 19
  td : ({ children }) => <Table.Cell>{children}</Table.Cell>,
};

/**
 * Renders the given string as markdown using Radix UI components.
 */
export default function RadixMarkdown({ children }: {
  children: string;
}) {
  return (
    /* @ts-expect-error - ReactMarkdown types broken under React 19 */
    <ReactMarkdown components={Components} remarkPlugins={[ remarkGfm, remarkBreaks ]}>
      {children}
    </ReactMarkdown>
  );
}
