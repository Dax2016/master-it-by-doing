import { useAuth } from 'react-oidc-context'
import { Navigate } from 'react-router-dom'

function Login() {
  const auth = useAuth()

  if (auth.isLoading) {
    return <p>Loading...</p>
  }

  if (auth.isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return (
    <main>
      <h1>Sign in</h1>
      <p>Continue your Master It By Doing journey.</p>

      {auth.error && (
        <p role="alert">
          Authentication error: {auth.error.message}
        </p>
      )}

      <button onClick={() => auth.signinRedirect()}>
        Sign in with Cognito
      </button>
    </main>
  )
}

export default Login