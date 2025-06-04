import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router';
import { Theme } from '@radix-ui/themes';
import NavBar from 'components/NavBar';
import FooterBar from 'components/Footer';
import Routes from './Routes';

import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Theme
        appearance="dark" // TODO: use system preference & allow user to toggle
        panelBackground="solid" // disable blur effect on surfaces for performance
        grayColor="olive"
        accentColor="lime"
      >
        <NavBar />
        <Routes />
        <FooterBar />
      </Theme>
    </BrowserRouter>
  </StrictMode>,
);
