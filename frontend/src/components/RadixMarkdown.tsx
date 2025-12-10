import {
  Blockquote,
  Code,
  Em,
  Heading,
  Link,
  Strong,
  Table,
  Text,
} from '@radix-ui/themes';
import ReactMarkdown, { type Components } from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import rehypeSanitize, { defaultSchema } from 'rehype-sanitize';
import remarkGfm from 'remark-gfm';

const DISALLOWED_TAGS = [ 'input', 'picture', 'source', 'kbd', 'script' ];

const SELF_ROOT_PATH = window.location.origin;
const PRESCUP_DOMAIN = 'presidentscup.us';

const SANITIZE_SCHEMA = {
  ...defaultSchema,
  tagNames : defaultSchema.tagNames?.filter((t) => !DISALLOWED_TAGS.includes(t)),
  attributes : {
    ...defaultSchema.attributes,
    img : [
      // Only allow src urls from predefined domains
      [ 'src', new RegExp(`^${SELF_ROOT_PATH}`) ],
      [ 'src', new RegExp(`^${PRESCUP_DOMAIN}`) ],
    ],
  },
};

/**
 * Mapping of html elements to their themed Radix UI counterparts to use when rendering markdown.
 */
const Components: Components = {
  p : ({ children }) => <Text as="p" color="gray" className="!mb-2 last:!mb-0">{children}</Text>,
  em : ({ children }) => <Em>{children}</Em>,
  strong : ({ children }) => <Strong>{children}</Strong>,
  code : ({ children }) => <Code color="gray">{children}</Code>,
  pre : ({ children }) => <pre className="[&>code]:block [&>code]:mb-2 [&>code]:!p-2">{children}</pre>,
  blockquote : ({ children }) => <Blockquote>{children}</Blockquote>,
  a : ({ href, children }) => <Link href={href} target="_blank" rel="noopener noreferrer">{children}</Link>,
  h1 : ({ children }) => <Heading size="6" as="h1">{children}</Heading>,
  h2 : ({ children }) => <Heading size="5" as="h2">{children}</Heading>,
  h3 : ({ children }) => <Heading size="4" as="h3">{children}</Heading>,
  h4 : ({ children }) => <Heading size="3" as="h4">{children}</Heading>,
  h5 : ({ children }) => <Heading size="3" as="h5">{children}</Heading>,
  h6 : ({ children }) => <Heading size="3" as="h6">{children}</Heading>,
  ul : ({ children }) => <ul className="list-disc list-inside mb-2 ms-2">{children}</ul>,
  ol : ({ children }) => <ol className="list-decimal list-inside mb-2 ms-2">{children}</ol>,
  li : ({ children }) => <Text asChild color="gray" mb="1"><li>{children}</li></Text>,
  table : ({ children }) => <Table.Root className="w-fit max-w-full mb-2">{children}</Table.Root>,
  thead : ({ children }) => <Table.Header>{children}</Table.Header>,
  tbody : ({ children }) => <Table.Body>{children}</Table.Body>,
  tr : ({ children }) => <Table.Row>{children}</Table.Row>,
  th : ({ children }) => <Table.ColumnHeaderCell>{children}</Table.ColumnHeaderCell>,
  td : ({ children }) => <Table.Cell>{children}</Table.Cell>,
};

/**
 * Renders the given string as markdown using Radix UI components.
 */
export default function RadixMarkdown({ children }: {
  children: string;
}) {
  return (
    <ReactMarkdown components={Components} remarkPlugins={[ remarkGfm ]} rehypePlugins={[ rehypeRaw, [ rehypeSanitize, SANITIZE_SCHEMA ] ]}>
      {children}
    </ReactMarkdown>
  );
}
