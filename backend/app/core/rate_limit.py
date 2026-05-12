"""Rate-limiting centralise pour les endpoints sensibles.

Pourquoi ?
==========
Sans rate-limit, trois familles d'attaques sont triviales :

1. **Brute-force login** : `/auth/login` accepte 1000 essais/seconde sur le
   meme compte. Un attaquant peut tester un dictionnaire de mots de passe.

2. **Budget OpenAI epuise** : `/tutor/sessions/{id}/ask` et
   `/quiz-ai/generate` appellent l'API OpenAI a chaque requete. Un utilisateur
   (ou un bot) peut envoyer 1000 questions en 30 secondes et faire exploser
   la facture en mode demo. Avec gpt-4o-mini a ~$0.15/M tokens, c'est
   theoriquement de l'ordre de quelques dollars, mais sur un quota Free Tier
   on bloque tout le projet en quelques minutes.

3. **Spam d'emails** : `/auth/forgot-password` et `/auth/request-verification`
   declenchent un envoi SMTP. Sans limite, on peut harceler n'importe quelle
   adresse email (et faire blacklister notre relais Gmail).

Strategie
=========
On utilise `slowapi`, fork moderne de Flask-Limiter pour ASGI/FastAPI.
- Backend : in-memory (suffisant pour une seule instance backend FastAPI).
  Pour un deploiement multi-replicas il faudra passer a Redis :
  `Limiter(storage_uri="redis://...")`.
- Cle : IP du client (`get_remote_address`). Comportement standard ;
  un utilisateur authentifie pourrait avoir une cle "user_id" mais pour
  les endpoints non-authentifies (`/auth/login`) c'est l'IP qui s'impose.

Quotas
======
Volontairement genereux pour ne pas casser les tests E2E ni la demo, mais
suffisants pour bloquer les attaques :

  AUTH_LOGIN          10/minute  (un humain n'essaie pas 10 mdp/min)
  AUTH_EMAIL          3/minute   (un email transactionnel par 20s suffit)
  LLM_HEAVY           20/minute  (max ~$0.10/min sur gpt-4o-mini)
  LLM_LIGHT           60/minute  (quiz statiques, peu chers)

Si tu vois ces quotas etre depasses pendant le user study en prod,
augmente-les ici plutot que de retirer le decorateur.
"""
from __future__ import annotations

import os

from slowapi import Limiter
from slowapi.util import get_remote_address

# ============================================================
# Activation conditionnelle du rate-limiting
# ============================================================
# En production : actif (defense brute-force + budget OpenAI).
# En tests pytest : on desactive pour ne pas saturer le quota apres 10
# tests qui font /auth/login. Le TestClient utilise toujours la meme IP
# fictive "testclient", donc TOUS les tests partagent le meme bucket.
#
# Pour desactiver, mettre dans le shell ou .env :
#     RATE_LIMIT_ENABLED=false
#
# Le conftest.py des tests set cette env var avant d'importer l'app.
_enabled = os.environ.get("RATE_LIMIT_ENABLED", "true").lower() != "false"

# Singleton : un seul Limiter pour toute l'app, importable depuis chaque router.
# default_limits=[] : pas de limite par defaut sur les routes non decorees,
# on opt-in explicitement sur les endpoints qui en ont besoin.
limiter = Limiter(key_func=get_remote_address, default_limits=[], enabled=_enabled)

# Quotas exportes comme constantes pour rester DRY et faciliter l'audit.
AUTH_LOGIN_LIMIT = "10/minute"
AUTH_EMAIL_LIMIT = "3/minute"
LLM_HEAVY_LIMIT = "20/minute"
LLM_LIGHT_LIMIT = "60/minute"
