import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { ThemeProvider } from 'flowbite-react';
import { baseTheme } from './theme/base';

import { BrowserRouter } from 'react-router';
import NavBar from 'components/NavBar';
import FooterBar from 'components/Footer';
import Routes from './Routes';

import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ThemeProvider theme={baseTheme}>
      <BrowserRouter>
        <NavBar />
        <Routes />
        <FooterBar />
      </BrowserRouter>
    </ThemeProvider>
  </StrictMode>,
);
