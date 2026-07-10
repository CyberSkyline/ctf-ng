import { Accordion as RadixAccordion } from 'radix-ui';
import { TbChevronDown } from 'react-icons/tb';
import type { ComponentProps } from 'react';
import { twMerge } from 'tailwind-merge';

type AccordionRootProps = ComponentProps<typeof RadixAccordion.Root>;

function Root({
  className,
  ...props
}: AccordionRootProps) {
  return (
    <RadixAccordion.Root
      className={twMerge(
        `
        overflow-hidden
        rounded-[var(--radius-3)]
        border
        border-[var(--gray-a6)]
        bg-[var(--color-panel-solid)]`,
        className,
      )}
      {...props}
    />
  );
}

function Item({
  className,
  ...props
}: ComponentProps<typeof RadixAccordion.Item>) {
  return (
    <RadixAccordion.Item
      className={twMerge(
        `
        border-b
        border-[var(--gray-a6)]
        last:border-b-0`,
        className,
      )}
      {...props}
    />
  );
}

function Header({
  className,
  ...props
}: ComponentProps<typeof RadixAccordion.Header>) {
  return (
    <RadixAccordion.Header
      className={twMerge(
        'm-0',
        className,
      )}
      {...props}
    />
  );
}

/*
  withBackground:
    - allows overriding background color of the trigger button to match the color prop or Theme accent
*/
type AccordionTriggerProps = ComponentProps<typeof RadixAccordion.Trigger> & {
  color?: string;
  withBackground?: boolean;
};

function Trigger({
  children,
  color,
  withBackground = false,
  className,
  ...props
}: AccordionTriggerProps) {
  return (
    <RadixAccordion.Trigger
      asChild
      {...props}
    >
      <button
        type="button"
        {...(color ? { 'data-accent-color' : color } : {})}
        className={twMerge(
          `
          group
          flex
          w-full
          items-center
          justify-between          
          px-3
          py-2
          focus-visible:outline-none
          focus-visible:ring-2
          focus-visible:ring-inset
          focus-visible:ring-[var(--accent-8)]
          hover:bg-[var(--accent-a3)]
          text-[var(--accent-11)]`,
          withBackground ? 'bg-[var(--accent-a2)]' : 'bg-[var(--color-panel-solid)]',
          className,
        )}
      >
        {children}

        <TbChevronDown
          className="
            transition-transform
            duration-200
            group-data-[state=open]:rotate-180
          "
        />
      </button>
    </RadixAccordion.Trigger>
  );
}

function Content({
  children,
  className,
  ...props
}: ComponentProps<typeof RadixAccordion.Content>) {
  return (
    <RadixAccordion.Content
      className={twMerge(
        `
        overflow-hidden
        data-[state=open]:border-t
        data-[state=open]:border-[var(--gray-a6)]
        data-[state=open]:animate-slideDown
        data-[state=closed]:animate-slideUp`,
        className,
      )}
      {...props}
    >
      <div className="px-3 py-3">
        {children}
      </div>
    </RadixAccordion.Content>
  );
}

const Accordion = {
  Root,
  Item,
  Header,
  Trigger,
  Content,
};

export default Accordion;
