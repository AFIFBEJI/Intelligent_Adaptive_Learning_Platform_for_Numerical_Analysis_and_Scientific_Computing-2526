// ============================================================
// Learning Path Page — Visual Progress Map (NEW)
// ============================================================

import { api } from '../api'
import { createNavbar } from '../components/navbar'

export function LearningPathPage(): HTMLElement {
  const container = document.createElement('div')
  const userStr = localStorage.getItem('user')
  const user = userStr ? JSON.parse(userStr) : null
  const token = localStorage.getItem('token')
  if (token) api.setToken(token)

  container.appendChild(createNavbar(user?.nom_complet))

  const main = document.createElement('div')
  main.innerHTML = `
    <style>
      @keyframes slideUp { from{opacity:0;transform:translateY(25px)} to{opacity:1;transform:translateY(0)} }
      @keyframes shimmer { 0%{background-position:-200% 0} 100%{background-position:200% 0} }
      @keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.08)} }
      @keyframes fillBar { from{width:0} to{width:var(--fill)} }

      .path-page { max-width:1000px;margin:0 auto;padding:2rem;position:relative;z-index:1; }
      .page-header { margin-bottom:2rem;animation:slideUp 0.5s ease; }
      .page-title {
        font-size:2rem;font-weight:900;
        background:linear-gradient(135deg,#f1f5f9 0%,#38bdf8 50%,#818cf8 100%);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:0.4rem;
      }
      .page-sub { color:#64748b;font-size:0.9rem; }

      /* Overall progress */
      .overall-bar {
        background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
        border-radius:20px;padding:1.5rem;margin-bottom:2rem;
        backdrop-filter:blur(20px);animation:slideUp 0.5s 0.1s ease both;
      }
      .overall-header { display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem; }
      .overall-label { font-size:0.85rem;font-weight:700;color:#94a3b8;letter-spacing:0.04em; }
      .overall-pct { font-size:1.5rem;font-weight:900;color:#38bdf8; }
      .progress-track { width:100%;height:8px;background:rgba(255,255,255,0.06);border-radius:4px;overflow:hidden; }
      .progress-fill { height:100%;border-radius:4px;background:linear-gradient(90deg,#38bdf8,#818cf8);transition:width 1.5s ease; }
      .overall-stats { display:flex;gap:2rem;margin-top:1rem;flex-wrap:wrap; }
      .overall-stat { font-size:0.8rem;color:#64748b; }
      .overall-stat strong { color:#e2e8f0; }

      /* Module sections */
      .module-section {
        background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.07);
        border-radius:20px;padding:1.5rem;margin-bottom:1.25rem;
        backdrop-filter:blur(20px);animation:slideUp 0.5s ease both;
      }
      .module-header { display:flex;align-items:center;gap:0.75rem;margin-bottom:1.25rem; }
      .module-icon {
        width:42px;height:42px;border-radius:12px;
        display:flex;align-items:center;justify-content:center;
        font-size:1.2rem;flex-shrink:0;
      }
      .mi-blue { background:rgba(14,165,233,0.15);border:1px solid rgba(14,165,233,0.3); }
      .mi-green { background:rgba(52,211,153,0.15);border:1px solid rgba(52,211,153,0.3); }
      .mi-purple { background:rgba(192,132,252,0.15);border:1px solid rgba(192,132,252,0.3); }
      .module-name { font-size:1.1rem;font-weight:800;color:#f1f5f9; }
      .module-count { font-size:0.75rem;color:#64748b;margin-top:0.1rem; }

      /* Concept rows */
      .concept-row {
        display:flex;align-items:center;gap:1rem;
        padding:0.85rem 0;border-bottom:1px solid rgba(255,255,255,0.04);
        transition:all 0.2s;
      }
      .concept-row:last-child { border-bottom:none; }
      .concept-row:hover { transform:translateX(4px); }

      .concept-status {
        width:28px;height:28px;border-radius:50%;
        display:flex;align-items:center;justify-content:center;
        font-size:0.75rem;flex-shrink:0;
      }
      .status-mastered { background:rgba(52,211,153,0.2);border:2px solid #34d399;color:#34d399; }
      .status-progress { background:rgba(251,146,60,0.2);border:2px solid #fb923c;color:#fb923c;animation:pulse 2s infinite; }
      .status-locked { background:rgba(100,116,139,0.15);border:2px solid #475569;color:#475569; }

      .concept-info { flex:1;min-width:0; }
      .concept-name { color:#e2e8f0;font-size:0.88rem;font-weight:600; }
      .concept-prereq { font-size:0.72rem;color:#475569;margin-top:0.1rem; }

      .mastery-bar-wrap { width:120px;height:6px;background:rgba(255,255,255,0.06);border-radius:3px;overflow:hidden;flex-shrink:0; }
      .mastery-bar { height:100%;border-radius:3px;transition:width 1.5s ease; }
      .bar-green { background:linear-gradient(90deg,#22c55e,#34d399); }
      .bar-orange { background:linear-gradient(90deg,#f97316,#fb923c); }
      .bar-gray { background:rgba(100,116,139,0.3); }

      .mastery-pct { font-size:0.78rem;font-weight:700;min-width:40px;text-align:right; }

      /* Action button */
      .action-btn {
        padding:0.35rem 0.8rem;border-radius:8px;font-size:0.72rem;font-weight:700;
        border:none;cursor:pointer;transition:all 0.2s;flex-shrink:0;
      }
      .btn-start { background:rgba(56,189,248,0.15);color:#38bdf8;border:1px solid rgba(56,189,248,0.3); }
      .btn-start:hover { background:rgba(56,189,248,0.25); }
      .btn-review { background:rgba(251,146,60,0.15);color:#fb923c;border:1px solid rgba(251,146,60,0.3); }
      .btn-review:hover { background:rgba(251,146,60,0.25); }

      .empty-state { text-align:center;padding:3rem;color:#475569; }
      .empty-icon { font-size:3rem;margin-bottom:1rem; }

      .skeleton { background:linear-gradient(90deg,rgba(255,255,255,0.05) 25%,rgba(255,255,255,0.1) 50%,rgba(255,255,255,0.05) 75%);background-size:200% 100%;animation:shimmer 1.5s infinite;border-radius:8px; }
      .sk-module { height:200px;border-radius:20px;margin-bottom:1.25rem; }
    </style>

    <div class="path-page">
      <div class="page-header">
        <h1 class="page-title">🗺️ Learning Path</h1>
        <p class="page-sub">Your personalized journey through numerical analysis</p>
      </div>

      <div id="path-content">
        <div class="overall-bar"><div class="skeleton" style="height:80px"></div></div>
        ${[1,2,3].map(_ => `<div class="skeleton sk-module"></div>`).join('')}
      </div>
    </div>
  `

  container.appendChild(main)

  if (!user) return container

  // Load learning path + concepts together
  Promise.all([
    api.getLearningPath(user.id),
    api.getConcepts()
  ]).then(([path, concepts]) => {
    const { total_concepts, mastered, in_progress } = path.overall_progress
    const pct = total_concepts > 0 ? Math.round((mastered / total_concepts) * 100) : 0

    // Build mastery map from path data
    const masteryMap: Record<string, number> = {}
    path.concepts_to_improve.forEach(c => { masteryMap[c.id] = c.mastery })
    // mastered ones = 70+
    // Concepts in next_recommended = 0

    // Group concepts by module
    const modules: Record<string, typeof concepts> = {}
    concepts.forEach(c => {
      const cat = c.category || 'Other'
      if (!modules[cat]) modules[cat] = []
      modules[cat].push(c)
    })

    const moduleColors: Record<string, { icon: string; cls: string; color: string }> = {
      'Interpolation': { icon: '📐', cls: 'mi-blue', color: '#38bdf8' },
      'Numerical Integration': { icon: '∫', cls: 'mi-green', color: '#34d399' },
      'Ordinary Differential Equations (ODEs)': { icon: '📈', cls: 'mi-purple', color: '#c084fc' },
    }

    const getStatus = (conceptId: string) => {
      const m = masteryMap[conceptId]
      if (m !== undefined && m >= 70) return 'mastered'
      if (m !== undefined && m > 0) return 'progress'
      // Check if in next_recommended
      if (path.next_recommended.some(r => r.id === conceptId)) return 'ready'
      return 'locked'
    }

    const getMastery = (conceptId: string) => masteryMap[conceptId] || 0

    const pathContent = main.querySelector('#path-content')!
    pathContent.innerHTML = `
      <div class="overall-bar">
        <div class="overall-header">
          <div class="overall-label">OVERALL MASTERY</div>
          <div class="overall-pct">${pct}%</div>
        </div>
        <div class="progress-track">
          <div class="progress-fill" style="width:${pct}%"></div>
        </div>
        <div class="overall-stats">
          <div class="overall-stat">✅ <strong>${mastered}</strong> mastered</div>
          <div class="overall-stat">🔥 <strong>${in_progress}</strong> in progress</div>
          <div class="overall-stat">📚 <strong>${total_concepts - mastered - in_progress}</strong> to discover</div>
        </div>
      </div>

      ${Object.entries(modules).map(([modName, modConcepts], idx) => {
        const mc = moduleColors[modName] || { icon: '📦', cls: 'mi-blue', color: '#38bdf8' }
        const modMastered = modConcepts.filter(c => getMastery(c.id) >= 70).length

        return `
          <div class="module-section" style="animation-delay:${0.15 * (idx + 1)}s">
            <div class="module-header">
              <div class="module-icon ${mc.cls}">${mc.icon}</div>
              <div>
                <div class="module-name">${modName}</div>
                <div class="module-count">${modMastered}/${modConcepts.length} concepts mastered</div>
              </div>
            </div>
            ${modConcepts.map(c => {
              const status = getStatus(c.id)
              const mastery = getMastery(c.id)
              const statusIcon = status === 'mastered' ? '✓' : status === 'progress' ? '◔' : status === 'ready' ? '○' : '🔒'
              const statusCls = status === 'mastered' ? 'status-mastered' : status === 'progress' ? 'status-progress' : 'status-locked'
              const barCls = mastery >= 70 ? 'bar-green' : mastery > 0 ? 'bar-orange' : 'bar-gray'
              const pctColor = mastery >= 70 ? '#34d399' : mastery > 0 ? '#fb923c' : '#475569'

              return `
                <div class="concept-row">
                  <div class="concept-status ${statusCls}">${statusIcon}</div>
                  <div class="concept-info">
                    <div class="concept-name">${c.name}</div>
                    ${status === 'locked' ? '<div class="concept-prereq">Prerequisites not met</div>' : ''}
                    ${status === 'ready' ? '<div class="concept-prereq" style="color:#38bdf8">Ready to start!</div>' : ''}
                  </div>
                  <div class="mastery-bar-wrap">
                    <div class="mastery-bar ${barCls}" style="width:${mastery}%"></div>
                  </div>
                  <div class="mastery-pct" style="color:${pctColor}">${mastery > 0 ? mastery.toFixed(0) + '%' : '—'}</div>
                  ${status === 'ready' ? '<a href="/quiz" data-link class="action-btn btn-start">Start →</a>' : ''}
                  ${status === 'progress' ? '<a href="/quiz" data-link class="action-btn btn-review">Review</a>' : ''}
                </div>
              `
            }).join('')}
          </div>
        `
      }).join('')}
    `

  }).catch(() => {
    main.querySelector('#path-content')!.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🎯</div>
        <p>Take your first quiz to generate your personalized learning path!</p>
        <a href="/quiz" data-link style="margin-top:1rem;display:inline-block;padding:0.7rem 1.5rem;background:linear-gradient(135deg,#0ea5e9,#6366f1);color:white;border-radius:10px;text-decoration:none;font-weight:700;">Go to Quizzes →</a>
      </div>
    `
  })

  return container
}
