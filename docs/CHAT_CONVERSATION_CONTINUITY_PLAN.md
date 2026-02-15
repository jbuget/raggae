# Plan d'implémentation - Continuité conversationnelle LLM

## Objectif

Garantir que chaque réponse LLM est produite à partir d'un contexte conversationnel réel (historique + contexte documentaire), et non d'un message isolé.

## Résultats attendus

- Une conversation conserve son état d'un message à l'autre.
- Le backend injecte un historique utile avant appel LLM.
- Le client réutilise systématiquement le `conversation_id`.
- Les tests prouvent la continuité.

## Phase 1 - Contrat API et session

- [ ] Exiger un `conversation_id` après le premier message.
- [ ] Créer explicitement une nouvelle conversation uniquement quand demandé.
- [ ] Vérifier ownership strict (`project_id`, `user_id`, `conversation_id`) à chaque requête.
- [ ] Ajouter logs structurés: `project_id`, `user_id`, `conversation_id`, `message_id`.

Critères d'acceptation:
- Un message sans `conversation_id` sur une session existante ne continue pas implicitement une autre conversation.
- Un `conversation_id` d'un autre user/projet est refusé (404/403 selon convention API).

## Phase 2 - Construction de contexte LLM

- [ ] Charger les `N` derniers messages de la conversation (user + assistant).
- [ ] Construire un prompt structuré en 4 sections:
  1. instructions système projet
  2. historique conversation
  3. contexte RAG (chunks)
  4. message utilisateur courant
- [ ] Appliquer une politique de budget tokens (truncate oldest-first).
- [ ] Séparer clairement mémoire conversationnelle et contexte documentaire.

Critères d'acceptation:
- Les réponses à des références anaphoriques ("ça", "le précédent") restent cohérentes.
- Le prompt final respecte la limite de tokens configurée.

## Phase 3 - Mémoire longue

- [ ] Générer périodiquement un `conversation_summary` (ex: toutes les 10 interactions).
- [ ] Stocker le résumé en base.
- [ ] Injecter `summary + derniers messages` plutôt que l'historique complet quand nécessaire.

Critères d'acceptation:
- Continuité conservée sur conversations longues sans explosion du coût token.

## Phase 4 - Observabilité

- [ ] Exposer en réponse (ou debug interne) :
  - `history_messages_used`
  - `chunks_used`
  - `retrieval_strategy_used`
  - `retrieval_execution_time_ms`
- [ ] Ajouter métriques:
  - taille moyenne d'historique injecté
  - taux de réponses "décorrélées" (heuristique/feedback)
  - latence p95 de génération

Critères d'acceptation:
- Diagnostic possible en prod d'une réponse décorrélée.

## Phase 5 - Tests

### Unit tests

- [ ] Use case chat: injection correcte de l'historique.
- [ ] Sélection de fenêtre d'historique selon budget.
- [ ] Fallback summary quand l'historique est trop long.

### Integration tests

- [ ] Repositories conversation/messages: ordre chronologique, pagination, latest message.
- [ ] Persistance/lecture du `conversation_summary`.

### E2E tests

- [ ] Scénario 3 tours de conversation cohérents.
- [ ] Scénario négatif sans `conversation_id` (pas de continuité).
- [ ] Scénario de sécurité cross-user/cross-project.

Critères d'acceptation:
- Les scénarios de continuité passent de façon déterministe.

## Découpage proposé (tickets)

- [ ] `feat(api): enforce conversation session contract`
- [ ] `feat(chat): inject conversation history into llm prompt`
- [ ] `feat(chat): add token budget windowing`
- [ ] `feat(chat): persist and use conversation summary`
- [ ] `feat(obs): add chat context observability fields`
- [ ] `test(e2e): add multi-turn continuity scenarios`

## Ordre de réalisation recommandé

1. Contrat session + sécurité
2. Injection historique + tests unitaires
3. Budget tokens
4. Résumé conversation
5. Observabilité et E2E de non-régression
