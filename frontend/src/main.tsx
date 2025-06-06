import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router';
import { Theme } from '@radix-ui/themes';
import NavBar from 'components/NavBar';
import FooterBar from 'components/Footer';
import { SWRConfig } from 'swr';
import Routes from './Routes';

import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Theme
        appearance="dark"
        panelBackground="solid" // disable blur effect on surfaces for performance
        grayColor="olive"
        accentColor="lime"
      >
        <SWRConfig
          value={{
            fetcher: (resource, init) => fetch(resource, init).then((res) => res.json()),
          }}
        >
          <NavBar />
          <Routes />
          <FooterBar />
        </SWRConfig>
      </Theme>
    </BrowserRouter>
  </StrictMode>,
);
