import { NavLink } from 'react-router';

export default function FooterBar() {
  const itemClass = `
    text-sm
    hover:text-(--gray-12)
    text-(--gray-a11)
  `

  return (
    <footer className="w-screen h-[var(--FooterBarHeight)] fixed bottom-0 flex shadow-inner p-1 justify-center gap-4 bg-black">
      <NavLink className={itemClass}
        to="/faq"
      >
        FAQs
      </NavLink>
      <NavLink className={itemClass} to="https://presidentscup.cisa.gov">
        {'President\'s Cup'}
      </NavLink>
    </footer>
  );
}
