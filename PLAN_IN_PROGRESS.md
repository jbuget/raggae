# PLAN_IN_PROGRESS.md

> Ce fichier décrit la fonctionnalité en cours de développement.
> Il est mis à jour au début et pendant l'implémentation, puis vidé (remis au template) une fois la PR mergée.
> Il est lu automatiquement par Claude Code à chaque session de travail.

## Fonctionnalité en cours

Refactoring front-end — migration vers Atomic Design strict

## Branche Git

```
refactor/atomic-design-chat-view
```

> La branche couvre la première vague (vue conversation). Les vagues suivantes
> ouvriront chacune leur propre branche depuis `main`.

## Problème / Contexte

Le front-end mélange des composants à des niveaux d'abstraction différents
dans des dossiers thématiques (`auth/`, `projects/`, `organizations/`, etc.)
sans respecter la hiérarchie Atomic Design. Cela rend difficile la
réutilisation, la lisibilité et la cohérence visuelle.

## Approche choisie

Migration en vagues successives (une branche par domaine), en respectant
TDD (test rouge → vert → refacto) et les Conventional Commits en français.

Hiérarchie cible :
```
atoms/      → éléments indivisibles, aucune logique métier
molecules/  → combinaisons d'atoms, logique locale auto-contenue
organisms/  → sections composites avec orchestration
templates/  → pages assemblant des organisms
```

`components/ui/` (shadcn/Radix) n'est pas touché.

## Découpage en tâches atomiques

### Vague 1 — Vue conversation ✅ (branche : refactor/atomic-design-chat-view)

- [x] atom/chat : `CopyButton`
- [x] atom/chat : `StreamingDot`
- [x] atom/chat : `SourceBadge`
- [x] atom/chat : `ScrollToBottomButton`
- [x] molecule/chat : `StreamingIndicator`
- [x] molecule/chat : `MessageBubble`
- [x] molecule/chat : `MessageInput`
- [x] organism/chat : `MessageList`
- [x] organism/chat : `DocumentPreviewDialog`
- [x] organism/chat : `SourcesBar`
- [x] organism/chat : `ChatPanel` (orchestrateur)
- [x] Supprimer l'ancien `components/chat/` + mettre à jour les pages
- [ ] Créer la PR et merger

### Vague 2 — Layout (branche : refactor/atomic-design-layout)

- [ ] atom/layout : `ThemeToggle` (depuis `layout/theme-toggle.tsx`, 23 lignes)
- [ ] atom/layout : `Header` (depuis `layout/header.tsx`, 25 lignes)
- [ ] molecule/layout : `LocaleSelector` (depuis `layout/locale-selector.tsx`, 64 lignes)
- [ ] organism/layout : `MobileSidebar` (depuis `layout/mobile-sidebar.tsx`, 167 lignes)
- [ ] organism/layout : `Sidebar` (depuis `layout/sidebar.tsx`, 378 lignes — à splitter)
- [ ] Supprimer l'ancien `components/layout/`

### Vague 3 — Auth (branche : refactor/atomic-design-auth)

- [ ] molecule/auth : `LoginForm` (depuis `auth/login-form.tsx`, 152 lignes)
- [ ] molecule/auth : `RegisterForm` (depuis `auth/register-form.tsx`, 118 lignes)
- [ ] Supprimer l'ancien `components/auth/`

### Vague 4 — Projects (branche : refactor/atomic-design-projects)

- [ ] atom/project : `ProjectCard` (depuis `projects/project-card.tsx`, 37 lignes)
- [ ] molecule/project : `SnapshotCard` (à extraire de `project-snapshots-list.tsx`)
- [ ] organism/project : `ProjectList` (depuis `projects/project-list.tsx`, 142 lignes)
- [ ] organism/project : `ProjectForm` (depuis `projects/project-form.tsx`, 293 lignes)
- [ ] organism/project : `ProjectSnapshotsList` (depuis `projects/project-snapshots-list.tsx`, 272 lignes)
- [ ] Supprimer l'ancien `components/projects/`

### Vague 5 — Organizations (branche : refactor/atomic-design-organizations)

- [ ] molecule/organization : `UserInvitationsList` (depuis `organizations/user-invitations-list.tsx`, 67 lignes)
- [ ] molecule/organization : `OrganizationProfileForm` (à extraire de `organization-settings.tsx`)
- [ ] organism/organization : `OrganizationList` (depuis `organizations/organization-list.tsx`, 153 lignes)
- [ ] organism/organization : `OrgCredentialsPanel` (depuis `organizations/org-credentials-panel.tsx`, 225 lignes)
- [ ] organism/organization : `OrganizationMembersPanel` (depuis `organizations/organization-members-panel.tsx`, 249 lignes)
- [ ] template : `OrganizationSettings` (depuis `organizations/organization-settings.tsx`, 248 lignes)
- [ ] Supprimer l'ancien `components/organizations/`

### Vague 6 — Documents (branche : refactor/atomic-design-documents)

- [ ] molecule/document : `DocumentUpload` (depuis `documents/document-upload.tsx`, 164 lignes)
- [ ] molecule/document : `DocumentRow` (depuis `documents/document-row.tsx`, 257 lignes — extraire dialogs)
- [ ] Supprimer l'ancien `components/documents/`

### Vague 7 — Stats (branche : refactor/atomic-design-stats)

- [ ] atom/stats : `StatCard` (à extraire de `stats/stats-page.tsx`)
- [ ] template : `StatsPage` (depuis `stats/stats-page.tsx`, 201 lignes)
- [ ] Supprimer l'ancien `components/stats/`

## Structure cible complète

```
components/
├── atoms/
│   ├── chat/         ✅
│   ├── form/         ✅
│   ├── sidebar/      ✅
│   ├── layout/       — header, theme-toggle
│   ├── project/      — project-card
│   └── stats/        — stat-card
│
├── molecules/
│   ├── chat/         ✅
│   ├── sidebar/      ✅
│   ├── auth/         — login-form, register-form
│   ├── document/     — document-upload, document-row
│   ├── layout/       — locale-selector
│   ├── organization/ — user-invitations-list, org-profile-form
│   └── project/      — snapshot-card
│
├── organisms/
│   ├── chat/         ✅
│   ├── sidebar/      ✅
│   ├── layout/       — sidebar, mobile-sidebar
│   ├── project/      — project-list, project-form, project-snapshots-list
│   └── organization/ — org-list, org-credentials-panel, org-members-panel
│
├── templates/        — organization-settings, stats-page
│
└── ui/              ✅ (shadcn/Radix — intouchable)
```

## Décisions prises en cours de route

- `components/ui/` (shadcn/Radix) est exclu du refactoring : c'est la librairie UI de base.
- Les anciens répertoires thématiques sont supprimés après migration complète de chaque vague.
- Les tests existants sont mis à jour ou remplacés par de nouveaux tests dans les bons répertoires.
- Les sous-composants définis en inline dans un fichier (ex : `SnapshotCard`, `StatCard`) sont extraits
  si réutilisables, ou laissés en place s'ils sont purement locaux.
- Le niveau "template" correspond aux composants-page qui assemblent des organisms sans logique propre.

## Notes

- Vague 2 (Layout) est prioritaire car `layout/sidebar.tsx` (378 lignes) est le composant
  le plus volumineux et le plus difficile à maintenir.
- `layout/sidebar.tsx` et `layout/mobile-sidebar.tsx` partagent beaucoup de logique :
  envisager un composant `SidebarContent` partagé lors du refactoring.
- `document-row.tsx` contient deux dialogs imbriqués (preview, delete) à extraire en molecules.
- `organization-settings.tsx` contient un `OrganizationProfileForm` inline (67 lignes) à extraire.
