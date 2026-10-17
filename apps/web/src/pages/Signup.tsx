import { Link } from 'react-router-dom'

export default function Signup() {
  return (
    <main className="auth-page auth-page--split">
      <div className="auth-layout">
        <aside className="auth-visual">
          <img
            src="/images/auth/auth-learning-visual-ms_01.jpg"
            alt="A visual representation of learning through practice"
          />
          <div className="auth-visual-copy">
            <span className="auth-visual-kicker">YOUR NEXT CHAPTER</span>
            <h2>Turn what you learn into what you can do.</h2>
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

          <span className="auth-form-kicker">START YOUR JOURNEY</span>
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
        </section>
      </div>
    </main>
  )
}
