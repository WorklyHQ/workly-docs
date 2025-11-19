"""
migrate_json_to_sqlite.py - Script de migration JSON → SQLite

Migre toutes les données JSON existantes vers la nouvelle base SQLite.
Sauvegarde les anciens fichiers JSON avant migration.

Usage:
    python src/ai/migrate_json_to_sqlite.py

Author: Workly Team
Date: 17 novembre 2025
"""

import os
import json
import shutil
import numpy as np
from datetime import datetime
from pathlib import Path
import logging

from src.ai.database import get_database

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class JSONToSQLiteMigrator:
    """Migre les données JSON vers SQLite sans perte."""

    def __init__(
        self, json_dir: str = "data/memory", backup_dir: str = "data/memory/json_backup"
    ):
        self.json_dir = Path(json_dir)
        self.backup_dir = Path(backup_dir)
        self.db = get_database()

        # Fichiers JSON à migrer
        self.json_files = {
            "conversations": self.json_dir / "conversations.json",
            "embeddings": self.json_dir / "embeddings.json",
            "facts": self.json_dir / "facts.json",
            "segments": self.json_dir / "segments.json",
            "emotion_history": self.json_dir / "emotion_history.json",
            "personality": self.json_dir / "personality.json",
        }

        self.stats = {
            "conversations": 0,
            "embeddings": 0,
            "facts": 0,
            "segments": 0,
            "emotions": 0,
            "personality_traits": 0,
            "errors": [],
        }

    def backup_json_files(self):
        """Sauvegarde tous les fichiers JSON avant migration."""
        logger.info("📦 Sauvegarde des fichiers JSON...")

        self.backup_dir.mkdir(parents=True, exist_ok=True)

        for name, filepath in self.json_files.items():
            if filepath.exists():
                backup_path = self.backup_dir / filepath.name
                shutil.copy2(filepath, backup_path)
                logger.info(f"  ✅ Sauvegardé : {filepath.name} → {backup_path}")
            else:
                logger.warning(f"  ⚠️ Fichier non trouvé : {filepath}")

        logger.info(f"✅ Sauvegarde terminée dans : {self.backup_dir}")

    def load_json_safe(self, filepath: Path) -> any:
        """Charge un fichier JSON de manière sécurisée."""
        if not filepath.exists():
            logger.warning(f"⚠️ Fichier non trouvé : {filepath}")
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur JSON dans {filepath}: {e}")
            self.stats["errors"].append(f"JSON decode error: {filepath}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur lecture {filepath}: {e}")
            self.stats["errors"].append(f"Read error: {filepath}")
            return None

    def migrate_conversations(self):
        """Migre conversations.json → table conversations."""
        logger.info("\n🔄 Migration des conversations...")

        data = self.load_json_safe(self.json_files["conversations"])
        if not data:
            logger.warning("  ⚠️ Aucune conversation à migrer")
            return

        # Format attendu : liste de messages
        conversations = data if isinstance(data, list) else []

        for msg in conversations:
            try:
                self.db.add_conversation(
                    role=msg.get("role", "user"),
                    content=msg.get("content", ""),
                    timestamp=msg.get("timestamp", datetime.now().isoformat()),
                    user_id=msg.get("user_id", "desktop_user"),
                    source=msg.get("source", "desktop"),
                    metadata=msg.get("metadata"),
                )
                self.stats["conversations"] += 1
            except Exception as e:
                logger.error(f"  ❌ Erreur migration message : {e}")
                self.stats["errors"].append(f"Conversation error: {e}")

        logger.info(f"  ✅ {self.stats['conversations']} conversations migrées")

    def migrate_embeddings(self):
        """Migre embeddings.json → table embeddings."""
        logger.info("\n🔄 Migration des embeddings...")

        data = self.load_json_safe(self.json_files["embeddings"])
        if not data:
            logger.warning("  ⚠️ Aucun embedding à migrer")
            return

        # Format attendu : dict avec 'embeddings' et 'texts'
        embeddings_list = data.get("embeddings", [])
        texts_list = data.get("texts", [])
        timestamps_list = data.get("timestamps", [])

        for i, (embedding, text) in enumerate(zip(embeddings_list, texts_list)):
            try:
                # Convertir liste → numpy array
                embedding_array = np.array(embedding, dtype=np.float32)

                # Timestamp
                timestamp = (
                    timestamps_list[i]
                    if i < len(timestamps_list)
                    else datetime.now().isoformat()
                )

                self.db.add_embedding(
                    conversation_id=None,  # Pas de lien direct
                    embedding=embedding_array,
                    text=text,
                    timestamp=timestamp,
                )
                self.stats["embeddings"] += 1
            except Exception as e:
                logger.error(f"  ❌ Erreur migration embedding {i}: {e}")
                self.stats["errors"].append(f"Embedding error: {e}")

        logger.info(f"  ✅ {self.stats['embeddings']} embeddings migrés")

    def migrate_facts(self):
        """Migre facts.json → table facts."""
        logger.info("\n🔄 Migration des faits...")

        data = self.load_json_safe(self.json_files["facts"])
        if not data:
            logger.warning("  ⚠️ Aucun fait à migrer")
            return

        # Format attendu : dict avec catégories
        for category in ["entities", "preferences", "events", "relationships"]:
            facts_in_category = data.get(category, [])

            for fact in facts_in_category:
                try:
                    self.db.add_fact(
                        category=category,
                        type_=fact.get("type", "unknown"),
                        data=fact.get("data", {}),
                        confidence=fact.get("confidence", 1.0),
                        timestamp=fact.get("timestamp", datetime.now().isoformat()),
                    )
                    self.stats["facts"] += 1
                except Exception as e:
                    logger.error(f"  ❌ Erreur migration fait : {e}")
                    self.stats["errors"].append(f"Fact error: {e}")

        logger.info(f"  ✅ {self.stats['facts']} faits migrés")

    def migrate_segments(self):
        """Migre segments.json → table segments."""
        logger.info("\n🔄 Migration des segments...")

        data = self.load_json_safe(self.json_files["segments"])
        if not data:
            logger.warning("  ⚠️ Aucun segment à migrer")
            return

        # Format attendu : liste de segments
        segments = data if isinstance(data, list) else []

        for segment in segments:
            try:
                self.db.add_segment(
                    summary=segment.get("summary", ""),
                    message_count=segment.get("message_count", 0),
                    start_timestamp=segment.get(
                        "start_timestamp", datetime.now().isoformat()
                    ),
                    end_timestamp=segment.get(
                        "end_timestamp", datetime.now().isoformat()
                    ),
                    topics=segment.get("topics"),
                    metadata=segment.get("metadata"),
                )
                self.stats["segments"] += 1
            except Exception as e:
                logger.error(f"  ❌ Erreur migration segment : {e}")
                self.stats["errors"].append(f"Segment error: {e}")

        logger.info(f"  ✅ {self.stats['segments']} segments migrés")

    def migrate_emotions(self):
        """Migre emotion_history.json → table emotion_history."""
        logger.info("\n🔄 Migration de l'historique émotionnel...")

        data = self.load_json_safe(self.json_files["emotion_history"])
        if not data:
            logger.warning("  ⚠️ Aucune émotion à migrer")
            return

        # Format attendu : liste d'émotions
        emotions = data if isinstance(data, list) else []

        for emotion in emotions:
            try:
                self.db.add_emotion(
                    emotion=emotion.get("emotion", "neutral"),
                    intensity=emotion.get("intensity", 0.5),
                    confidence=emotion.get("confidence", 1.0),
                    source=emotion.get("source", "user"),
                    message_preview=emotion.get("message_preview", ""),
                    context=emotion.get("context", ""),
                    timestamp=emotion.get("timestamp", datetime.now().isoformat()),
                    user_id=emotion.get("user_id", "desktop_user"),
                )
                self.stats["emotions"] += 1
            except Exception as e:
                logger.error(f"  ❌ Erreur migration émotion : {e}")
                self.stats["errors"].append(f"Emotion error: {e}")

        logger.info(f"  ✅ {self.stats['emotions']} émotions migrées")

    def migrate_personality(self):
        """Migre personality.json → tables personality_traits + personality_evolution."""
        logger.info("\n🔄 Migration de la personnalité...")

        data = self.load_json_safe(self.json_files["personality"])
        if not data:
            logger.warning("  ⚠️ Aucune personnalité à migrer")
            return

        # Format attendu : dict avec traits
        personality = data.get("personality", {})

        for trait_name, trait_data in personality.items():
            try:
                # Si c'est juste un score
                if isinstance(trait_data, (int, float)):
                    score = float(trait_data)
                    description = ""
                # Si c'est un dict complet
                elif isinstance(trait_data, dict):
                    score = float(trait_data.get("score", 0.5))
                    description = trait_data.get("description", "")
                else:
                    logger.warning(f"  ⚠️ Format trait inconnu : {trait_name}")
                    continue

                self.db.set_personality_trait(
                    trait_name=trait_name, score=score, description=description
                )
                self.stats["personality_traits"] += 1
            except Exception as e:
                logger.error(f"  ❌ Erreur migration trait {trait_name}: {e}")
                self.stats["errors"].append(f"Personality error: {e}")

        logger.info(
            f"  ✅ {self.stats['personality_traits']} traits de personnalité migrés"
        )

    def print_summary(self):
        """Affiche le résumé de la migration."""
        logger.info("\n" + "=" * 60)
        logger.info("📊 RÉSUMÉ DE LA MIGRATION")
        logger.info("=" * 60)
        logger.info(f"✅ Conversations      : {self.stats['conversations']}")
        logger.info(f"✅ Embeddings         : {self.stats['embeddings']}")
        logger.info(f"✅ Faits              : {self.stats['facts']}")
        logger.info(f"✅ Segments           : {self.stats['segments']}")
        logger.info(f"✅ Émotions           : {self.stats['emotions']}")
        logger.info(f"✅ Traits personnalité: {self.stats['personality_traits']}")

        total = sum([v for k, v in self.stats.items() if k != "errors"])
        logger.info("-" * 60)
        logger.info(f"📦 TOTAL              : {total} éléments migrés")

        if self.stats["errors"]:
            logger.warning(f"\n⚠️ {len(self.stats['errors'])} erreurs rencontrées :")
            for error in self.stats["errors"][:10]:  # Max 10 erreurs affichées
                logger.warning(f"  - {error}")
        else:
            logger.info("\n✅ Migration réussie sans erreur !")

        logger.info("=" * 60)
        logger.info(f"📁 Fichiers JSON sauvegardés dans : {self.backup_dir}")
        logger.info("=" * 60)

    def run(self):
        """Lance la migration complète."""
        logger.info("\n" + "=" * 60)
        logger.info("🚀 MIGRATION JSON → SQLite")
        logger.info("=" * 60)

        # Étape 1 : Sauvegarde
        self.backup_json_files()

        # Étape 2 : Migrations
        self.migrate_conversations()
        self.migrate_embeddings()
        self.migrate_facts()
        self.migrate_segments()
        self.migrate_emotions()
        self.migrate_personality()

        # Étape 3 : Résumé
        self.print_summary()

        # Optimiser la base
        logger.info("\n🔧 Optimisation de la base de données...")
        self.db.vacuum()

        logger.info("\n🎉 Migration terminée !")
        logger.info(
            "💡 Les anciens fichiers JSON sont sauvegardés et peuvent être supprimés plus tard."
        )


def main():
    """Point d'entrée du script."""
    print("\n" + "=" * 60)
    print("🎭 Workly - Migration JSON vers SQLite")
    print("=" * 60)
    print("\n⚠️  ATTENTION : Ce script va migrer toutes les données JSON vers SQLite.")
    print("📦 Les fichiers JSON seront sauvegardés dans data/memory/json_backup/")
    print()

    response = input("Continuer ? (o/n) : ").strip().lower()

    if response != "o":
        print("\n❌ Migration annulée.")
        return

    try:
        migrator = JSONToSQLiteMigrator()
        migrator.run()
    except Exception as e:
        logger.error(f"\n❌ ERREUR FATALE : {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
