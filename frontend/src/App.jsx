import { useState, useRef } from 'react'
import axios from 'axios'

const TOOL_ICONS = {
  navigate: '🌐',
  search_google: '🔍',
  get_page_content: '📄',
  click_link: '🖱️',
  extract_data: '⚡',
  finish: '✅',
}

const EXAMPLE_GOALS = [
  "Find the current Bitcoin price on CoinGecko",
  "Get today's top 5 HackerNews stories with their URLs",
  "Find the weather forecast for London this week",
  "Find the cheapest iPhone 16 on Amazon UK",
  "Get the latest headlines from BBC News",
]

function formatInput(input) {
  if (!input || typeof input !== 'object') return String(input || '')
  const entries = Object.entries(input)
  if (entries.length === 0) return '(no params)'
  return entries.map(([k, v]) => `${k}: ${typeof v === 'string' ? v : JSON.stringify(v)}`).join(' | ')
}

function StepItem({ step, index }) {
  const [expanded, setExpanded] = useState(index < 3)
  const toolKey = step.tool || 'navigate'

  return (
    <div className="step-item" style={{ animationDelay: `${index * 0.06}s` }}>
      <div className={`step-icon tool-${toolKey}`}>
        {TOOL_ICONS[toolKey] || '🔧'}
      </div>
      <div className="step-body">
        <div className="step-meta">
          <span className="step-num">#{step.step_num}</span>
          <span className={`step-tool-name tool-badge-${toolKey}`}>{toolKey}</span>
          <button
            onClick={() => setExpanded(e => !e)}
            style={{
              marginLeft: 'auto',
              background: 'none',
              border: 'none',
              color: 'var(--text-muted)',
              cursor: 'pointer',
              fontSize: '12px',
              padding: '2px 6px',
            }}
          >
            {expanded ? '▲' : '▼'}
          </button>
        </div>

        {step.thought && (
          <div className="step-thought">{step.thought.slice(0, 200)}{step.thought.length > 200 ? '…' : ''}</div>
        )}

        <div className="step-input">
          → {formatInput(step.input)}
        </div>

        {expanded && step.output && (
          <div className="step-output">{step.output}</div>
        )}
      </div>
    </div>
  )
}

function ScreenshotCarousel({ screenshots }) {
  const [modal, setModal] = useState(null)

  if (!screenshots || screenshots.length === 0) return null

  return (
    <div className="screenshots-section">
      <div className="steps-header">
        <h2>Screenshots</h2>
        <span className="steps-count">{screenshots.length}</span>
      </div>
      <div className="screenshots-scroll">
        {screenshots.map((src, i) => (
          <div key={i} className="screenshot-thumb" onClick={() => setModal(src)}>
            <img src={`data:image/png;base64,${src}`} alt={`Step ${i + 1}`} />
            <div className="screenshot-label">Screenshot {i + 1}</div>
          </div>
        ))}
      </div>

      {modal && (
        <div className="modal-overlay" onClick={() => setModal(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setModal(null)}>✕ Close</button>
            <img src={`data:image/png;base64,${modal}`} alt="Screenshot" />
          </div>
        </div>
      )}
    </div>
  )
}

export default function App() {
  const [goal, setGoal] = useState('')
  const [maxSteps, setMaxSteps] = useState(10)
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const abortRef = useRef(null)

  const sliderPct = ((maxSteps - 5) / (20 - 5)) * 100

  async function handleRun() {
    if (!goal.trim() || running) return
    setRunning(true)
    setResult(null)
    setError(null)

    try {
      const response = await axios.post('/run', {
        goal: goal.trim(),
        max_steps: maxSteps,
      }, {
        timeout: 300000, // 5 min
      })
      setResult(response.data)
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Unknown error'
      setError(detail)
    } finally {
      setRunning(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) handleRun()
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-icon">🕷️</div>
        <div className="header-text">
          <h1>Autonomous Web Scraping Agent</h1>
          <p>Natural language goals → multi-step browser execution</p>
        </div>
        <div className="header-badges">
          <span className="badge badge-purple">Claude Tool Use</span>
          <span className="badge badge-cyan">Playwright</span>
          <span className="badge badge-green">FastAPI</span>
        </div>
      </header>

      <main className="main">
        {/* Input */}
        <div className="input-section">
          <div className="section-label">Goal</div>

          <textarea
            className="goal-textarea"
            placeholder="e.g. Find the current Bitcoin price on CoinGecko"
            value={goal}
            onChange={e => setGoal(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={3}
            disabled={running}
          />

          <div>
            <div className="section-label" style={{ marginBottom: 10 }}>Examples</div>
            <div className="example-chips">
              {EXAMPLE_GOALS.map(g => (
                <button
                  key={g}
                  className="chip"
                  onClick={() => setGoal(g)}
                  disabled={running}
                >
                  {g}
                </button>
              ))}
            </div>
          </div>

          <div className="controls-row">
            <div className="slider-group">
              <span className="slider-label">Max Steps</span>
              <input
                type="range"
                min={5}
                max={20}
                value={maxSteps}
                className="slider"
                style={{ '--pct': `${sliderPct}%` }}
                onChange={e => setMaxSteps(Number(e.target.value))}
                disabled={running}
              />
              <span className="slider-value">{maxSteps}</span>
            </div>

            <button
              className="run-btn"
              onClick={handleRun}
              disabled={running || !goal.trim()}
            >
              {running ? '⏳ Running…' : '▶ Run Agent'}
            </button>
          </div>
        </div>

        {/* Status bar */}
        {(running || result || error) && (
          <div className="status-bar">
            {running ? (
              <>
                <div className="spinner" />
                <div className="status-dot running" />
                <span className="status-text">Agent executing… (Ctrl+meta+Enter to submit again)</span>
                <span className="status-steps">up to {maxSteps} steps</span>
              </>
            ) : error ? (
              <>
                <div className="status-dot error" />
                <span className="status-text">Error occurred</span>
              </>
            ) : result ? (
              <>
                <div className="status-dot done" />
                <span className="status-text">
                  {result.success ? '✓ Completed successfully' : '⚠ Finished with issues'}
                </span>
                <span className="status-steps">{result.total_steps} steps</span>
              </>
            ) : null}
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="error-notice">
            ✕ {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <>
            {/* Final result */}
            <div className="result-section">
              <div className={`result-card ${result.success ? '' : 'error'}`}>
                <div className="result-header">
                  <span className="result-icon">{result.success ? '✅' : '⚠️'}</span>
                  <h3>Result</h3>
                  <span className={`result-badge ${result.success ? 'success' : 'failure'}`}>
                    {result.success ? 'Success' : 'Partial'}
                  </span>
                </div>
                <p className="result-text">{result.result}</p>
              </div>
            </div>

            {/* Steps */}
            {result.steps && result.steps.length > 0 && (
              <div className="steps-section">
                <div className="steps-header">
                  <h2>Execution Steps</h2>
                  <span className="steps-count">{result.steps.length}</span>
                </div>
                <div className="timeline">
                  {result.steps.map((step, i) => (
                    <StepItem key={i} step={step} index={i} />
                  ))}
                </div>
              </div>
            )}

            {/* Screenshots */}
            {result.screenshots && result.screenshots.length > 0 && (
              <ScreenshotCarousel screenshots={result.screenshots} />
            )}
          </>
        )}

        {/* Empty state */}
        {!running && !result && !error && (
          <div className="empty-state">
            <div className="empty-icon">🕷️</div>
            <p>Enter a natural language goal above and the agent will plan and execute browser actions to complete it.</p>
          </div>
        )}
      </main>

      <footer className="footer">
        <span>Autonomous Web Scraping Agent</span>
        <span>·</span>
        <span>Playwright + Claude Tool Use + FastAPI</span>
      </footer>
    </div>
  )
}
