import { Link } from 'react-router-dom'
import { useAuth } from 'react-oidc-context'
import '../App.css'

export default function Home() {
  const auth = useAuth()

  return (
    <main className="app">
      <nav className="navbar">
        <Link to="/" className="brand">
          <img
            src="/brand/master-it-by-doing.png"
            alt="Master It By Doing"
            className="brand-logo"
          />
          <span>Master It By Doing</span>
        </Link>

        <div className="nav-links">
          <a href="#how-it-works">How it works</a>
          <a href="#missions">Missions</a>
          <a href="#about">About</a>

          {auth.isAuthenticated ? (
            <>
              <Link to="/dashboard" className="login-btn">
                Dashboard
              </Link>

              <button
                type="button"
                className="login-btn"
                onClick={() => auth.signoutRedirect()}
              >
                Sign out
              </button>
            </>
          ) : (
            <Link to="/login" className="login-btn">
              Sign in
            </Link>
          )}
        </div>
      </nav>

      <section className="hero-section">
        <div className="hero-content">
          <div className="badge">⚡ Learn by doing</div>

          <h1>
            Stop studying.
            <br />
            <span>Start mastering.</span>
          </h1>

          <p className="hero-description">
            Master It By Doing turns your learning goal into practical
            missions, evaluates what you actually do, and adapts your
            next challenge until you truly master the skill.
          </p>

          <div className="hero-actions">
            <Link
              to={auth.isAuthenticated ? '/dashboard' : '/signup'}
              className="primary-btn"
            >
              {auth.isAuthenticated ? 'Continue learning' : 'Start learning'}
            </Link>

            <a href="#how-it-works" className="secondary-btn">
              Explore how it works →
            </a>
          </div>
        </div>

        <div className="hero-visual">
          <div className="learning-card">
            <div className="card-header">
              <span>Your current mission</span>
              <span className="status">ACTIVE</span>
            </div>

            <h3>Build a REST API with Python</h3>

            <p>
              Create an API that allows users to create, read, update,
              and delete learning resources.
            </p>

            <div className="progress-label">
              <span>Mission progress</span>
              <strong>72%</strong>
            </div>

            <div className="progress-bar">
              <div className="progress-fill" />
            </div>

            <div className="mission-footer">
              <span>3 tasks remaining</span>

              <Link to="/mission/1">
                Continue →
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section id="how-it-works" className="loop-section">
        <div className="section-heading">
          <span className="eyebrow">THE CORE LOOP</span>

          <h2>
            Knowledge is not mastery.
            <br />
            <span>Doing is.</span>
          </h2>

          <p>
            Master It By Doing closes the gap between understanding
            something and actually being able to do it.
          </p>
        </div>

        <div className="loop-grid">
          <article>
            <span className="step-number">01</span>
            <h3>Goal</h3>
            <p>Define what you want to master.</p>
          </article>

          <article>
            <span className="step-number">02</span>
            <h3>Assess</h3>
            <p>Discover what you can actually do.</p>
          </article>

          <article>
            <span className="step-number">03</span>
            <h3>Mission</h3>
            <p>Practice through real-world challenges.</p>
          </article>

          <article>
            <span className="step-number">04</span>
            <h3>Adapt</h3>
            <p>Your AI coach adjusts what comes next.</p>
          </article>

          <article>
            <span className="step-number">05</span>
            <h3>Master</h3>
            <p>Prove consistent ability.</p>
          </article>
        </div>
      </section>
    </main>
  )
}

