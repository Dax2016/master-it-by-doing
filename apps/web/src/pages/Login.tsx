import { useAuth } from 'react-oidc-context'
import { Link, Navigate } from 'react-router-dom'

function Login() {
  const auth = useAuth()

  if (auth.isLoading) {
    return <p>Loading...</p>
  }

  if (auth.isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return (
    <main className="auth-page auth-page--split">
      <div className="auth-layout">
        <aside className="auth-visual">
          <img
            src="/images/auth/auth-learning-visual-ms_01.jpg"
            alt="A visual representation of learning through practice"
          />
          <div className="auth-visual-copy">
            <span className="auth-visual-kicker">LEARN BY DOING</span>
            <h2>Your next skill starts with your next action.</h2>
            <p>Learn. Build. Prove. Advance.</p>
          </div>
        </aside>

        <section className="auth-card auth-content">
          <Link to="/" className="auth-brand">
            <img
              src="/brand/master-it-by-doing.png"
              alt="Master It By Doing"
            />
            <span>Master It By Doing</span>
          </Link>

          <span className="auth-form-kicker">WELCOME BACK</span>
          <h1>Continue mastering</h1>
          <p>Sign in and pick up where your learning journey left off.</p>

          {auth.error && (
            <p className="auth-error" role="alert">
              Authentication error: {auth.error.message}
            </p>
          )}

          <button
            type="button"
            className="primary-btn auth-submit"
            onClick={() => auth.signinRedirect()}
          >
            Sign in with Cognito
          </button>

          <p className="auth-footer">
            New to the journey? <Link to="/signup">Create an account</Link>
          </p>
        </section>
      </div>
    </main>
  )
}

export default Login
