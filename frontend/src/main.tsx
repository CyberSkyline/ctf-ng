import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import { BrowserRouter } from 'react-router'
import Routes from './Routes'
import NavBar from 'components/NavBar'
import FooterBar from 'components/Footer'

import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <NavBar/>
      <Routes />
      <FooterBar/>
    </BrowserRouter>
  </StrictMode>,
)
