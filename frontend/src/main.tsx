import { Theme } from '@radix-ui/themes';
import { ThemeProvider } from 'next-themes';
import FooterBar from 'components/Footer';
import NavBar from 'components/NavBar';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router';
import { SWRConfig } from 'swr';
import Routes from './Routes';

import { ROUTEPREFIX } from '@/constants';
import { apiFetcher } from '@/fetchers';
import './grid';
import './index.css';

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
          grayColor="sand"
          accentColor="amber"
        >
          <SWRConfig
            value={{ fetcher : apiFetcher }}
          >
            <NavBar />
            <Routes />
            <FooterBar />
          </SWRConfig>
        </Theme>
      </ThemeProvider>
    </BrowserRouter>
  </StrictMode>,
);
