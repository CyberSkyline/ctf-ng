import { NavLink } from 'react-router';

export default function FooterBar() {
  return (
    <footer className="w-screen h-[var(--FooterBarHeight)] fixed bottom-0 flex shadow-inner p-1 justify-center gap-4 bg-black text-white text-sm">
      <NavLink to="https://presidentscup.cisa.gov">
        {'President\'s Cup'}
      </NavLink>
      <NavLink to="https://cyberskyline.com/">Powered by Cyber Skyline</NavLink>
    </footer>
  );
}
