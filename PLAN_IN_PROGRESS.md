# PLAN_IN_PROGRESS.md

> Ce fichier décrit la fonctionnalité en cours de développement.
> Il est mis à jour au début et pendant l'implémentation, puis vidé (remis au template) une fois la PR mergée.
> Il est lu automatiquement par Claude Code à chaque session de travail.

## Fonctionnalité en cours

Refactoring front-end — Vague 8 : introduction de la couche Templates (Atomic Design)

## Branche Git

```
refactor/atomic-design-templates
```

## Problème / Contexte

Après les vagues 1–7, la hiérarchie atoms/molecules/organisms est en place, mais la couche
"Template" (Atomic Design) est absente. Cela crée trois incohérences :

1. Certains organisms contiennent des `<h1>` et headers de page (ex. `StatsPage`, `ProjectList`)
   → ils empiètent sur la responsabilité des templates.
2. Certains `page.tsx` contiennent des headers inline (`invitations/page.tsx`, `snapshots/page.tsx`)
   → logique de présentation dans la couche route.
3. Certains `page.tsx` sont monolithiques avec logique + UI (~300 lignes : `settings/page.tsx`,
   `projects/[projectId]/page.tsx`, pages chat).

## Approche choisie

Introduire deux templates génériques réutilisables, puis les appliquer page par page :

### `PageTemplate` — pages "document" (listes, formulaires, settings)
Props : `title`, `description?`, `actions?` (slot boutons CTA), `children`
Layout : barre de titre + contenu scrollable.

### `WorkspaceTemplate` — pages "outil" immersives (chat, éditeur…)
Props : `breadcrumb` (items avec label + href?), `actions?`, `children`
Layout : top bar sticky h-14 + contenu pleine hauteur (overflow géré en interne).

### Règle cardinale
- `page.tsx` : extrait les params URL uniquement, rend un template
- Template : `<h1>`, description, CTAs — reçoit les params de route en props, ne fetche pas
- Organism : fetche ses données, pas de `<h1>` de page

## Découpage en tâches atomiques

### Étape 0 — Templates génériques (branche : refactor/atomic-design-templates)

- [x] docs: documenter PageTemplate / WorkspaceTemplate dans CLAUDE.md et PLAN_IN_PROGRESS.md
- [ ] feat(templates): créer PageTemplate générique + tests
- [ ] feat(templates): créer WorkspaceTemplate générique + tests

### Étape 1 — Pages simples (PageTemplate)

- [ ] refactor(templates/stats): StatsPage → retirer `<header>` de l'organism, créer stats-template
- [ ] refactor(templates/project): ProjectList → retirer `<h1>` de l'organism, créer projects-template
- [ ] refactor(templates/organization): OrganizationList → retirer `<h1>`, créer organizations-template
- [ ] refactor(templates/organization): invitations/page → créer invitations-template
- [ ] refactor(templates/project): snapshots/page → créer project-snapshots-template

### Étape 2 — Pages complexes inline (PageTemplate + nouveaux organisms)

- [ ] refactor(templates/project): projects/[projectId]/page → créer project-detail-template + organism ProjectDetail
- [ ] refactor(templates/settings): settings/page → créer user-settings-template + extraire organisms (UserProfilePanel, UserLocalePanel, UserApiKeysPanel)
- [ ] refactor(templates/organization): invitations/accept/page → créer accept-invitation-template + organism AcceptInvitationContent

### Étape 3 — Pages workspace (WorkspaceTemplate)

- [ ] refactor(templates/project): chat/page + chat/[id]/page → créer chat-template (WorkspaceTemplate)

## Décisions prises

- `PageTemplate` et `WorkspaceTemplate` sont des composants génériques dans `templates/` (pas sous-dossier domaine).
- Les organisms existants qui contiennent des `<h1>` sont refactorés pour les retirer : le header
  appartient au template, pas à l'organism.
- Chaque `page.tsx` devient une coquille ≤ 10 lignes après refactoring.
- TDD strict : test RED → composant → GREEN → nettoyage → commit atomique.

## Vagues précédentes (terminées)

| Vague | Domaine | PR | Statut |
|-------|---------|-----|--------|
| 1 | Chat | #83 | ✅ |
| 2 | Layout | #84 | ✅ |
| 3 | Auth | #85 | ✅ |
| 4 | Projects | #86 | ✅ |
| 5 | Organizations | #87 | ✅ |
| 6 | Documents | #88 | ✅ |
| 7 | Stats | #89 | ✅ |
