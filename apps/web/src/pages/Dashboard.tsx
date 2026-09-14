import { Link } from 'react-router-dom'

export default function Dashboard() {
  return (
    <main className="dashboard">
      <header className="dashboard-header">
        <div className="brand">
          <img
            src="/brand/master-it-by-doing.png"
            alt="Master It By Doing"
            className="brand-logo"
          />

          <span>Master It By Doing</span>
        </div>

        <button>Sign out</button>
      </header>

      <section className="dashboard-content">
        <div>
          <span className="eyebrow">YOUR MASTERY JOURNEY</span>

          <h1>
            Welcome back.
          </h1>

          <p>
            Your next challenge is waiting for you.
          </p>
        </div>

        <div className="dashboard-grid">
          <div className="dashboard-card">
            <span>Current goal</span>

            <h2>Python Backend Engineering</h2>

            <p>
              Build production-ready backend applications.
            </p>
          </div>

          <div className="dashboard-card">
            <span>Overall mastery</span>

            <strong className="big-score">68%</strong>

            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: '68%' }}
              />
            </div>
          </div>

          <div className="dashboard-card mission-dashboard-card">
            <span>Current mission</span>

            <h2>Build an authenticated API</h2>

            <p>
              Complete the next practical challenge.
            </p>

            <Link to="/mission/1" className="primary-btn">
              Continue mission →
            </Link>
          </div>
        </div>
      </section>
    </main>
  )
}