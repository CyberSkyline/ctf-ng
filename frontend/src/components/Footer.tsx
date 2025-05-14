import { Footer, FooterCopyright, FooterLink, FooterLinkGroup } from "flowbite-react";

export default function FooterBar() {
  return (
    <Footer container className='fixed bottom-0'>
      <FooterCopyright href="https://cyberskyline.com/" by="Cyber Skyline™" year={2025} />
      <FooterLinkGroup>
        <FooterLink href="/">Home</FooterLink>
      </FooterLinkGroup>
    </Footer>
  );
}