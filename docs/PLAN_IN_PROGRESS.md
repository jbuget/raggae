# Refactoring front — Atomic Design (Sidebar)

**Branche** : `refactor/sidebar-atomic-design`  
**Statut** : En cours de planification

---

## Objectif

Réorganiser le code frontend selon les principes d'**Atomic Design** en commençant par la sidebar.  
Cela servira de référence pour la migration progressive des autres parties de l'interface.

---

## Points importants / complexités à anticiper

### 1. Duplication de logique entre `Sidebar` et `MobileSidebar` (priorité haute)

Les deux composants dupliquent intégralement la logique de data fetching :
- `useQueries` pour les projets d'organisations
- `useQueries` pour les membres d'organisations
- Construction de `organizationProjectsMap` et `editableOrganizationIds`
- Tri des organisations

**Solution** : extraire un hook `useSidebarData()` partagé (dans `use-sidebar-data.ts`).  
C'est le gain le plus important — réduction immédiate de ~80 lignes dupliquées.

### 2. Variante desktop vs mobile du `ProjectItem`

Sur desktop : chaque projet a un bouton `MoreVertical` au hover avec un `DropdownMenu` (chat, settings).  
Sur mobile : lien simple sans dropdown.

**Décision validée** : deux composants distincts — `DesktopProjectItem` et `MobileProjectItem`.  
Avantage : chaque composant est plus lisible et évolue indépendamment.

### 3. Section "Mes Projets" vs section "Organisation"

Très similaires mais avec une différence : le bouton `+` de création est toujours affiché pour les projets personnels, conditionnel (role `owner`/`maker`) pour les organisations.

**Décision** : un seul composant `ProjectsSection` avec :
- `title: string`
- `projects: Project[]`
- `canCreate: boolean`
- `createHref: string`
- `showActions?: boolean` (transmis aux `ProjectItem`)

### 4. Structure de dossiers

Pas de convention atomic design existante dans le projet. Proposition :

```
client/src/components/layout/sidebar/
├── atoms/
│   ├── sidebar-logo.tsx          # Lien "Raggae" + styles
│   ├── sidebar-nav-link.tsx      # Lien de navigation avec état actif
│   └── sidebar-section-header.tsx # Titre de section + bouton optionnel
├── molecules/
│   ├── desktop-project-item.tsx  # Lien projet + DropdownMenu (desktop)
│   └── mobile-project-item.tsx   # Lien projet simple (mobile)
├── organisms/
│   ├── sidebar-nav.tsx            # Section de navigation principale
│   ├── projects-section.tsx       # Section de projets (perso ou org)
│   ├── organization-section.tsx   # Section d'une organisation (wraps projects-section)
│   └── user-menu.tsx              # Menu utilisateur du bas (desktop only)
├── use-sidebar-data.ts            # Hook partagé : fetch projets, orgs, membres, permissions
├── sidebar.tsx                    # Sidebar desktop (assemble les organisms)
├── mobile-sidebar.tsx             # Sidebar mobile (assemble les organisms, sans UserMenu)
└── index.ts                       # Re-exports publics
```

**La convention `ui/` reste inchangée** (shadcn/ui, considérés comme atoms du design system).

### 5. Mise à jour des imports existants

Les fichiers suivants importent directement les composants :
- `app/(dashboard)/layout.tsx` → `import { Sidebar } from "@/components/layout/sidebar"`
- `components/layout/header.tsx` → `import { MobileSidebar } from "./mobile-sidebar"`

Ces imports doivent rester valides. **Solutions** :
- `sidebar/index.ts` re-exporte `Sidebar` et `MobileSidebar` → l'import `@/components/layout/sidebar` résoudra sur `sidebar/index.ts`.
- L'import de `MobileSidebar` dans `header.tsx` devra pointer sur `./sidebar/mobile-sidebar` ou `./sidebar`.

### 6. Tests à écrire (TDD)

Chaque composant extrait doit avoir son test. Ordre de priorité :
- **Atoms** : purement visuels/présentationnels → tests simples de rendu (RTL).
- **Molecules** : `ProjectItem` → tester avec/sans `showActions`, état actif/inactif.
- **Organisms** : tester avec des props mockées (pas de vraie API). Le hook `useSidebarData` est mocké.
- **Hook `useSidebarData`** : test isolé avec `renderHook` + MSW ou fakes.

---

## Découpage en tâches

### Branche : `refactor/sidebar-atomic-design`

#### Tâche 1 — Préparer la structure de dossiers
- Créer `client/src/components/layout/sidebar/` avec les sous-dossiers `atoms/`, `molecules/`, `organisms/`
- Créer `sidebar/index.ts` vide (sera rempli au fil des tâches)
- Mettre à jour l'import de `MobileSidebar` dans `header.tsx` en avance pour éviter la régression

#### Tâche 2 — Extraire le hook `useSidebarData`
> TDD : écrire le test d'abord
- Déplacer toute la logique de fetch (projets, organisations, queries d'org, membres, `editableOrganizationIds`) dans `use-sidebar-data.ts`
- Le hook renvoie : `{ projects, isLoadingProjects, sortedOrganizations, organizationProjectsMap, editableOrganizationIds }`
- Tests avec `renderHook` + données mockées

#### Tâche 3 — Atoms
> TDD : écrire les tests d'abord
- **`sidebar-logo.tsx`** : `<SidebarLogo />` — lien vers `/projects` avec le nom "Raggae"
- **`sidebar-nav-link.tsx`** : `<SidebarNavLink href icon label />` — lien avec état actif basé sur `usePathname()`
- **`sidebar-section-header.tsx`** : `<SidebarSectionHeader title canCreate createHref createAriaLabel />` — titre + bouton `+` optionnel

#### Tâche 4 — Molecules : `DesktopProjectItem` et `MobileProjectItem`
> TDD : écrire les tests d'abord
- **`desktop-project-item.tsx`** : `<DesktopProjectItem project canAccessSettings />` — lien tronqué + `DropdownMenu` au hover
- **`mobile-project-item.tsx`** : `<MobileProjectItem project />` — lien simple tronqué
- Tests desktop : état actif, menu visible au hover, item settings conditionnel
- Tests mobile : état actif, rendu sans dropdown

#### Tâche 5 — Organisms
> TDD : écrire les tests d'abord
- **`sidebar-nav.tsx`** : `<SidebarNav />` — liste de `SidebarNavLink` (projets, organisations, invitations)
- **`projects-section.tsx`** : `<ProjectsSection title projects canCreate createHref showActions />` — utilise `SidebarSectionHeader` + liste de `ProjectItem`
- **`organization-section.tsx`** : `<OrganizationSection organization projects canCreate showActions />` — wraps `ProjectsSection`
- **`user-menu.tsx`** : `<UserMenu />` — extrait tel quel du bas de `sidebar.tsx`

#### Tâche 6 — Réécrire `Sidebar` (desktop) et `MobileSidebar`
- `sidebar.tsx` : composition d'organisms + `useSidebarData()`, sans logique propre
- `mobile-sidebar.tsx` : idem, sans `UserMenu`
- `index.ts` : re-exporte `Sidebar` et `MobileSidebar`

#### Tâche 7 — Mettre à jour les imports dans l'app
- `app/(dashboard)/layout.tsx` → vérifier que l'import `@/components/layout/sidebar` fonctionne via `index.ts`
- `components/layout/header.tsx` → mettre à jour l'import de `MobileSidebar`
- Supprimer les anciens fichiers `layout/sidebar.tsx` et `layout/mobile-sidebar.tsx` si déplacés

#### Tâche 8 — Validation
- `npm run build` : zéro erreur TypeScript
- `npm test` : tous les tests passent
- Vérification manuelle dans le navigateur (desktop + mobile)

---

## Décisions

| # | Question | Décision |
|---|----------|----------|
| 1 | Un seul `ProjectItem` avec `showActions` ou deux composants ? | ✅ Deux composants distincts : `DesktopProjectItem` et `MobileProjectItem` |
| 2 | `ProjectsSection` unique ou `PersonalProjectsSection` + `OrganizationSection` distincts ? | ✅ Un seul générique + wrapper `OrganizationSection` |
| 3 | Structure `atoms/molecules/organisms/` ou flat dans `sidebar/` ? | ✅ Sous-dossiers |

---

## Ce qui ne change PAS

- Le rendu visuel et le comportement (refactoring pur, pas de redesign)
- Le hook `useAuth`, `useProjects`, `useOrganizations` (ils restent dans `lib/hooks/`)
- Les composants shadcn/ui dans `components/ui/` (atoms du design system, non touchés)
- Le layout `app/(dashboard)/layout.tsx` (au maximum une ligne d'import à changer)
