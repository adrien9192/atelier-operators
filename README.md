# Atelier Operators

Asset pack initial pour lancer aujourd'hui une newsletter + communauté orientées workflows IA pour opérateurs français.

## Fichiers
- `index.html` — landing page connectée à l'API locale
- `styles.css` — styles
- `app.py` — backend FastAPI pour inscriptions
- `.env` — clés Brevo + Resend
- `run.sh` — lancement local rapide
- `lead-magnet-atelier-operators.html` — source HTML du pack de départ
- `lead-magnet-atelier-operators.pdf` — PDF téléchargeable
- `newsletter/welcome-email.md` — email de bienvenue
- `newsletter/issue-001.md` — première édition
- `ops/agentmail-inbox.json` — détails de la boîte AgentMail créée
- `data/subscribers.jsonl` — journal local des inscriptions

## Positionnement
Atelier Operators = l'atelier des workflows IA qui livrent.

## Stack actuelle
- Brevo pour la collecte newsletter
- Resend pour les emails transactionnels
- AgentMail pour l'adresse de reply/support
- FastAPI pour servir le site et l'endpoint `/api/subscribe`

## Lancer localement
```bash
cd /root/hermes-workspace/atelier-operators
chmod +x run.sh
./run.sh
```
Puis ouvrir `http://localhost:8030`.

## Comportement actuel
- le formulaire ajoute/maj le contact dans la liste Brevo `Atelier Operators — Newsletter` (id 17)
- un email de bienvenue est tenté via Resend
- une notification admin est tentée vers `adrienlaine91@gmail.com`
- chaque inscription est loggée localement

## Point d'attention
Sans domaine vérifié chez Resend, certains emails transactionnels peuvent être limités. Le backend est prêt ; la délivrabilité augmentera dès qu'un domaine sera branché.
