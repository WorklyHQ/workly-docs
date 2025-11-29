"""
database.py - Gestionnaire de base de données SQLite pour Workly

Migration Phase 6 : Remplacement JSON → SQLite
- Meilleure performance
- Transactions ACID (pas de corruption)
- Requêtes SQL optimisées
- Index automatiques

Tables :
- conversations : Messages utilisateur/assistant
- embeddings : Vecteurs sémantiques pour recherche
- facts : Faits extraits (noms, préférences, événements)
- segments : Résumés de conversations
- emotion_history : Historique émotionnel
- personality_traits : Traits de personnalité
- personality_evolution : Évolution personnalité

Author: Workly Team
Date: 17 novembre 2025
"""

import sqlite3
import json
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)


class WorklyDatabase:
    """
    Gestionnaire centralisé de la base de données SQLite.

    Fonctionnalités :
    - Création/migration automatique du schéma
    - Transactions ACID
    - Méthodes CRUD optimisées
    - Sérialisation numpy arrays (embeddings)
    - Backward compatibility avec JSON
    """

    def __init__(self, db_path: str = "data/memory/workly.db"):
        """
        Initialise la connexion à la base de données.

        Args:
            db_path: Chemin vers le fichier SQLite
        """
        self.db_path = db_path

        # Créer dossier si nécessaire
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Connexion avec paramètres optimisés
        self.conn = sqlite3.connect(
            db_path,
            check_same_thread=False,  # Pour utilisation multi-thread
            isolation_level=None,  # Autocommit mode
        )
        self.conn.row_factory = sqlite3.Row  # Résultats en dict

        # Optimisations SQLite
        self.conn.execute(
            "PRAGMA journal_mode=WAL"
        )  # Write-Ahead Logging (performance)
        self.conn.execute("PRAGMA synchronous=NORMAL")  # Balance perf/sécurité
        self.conn.execute("PRAGMA foreign_keys=ON")  # Intégrité référentielle

        # Créer schéma
        self._create_schema()

        logger.info(f"✅ Base de données SQLite initialisée : {db_path}")

    def _create_schema(self):
        """Crée toutes les tables et index."""
        cursor = self.conn.cursor()

        # Table conversations (messages)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                user_id TEXT DEFAULT 'desktop_user',
                source TEXT DEFAULT 'desktop',
                metadata TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_conversations_role ON conversations(role)"
        )

        # Table embeddings (vecteurs sémantiques)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                embedding BLOB NOT NULL,
                text TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_embeddings_timestamp ON embeddings(timestamp)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_embeddings_conversation ON embeddings(conversation_id)"
        )

        # Table facts (faits extraits)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL CHECK(category IN ('entities', 'preferences', 'events', 'relationships')),
                type TEXT NOT NULL,
                data TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                timestamp TEXT NOT NULL,
                source_message_id INTEGER,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (source_message_id) REFERENCES conversations(id) ON DELETE SET NULL
            )
        """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_facts_category ON facts(category)"
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_facts_type ON facts(type)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_facts_timestamp ON facts(timestamp)"
        )

        # Table segments (résumés)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS segments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                summary TEXT NOT NULL,
                message_count INTEGER NOT NULL DEFAULT 0,
                start_timestamp TEXT NOT NULL,
                end_timestamp TEXT NOT NULL,
                topics TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_segments_start ON segments(start_timestamp)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_segments_end ON segments(end_timestamp)"
        )

        # Table emotion_history
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS emotion_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emotion TEXT NOT NULL,
                intensity REAL NOT NULL,
                confidence REAL NOT NULL,
                source TEXT NOT NULL CHECK(source IN ('user', 'assistant')),
                message_preview TEXT,
                context TEXT,
                timestamp TEXT NOT NULL,
                user_id TEXT DEFAULT 'desktop_user',
                created_at TEXT DEFAULT (datetime('now'))
            )
        """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_emotions_timestamp ON emotion_history(timestamp)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_emotions_source ON emotion_history(source)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_emotions_user ON emotion_history(user_id)"
        )

        # Table personality_traits
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS personality_traits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trait_name TEXT NOT NULL UNIQUE,
                score REAL NOT NULL CHECK(score >= 0.0 AND score <= 1.0),
                description TEXT,
                last_updated TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """
        )

        # Table personality_evolution (historique changements)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS personality_evolution (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trait_name TEXT NOT NULL,
                old_score REAL NOT NULL,
                new_score REAL NOT NULL,
                reason TEXT,
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (trait_name) REFERENCES personality_traits(trait_name) ON DELETE CASCADE
            )
        """
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_personality_evolution_trait ON personality_evolution(trait_name)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_personality_evolution_timestamp ON personality_evolution(timestamp)"
        )

        self.conn.commit()
        logger.debug("✅ Schéma SQLite créé/vérifié")

    # ========================================================================
    # CONVERSATIONS
    # ========================================================================

    def add_conversation(
        self,
        role: str,
        content: str,
        timestamp: str,
        user_id: str = "desktop_user",
        source: str = "desktop",
        metadata: Optional[Dict] = None,
    ) -> int:
        """
        Ajoute un message de conversation.

        Args:
            role: 'user', 'assistant' ou 'system'
            content: Texte du message
            timestamp: ISO format timestamp
            user_id: ID utilisateur
            source: Source du message
            metadata: Métadonnées optionnelles (JSON)

        Returns:
            ID du message inséré
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO conversations (role, content, timestamp, user_id, source, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                role,
                content,
                timestamp,
                user_id,
                source,
                json.dumps(metadata) if metadata else None,
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_conversations(
        self,
        user_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        start_timestamp: Optional[str] = None,
        end_timestamp: Optional[str] = None,
    ) -> List[Dict]:
        """
        Récupère les conversations avec filtres.

        Args:
            user_id: Filtrer par utilisateur
            limit: Nombre max de résultats
            offset: Décalage pour pagination
            start_timestamp: Date de début
            end_timestamp: Date de fin

        Returns:
            Liste de conversations (dict)
        """
        cursor = self.conn.cursor()

        query = "SELECT * FROM conversations WHERE 1=1"
        params = []

        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)

        if start_timestamp:
            query += " AND timestamp >= ?"
            params.append(start_timestamp)

        if end_timestamp:
            query += " AND timestamp <= ?"
            params.append(end_timestamp)

        query += " ORDER BY timestamp DESC"

        if limit:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def get_conversation_count(self, user_id: Optional[str] = None) -> int:
        """Compte le nombre de conversations."""
        cursor = self.conn.cursor()
        if user_id:
            cursor.execute(
                "SELECT COUNT(*) FROM conversations WHERE user_id = ?", (user_id,)
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM conversations")
        return cursor.fetchone()[0]

    def delete_conversations_before(self, timestamp: str) -> int:
        """Supprime conversations avant une date."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM conversations WHERE timestamp < ?", (timestamp,))
        self.conn.commit()
        return cursor.rowcount

    # ========================================================================
    # EMBEDDINGS
    # ========================================================================

    def add_embedding(
        self,
        conversation_id: Optional[int],
        embedding: np.ndarray,
        text: str,
        timestamp: str,
    ) -> int:
        """
        Ajoute un embedding (vecteur sémantique).

        Args:
            conversation_id: ID du message associé
            embedding: Vecteur numpy
            text: Texte source
            timestamp: ISO format timestamp

        Returns:
            ID de l'embedding inséré
        """
        cursor = self.conn.cursor()

        # Sérialiser numpy array en bytes
        embedding_bytes = embedding.tobytes()

        cursor.execute(
            """
            INSERT INTO embeddings (conversation_id, embedding, text, timestamp)
            VALUES (?, ?, ?, ?)
        """,
            (conversation_id, embedding_bytes, text, timestamp),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_embeddings(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Récupère tous les embeddings.

        Args:
            limit: Nombre max de résultats

        Returns:
            Liste d'embeddings avec numpy arrays désérialisés
        """
        cursor = self.conn.cursor()

        query = "SELECT * FROM embeddings ORDER BY timestamp DESC"
        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query)
        rows = cursor.fetchall()

        results = []
        for row in rows:
            data = dict(row)
            # Désérialiser embedding bytes → numpy array
            embedding_bytes = data["embedding"]
            data["embedding"] = np.frombuffer(embedding_bytes, dtype=np.float32)
            results.append(data)

        return results

    def get_all_embeddings_matrix(self) -> Tuple[np.ndarray, List[int]]:
        """
        Récupère tous les embeddings comme matrice numpy.

        Returns:
            (embeddings_matrix, ids_list)
        """
        embeddings_data = self.get_embeddings()

        if not embeddings_data:
            return np.array([]), []

        embeddings_matrix = np.vstack([e["embedding"] for e in embeddings_data])
        ids = [e["id"] for e in embeddings_data]

        return embeddings_matrix, ids

    # ========================================================================
    # FACTS
    # ========================================================================

    def add_fact(
        self,
        category: str,
        type_: str,
        data: Dict,
        confidence: float = 1.0,
        timestamp: str = None,
        source_message_id: Optional[int] = None,
    ) -> int:
        """
        Ajoute un fait extrait.

        Args:
            category: 'entities', 'preferences', 'events', 'relationships'
            type_: Type spécifique du fait
            data: Données du fait (dict sérialisé en JSON)
            confidence: Score de confiance
            timestamp: ISO format timestamp
            source_message_id: ID du message source

        Returns:
            ID du fait inséré
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO facts (category, type, data, confidence, timestamp, source_message_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                category,
                type_,
                json.dumps(data),
                confidence,
                timestamp,
                source_message_id,
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_facts(
        self,
        category: Optional[str] = None,
        type_: Optional[str] = None,
        min_confidence: float = 0.0,
    ) -> List[Dict]:
        """
        Récupère les faits avec filtres.

        Args:
            category: Filtrer par catégorie
            type_: Filtrer par type
            min_confidence: Confiance minimum

        Returns:
            Liste de faits
        """
        cursor = self.conn.cursor()

        query = "SELECT * FROM facts WHERE confidence >= ?"
        params = [min_confidence]

        if category:
            query += " AND category = ?"
            params.append(category)

        if type_:
            query += " AND type = ?"
            params.append(type_)

        query += " ORDER BY timestamp DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        results = []
        for row in rows:
            data = dict(row)
            # Désérialiser JSON data
            data["data"] = json.loads(data["data"])
            results.append(data)

        return results

    # ========================================================================
    # SEGMENTS (Résumés)
    # ========================================================================

    def add_segment(
        self,
        summary: str,
        message_count: int,
        start_timestamp: str,
        end_timestamp: str,
        topics: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
    ) -> int:
        """Ajoute un segment (résumé de conversation)."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO segments (summary, message_count, start_timestamp, end_timestamp, topics, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                summary,
                message_count,
                start_timestamp,
                end_timestamp,
                json.dumps(topics) if topics else None,
                json.dumps(metadata) if metadata else None,
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_segments(self, limit: Optional[int] = None) -> List[Dict]:
        """Récupère les segments."""
        cursor = self.conn.cursor()

        query = "SELECT * FROM segments ORDER BY start_timestamp DESC"
        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query)
        rows = cursor.fetchall()

        results = []
        for row in rows:
            data = dict(row)
            if data["topics"]:
                data["topics"] = json.loads(data["topics"])
            if data["metadata"]:
                data["metadata"] = json.loads(data["metadata"])
            results.append(data)

        return results

    # ========================================================================
    # EMOTION HISTORY
    # ========================================================================

    def add_emotion(
        self,
        emotion: str,
        intensity: float,
        confidence: float,
        source: str,
        message_preview: str,
        context: str,
        timestamp: str,
        user_id: str = "desktop_user",
    ) -> int:
        """Ajoute une émotion à l'historique."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO emotion_history (emotion, intensity, confidence, source,
                                        message_preview, context, timestamp, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                emotion,
                intensity,
                confidence,
                source,
                message_preview,
                context,
                timestamp,
                user_id,
            ),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_emotions(
        self,
        user_id: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """Récupère l'historique émotionnel."""
        cursor = self.conn.cursor()

        query = "SELECT * FROM emotion_history WHERE 1=1"
        params = []

        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)

        if source:
            query += " AND source = ?"
            params.append(source)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def get_emotion_count(self, user_id: Optional[str] = None) -> int:
        """Compte le nombre d'émotions."""
        cursor = self.conn.cursor()
        if user_id:
            cursor.execute(
                "SELECT COUNT(*) FROM emotion_history WHERE user_id = ?", (user_id,)
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM emotion_history")
        return cursor.fetchone()[0]

    # ========================================================================
    # PERSONALITY
    # ========================================================================

    def set_personality_trait(
        self,
        trait_name: str,
        score: float,
        description: str = "",
        last_updated: str = None,
    ) -> int:
        """
        Définit ou met à jour un trait de personnalité.

        Args:
            trait_name: Nom du trait
            score: Score du trait (0.0-1.0)
            description: Description du trait
            last_updated: Timestamp personnalisé (optionnel, sinon utilise maintenant)
        """
        timestamp = last_updated or datetime.now().isoformat()
        cursor = self.conn.cursor()

        # Vérifier si existe
        cursor.execute(
            "SELECT score FROM personality_traits WHERE trait_name = ?", (trait_name,)
        )
        row = cursor.fetchone()

        if row:
            # Update (sans créer d'évolution ici, ça sera fait par add_personality_evolution)
            cursor.execute(
                """
                UPDATE personality_traits
                SET score = ?, description = ?, last_updated = ?
                WHERE trait_name = ?
            """,
                (score, description, timestamp, trait_name),
            )
        else:
            # Insert
            cursor.execute(
                """
                INSERT INTO personality_traits (trait_name, score, description, last_updated)
                VALUES (?, ?, ?, ?)
            """,
                (trait_name, score, description, timestamp),
            )

        self.conn.commit()
        return cursor.lastrowid

    def get_personality_traits(self) -> Dict[str, Dict]:
        """Récupère tous les traits de personnalité."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM personality_traits")
        rows = cursor.fetchall()

        return {row["trait_name"]: dict(row) for row in rows}

    def get_personality_evolution(
        self, trait_name: Optional[str] = None, limit: int = 100
    ) -> List[Dict]:
        """Récupère l'historique d'évolution de la personnalité."""
        cursor = self.conn.cursor()

        if trait_name:
            cursor.execute(
                """
                SELECT * FROM personality_evolution
                WHERE trait_name = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (trait_name, limit),
            )
        else:
            cursor.execute(
                """
                SELECT * FROM personality_evolution
                ORDER BY timestamp DESC
                LIMIT ?
            """,
                (limit,),
            )

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def add_personality_evolution(
        self, trait_name: str, old_score: float, new_score: float, reason: str = ""
    ) -> int:
        """
        Ajoute une entrée d'évolution de personnalité.

        Args:
            trait_name: Nom du trait
            old_score: Ancien score
            new_score: Nouveau score
            reason: Raison du changement

        Returns:
            ID de l'entrée créée
        """
        cursor = self.conn.cursor()
        timestamp = datetime.utcnow().isoformat()

        cursor.execute(
            """
            INSERT INTO personality_evolution
            (trait_name, old_score, new_score, reason, timestamp, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (trait_name, old_score, new_score, reason, timestamp, timestamp),
        )
        self.conn.commit()

        return cursor.lastrowid

    # ========================================================================
    # UTILITY
    # ========================================================================

    def execute_raw(self, query: str, params: Tuple = ()) -> List[Dict]:
        """Exécute une requête SQL brute."""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def vacuum(self):
        """Optimise la base de données (compression, réindexation)."""
        self.conn.execute("VACUUM")
        logger.info("✅ Base de données optimisée (VACUUM)")

    def close(self):
        """Ferme la connexion à la base de données."""
        self.conn.close()
        logger.info("✅ Connexion base de données fermée")

    def __repr__(self):
        return f"<WorklyDatabase: {self.db_path}>"


# ============================================================================
# SINGLETON (modifié pour supporter DBs multiples)
# ============================================================================

_db_instances: Dict[str, WorklyDatabase] = {}


def get_database(db_path: str = "data/memory/workly.db") -> WorklyDatabase:
    """
    Récupère l'instance de base de données pour un chemin donné.

    Utilise un pattern singleton par chemin : chaque db_path unique
    a sa propre instance. Cela permet l'isolation des tests.

    Args:
        db_path: Chemin vers le fichier SQLite

    Returns:
        Instance WorklyDatabase
    """
    global _db_instances

    # Normaliser le chemin (absolu)
    db_path_abs = os.path.abspath(db_path)

    if db_path_abs not in _db_instances:
        _db_instances[db_path_abs] = WorklyDatabase(db_path)

    return _db_instances[db_path_abs]
