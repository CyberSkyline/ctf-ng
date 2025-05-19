import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import { BrowserRouter } from 'react-router';
import NavBar from 'components/NavBar';
import FooterBar from 'components/Footer';
import Routes from './Routes';

import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <NavBar />
      <Routes />
      <FooterBar />
    </BrowserRouter>
  </StrictMode>,
);
