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
      <Theme>
        <NavBar />
        <Routes />
        <FooterBar />
      </Theme>
    </BrowserRouter>
  </StrictMode>,
);
