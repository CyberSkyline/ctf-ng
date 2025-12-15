import { Theme } from '@radix-ui/themes';
import FooterBar from 'components/Footer';
import NavBar from 'components/NavBar';
import { ThemeProvider } from 'next-themes';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router';
import { SWRConfig } from 'swr';

import { ROUTEPREFIX } from '@/constants';
import { apiFetcher } from '@/fetchers';
import Favicon from 'components/Favicon';
import Routes from './Routes';
import './grid';
import './index.css';
import './socket';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter basename={ROUTEPREFIX}>
      <ThemeProvider
        attribute="class"
        defaultTheme="dark"
        enableSystem
      >
        <Theme
          panelBackground="solid" // disable blur effect on surfaces for performance
          grayColor="sage"
          accentColor="teal"
        >
          <SWRConfig
            value={{ fetcher : apiFetcher }}
          >
            <Favicon />
            <NavBar />
            <Routes />
            <FooterBar />
          </SWRConfig>
        </Theme>
      </ThemeProvider>
    </BrowserRouter>
  </StrictMode>,
);
