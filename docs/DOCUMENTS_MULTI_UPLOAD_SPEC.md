# Specifications fonctionnelles et techniques - Upload multiple de documents

## 1. Contexte

Permettre l'ajout de plusieurs fichiers en une seule requete sur un projet, en conservant l'endpoint existant et un comportement en succes partiel.

## 2. Objectif

Ajouter la capacite d'uploader jusqu'a 10 fichiers dans une seule requete `POST /projects/{project_id}/documents`, avec un resultat detaille par fichier.

## 3. Specifications fonctionnelles

### 3.1 Endpoint

- Endpoint conserve: `POST /projects/{project_id}/documents`
- Content-Type: `multipart/form-data`
- Parametre: `files[]` (liste de fichiers)

### 3.2 Regles metier

- Mode de traitement: succes partiel
- Traitement des fichiers: sequentiel (v1)
- Maximum: 10 fichiers par requete
- Autorisation: seul le proprietaire du projet peut uploader
- Doublon dans la meme requete:
  - si un nom de fichier apparait plusieurs fois, le premier est traite
  - les occurrences suivantes sont rejetees avec erreur detaillee
- Doublon avec fichier existant sur le projet:
  - renommage automatique avec suffixe `-copie-#` avant l'extension
  - exemple: `doc.pdf` -> `doc-copie-1.pdf`, puis `doc-copie-2.pdf`
- Echec du processing d'un fichier:
  - le fichier est marque en erreur dans la reponse
  - les donnees/artefacts de ce fichier sont supprimes
  - le traitement continue sur le fichier suivant
- Nettoyage:
  - nettoyage obligatoire des artefacts temporaires pour chaque fichier en echec

### 3.3 Formats et taille

- Formats autorises: `txt`, `md`, `pdf`, `doc`, `docx`
- Taille maximale: 100 Mo par fichier

## 4. Contrat API

### 4.1 Requete

- Methode: `POST`
- URL: `/projects/{project_id}/documents`
- Body multipart:
  - `files`: liste de 1 a 10 fichiers

### 4.2 Reponse

- HTTP recommande: `200 OK` (succes partiel possible)
- Corps detaille:

```json
{
  "total": 4,
  "succeeded": 2,
  "failed": 2,
  "created": [
    {
      "original_filename": "a.pdf",
      "stored_filename": "a.pdf",
      "document_id": "uuid"
    },
    {
      "original_filename": "b.pdf",
      "stored_filename": "b-copie-1.pdf",
      "document_id": "uuid"
    }
  ],
  "errors": [
    {
      "filename": "a.pdf",
      "code": "DUPLICATE_IN_REQUEST",
      "message": "Duplicate filename in request."
    },
    {
      "filename": "c.docx",
      "code": "PROCESSING_FAILED",
      "message": "Document processing failed."
    }
  ]
}
```

### 4.3 Codes d'erreur metier (par fichier)

- `DUPLICATE_IN_REQUEST`
- `INVALID_FILE_TYPE`
- `FILE_TOO_LARGE`
- `PROJECT_NOT_FOUND`
- `FORBIDDEN`
- `STORAGE_FAILED`
- `PROCESSING_FAILED`
- `UNEXPECTED_ERROR`

## 5. Specifications techniques

### 5.1 Couche Application

- Introduire un use case batch (recommande): `UploadDocuments`
- Entree: `project_id`, `uploaded_by`, `files[]`
- Sortie: resultat agrege (`total`, `succeeded`, `failed`, `created[]`, `errors[]`)
- Etapes par fichier:
  1. Validation metadonnees (nom, type, taille)
  2. Resolution du nom cible (gestion `-copie-#`)
  3. Upload storage
  4. Persistance document
  5. Processing document
  6. En cas d'echec: rollback cible + cleanup + ajout erreur

### 5.2 Couche Presentation (FastAPI)

- Conserver l'endpoint existant
- Accepter `files: list[UploadFile] = File(...)`
- Ajouter validation `1 <= len(files) <= 10`
- Retourner le DTO batch detaille

### 5.3 Couche Infrastructure

- Reutiliser repository/storage existants
- Ajouter logique de generation de nom unique (`-copie-#`)
- Garantir les operations de cleanup lors des echecs processing/storage

### 5.4 Base de donnees et migrations

- Aucune migration Alembic requise pour ce scope
- Regle projet: si le schema evolue pendant implementation, creer une migration Alembic dediee

## 6. Strategie de tests (TDD)

### 6.1 Unit tests (prioritaires)

- Upload multi-fichiers valides -> succes complet
- Upload avec echec partiel -> succes partiel + erreurs detaillees
- Doublons intra-requete -> second fichier rejete
- Doublons existants projet -> renommage `-copie-#`
- Echec processing -> suppression donnees/artefacts + continuation
- Validation max 10 fichiers

### 6.2 Integration tests

- Persistance correcte des documents crees
- Suppression correcte en cas d'echec processing
- Coherence storage + repository

### 6.3 E2E tests

- `POST /projects/{project_id}/documents` avec plusieurs fichiers
- Verification de la reponse detaillee (`created`, `errors`)
- Verification des regles d'autorisation (owner uniquement)

## 7. Non-objectifs (v1)

- Traitement parallele des fichiers
- Ajout d'un `batch_id`
- Nouveau endpoint dedie batch

## 8. Criteres d'acceptation

- L'endpoint existant accepte une liste de fichiers (max 10)
- Le systeme traite en mode succes partiel avec detail par fichier
- Les doublons intra-requete sont rejetes
- Les doublons existants sont renommes en `-copie-#`
- En cas d'echec processing, les artefacts du fichier sont nettoyes
- Les droits projet sont strictement respectes
