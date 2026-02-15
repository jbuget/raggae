# Spécifications Fonctionnelles et Techniques
## Amélioration de la recherche hybride de chunks/documents

---

## 1. Contexte et objectifs

### 1.1 Problématique actuelle
La recherche basée uniquement sur les embeddings présente des limitations :
- Manque de précision sur les termes techniques exacts
- Difficulté à retrouver des entités nommées spécifiques
- Absence de filtrage par métadonnées structurées
- Performance sous-optimale pour les requêtes courtes ou très spécifiques

### 1.2 Objectifs
Implémenter une **recherche hybride** combinant :
- Recherche sémantique (embeddings vectoriels)
- Recherche textuelle full-text (BM25, trigrams)
- Filtrage par métadonnées
- Système de scoring fusionné et pondéré

---

## 2. Spécifications Fonctionnelles

### 2.1 Cas d'usage

#### UC1 : Recherche sémantique pure
**Acteur** : Utilisateur  
**Déclencheur** : Requête conceptuelle ("comment gérer l'authentification ?")  
**Résultat** : Documents pertinents basés sur la similarité sémantique

#### UC2 : Recherche textuelle exacte
**Acteur** : Utilisateur  
**Déclencheur** : Requête avec terme technique ("JWT token expiration")  
**Résultat** : Documents contenant exactement ces termes

#### UC3 : Recherche hybride pondérée
**Acteur** : Utilisateur  
**Déclencheur** : Requête mixte avec filtres de métadonnées  
**Résultat** : Fusion des résultats sémantiques et textuels, filtrés par métadonnées

#### UC4 : Filtrage par métadonnées
**Acteur** : Utilisateur  
**Déclencheur** : Recherche avec contraintes (date, auteur, type, tags)  
**Résultat** : Résultats pré-filtrés avant scoring

### 2.2 Exigences fonctionnelles

**RF1** : Le système doit supporter la recherche par embeddings (existant)  
**RF2** : Le système doit supporter la recherche full-text avec ranking BM25  
**RF3** : Le système doit permettre le filtrage par métadonnées multiples  
**RF4** : Le système doit fusionner les scores avec pondération configurable  
**RF5** : Le système doit supporter les opérateurs booléens (AND, OR, NOT) en full-text  
**RF6** : Le système doit permettre la configuration des poids par type de recherche  
**RF7** : Le système doit retourner des scores explicites pour chaque méthode  
**RF8** : Le système doit supporter la pagination efficace sur résultats fusionnés

### 2.3 Métadonnées supportées

```typescript
interface DocumentMetadata {
  id: string;
  title?: string;
  author?: string;
  created_at: Date;
  updated_at: Date;
  document_type?: string; // 'code', 'doc', 'api', 'spec'
  tags?: string[];
  language?: string;
  file_path?: string;
  file_extension?: string;
  chunk_index?: number;
  total_chunks?: number;
  custom_fields?: Record<string, any>;
}
```

---

## 3. Spécifications Techniques

### 3.1 Architecture

```
┌─────────────────┐
│  Search API     │
│  (Controller)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  HybridSearchService        │
│  - Orchestration            │
│  - Score fusion             │
│  - Result ranking           │
└───┬─────────┬──────────┬────┘
    │         │          │
    ▼         ▼          ▼
┌─────────┐ ┌──────────┐ ┌──────────────┐
│ Vector  │ │ FullText │ │ Metadata     │
│ Search  │ │ Search   │ │ Filter       │
└─────────┘ └──────────┘ └──────────────┘
    │         │          │
    ▼         ▼          ▼
┌─────────────────────────────┐
│  Database Layer             │
│  - pgvector (embeddings)    │
│  - pg_trgm (trigrams)       │
│  - GIN indexes (full-text)  │
│  - JSONB (metadata)         │
└─────────────────────────────┘
```

### 3.2 Stack technique

#### Base de données : PostgreSQL 14+
**Extensions requises** :
- `pgvector` : recherche vectorielle
- `pg_trgm` : trigrams pour similarité textuelle
- `pg_stat_statements` : monitoring performances

**Indexes à créer** :
```sql
-- Index vectoriel (existant probablement)
CREATE INDEX idx_chunks_embedding ON chunks 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Index full-text search
CREATE INDEX idx_chunks_content_fts ON chunks 
USING GIN (to_tsvector('english', content));

-- Index trigram pour recherche floue
CREATE INDEX idx_chunks_content_trgm ON chunks 
USING GIN (content gin_trgm_ops);

-- Index sur métadonnées JSONB
CREATE INDEX idx_chunks_metadata ON chunks 
USING GIN (metadata jsonb_path_ops);

-- Index composites pour filtres fréquents
CREATE INDEX idx_chunks_type_date ON chunks (
  (metadata->>'document_type'), 
  (metadata->>'created_at')
);
```

#### Backend
**Langage** : TypeScript/Node.js (assumé)  
**ORM** : Prisma ou TypeORM avec support raw queries  
**Librairies** :
- `@neondatabase/serverless` ou `pg` pour PostgreSQL
- `@pgvector/pg` pour embeddings
- Framework embedding : OpenAI, Cohere, ou local (sentence-transformers)

### 3.3 Schéma de données

```sql
-- Table principale (probablement existante, à adapter)
CREATE TABLE chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL,
  content TEXT NOT NULL,
  embedding vector(1536), -- dimension selon le modèle
  metadata JSONB DEFAULT '{}',
  chunk_index INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table de configuration des poids
CREATE TABLE search_config (
  id SERIAL PRIMARY KEY,
  config_name VARCHAR(100) UNIQUE NOT NULL,
  vector_weight DECIMAL(3,2) DEFAULT 0.5,
  fulltext_weight DECIMAL(3,2) DEFAULT 0.3,
  metadata_weight DECIMAL(3,2) DEFAULT 0.2,
  min_score_threshold DECIMAL(3,2) DEFAULT 0.1,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3.4 Algorithmes de fusion des scores

#### A. Reciprocal Rank Fusion (RRF)
```typescript
function reciprocalRankFusion(
  results: SearchResult[][],
  k: number = 60
): SearchResult[] {
  const scoreMap = new Map<string, number>();
  
  results.forEach(resultSet => {
    resultSet.forEach((result, rank) => {
      const rrf = 1 / (k + rank + 1);
      scoreMap.set(
        result.id,
        (scoreMap.get(result.id) || 0) + rrf
      );
    });
  });
  
  return Array.from(scoreMap.entries())
    .sort((a, b) => b[1] - a[1])
    .map(([id, score]) => ({ id, score }));
}
```

#### B. Weighted Sum (plus simple, plus configurable)
```typescript
function weightedScoreFusion(
  vectorResults: SearchResult[],
  fulltextResults: SearchResult[],
  weights: { vector: number; fulltext: number }
): SearchResult[] {
  const scoreMap = new Map<string, {
    vectorScore: number;
    fulltextScore: number;
    finalScore: number;
  }>();
  
  // Normalisation des scores [0-1]
  const normalize = (results: SearchResult[]) => {
    const max = Math.max(...results.map(r => r.score));
    return results.map(r => ({
      ...r,
      score: max > 0 ? r.score / max : 0
    }));
  };
  
  const normVector = normalize(vectorResults);
  const normFulltext = normalize(fulltextResults);
  
  // Fusion
  [...normVector, ...normFulltext].forEach(result => {
    const existing = scoreMap.get(result.id) || {
      vectorScore: 0,
      fulltextScore: 0,
      finalScore: 0
    };
    
    if (normVector.find(r => r.id === result.id)) {
      existing.vectorScore = result.score;
    }
    if (normFulltext.find(r => r.id === result.id)) {
      existing.fulltextScore = result.score;
    }
    
    existing.finalScore = 
      existing.vectorScore * weights.vector +
      existing.fulltextScore * weights.fulltext;
    
    scoreMap.set(result.id, existing);
  });
  
  return Array.from(scoreMap.entries())
    .sort((a, b) => b[1].finalScore - a[1].finalScore)
    .map(([id, scores]) => ({
      id,
      score: scores.finalScore,
      breakdown: {
        vector: scores.vectorScore,
        fulltext: scores.fulltextScore
      }
    }));
}
```

### 3.5 Requêtes SQL optimisées

#### Recherche vectorielle
```sql
-- Version multi-lignes (lisible)
SELECT 
  id,
  content,
  metadata,
  1 - (embedding <=> $1::vector) AS similarity_score
FROM chunks
WHERE metadata @> $2::jsonb  -- Filtre métadonnées
ORDER BY embedding <=> $1::vector
LIMIT $3;

-- Version 1-ligne (terminal)
SELECT id, content, metadata, 1 - (embedding <=> $1::vector) AS similarity_score FROM chunks WHERE metadata @> $2::jsonb ORDER BY embedding <=> $1::vector LIMIT $3;
```

#### Recherche full-text (BM25-like avec ts_rank)
```sql
-- Version multi-lignes
SELECT 
  id,
  content,
  metadata,
  ts_rank_cd(
    to_tsvector('english', content),
    plainto_tsquery('english', $1)
  ) AS text_score
FROM chunks
WHERE 
  to_tsvector('english', content) @@ plainto_tsquery('english', $1)
  AND metadata @> $2::jsonb
ORDER BY text_score DESC
LIMIT $3;

-- Version 1-ligne
SELECT id, content, metadata, ts_rank_cd(to_tsvector('english', content), plainto_tsquery('english', $1)) AS text_score FROM chunks WHERE to_tsvector('english', content) @@ plainto_tsquery('english', $1) AND metadata @> $2::jsonb ORDER BY text_score DESC LIMIT $3;
```

#### Recherche hybride (CTE)
```sql
-- Version multi-lignes
WITH vector_search AS (
  SELECT 
    id,
    content,
    metadata,
    1 - (embedding <=> $1::vector) AS score,
    'vector' AS source
  FROM chunks
  WHERE metadata @> $2::jsonb
  ORDER BY embedding <=> $1::vector
  LIMIT 100
),
fulltext_search AS (
  SELECT 
    id,
    content,
    metadata,
    ts_rank_cd(
      to_tsvector('english', content),
      plainto_tsquery('english', $3)
    ) AS score,
    'fulltext' AS source
  FROM chunks
  WHERE 
    to_tsvector('english', content) @@ plainto_tsquery('english', $3)
    AND metadata @> $2::jsonb
  ORDER BY score DESC
  LIMIT 100
),
combined AS (
  SELECT * FROM vector_search
  UNION ALL
  SELECT * FROM fulltext_search
)
SELECT 
  id,
  content,
  metadata,
  MAX(CASE WHEN source = 'vector' THEN score ELSE 0 END) AS vector_score,
  MAX(CASE WHEN source = 'fulltext' THEN score ELSE 0 END) AS fulltext_score,
  (
    MAX(CASE WHEN source = 'vector' THEN score ELSE 0 END) * $4 +
    MAX(CASE WHEN source = 'fulltext' THEN score ELSE 0 END) * $5
  ) AS final_score
FROM combined
GROUP BY id, content, metadata
ORDER BY final_score DESC
LIMIT $6;

-- Version 1-ligne
WITH vector_search AS (SELECT id, content, metadata, 1 - (embedding <=> $1::vector) AS score, 'vector' AS source FROM chunks WHERE metadata @> $2::jsonb ORDER BY embedding <=> $1::vector LIMIT 100), fulltext_search AS (SELECT id, content, metadata, ts_rank_cd(to_tsvector('english', content), plainto_tsquery('english', $3)) AS score, 'fulltext' AS source FROM chunks WHERE to_tsvector('english', content) @@ plainto_tsquery('english', $3) AND metadata @> $2::jsonb ORDER BY score DESC LIMIT 100), combined AS (SELECT * FROM vector_search UNION ALL SELECT * FROM fulltext_search) SELECT id, content, metadata, MAX(CASE WHEN source = 'vector' THEN score ELSE 0 END) AS vector_score, MAX(CASE WHEN source = 'fulltext' THEN score ELSE 0 END) AS fulltext_score, (MAX(CASE WHEN source = 'vector' THEN score ELSE 0 END) * $4 + MAX(CASE WHEN source = 'fulltext' THEN score ELSE 0 END) * $5) AS final_score FROM combined GROUP BY id, content, metadata ORDER BY final_score DESC LIMIT $6;
```

### 3.6 API Interface

```typescript
interface HybridSearchRequest {
  query: string;
  
  // Stratégie de recherche
  strategy: 'vector' | 'fulltext' | 'hybrid' | 'auto';
  
  // Poids (si hybrid)
  weights?: {
    vector?: number;    // 0-1, default 0.5
    fulltext?: number;  // 0-1, default 0.5
  };
  
  // Filtres métadonnées
  filters?: {
    document_type?: string[];
    tags?: string[];
    author?: string;
    date_from?: Date;
    date_to?: Date;
    language?: string;
    custom?: Record<string, any>;
  };
  
  // Options
  limit?: number;           // default 10
  offset?: number;          // default 0
  min_score?: number;       // threshold, default 0.1
  include_breakdown?: boolean; // scores détaillés
}

interface HybridSearchResponse {
  results: SearchResult[];
  total: number;
  strategy_used: string;
  execution_time_ms: number;
}

interface SearchResult {
  id: string;
  content: string;
  metadata: DocumentMetadata;
  score: number;
  breakdown?: {
    vector_score: number;
    fulltext_score: number;
    metadata_boost?: number;
  };
  highlights?: string[]; // Extraits pertinents
}
```

### 3.7 Service Layer

```typescript
class HybridSearchService {
  constructor(
    private db: DatabaseConnection,
    private embeddingService: EmbeddingService,
    private config: SearchConfig
  ) {}

  async search(request: HybridSearchRequest): Promise<HybridSearchResponse> {
    const startTime = Date.now();
    
    // 1. Déterminer la stratégie
    const strategy = this.determineStrategy(request);
    
    // 2. Construire les filtres métadonnées
    const metadataFilter = this.buildMetadataFilter(request.filters);
    
    // 3. Exécuter les recherches
    let results: SearchResult[];
    
    switch (strategy) {
      case 'vector':
        results = await this.vectorSearch(
          request.query,
          metadataFilter,
          request.limit
        );
        break;
        
      case 'fulltext':
        results = await this.fulltextSearch(
          request.query,
          metadataFilter,
          request.limit
        );
        break;
        
      case 'hybrid':
        results = await this.hybridSearch(
          request.query,
          metadataFilter,
          request.weights || this.config.defaultWeights,
          request.limit
        );
        break;
    }
    
    // 4. Post-traitement
    results = this.applyMinScoreThreshold(results, request.min_score);
    results = this.addHighlights(results, request.query);
    
    return {
      results,
      total: results.length,
      strategy_used: strategy,
      execution_time_ms: Date.now() - startTime
    };
  }
  
  private determineStrategy(request: HybridSearchRequest): string {
    if (request.strategy !== 'auto') {
      return request.strategy;
    }
    
    // Heuristiques pour auto-détection
    const hasExactTerms = /["']/.test(request.query);
    const isTechnical = /[A-Z]{2,}|[_-]/.test(request.query);
    const isShort = request.query.split(' ').length <= 3;
    
    if (hasExactTerms || (isTechnical && isShort)) {
      return 'fulltext';
    }
    
    return 'hybrid';
  }
  
  private buildMetadataFilter(filters?: any): any {
    if (!filters) return {};
    
    const jsonbFilter: any = {};
    
    if (filters.document_type) {
      jsonbFilter.document_type = { $in: filters.document_type };
    }
    if (filters.tags) {
      jsonbFilter.tags = { $containsAny: filters.tags };
    }
    // ... autres filtres
    
    return jsonbFilter;
  }
  
  private async hybridSearch(
    query: string,
    metadataFilter: any,
    weights: { vector: number; fulltext: number },
    limit: number
  ): Promise<SearchResult[]> {
    // Exécution parallèle
    const [vectorResults, fulltextResults] = await Promise.all([
      this.vectorSearch(query, metadataFilter, limit * 2),
      this.fulltextSearch(query, metadataFilter, limit * 2)
    ]);
    
    // Fusion des scores
    const merged = weightedScoreFusion(
      vectorResults,
      fulltextResults,
      weights
    );
    
    return merged.slice(0, limit);
  }
}
```

### 3.8 Performance et optimisation

#### Caching strategy
```typescript
interface CacheStrategy {
  // Cache des embeddings de requêtes fréquentes
  queryEmbeddingCache: LRUCache<string, number[]>;
  
  // Cache des résultats pour requêtes identiques
  resultCache: LRUCache<string, SearchResult[]>;
  
  // TTL configurable
  ttl: number; // secondes
}
```

#### Monitoring
```typescript
interface SearchMetrics {
  query: string;
  strategy: string;
  execution_time_ms: number;
  results_count: number;
  cache_hit: boolean;
  timestamp: Date;
}
```

#### Limites de performance cibles
- Recherche vectorielle : < 100ms (p95)
- Recherche full-text : < 50ms (p95)
- Recherche hybride : < 150ms (p95)
- Throughput : > 100 req/s

---

## 4. Plan d'implémentation

### Phase 1 : Infrastructure (Sprint 1)
- [ ] Mise en place des extensions PostgreSQL
- [ ] Création des indexes optimisés
- [ ] Migration des métadonnées au format JSONB
- [ ] Tests de performance baseline

### Phase 2 : Core Search (Sprint 2)
- [ ] Implémentation service de recherche vectorielle
- [ ] Implémentation service de recherche full-text
- [ ] Système de filtrage métadonnées
- [ ] Tests unitaires et d'intégration

### Phase 3 : Fusion & Optimisation (Sprint 3)
- [ ] Algorithmes de fusion des scores (RRF + Weighted)
- [ ] Système de configuration des poids
- [ ] Cache layer
- [ ] Tests de performance et tuning

### Phase 4 : API & Monitoring (Sprint 4)
- [ ] Endpoints REST/GraphQL
- [ ] Documentation OpenAPI
- [ ] Métriques et monitoring
- [ ] Tests end-to-end

### Phase 5 : Features avancées (Sprint 5+)
- [ ] Auto-détection de stratégie
- [ ] Highlighting des résultats
- [ ] Recherche par similarité de chunks
- [ ] A/B testing des stratégies

---

## 5. Métriques de succès

### Techniques
- Amélioration du recall@10 de 20%
- Amélioration de la précision@5 de 15%
- Temps de réponse p95 < 150ms
- Taux de cache hit > 60%

### Fonctionnelles
- 80% des utilisateurs trouvent le résultat pertinent dans les 5 premiers
- Réduction de 30% du nombre de recherches par session
- Satisfaction utilisateur > 4/5

---

## 6. Risques et mitigations

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| Performance dégradée sur gros volumes | Élevé | Moyenne | Partitionnement, index BRIN, archivage |
| Complexité configuration poids | Moyen | Élevée | Presets par défaut, A/B testing |
| Coût infrastructure (CPU/RAM) | Moyen | Moyenne | Monitoring, auto-scaling, caching |
| Migration métadonnées | Moyen | Faible | Migration progressive, rollback plan |

---

## 7. Annexes

### A. Exemples de requêtes

```typescript
// Recherche sémantique pure
await search({
  query: "how to implement authentication",
  strategy: "vector",
  limit: 10
});

// Recherche exacte avec filtres
await search({
  query: "JWT token",
  strategy: "fulltext",
  filters: {
    document_type: ["api", "doc"],
    language: "en"
  }
});

// Recherche hybride optimisée
await search({
  query: "user authentication best practices",
  strategy: "hybrid",
  weights: { vector: 0.6, fulltext: 0.4 },
  filters: {
    date_from: new Date("2024-01-01"),
    tags: ["security", "backend"]
  },
  min_score: 0.3
});
```

### B. Configuration recommandée PostgreSQL

```ini
# postgresql.conf optimisations
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
work_mem = 64MB
random_page_cost = 1.1  # SSD
effective_io_concurrency = 200

# pgvector specific
ivfflat.probes = 10
```