import { NavLink } from 'react-router';
import { Flex, Theme } from '@radix-ui/themes';

export default function FooterBar() {
  const itemClass = `
    text-sm
    dark:hover:text-(--gray-12)
    dark:text-(--gray-a11)
  `;

  return (
    <Theme appearance="dark">
      <footer className="w-screen h-[var(--FooterBarHeight)] fixed bottom-0 shadow-inner bg-black">
        <Flex gap="4" justify="center" align="center" height="100%">
          <NavLink
            className={itemClass}
            to="/faq"
          >
            FAQs
          </NavLink>
          <NavLink className={itemClass} to="https://presidentscup.cisa.gov">
            {'President\'s Cup'}
          </NavLink>
        </Flex>
      </footer>
    </Theme>
  );
}
