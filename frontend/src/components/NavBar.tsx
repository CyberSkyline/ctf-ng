import { Navbar, NavbarBrand, NavbarCollapse, NavbarLink } from "flowbite-react";
import reactLogo from '../assets/reactLogo.svg'

export default function NavBar() {
    return (
        <Navbar fluid rounded>
          <NavbarBrand href="#">
            <img src={reactLogo} className="mr-3 h-6 sm:h-9" alt="Presidents Cup Logo" />
            <span className="self-center whitespace-nowrap text-xl font-semibold dark:text-white">President's Cup</span>
          </NavbarBrand>
          <NavbarCollapse>
            <NavbarLink href="#" active>
              Home
            </NavbarLink>
          </NavbarCollapse>
        </Navbar>
    );
}