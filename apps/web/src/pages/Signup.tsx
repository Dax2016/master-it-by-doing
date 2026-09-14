import { Link } from 'react-router-dom'

export default function Signup() {
  return (
    <main className="auth-page">
      <div className="auth-card">
        <Link to="/" className="auth-brand">
          <img
            src="/brand/master-it-by-doing.png"
            alt="Master It By Doing"
          />
          <span>Master It By Doing</span>
        </Link>

        <h1>Start mastering</h1>

        <p>
          Create your account and begin learning through action.
        </p>

        <form>
          <label>
            Name
            <input
              type="text"
              placeholder="Your name"
            />
          </label>

          <label>
            Email
            <input
              type="email"
              placeholder="you@example.com"
            />
          </label>

          <label>
            Password
            <input
              type="password"
              placeholder="Create a password"
            />
          </label>

          <button type="submit" className="primary-btn">
            Create account
          </button>
        </form>

        <p className="auth-footer">
          Already have an account?{' '}
          <Link to="/login">Sign in</Link>
        </p>
      </div>
    </main>
  )
}