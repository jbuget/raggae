# PLAN_IN_PROGRESS.md

> Ce fichier décrit la fonctionnalité en cours de développement.
> Il est mis à jour au début et pendant l'implémentation, puis vidé (remis au template) une fois la PR mergée.
> Il est lu automatiquement par Claude Code à chaque session de travail.

## Fonctionnalité en cours

Refactoring front-end — migration vers Atomic Design strict (vague 5 : organizations)

## Branche Git

```
refactor/atomic-design-organizations
```

## Problème / Contexte

Le front-end mélange des composants à des niveaux d'abstraction différents
dans des dossiers thématiques (`auth/`, `projects/`, `organizations/`, etc.)
sans respecter la hiérarchie Atomic Design. Cela rend difficile la
réutilisation, la lisibilité et la cohérence visuelle.

## Approche choisie

Migration en vagues successives (une branche par domaine), en respectant
TDD (test rouge → vert → refacto) et les Conventional Commits en français.

Hiérarchie cible :

- atoms/      → éléments indivisibles, aucune logique métier
- molecules/  → combinaisons d'atoms, logique locale auto-contenue
- organisms/  → sections composites avec orchestration
- templates/  → pages assemblant des organisms

components/ui/ (shadcn/Radix) n'est pas touché.

## Découpage en tâches atomiques

### Vague 1 — Vue conversation ✅ (PR #83 mergée)

- [x] atom/chat : CopyButton
- [x] atom/chat : StreamingDot
- [x] atom/chat : SourceBadge
- [x] atom/chat : ScrollToBottomButton
- [x] molecule/chat : StreamingIndicator
- [x] molecule/chat : MessageBubble
- [x] molecule/chat : MessageInput
- [x] organism/chat : MessageList
- [x] organism/chat : DocumentPreviewDialog
- [x] organism/chat : SourcesBar
- [x] organism/chat : ChatPanel (orchestrateur)
- [x] Supprimer l'ancien components/chat/ + mettre à jour les pages
- [x] PR mergée

### Vague 2 — Layout ✅ (PR #84 mergée)

- [x] atom/layout : ThemeToggle (depuis layout/theme-toggle.tsx)
- [x] molecule/layout : LocaleSelector (depuis layout/locale-selector.tsx)
- [x] organism/layout : Header (depuis layout/header.tsx)
- [x] Mettre à jour l'import dans app/(dashboard)/layout.tsx
- [x] Supprimer l'ancien components/layout/
- [x] PR mergée

Note : ThemeToggle et LocaleSelector ne sont pas injectés dans UserMenu car ce dernier
utilise des sous-menus DropdownMenuSub (pattern différent). Ils restent disponibles pour
d'autres surfaces (settings page, header alternatif, etc.).

### Vague 3 — Auth ✅ (PR #85 mergée)

- [x] molecule/auth : LoginForm (depuis auth/login-form.tsx, 152 lignes)
- [x] molecule/auth : RegisterForm (depuis auth/register-form.tsx, 118 lignes)
- [x] Supprimer l'ancien components/auth/
- [x] PR mergée

### Vague 4 — Projects ✅ (PR #86 mergée)

- [x] molecule/project : ProjectCard (depuis projects/project-card.tsx)
- [x] molecule/project : SnapshotCard (extrait de project-snapshots-list.tsx)
- [x] organism/project : ProjectList (depuis projects/project-list.tsx)
- [x] organism/project : ProjectSnapshotsList (depuis projects/project-snapshots-list.tsx)
- [x] Supprimer l'ancien components/projects/ (ProjectForm était dead code)
- [x] PR mergée

### Vague 5 — Organizations (branche : refactor/atomic-design-organizations)

- [ ] molecule/organization : UserInvitationsList (depuis organizations/user-invitations-list.tsx, 67 lignes)
- [ ] molecule/organization : OrganizationProfileForm (à extraire de organization-settings.tsx)
- [ ] organism/organization : OrganizationList (depuis organizations/organization-list.tsx, 153 lignes)
- [ ] organism/organization : OrgCredentialsPanel (depuis organizations/org-credentials-panel.tsx, 225 lignes)
- [ ] organism/organization : OrganizationMembersPanel (depuis organizations/organization-members-panel.tsx, 249 lignes)
- [ ] template : OrganizationSettings (depuis organizations/organization-settings.tsx, 248 lignes)
- [ ] Supprimer l'ancien components/organizations/

### Vague 6 — Documents (branche : refactor/atomic-design-documents)

- [ ] molecule/document : DocumentUpload (depuis documents/document-upload.tsx, 164 lignes)
- [ ] molecule/document : DocumentRow (depuis documents/document-row.tsx, 257 lignes — extraire dialogs)
- [ ] Supprimer l'ancien components/documents/

### Vague 7 — Stats (branche : refactor/atomic-design-stats)

- [ ] atom/stats : StatCard (à extraire de stats/stats-page.tsx)
- [ ] template : StatsPage (depuis stats/stats-page.tsx, 201 lignes)
- [ ] Supprimer l'ancien components/stats/

## Décisions prises en cours de route

- components/ui/ (shadcn/Radix) est exclu du refactoring : c'est la librairie UI de base.
- Les anciens répertoires thématiques sont supprimés après migration complète de chaque vague.
- Les tests existants sont mis à jour ou remplacés par de nouveaux tests dans les bons répertoires.
- ThemeToggle et LocaleSelector ne remplacent pas les sous-menus dans UserMenu :
  ce sont des variantes standalone (usage différent).
- Le niveau "template" correspond aux composants-page qui assemblent des organisms sans logique propre.

## Notes

- Vague 5 (Organizations) est la prochaine : UserInvitationsList, OrganizationProfileForm (molecules), OrganizationList/OrgCredentialsPanel/OrganizationMembersPanel (organisms), OrganizationSettings (template).
- document-row.tsx contient deux dialogs imbriqués (preview, delete) à extraire en molecules.
- organization-settings.tsx contient un OrganizationProfileForm inline (67 lignes) à extraire.
