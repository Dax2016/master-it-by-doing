import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { AuthProvider } from 'react-oidc-context'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.tsx'

const cognitoAuthConfig = {
  authority:
    'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_9mlfOgAbA',
  client_id: '3mkbt1dhustt0lc91q3cp3d7cb',
  redirect_uri: 'http://localhost:5173/',
  response_type: 'code',
  scope: 'email openid phone',
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider
      {...cognitoAuthConfig}
      onSigninCallback={() => {
        window.history.replaceState(
          {},
          document.title,
          window.location.pathname + window.location.hash,
        )
      }}
    >
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </AuthProvider>
  </StrictMode>,
)
