# 📊 Structures JSON - Persistance Données

**Date** : 16 novembre 2025
**Version** : 0.18.0-alpha (cible)

---

## 📁 Vue d'Ensemble Fichiers Data

```
data/
├── config.json (existant, ne pas modifier)
├── memory/
│   ├── conversations.json
│   ├── facts.json
│   └── embeddings.json
├── personality.json
└── emotion_history.json
```

---

## 1️⃣ data/memory/conversations.json

**Objectif** : Stocker résumés conversations pour mémoire long-terme

### Structure

```json
{
  "version": "1.0",
  "last_updated": "2025-11-16T14:30:00Z",
  "conversations": [
    {
      "id": "conv_20251116_001",
      "start_timestamp": "2025-11-16T10:00:00Z",
      "end_timestamp": "2025-11-16T10:45:00Z",
      "message_count": 25,
      "summary": "Alice s'est présentée et a parlé de sa passion pour le jazz. Elle a demandé des conseils pour apprendre la guitare. Discussion sur les artistes de jazz préférés.",
      "key_points": [
        "Nom utilisateur : Alice",
        "Passion : musique jazz",
        "Intérêt : apprendre guitare",
        "Artistes préférés : Miles Davis, John Coltrane"
      ],
      "topics": ["musique", "jazz", "guitare", "apprentissage"],
      "overall_sentiment": "positive",
      "sentiment_score": 0.75,
      "dominant_emotion": "joyeux",
      "message_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
    },
    {
      "id": "conv_20251116_002",
      "start_timestamp": "2025-11-16T15:00:00Z",
      "end_timestamp": "2025-11-16T15:30:00Z",
      "message_count": 18,
      "summary": "Alice a partagé ses frustrations sur un projet de travail difficile. Discussion sur la gestion du stress et techniques de productivité.",
      "key_points": [
        "Projet travail frustrant",
        "Besoin techniques gestion stress",
        "Intérêt pour techniques Pomodoro"
      ],
      "topics": ["travail", "productivité", "stress", "bien-être"],
      "overall_sentiment": "mixed",
      "sentiment_score": -0.2,
      "dominant_emotion": "frustré",
      "message_ids": [26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43]
    }
  ],
  "total_conversations": 2,
  "total_messages": 43
}
```

### Champs Détaillés

| Champ | Type | Description |
|-------|------|-------------|
| `version` | string | Version schéma JSON (pour migrations futures) |
| `last_updated` | ISO 8601 | Timestamp dernière mise à jour |
| `conversations` | array | Liste résumés conversations |
| `conversations[].id` | string | ID unique conversation (format: conv_YYYYMMDD_NNN) |
| `conversations[].start_timestamp` | ISO 8601 | Début conversation |
| `conversations[].end_timestamp` | ISO 8601 | Fin conversation |
| `conversations[].message_count` | int | Nombre messages dans conversation |
| `conversations[].summary` | string | Résumé 2-3 phrases généré par LLM |
| `conversations[].key_points` | array[string] | Points clés extraits |
| `conversations[].topics` | array[string] | Sujets principaux abordés |
| `conversations[].overall_sentiment` | string | "positive", "negative", "neutral", "mixed" |
| `conversations[].sentiment_score` | float | Score -1.0 (négatif) à +1.0 (positif) |
| `conversations[].dominant_emotion` | string | Émotion dominante conversation |
| `conversations[].message_ids` | array[int] | IDs messages originaux (référence interne) |

### Création Nouvelle Conversation

```python
new_conversation = {
    "id": f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    "start_timestamp": datetime.now().isoformat() + "Z",
    "end_timestamp": datetime.now().isoformat() + "Z",
    "message_count": len(messages),
    "summary": summarizer.summarize(messages),
    "key_points": fact_extractor.extract_key_points(messages),
    "topics": context_analyzer.extract_topics(messages),
    "overall_sentiment": context_analyzer.analyze_sentiment_global(messages),
    "sentiment_score": compute_sentiment_score(messages),
    "dominant_emotion": emotion_analyzer.get_dominant_emotion(messages),
    "message_ids": [msg["id"] for msg in messages]
}
```

---

## 2️⃣ data/memory/facts.json

**Objectif** : Stocker faits importants extraits (nom, préférences, événements)

### Structure

```json
{
  "version": "1.0",
  "last_updated": "2025-11-16T14:30:00Z",
  "user_profile": {
    "name": "Alice",
    "name_confidence": 1.0,
    "name_extracted_from": "conv_20251116_001",
    "name_timestamp": "2025-11-16T10:05:00Z"
  },
  "preferences": [
    {
      "id": "pref_001",
      "category": "musique",
      "item": "jazz",
      "sentiment": "positive",
      "confidence": 0.95,
      "extracted_from": "conv_20251116_001",
      "timestamp": "2025-11-16T10:10:00Z",
      "context": "Alice a dit 'j'aime beaucoup la musique jazz'"
    },
    {
      "id": "pref_002",
      "category": "instrument",
      "item": "guitare",
      "sentiment": "positive",
      "confidence": 0.85,
      "extracted_from": "conv_20251116_001",
      "timestamp": "2025-11-16T10:15:00Z",
      "context": "Alice veut apprendre la guitare"
    },
    {
      "id": "pref_003",
      "category": "nourriture",
      "item": "pizza",
      "sentiment": "positive",
      "confidence": 0.9,
      "extracted_from": "conv_20251117_001",
      "timestamp": "2025-11-17T12:00:00Z",
      "context": "Alice a dit 'j'adore la pizza'"
    }
  ],
  "events": [
    {
      "id": "event_001",
      "description": "Alice a commencé un projet de travail frustrant",
      "timestamp": "2025-11-16T15:00:00Z",
      "importance": 0.7,
      "sentiment": "negative",
      "extracted_from": "conv_20251116_002",
      "related_topics": ["travail", "stress"]
    }
  ],
  "relationships": [
    {
      "id": "rel_001",
      "entity_1": "Alice",
      "relation_type": "aime",
      "entity_2": "Miles Davis",
      "confidence": 0.9,
      "extracted_from": "conv_20251116_001"
    },
    {
      "id": "rel_002",
      "entity_1": "Alice",
      "relation_type": "veut_apprendre",
      "entity_2": "guitare",
      "confidence": 0.85,
      "extracted_from": "conv_20251116_001"
    }
  ],
  "total_preferences": 3,
  "total_events": 1,
  "total_relationships": 2
}
```

### Champs Détaillés

#### user_profile

| Champ | Type | Description |
|-------|------|-------------|
| `name` | string | Nom utilisateur extrait |
| `name_confidence` | float | Confiance extraction (0.0-1.0) |
| `name_extracted_from` | string | ID conversation source |
| `name_timestamp` | ISO 8601 | Quand extrait |

#### preferences[]

| Champ | Type | Description |
|-------|------|-------------|
| `id` | string | ID unique préférence (pref_NNN) |
| `category` | string | Catégorie (musique, nourriture, activité, etc.) |
| `item` | string | Item spécifique (jazz, pizza, course, etc.) |
| `sentiment` | string | "positive" ou "negative" |
| `confidence` | float | Confiance extraction (0.0-1.0) |
| `extracted_from` | string | ID conversation source |
| `timestamp` | ISO 8601 | Quand extrait |
| `context` | string | Phrase originale (pour vérification) |

#### events[]

| Champ | Type | Description |
|-------|------|-------------|
| `id` | string | ID unique événement (event_NNN) |
| `description` | string | Description événement |
| `timestamp` | ISO 8601 | Quand événement s'est produit |
| `importance` | float | Importance 0.0-1.0 (1.0 = très important) |
| `sentiment` | string | "positive", "negative", "neutral" |
| `extracted_from` | string | ID conversation source |
| `related_topics` | array[string] | Sujets associés |

#### relationships[]

| Champ | Type | Description |
|-------|------|-------------|
| `id` | string | ID unique relation (rel_NNN) |
| `entity_1` | string | Entité 1 (ex: "Alice") |
| `relation_type` | string | Type relation (aime, déteste, veut_apprendre, connaît, etc.) |
| `entity_2` | string | Entité 2 (ex: "Miles Davis", "guitare") |
| `confidence` | float | Confiance extraction (0.0-1.0) |
| `extracted_from` | string | ID conversation source |

---

## 3️⃣ data/memory/embeddings.json

**Objectif** : Stocker vecteurs embeddings pour recherche sémantique rapide

### Structure

```json
{
  "version": "1.0",
  "model": "all-MiniLM-L6-v2",
  "embedding_dim": 384,
  "last_updated": "2025-11-16T14:30:00Z",
  "embeddings": [
    {
      "id": "conv_20251116_001",
      "type": "conversation_summary",
      "text": "Alice s'est présentée et a parlé de sa passion pour le jazz...",
      "embedding": [0.123, -0.456, 0.789, ..., 0.234],
      "timestamp": "2025-11-16T10:45:00Z"
    },
    {
      "id": "pref_001",
      "type": "preference",
      "text": "Alice aime beaucoup la musique jazz",
      "embedding": [0.321, -0.654, 0.987, ..., 0.432],
      "timestamp": "2025-11-16T10:10:00Z"
    }
  ],
  "total_embeddings": 2
}
```

### Champs Détaillés

| Champ | Type | Description |
|-------|------|-------------|
| `version` | string | Version schéma JSON |
| `model` | string | Modèle embeddings utilisé |
| `embedding_dim` | int | Dimension vecteurs (384 pour all-MiniLM-L6-v2) |
| `last_updated` | ISO 8601 | Dernière mise à jour |
| `embeddings` | array | Liste vecteurs embeddings |
| `embeddings[].id` | string | ID entité (conv_XXX, pref_XXX, event_XXX, etc.) |
| `embeddings[].type` | string | Type entité (conversation_summary, preference, event, etc.) |
| `embeddings[].text` | string | Texte original (pour vérification) |
| `embeddings[].embedding` | array[float] | Vecteur embedding (384 dimensions) |
| `embeddings[].timestamp` | ISO 8601 | Quand créé |

### Utilisation Recherche Sémantique

```python
# Query utilisateur
query = "Quels sont mes genres musicaux préférés ?"

# 1. Encoder query
query_embedding = embeddings_model.encode(query)

# 2. Calculer similarités cosine avec tous embeddings
similarities = []
for emb_entry in embeddings_data["embeddings"]:
    similarity = cosine_similarity(query_embedding, emb_entry["embedding"])
    similarities.append((emb_entry["id"], similarity))

# 3. Trier par similarité décroissante
similarities.sort(key=lambda x: x[1], reverse=True)

# 4. Retourner top-k (ex: k=5)
top_results = similarities[:5]

# Résultats :
# [
#   ("pref_001", 0.92),  # Alice aime musique jazz
#   ("conv_20251116_001", 0.85),  # Conversation sur jazz
#   ("pref_004", 0.78),  # Alice aime rock
#   ...
# ]
```

**Optimisation** : Si fichier embeddings devient trop gros (>10 MB), envisager SQLite avec indexation vectorielle.

---

## 4️⃣ data/personality.json

**Objectif** : Stocker traits personnalité évolutifs

### Structure

```json
{
  "version": "1.0",
  "last_updated": "2025-11-16T14:30:00Z",
  "current_traits": {
    "extraversion": 0.68,
    "empathie": 0.82,
    "humour": 0.54,
    "formalité": 0.35,
    "curiosité": 0.71,
    "enthousiasme": 0.63,
    "patience": 0.75
  },
  "trait_history": [
    {
      "timestamp": "2025-11-16T10:00:00Z",
      "traits": {
        "extraversion": 0.60,
        "empathie": 0.80,
        "humour": 0.50,
        "formalité": 0.30,
        "curiosité": 0.70,
        "enthousiasme": 0.60,
        "patience": 0.70
      },
      "reason": "Initial default values"
    },
    {
      "timestamp": "2025-11-16T14:30:00Z",
      "traits": {
        "extraversion": 0.68,
        "empathie": 0.82,
        "humour": 0.54,
        "formalité": 0.35,
        "curiosité": 0.71,
        "enthousiasme": 0.63,
        "patience": 0.75
      },
      "reason": "Updated after 100 interactions (user feedback positive, conversational style preferred)",
      "interactions_count": 100,
      "changes": {
        "extraversion": "+0.08",
        "empathie": "+0.02",
        "humour": "+0.04",
        "formalité": "+0.05",
        "curiosité": "+0.01",
        "enthousiasme": "+0.03",
        "patience": "+0.05"
      }
    }
  ],
  "total_interactions": 150,
  "last_trait_update": "2025-11-16T14:30:00Z",
  "update_frequency": 50
}
```

### Champs Détaillés

#### current_traits

| Trait | Type | Plage | Description |
|-------|------|-------|-------------|
| `extraversion` | float | 0.0-1.0 | 0.0=introverti (concis), 1.0=extraverti (bavard) |
| `empathie` | float | 0.0-1.0 | 0.0=rationnel (factuel), 1.0=empathique (sensible) |
| `humour` | float | 0.0-1.0 | 0.0=sérieux, 1.0=blagueur |
| `formalité` | float | 0.0-1.0 | 0.0=casual (tutoiement), 1.0=formel (vouvoiement) |
| `curiosité` | float | 0.0-1.0 | 0.0=passif (répond), 1.0=curieux (pose questions) |
| `enthousiasme` | float | 0.0-1.0 | 0.0=calme (mesuré), 1.0=énergique (exclamatif) |
| `patience` | float | 0.0-1.0 | 0.0=impatient (direct), 1.0=patient (détaillé) |

#### trait_history[]

| Champ | Type | Description |
|-------|------|-------------|
| `timestamp` | ISO 8601 | Quand mise à jour effectuée |
| `traits` | object | Snapshot tous traits à ce moment |
| `reason` | string | Raison mise à jour (feedback user, nombre interactions, etc.) |
| `interactions_count` | int | Nombre interactions depuis dernière mise à jour |
| `changes` | object | Delta changements (+/- pour chaque trait) |

### Génération Prompt Système

```python
def generate_system_prompt(traits: dict) -> str:
    """Génère prompt adaptatif selon traits personnalité."""

    base = "Tu es Kira, une assistante virtuelle"

    # Extraversion
    if traits["extraversion"] > 0.7:
        base += " très bavarde et engageante"
    elif traits["extraversion"] < 0.3:
        base += " concise et directe"
    else:
        base += " équilibrée"

    # Empathie
    if traits["empathie"] > 0.7:
        base += ", profondément empathique et sensible aux émotions"
    elif traits["empathie"] < 0.3:
        base += ", rationnelle et factuelle"
    else:
        base += ", avec un équilibre entre raison et émotion"

    # Humour
    if traits["humour"] > 0.6:
        base += ". Tu utilises souvent l'humour pour détendre."
    elif traits["humour"] < 0.3:
        base += ". Tu restes sérieuse et professionnelle."

    # Formalité
    if traits["formalité"] > 0.6:
        base += " Tu vouvoies l'utilisateur et gardes un ton formel."
    else:
        base += " Tu tutoies l'utilisateur avec un ton casual et amical."

    # Curiosité
    if traits["curiosité"] > 0.7:
        base += " Tu poses beaucoup de questions et t'intéresses activement."

    # Patience
    if traits["patience"] > 0.7:
        base += " Tu prends le temps d'expliquer en détail."
    elif traits["patience"] < 0.3:
        base += " Tu vas droit au but sans détails superflus."

    return base
```

**Exemple prompt généré** (extraversion=0.8, empathie=0.9, humour=0.6, formalité=0.2, curiosité=0.8) :

> "Tu es Kira, une assistante virtuelle très bavarde et engageante, profondément empathique et sensible aux émotions. Tu utilises souvent l'humour pour détendre. Tu tutoies l'utilisateur avec un ton casual et amical. Tu poses beaucoup de questions et t'intéresses activement."

---

## 5️⃣ data/emotion_history.json

**Objectif** : Historique émotions pour transitions réalistes et analyse tendances

### Structure

```json
{
  "version": "1.0",
  "last_updated": "2025-11-16T14:30:00Z",
  "max_history": 100,
  "current_emotion": "joyeux",
  "current_intensity": 0.75,
  "history": [
    {
      "timestamp": "2025-11-16T10:00:00Z",
      "emotion": "neutre",
      "intensity": 0.5,
      "context": "Début conversation",
      "triggered_by": "system"
    },
    {
      "timestamp": "2025-11-16T10:05:00Z",
      "emotion": "joyeux",
      "intensity": 0.7,
      "context": "Alice s'est présentée avec enthousiasme",
      "triggered_by": "user_message"
    },
    {
      "timestamp": "2025-11-16T10:10:00Z",
      "emotion": "joyeux",
      "intensity": 0.8,
      "context": "Discussion passionnée sur le jazz",
      "triggered_by": "user_message"
    },
    {
      "timestamp": "2025-11-16T15:00:00Z",
      "emotion": "frustré",
      "intensity": 0.65,
      "context": "Alice partage frustrations projet travail",
      "triggered_by": "user_message"
    },
    {
      "timestamp": "2025-11-16T15:15:00Z",
      "emotion": "empathique",
      "intensity": 0.7,
      "context": "Réponse empathique aux frustrations Alice",
      "triggered_by": "assistant_response"
    }
  ],
  "transitions": [
    {
      "from": "neutre",
      "to": "joyeux",
      "count": 15,
      "avg_duration_seconds": 120
    },
    {
      "from": "joyeux",
      "to": "frustré",
      "count": 3,
      "avg_duration_seconds": 300
    },
    {
      "from": "frustré",
      "to": "neutre",
      "count": 5,
      "avg_duration_seconds": 180
    }
  ],
  "statistics": {
    "total_emotions_recorded": 98,
    "most_frequent_emotion": "joyeux",
    "most_frequent_emotion_count": 35,
    "avg_intensity_overall": 0.68,
    "total_transitions": 42
  }
}
```

### Champs Détaillés

#### history[]

| Champ | Type | Description |
|-------|------|-------------|
| `timestamp` | ISO 8601 | Quand émotion détectée |
| `emotion` | string | Émotion (neutre, joyeux, triste, etc.) |
| `intensity` | float | Intensité 0.0-1.0 |
| `context` | string | Court résumé contexte (pourquoi cette émotion) |
| `triggered_by` | string | "user_message", "assistant_response", "system" |

#### transitions[]

| Champ | Type | Description |
|-------|------|-------------|
| `from` | string | Émotion départ |
| `to` | string | Émotion arrivée |
| `count` | int | Nombre fois transition observée |
| `avg_duration_seconds` | int | Durée moyenne transition (secondes) |

### Validation Transitions

**Matrice Transitions Réalistes** (probabilités) :

```python
TRANSITION_MATRIX = {
    "neutre": {"neutre": 0.4, "joyeux": 0.25, "pensif": 0.15, "triste": 0.1, "surpris": 0.1},
    "joyeux": {"joyeux": 0.5, "neutre": 0.2, "surpris": 0.15, "excité": 0.1, "triste": 0.05},
    "triste": {"triste": 0.4, "neutre": 0.3, "frustré": 0.15, "joyeux": 0.1, "pensif": 0.05},
    "énervé": {"énervé": 0.35, "frustré": 0.25, "neutre": 0.2, "triste": 0.15, "joyeux": 0.05},
    "surpris": {"surpris": 0.2, "joyeux": 0.3, "neutre": 0.25, "excité": 0.15, "pensif": 0.1},
    # ... etc
}
```

**Fonction Validation** :

```python
def should_allow_transition(current: str, new: str, transition_matrix: dict) -> bool:
    """Vérifie si transition émotionnelle est réaliste."""
    if current not in transition_matrix:
        return True  # Pas de contrainte

    allowed_transitions = transition_matrix[current]
    if new not in allowed_transitions:
        return False  # Transition non autorisée

    probability = allowed_transitions[new]
    return probability > 0.05  # Seuil minimum 5%
```

---

## 📊 Tailles Fichiers Estimées

| Fichier | Taille Initiale | Après 1000 Messages | Après 10000 Messages |
|---------|-----------------|---------------------|----------------------|
| `conversations.json` | ~2 KB | ~50 KB | ~400 KB |
| `facts.json` | ~1 KB | ~20 KB | ~150 KB |
| `embeddings.json` | ~5 KB | ~500 KB | ~5 MB |
| `personality.json` | ~3 KB | ~5 KB | ~10 KB |
| `emotion_history.json` | ~2 KB | ~15 KB | ~30 KB (limité 100 entries) |
| **TOTAL** | **~13 KB** | **~590 KB** | **~5.6 MB** |

**✅ OK** : Tailles raisonnables, pas de problème performance.

**Optimisations possibles** (si nécessaire) :
- Archiver anciennes conversations (>6 mois) dans fichiers séparés
- Compresser embeddings avec quantization (float32 → float16)
- Migrer vers SQLite si recherches deviennent lentes (>1s)

---

## 🔄 Migrations Futures

### Version 1.0 → 2.0 (exemple)

Si besoin ajouter champs, stratégie migration :

```python
def migrate_conversations_v1_to_v2(data: dict) -> dict:
    """Migre conversations.json de v1.0 à v2.0."""
    if data["version"] != "1.0":
        return data  # Déjà migré

    # Ajouter nouveaux champs
    for conv in data["conversations"]:
        conv["language"] = "fr"  # Nouveau champ v2.0
        conv["embedding_id"] = conv["id"]  # Nouveau champ v2.0

    data["version"] = "2.0"
    return data
```

---

## 📝 Prochaines Étapes

✅ Schémas JSON définis
🚧 Guide intégration ChatEngine → **INTEGRATION_GUIDE.md**
🚧 Stratégie tests détaillée → **TESTING_STRATEGY.md**
🚧 Plan phases développement → **DEVELOPMENT_PHASES.md**

---

**Créé le** : 16 novembre 2025
**Dernière mise à jour** : 16 novembre 2025
