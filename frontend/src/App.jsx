import { useEffect, useMemo, useState } from 'react'

const highlightMetrics = [
  { value: '7', label: 'workflows prêts à tester' },
  { value: '1', label: 'guide PDF à télécharger' },
  { value: '1', label: 'édition réelle pour voir le ton' },
]

const proofPoints = [
  'Pas de jargon inutile. Des workflows lisibles, à exécuter.',
  'Un angle concret : quoi faire lundi matin, pas quoi penser un jour.',
  'Le format newsletter sert à choisir vite, pas à surcharger.',
]

const workflowCards = [
  {
    title: 'Capter le bon angle',
    text: 'Repérer le sujet qui mérite une publication, un test ou une relance commerciale.',
  },
  {
    title: 'Structurer le livrable',
    text: 'Transformer une idée brute en note claire, séquence, checklist ou email.',
  },
  {
    title: 'Réduire le temps mort',
    text: 'Garder un cadre simple pour aller du point A au point B sans friction.',
  },
  {
    title: 'Tester sans se disperser',
    text: 'Lancer un workflow, mesurer le résultat, puis garder seulement ce qui tient.',
  },
]

const faqs = [
  {
    question: 'C’est pour qui ? ',
    answer:
      'Pour les indépendants, consultants, équipes marketing et opérateurs qui veulent des usages IA utiles, pas une collection de démos.',
  },
  {
    question: 'Je vais recevoir quoi ?',
    answer:
      'Le guide PDF, un email de bienvenue avec lien direct, et des éditions centrées sur des workflows réutilisables.',
  },
  {
    question: 'Je peux arrêter quand je veux ?',
    answer:
      'Oui. Le lien de désinscription est inclus dans les emails envoyés via la stack newsletter.',
  },
]

function App() {
  const [form, setForm] = useState({ email: '', first_name: '', role: '', bottleneck: '' })
  const [status, setStatus] = useState({ state: 'idle', message: '' })
  const [issueExcerpt, setIssueExcerpt] = useState({ loading: true, title: '', bullets: [], raw: '' })

  useEffect(() => {
    let alive = true

    async function loadIssue() {
      try {
        const response = await fetch('/static/newsletter/issue-001.md', { cache: 'no-store' })
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }
        const raw = await response.text()
        const lines = raw
          .split(/\r?\n/)
          .map((line) => line.trim())
          .filter(Boolean)
          .filter((line) => !line.startsWith('#'))

        const paragraphs = lines.slice(0, 5)
        const bullets = paragraphs
          .map((line) => line.replace(/^[-*]\s*/, ''))
          .filter((line) => line.length > 0)
          .slice(0, 3)

        const title = raw.split(/\r?\n/).find((line) => line.trim().startsWith('#'))?.replace(/^#+\s*/, '').trim() || 'Édition 001'

        if (alive) {
          setIssueExcerpt({
            loading: false,
            title,
            bullets: bullets.length ? bullets : paragraphs.slice(0, 3),
            raw,
          })
        }
      } catch {
        if (alive) {
          setIssueExcerpt({
            loading: false,
            title: 'Édition 001',
            bullets: [
              'L’extrait réel sera chargé depuis le fichier markdown servi par le backend.',
              'Le format est prévu pour montrer le ton avant même le téléchargement du guide.',
            ],
            raw: '',
          })
        }
      }
    }

    loadIssue()
    return () => {
      alive = false
    }
  }, [])

  const canSubmit = useMemo(() => form.email.trim().length > 0, [form.email])

  async function handleSubmit(event) {
    event.preventDefault()
    if (!canSubmit) {
      setStatus({ state: 'error', message: 'Entre un email valide pour continuer.' })
      return
    }

    setStatus({ state: 'loading', message: 'Envoi en cours…' })

    try {
      const response = await fetch('/api/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: form.email,
          first_name: form.first_name || null,
          role: form.role || null,
          bottleneck: form.bottleneck || null,
          source: 'landing',
        }),
      })

      const payload = await response.json().catch(() => ({}))

      if (!response.ok) {
        throw new Error(payload.detail || payload.error || 'L’inscription a échoué.')
      }

      setStatus({
        state: 'success',
        message: 'Inscription prise en compte. Vérifie ta boîte mail pour le guide.',
      })
      setForm({ email: '', first_name: '', role: '', bottleneck: '' })
    } catch (error) {
      setStatus({
        state: 'error',
        message: error instanceof Error ? error.message : 'Connexion impossible. Réessaie.',
      })
    }
  }

  return (
    <div className="page-shell">
      <div className="page-grain" aria-hidden="true" />
      <header className="topbar">
        <a className="brand" href="#top">
          <span className="brand-mark">AO</span>
          <span className="brand-text">
            <strong>Atelier Operators</strong>
            <small>newsletter · workflows IA</small>
          </span>
        </a>
        <nav className="topnav" aria-label="Navigation principale">
          <a href="#guide">Guide</a>
          <a href="#edition">Édition 001</a>
          <a href="#faq">FAQ</a>
        </nav>
      </header>

      <main id="top">
        <section className="hero section">
          <div className="hero-copy">
            <p className="eyebrow">Atelier Operators</p>
            <h1>Des workflows IA qui livrent, pas des promesses de démo.</h1>
            <p className="lede">
              Un guide PDF, une édition réelle, et des séquences simples pour passer d’une idée
              floue à un livrable exploitable.
            </p>

            <div className="metric-row" aria-label="Repères rapides">
              {highlightMetrics.map((metric) => (
                <div key={metric.label} className="metric-card">
                  <strong>{metric.value}</strong>
                  <span>{metric.label}</span>
                </div>
              ))}
            </div>

            <div className="proof-list">
              {proofPoints.map((point) => (
                <div className="proof-item" key={point}>
                  <span className="proof-dot" aria-hidden="true" />
                  <p>{point}</p>
                </div>
              ))}
            </div>

            <div className="hero-actions">
              <a className="button button-primary" href="#guide">
                Voir le guide
              </a>
              <a className="button button-secondary" href="#edition">
                Lire l’extrait
              </a>
            </div>
          </div>

          <aside className="hero-panel" aria-label="Aperçu du formulaire d’inscription">
            <div className="panel-header">
              <div>
                <p className="panel-kicker">Email-first</p>
                <h2>Recevoir le guide + suivre l’édition 001</h2>
              </div>
              <span className="panel-chip">Brevo · Resend</span>
            </div>

            <form className="lead-form" onSubmit={handleSubmit}>
              <label>
                <span>Email</span>
                <input
                  type="email"
                  name="email"
                  placeholder="ton@email.fr"
                  value={form.email}
                  onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
                  autoComplete="email"
                  required
                />
              </label>

              <div className="form-grid">
                <label>
                  <span>Prénom</span>
                  <input
                    type="text"
                    name="first_name"
                    placeholder="Adrien"
                    value={form.first_name}
                    onChange={(event) =>
                      setForm((current) => ({ ...current, first_name: event.target.value }))
                    }
                    autoComplete="given-name"
                  />
                </label>

                <label>
                  <span>Rôle</span>
                  <input
                    type="text"
                    name="role"
                    placeholder="Ops, marketing, freelance…"
                    value={form.role}
                    onChange={(event) => setForm((current) => ({ ...current, role: event.target.value }))}
                  />
                </label>
              </div>

              <label>
                <span>Ton principal blocage</span>
                <textarea
                  name="bottleneck"
                  placeholder="Ex. produire plus vite sans perdre la qualité"
                  rows="4"
                  value={form.bottleneck}
                  onChange={(event) =>
                    setForm((current) => ({ ...current, bottleneck: event.target.value }))
                  }
                />
              </label>

              <button className="button button-primary button-submit" type="submit" disabled={!canSubmit || status.state === 'loading'}>
                {status.state === 'loading' ? 'Envoi…' : 'Recevoir le guide'}
              </button>

              <p className={`form-status ${status.state}`} role="status" aria-live="polite">
                {status.message || 'Le guide part par email. Le contenu réel est branché côté backend.'}
              </p>
            </form>
          </aside>
        </section>

        <section className="section split-block" id="guide">
          <div className="section-heading">
            <p className="eyebrow">Le guide</p>
            <h2>Un PDF court, utile, et pensé pour être ouvert aujourd’hui.</h2>
          </div>

          <div className="content-grid">
            <article className="content-card accent-card">
              <p className="card-label">Ce que tu obtiens</p>
              <h3>Le PDF téléchargeable</h3>
              <p>
                Il sert de base pratique : workflows, checklists et séquences prêtes à être
                réutilisées.
              </p>
              <a className="text-link" href="/static/lead-magnet-atelier-operators.pdf" target="_blank" rel="noreferrer">
                Ouvrir le PDF
              </a>
            </article>

            <article className="content-card">
              <p className="card-label">Mode d’usage</p>
              <h3>Choisis un workflow, pas tout le catalogue.</h3>
              <p>
                Le bon usage n’est pas de tout lire. Prends un seul cas, teste-le, puis garde ce qui
                te fait gagner du temps.
              </p>
            </article>

            <article className="content-card">
              <p className="card-label">Ce qu’on évite</p>
              <h3>Les pages pleines de concepts et vides d’exécution.</h3>
              <p>
                Pas de grand discours. Les écrans doivent aider à décider vite et à passer à l’action.
              </p>
            </article>
          </div>
        </section>

        <section className="section edition-section" id="edition">
          <div className="section-heading section-heading-wide">
            <p className="eyebrow">Édition 001</p>
            <h2>Un extrait réel pour montrer le ton avant le téléchargement.</h2>
          </div>

          <div className="edition-layout">
            <article className="edition-card">
              <div className="edition-card-header">
                <span className="panel-chip">Lecture rapide</span>
                <span className="edition-title">{issueExcerpt.loading ? 'Chargement…' : issueExcerpt.title}</span>
              </div>
              <div className="edition-excerpt">
                {issueExcerpt.bullets.map((item, index) => (
                  <p key={`${item}-${index}`}>{item}</p>
                ))}
              </div>
              <div className="edition-actions">
                <a className="button button-secondary" href="/static/newsletter/issue-001.md" target="_blank" rel="noreferrer">
                  Ouvrir l’édition
                </a>
                <a className="text-link" href="/static/lead-magnet-atelier-operators.pdf" target="_blank" rel="noreferrer">
                  Télécharger le guide
                </a>
              </div>
            </article>

            <article className="workflow-stack" aria-label="Ce qui est couvert dans le guide">
              {workflowCards.map((card) => (
                <div className="workflow-card" key={card.title}>
                  <h3>{card.title}</h3>
                  <p>{card.text}</p>
                </div>
              ))}
            </article>
          </div>
        </section>

        <section className="section faq-section" id="faq">
          <div className="section-heading">
            <p className="eyebrow">FAQ</p>
            <h2>Les questions les plus fréquentes, sans détour.</h2>
          </div>

          <div className="faq-list">
            {faqs.map((faq) => (
              <article className="faq-item" key={faq.question}>
                <h3>{faq.question}</h3>
                <p>{faq.answer}</p>
              </article>
            ))}
          </div>
        </section>
      </main>

      <footer className="footer">
        <p>Atelier Operators — workflows IA qui livrent.</p>
        <a href="#top">Retour en haut</a>
      </footer>
    </div>
  )
}

export default App
