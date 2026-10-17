import { Link } from 'react-router-dom'
import { useAuth } from 'react-oidc-context'
import '../App.css'

export default function Home() {
  const auth = useAuth()
  const isAuthenticated = auth.isAuthenticated

  return (
    <main className="mibd-home">
      <header className="mibd-home-nav">
        <Link to="/" className="mibd-home-brand" aria-label="Master It By Doing home">
          <img
            className="brand-logo"
            src="/brand/master-it-by-doing.png"
            alt="Master It By Doing"
          />
        </Link>

        <nav className="mibd-home-nav-links" aria-label="Main navigation">
          <a href="#how-it-works">How it works</a>
          <a href="#experience">The experience</a>
          <a href="#mastery">Mastery</a>

          {isAuthenticated ? (
            <>
              <Link className="login-btn" to="/dashboard">Dashboard</Link>
              <button
                className="login-btn"
                type="button"
                onClick={() => void auth.signoutRedirect()}
              >
                Sign out
              </button>
            </>
          ) : (
            <>
              <Link className="login-btn" to="/login">Sign in</Link>
              <Link className="mibd-primary-btn" to="/signup">
                Get started <span>→</span>
              </Link>
            </>
          )}
        </nav>
      </header>

      <section className="mibd-hero">
        <div className="mibd-hero-copy">
          <div className="mibd-eyebrow-pill">
            <span className="mibd-status-dot" />
            Learn by doing, not just watching
          </div>

          <h1>
            Stop studying.
            <br />
            Start <span>mastering.</span>
          </h1>

          <p className="mibd-hero-description">
            Turn your learning goals into practical missions. Build real skills,
            prove what you can do, and advance with evidence of your progress.
          </p>

          <div className="mibd-hero-actions">
            <Link
              className="mibd-primary-btn"
              to={isAuthenticated ? '/dashboard' : '/signup'}
            >
              {isAuthenticated ? 'Continue learning' : 'Start your journey'}
              <span>→</span>
            </Link>
            <a className="mibd-secondary-btn" href="#how-it-works">
              Explore the method <span>↓</span>
            </a>
          </div>

          <div className="mibd-hero-principles">
            <span><b>01</b> Learn</span>
            <span><b>02</b> Build</span>
            <span><b>03</b> Prove</span>
            <span><b>04</b> Advance</span>
          </div>
        </div>

        <div className="mibd-hero-art" aria-label="A preview of the learning dashboard">
          <div className="mibd-art-glow" />
          <div className="mibd-art-orbit mibd-art-orbit-one" />
          <div className="mibd-art-orbit mibd-art-orbit-two" />

          <div className="mibd-art-label">
            <span className="mibd-art-label-icon">✦</span>
            Your next level starts here
          </div>

          <div className="mibd-product-window">
            <div className="mibd-window-bar">
              <div className="mibd-window-dots"><i /><i /><i /></div>
              <span className="mibd-window-mark">MASTER IT BY DOING</span>
            </div>

            <img
              className="mibd-product-image"
              src="/images/dashboard/ms_04.jpg"
              alt="Real Master It By Doing dashboard screenshot"
            />

            <div className="mibd-image-caption">
              <div>
                <span className="mibd-caption-indicator" />
                <span>Learn through real practice</span>
              </div>
              <span className="mibd-caption-arrow">↗</span>
            </div>
          </div>

          <div className="mibd-floating-note mibd-floating-note-top">
            <span className="mibd-note-icon mibd-note-violet">✦</span>
            <div>
              <strong>Practice with purpose</strong>
              <small>Every mission moves you forward</small>
            </div>
          </div>

          <div className="mibd-floating-note mibd-floating-note-bottom">
            <span className="mibd-note-icon mibd-note-amber">✓</span>
            <div>
              <strong>Prove your skills</strong>
              <small>Build evidence, not just notes</small>
            </div>
          </div>
        </div>
      </section>

      <section className="mibd-principle-strip" aria-label="Our learning principles">
        <p>Progress you can demonstrate</p>
        <div>
          <span>Practical missions</span>
          <span>Adaptive learning</span>
          <span>Independent challenges</span>
          <span>Portfolio evidence</span>
        </div>
      </section>

      <section className="mibd-journey" id="how-it-works">
        <div className="mibd-section-intro">
          <span className="mibd-section-kicker">THE METHOD</span>
          <h2>From learning something to <span>doing it well.</span></h2>
          <p>
            A structured learning loop that helps you move from a goal to
            demonstrated ability, one practical step at a time.
          </p>
        </div>

        <div className="mibd-journey-grid">
          <article className="mibd-journey-card">
            <div className="mibd-step-top">
              <span className="mibd-step-symbol">◎</span>
              <span>01 / GOAL</span>
            </div>
            <h3>Choose your goal</h3>
            <p>Set a clear direction and select the skill you want to develop.</p>
          </article>

          <article className="mibd-journey-card">
            <div className="mibd-step-top">
              <span className="mibd-step-symbol">⌁</span>
              <span>02 / ASSESS</span>
            </div>
            <h3>Find your level</h3>
            <p>Start from your current ability instead of following a one-size-fits-all path.</p>
          </article>

          <article className="mibd-journey-card">
            <div className="mibd-step-top">
              <span className="mibd-step-symbol">⌘</span>
              <span>03 / MISSION</span>
            </div>
            <h3>Learn by building</h3>
            <p>Work through practical missions that turn concepts into applied skills.</p>
          </article>

          <article className="mibd-journey-card">
            <div className="mibd-step-top">
              <span className="mibd-step-symbol">↗</span>
              <span>04 / ADAPT</span>
            </div>
            <h3>Improve with feedback</h3>
            <p>Use evaluation and targeted practice to work on what needs improvement.</p>
          </article>

          <article className="mibd-journey-card">
            <div className="mibd-step-top">
              <span className="mibd-step-symbol">✦</span>
              <span>05 / MASTER</span>
            </div>
            <h3>Demonstrate mastery</h3>
            <p>Show what you can do through independent challenges and portfolio evidence.</p>
          </article>
        </div>
      </section>

      <section className="mibd-experience" id="experience">
        <div className="mibd-experience-copy">
          <span className="mibd-section-kicker">BUILT FOR REAL PROGRESS</span>
          <h2>Don't just collect lessons. <span>Build capability.</span></h2>
          <p>
            Master It By Doing is designed around the work you can complete,
            the feedback you can act on, and the skills you can demonstrate.
          </p>

          <ul className="mibd-feature-list">
            <li><span>✓</span> Skill-focused learning paths</li>
            <li><span>✓</span> Hands-on missions and practice</li>
            <li><span>✓</span> Feedback that guides your next step</li>
            <li><span>✓</span> Progress and achievement evidence</li>
          </ul>

          <Link
            className="mibd-text-link"
            to={isAuthenticated ? '/dashboard' : '/signup'}
          >
            {isAuthenticated ? 'Return to your dashboard' : 'Start building your skills'}
            <span>→</span>
          </Link>
        </div>

        <div className="mibd-experience-visual">
          <div className="mibd-experience-glow" />
          <div className="mibd-experience-frame">
            <div className="mibd-experience-frame-top">
              <span><i className="mibd-frame-dot" /> PRODUCT PREVIEW</span>
              <span>LEARN / BUILD / PROVE</span>
            </div>

            <img
              className="mibd-experience-image"
              src="/images/dashboard/ms_05.jpg"
              alt="Real Master It By Doing mission experience screenshot"
              loading="lazy"
            />

            <div className="mibd-experience-frame-bottom">
              <span>Designed around practice</span>
              <span>✦</span>
            </div>
          </div>

          <div className="mibd-experience-stamp">
            <span>THE OUTCOME</span>
            <b>Skills you can show.</b>
          </div>
        </div>
      </section>

      <section className="mibd-mastery" id="mastery">
        <div className="mibd-mastery-heading">
          <span className="mibd-section-kicker">YOUR PROGRESS, MADE VISIBLE</span>
          <h2>Every step should <span>take you further.</span></h2>
          <p>Practice, test your ability, and keep evidence of the work you accomplish.</p>
        </div>

        <div className="mibd-mastery-grid">
          <article className="mibd-mastery-card">
            <span className="mibd-mastery-icon mibd-icon-violet">⌘</span>
            <span className="mibd-card-overline">LEARN BY DOING</span>
            <h3>Practical missions</h3>
            <p>Build projects and solve skill-specific tasks instead of relying on passive study alone.</p>
          </article>

          <article className="mibd-mastery-card mibd-mastery-card-featured">
            <span className="mibd-mastery-icon mibd-icon-amber">⚡</span>
            <span className="mibd-card-overline">PROVE YOUR ABILITY</span>
            <h3>Boss Fight challenges</h3>
            <p>Take on independent assessments to demonstrate what you can do beyond a guided mission.</p>
          </article>

          <article className="mibd-mastery-card">
            <span className="mibd-mastery-icon mibd-icon-white">✦</span>
            <span className="mibd-card-overline">SHOW YOUR WORK</span>
            <h3>Portfolio evidence</h3>
            <p>Keep a record of your completed work and achievements as you advance your skills.</p>
          </article>
        </div>
      </section>

      <section className="mibd-final-cta">
        <div className="mibd-cta-decoration" />
        <span className="mibd-section-kicker">YOUR NEXT LEVEL IS A PRACTICE AWAY</span>
        <h2>Ready to turn effort into <span>mastery?</span></h2>
        <p>Choose a skill. Take on a mission. Build something you can prove.</p>
        <Link
          className="mibd-primary-btn mibd-cta-button"
          to={isAuthenticated ? '/dashboard' : '/signup'}
        >
          {isAuthenticated ? 'Continue your journey' : 'Start learning today'}
          <span>→</span>
        </Link>
      </section>

      <footer className="mibd-home-footer">
        <Link to="/" className="mibd-footer-brand">
          <img src="/brand/master-it-by-doing.png" alt="" />
          <span>Master It By Doing</span>
        </Link>
        <p>Learn. Build. Prove. Advance.</p>
        <a href="#how-it-works">Back to the method ↑</a>
      </footer>
    </main>
  )
}
