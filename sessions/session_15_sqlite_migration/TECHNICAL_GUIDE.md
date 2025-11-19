# 🔧 Guide Technique - Migration SQLite Phase 6

Guide détaillé pour comprendre et maintenir l'architecture SQLite de Workly.

---

## 📐 Architecture globale

### Vue d'ensemble
```
┌─────────────────────────────────────────┐
│         Application Layer               │
│  (EmotionMemory, PersonalityEngine,     │
│   MemoryManager, ChatEngine)            │
└──────────────┬──────────────────────────┘
               │ Appels API
               ▼
┌─────────────────────────────────────────┐
│         database.py                     │
│  WorklyDatabase class (singleton)       │
│  - add_conversation()                   │
│  - add_emotion()                        │
│  - set_personality_trait()              │
│  - add_fact()                           │
│  - add_segment()                        │
│  - add_embedding()                      │
└──────────────┬──────────────────────────┘
               │ SQL queries
               ▼
┌─────────────────────────────────────────┐
│         SQLite Database                 │
│         workly.db                       │
│  - conversations (messages)             │
│  - emotion_history (émotions)           │
│  - personality_traits (traits actuels)  │
│  - personality_evolution (historique)   │
│  - facts (entités, prefs, events)       │
│  - segments (résumés)                   │
│  - embeddings (vecteurs sémantiques)    │
└─────────────────────────────────────────┘
```

---

## 🗄️ Schéma de base de données

### Table: `conversations`
Stocke tous les messages de conversation.

```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL,           -- 'user' | 'assistant' | 'system'
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,      -- ISO format
    source TEXT DEFAULT 'desktop',
    metadata TEXT                 -- JSON optionnel
);

CREATE INDEX idx_conversations_timestamp ON conversations(timestamp);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

**Usage** :
```python
db.add_conversation(
    role="user",
    content="Bonjour !",
    timestamp=datetime.utcnow().isoformat(),
    user_id="default"
)

messages = db.get_conversations(user_id="default", limit=50)
```

---

### Table: `emotion_history`
Historique émotionnel (100 dernières émotions).

```sql
CREATE TABLE emotion_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    emotion TEXT NOT NULL,        -- 'joy', 'sadness', etc.
    intensity REAL NOT NULL,      -- 0.0 - 1.0
    context TEXT,
    timestamp TEXT NOT NULL
);

CREATE INDEX idx_emotion_timestamp ON emotion_history(timestamp);
CREATE INDEX idx_emotion_user_id ON emotion_history(user_id);
```

**Usage** :
```python
db.add_emotion(
    emotion="joy",
    intensity=0.8,
    context="User achieved goal",
    user_id="default"
)

emotions = db.get_emotions(user_id="default", limit=100)
```

---

### Table: `personality_traits`
Traits de personnalité actuels.

```sql
CREATE TABLE personality_traits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    trait_name TEXT NOT NULL,     -- 'humor', 'empathy', 'curiosity'
    value REAL NOT NULL,          -- 0.0 - 1.0
    last_updated TEXT NOT NULL,
    UNIQUE(user_id, trait_name)
);

CREATE INDEX idx_personality_user_trait ON personality_traits(user_id, trait_name);
```

**Usage** :
```python
db.set_personality_trait(
    trait_name="humor",
    value=0.75,
    user_id="default"
)

traits = db.get_personality_traits(user_id="default")
```

---

### Table: `personality_evolution`
Historique d'évolution des traits.

```sql
CREATE TABLE personality_evolution (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    trait_name TEXT NOT NULL,
    old_value REAL NOT NULL,
    new_value REAL NOT NULL,
    reason TEXT,
    timestamp TEXT NOT NULL
);

CREATE INDEX idx_evolution_timestamp ON personality_evolution(timestamp);
CREATE INDEX idx_evolution_trait ON personality_evolution(trait_name);
```

**Usage** :
```python
# Automatique lors de set_personality_trait()
evolution = db.get_personality_evolution(
    user_id="default",
    trait_name="humor"
)
```

---

### Table: `facts`
Faits extraits (entités, préférences, événements, relations).

```sql
CREATE TABLE facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    category TEXT NOT NULL,       -- 'entities' | 'preferences' | 'events' | 'relationships'
    type TEXT NOT NULL,           -- Type spécifique du fait
    data TEXT NOT NULL,           -- JSON
    confidence REAL DEFAULT 1.0,
    extracted_at TEXT NOT NULL,
    source_message_id INTEGER,
    FOREIGN KEY (source_message_id) REFERENCES conversations(id)
);

CREATE INDEX idx_facts_category ON facts(category);
CREATE INDEX idx_facts_user_id ON facts(user_id);
CREATE INDEX idx_facts_extracted_at ON facts(extracted_at);
```

**Usage** :
```python
db.add_fact(
    category="preferences",
    type_="subject",
    data={"subject": "Python", "sentiment": "positive"},
    confidence=0.9,
    user_id="default"
)

prefs = db.get_facts(user_id="default", category="preferences")
```

---

### Table: `segments`
Résumés de conversations.

```sql
CREATE TABLE segments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    summary TEXT NOT NULL,
    message_count INTEGER NOT NULL,
    start_timestamp TEXT NOT NULL,
    end_timestamp TEXT NOT NULL,
    topics TEXT,                  -- JSON list
    metadata TEXT                 -- JSON optionnel
);

CREATE INDEX idx_segments_user_id ON segments(user_id);
CREATE INDEX idx_segments_start_timestamp ON segments(start_timestamp);
```

**Usage** :
```python
db.add_segment(
    summary="Discussion sur Python et IA",
    message_count=20,
    start_timestamp="2025-11-18T10:00:00",
    end_timestamp="2025-11-18T10:30:00",
    topics=["Python", "IA", "Machine Learning"],
    user_id="default"
)

segments = db.get_segments(user_id="default")
```

---

### Table: `embeddings`
Vecteurs sémantiques pour recherche.

```sql
CREATE TABLE embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id INTEGER,
    embedding BLOB NOT NULL,      -- numpy array sérialisé
    text TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

CREATE INDEX idx_embeddings_timestamp ON embeddings(timestamp);
```

**Usage** :
```python
import numpy as np

embedding = model.encode("Texte à encoder")  # numpy array
db.add_embedding(
    conversation_id=None,
    embedding=embedding,
    text="Texte à encoder",
    timestamp=datetime.utcnow().isoformat()
)

# Récupération avec conversion automatique
embeddings = db.get_embeddings()  # Returns list[{"id": int, "embedding": np.ndarray, ...}]

# Ou matrice complète
matrix, ids = db.get_all_embeddings_matrix()  # (np.ndarray, list[int])
```

---

## 🔌 Pattern Singleton multi-instance

### Problème
Tests nécessitent isolation → chaque test doit avoir sa propre DB.

### Solution
```python
# database.py
_db_instances: Dict[str, WorklyDatabase] = {}

def get_database(db_path: str = "data/memory/workly.db") -> WorklyDatabase:
    """Singleton par chemin - permet isolation tests"""
    db_path_abs = os.path.abspath(db_path)

    if db_path_abs not in _db_instances:
        _db_instances[db_path_abs] = WorklyDatabase(db_path)

    return _db_instances[db_path_abs]
```

**Avantages** :
- ✅ Tests isolés (temp dir → unique path → unique instance)
- ✅ Production singleton (même path → même instance)
- ✅ Pas de contamination entre tests

---

## 🔄 Migration de modules

### Pattern général
1. **Backup** : Copier fichier original → `*_json_backup.py`
2. **Import database** : `from .database import get_database`
3. **Init DB** : `self.db = get_database(db_path)`
4. **Charger cache** : Lire DB → structures en mémoire
5. **Modifier writes** : Remplacer `_save_json()` par `db.add_*()`
6. **No-op saves** : `_save_*()` devient commentaire
7. **Tests** : Adapter assertions pour SQLite

### Exemple: EmotionMemory
```python
# AVANT (JSON)
def __init__(self, storage_file="data/emotion_history.json"):
    self.storage_file = storage_file
    self.history = deque(maxlen=100)
    self.history = self._load_history()  # Lit JSON

def _load_history(self):
    if os.path.exists(self.storage_file):
        with open(self.storage_file, 'r') as f:
            data = json.load(f)
            return deque([EmotionEntry(**e) for e in data], maxlen=100)
    return deque(maxlen=100)

def add_emotion(self, emotion, intensity, context):
    entry = EmotionEntry(...)
    self.history.append(entry)
    self._save_history()  # Écrit JSON

def _save_history(self):
    with open(self.storage_file, 'w') as f:
        json.dump([e.__dict__ for e in self.history], f)

# APRÈS (SQLite)
def __init__(self, storage_file="data/emotion_history.json"):
    self.storage_file = storage_file  # Gardé pour compatibilité
    storage_dir = os.path.dirname(storage_file) or "data/memory"
    db_path = os.path.join(storage_dir, "workly.db")
    self.db = get_database(db_path)  # Init DB
    self.history = deque(maxlen=100)
    self.history = self._load_history()  # Lit SQLite

def _load_history(self):
    db_emotions = self.db.get_emotions(limit=100)
    return deque([
        EmotionEntry(
            emotion=e["emotion"],
            intensity=e["intensity"],
            context=e["context"],
            timestamp=e["timestamp"]
        )
        for e in db_emotions
    ], maxlen=100)

def add_emotion(self, emotion, intensity, context):
    entry = EmotionEntry(...)
    # Écriture SQLite
    self.db.add_emotion(
        emotion=emotion,
        intensity=intensity,
        context=context,
        user_id="default"
    )
    self.history.append(entry)  # Cache
    # Pas besoin de _save_history()

def _save_history(self):
    # No-op - SQLite écrit directement dans add_emotion()
    pass
```

---

## 🧪 Tests et validation

### Test isolation
```python
@pytest.fixture
def temp_storage(tmp_path):
    """Chaque test a son propre dossier temporaire"""
    storage = tmp_path / "workly_memory_test"
    storage.mkdir()
    yield str(storage)
    # Cleanup automatique par pytest

def test_example(temp_storage):
    # temp_storage = "/tmp/pytest-xxx/test_example0/workly_memory_test"
    manager = MemoryManager(storage_dir=temp_storage)
    # → db_path = "/tmp/.../workly_memory_test/workly.db"
    # → Instance unique pour ce test ✅
```

### Vérification SQLite
```python
def test_persistence(memory_manager):
    memory_manager.add_message("user", "Test")

    # Vérifier fichier DB existe
    db_path = os.path.join(memory_manager.storage_dir, "workly.db")
    assert os.path.exists(db_path)

    # Vérifier données dans DB
    conversations = memory_manager.db.get_conversations()
    assert len(conversations) > 0
```

---

## ⚡ Optimisations

### Indexes
```sql
-- Déjà créés dans database.py
CREATE INDEX idx_conversations_timestamp ON conversations(timestamp);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_emotion_timestamp ON emotion_history(timestamp);
-- etc.
```

### PRAGMA optimizations
```python
# database.py - WorklyDatabase.__init__()
self.conn.execute("PRAGMA journal_mode=WAL")           # Write-Ahead Logging
self.conn.execute("PRAGMA synchronous=NORMAL")         # Balance perf/sécurité
self.conn.execute("PRAGMA cache_size=-64000")          # 64 MB cache
self.conn.execute("PRAGMA temp_store=MEMORY")          # Temp en RAM
self.conn.execute("PRAGMA mmap_size=268435456")        # Memory-mapped I/O
self.conn.execute("PRAGMA foreign_keys=ON")            # Intégrité référentielle
```

### Query optimization
```python
# AVANT (lent)
all_conversations = db.get_conversations()
recent = [c for c in all_conversations if c['timestamp'] > cutoff]

# APRÈS (rapide avec index)
recent = db.get_conversations(since=cutoff)
```

---

## 🐛 Debugging

### Vérifier taille DB
```python
import os
db_path = "data/memory/workly.db"
size_mb = os.path.getsize(db_path) / (1024 * 1024)
print(f"DB size: {size_mb:.2f} MB")
```

### Inspecter schéma
```python
cursor = db.conn.cursor()
tables = cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table'"
).fetchall()
print("Tables:", [t[0] for t in tables])

for table in tables:
    count = cursor.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
    print(f"  {table[0]}: {count} rows")
```

### EXPLAIN QUERY PLAN
```python
cursor = db.conn.cursor()
plan = cursor.execute(
    "EXPLAIN QUERY PLAN SELECT * FROM conversations WHERE user_id = 'default'"
).fetchall()
print(plan)
# Vérifier "USING INDEX" dans le plan
```

---

## 📦 Backup et restauration

### Backup manuel
```python
import shutil
shutil.copy("data/memory/workly.db", "backup/workly_backup.db")
```

### Backup SQLite natif
```python
import sqlite3
source = sqlite3.connect("data/memory/workly.db")
backup = sqlite3.connect("backup/workly_backup.db")
source.backup(backup)
backup.close()
source.close()
```

### Restauration
```python
# Remplacer DB actuelle par backup
shutil.copy("backup/workly_backup.db", "data/memory/workly.db")
```

---

## 🚨 Troubleshooting

### "Database is locked"
**Cause** : Connexion non fermée ou transaction en cours
**Solution** : Fermer connexions, commit transactions

### WAL trop gros
**Cause** : Checkpoint pas exécuté
**Solution** :
```python
db.conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
```

### Tests qui échouent aléatoirement
**Cause** : Contamination entre tests (même DB)
**Solution** : Vérifier fixtures `tmp_path`, nettoyer singletons

### Performances lentes
**Cause** : Pas d'indexes, requêtes non optimisées
**Solution** : `EXPLAIN QUERY PLAN`, ajouter indexes

---

## 📚 Ressources

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Python sqlite3](https://docs.python.org/3/library/sqlite3.html)
- [WAL Mode](https://www.sqlite.org/wal.html)
- [Numpy dtype](https://numpy.org/doc/stable/reference/arrays.dtypes.html)

---

**Guide complet pour maintenir et étendre l'architecture SQLite !** 🔧✨
