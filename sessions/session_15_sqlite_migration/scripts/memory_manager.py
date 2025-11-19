"""
memory_manager.py - Gestionnaire central de mémoire long-terme

Ce module orchestre toutes les fonctionnalités de mémoire :
- Stockage persistant (SQLite) de conversations, faits, embeddings
- Extraction automatique de faits (via FactExtractor)
- Résumés automatiques (via ConversationSummarizer)
- Recherche sémantique (via sentence-transformers)

Architecture :
- Conversations stockées dans base SQLite avec résumés
- Faits extraits et indexés par type
- Embeddings pour recherche sémantique rapide
- Résumés générés automatiquement tous les 20-30 messages

Migration Phase 6 : JSON → SQLite (performance + ACID)
"""

import json
import os
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
import numpy as np

# Sentence-transformers pour embeddings sémantiques
try:
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Modules Workly
try:
    from .fact_extractor import FactExtractor
    from .conversation_summarizer import ConversationSummarizer
    from .database import get_database
except ImportError:
    # Fallback pour exécution standalone (test)
    from fact_extractor import FactExtractor
    from conversation_summarizer import ConversationSummarizer
    from database import get_database


class MemoryManager:
    """
    Gestionnaire central de la mémoire long-terme

    Responsabilités :
    - Stocker conversations en segments avec résumés
    - Extraire et indexer faits (entités, préférences, événements)
    - Générer embeddings pour recherche sémantique
    - Récupérer contexte pertinent pour nouvelle requête
    """

    def __init__(
        self,
        storage_dir: str = "data/memory",
        llm_callback=None,
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        """
        Initialise le gestionnaire de mémoire

        Args:
            storage_dir: Dossier de stockage (base SQLite + cache)
            llm_callback: Callback pour générer texte via LLM (pour résumés)
            embedding_model: Nom du modèle sentence-transformers
        """
        self.storage_dir = storage_dir
        self.llm_callback = llm_callback

        # Créer dossier si nécessaire
        os.makedirs(storage_dir, exist_ok=True)

        # Base de données SQLite
        db_path = os.path.join(storage_dir, "workly.db")
        self.db = get_database(db_path)

        # Chemins des fichiers de persistance (gardés pour backward compatibility)
        self.conversations_file = os.path.join(storage_dir, "conversations.json")
        self.facts_file = os.path.join(storage_dir, "facts.json")
        self.embeddings_file = os.path.join(storage_dir, "embeddings.json")

        # Modules d'extraction
        self.fact_extractor = FactExtractor()
        self.summarizer = ConversationSummarizer(
            llm_callback=llm_callback, max_tokens=200
        )

        # Modèle d'embeddings sémantiques
        self.embedding_model_name = embedding_model
        self.embedding_model = None
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer(embedding_model)
                print(f"✅ Modèle d'embeddings chargé: {embedding_model}")
            except Exception as e:
                print(f"⚠️ Erreur chargement modèle embeddings: {e}")
        else:
            print(
                "⚠️ sentence-transformers non disponible - recherche sémantique désactivée"
            )

        # Cache en mémoire (chargé depuis SQLite)
        self.conversations = {"segments": self._load_segments_from_db()}
        self.facts = self._load_facts_from_db()
        self.embeddings_data = {"embeddings": []}  # Pas de cache (requêtes directes DB)

        # État de la conversation courante (en mémoire)
        self.current_conversation = []
        self.current_segment_id = self._get_next_segment_id()

        # Configuration
        self.max_messages_per_segment = 30
        self.auto_summarize_threshold = 20

    # ========== MÉTHODES HELPER CHARGEMENT ==========

    def _load_segments_from_db(self) -> List[Dict[str, Any]]:
        """Charge tous les segments depuis SQLite"""
        try:
            db_segments = self.db.get_segments()
            return [
                {
                    "segment_id": seg["segment_id"],
                    "messages": (
                        json.loads(seg["messages"])
                        if isinstance(seg["messages"], str)
                        else seg["messages"]
                    ),
                    "summary": (
                        json.loads(seg["summary"])
                        if isinstance(seg["summary"], str)
                        else seg["summary"]
                    ),
                    "created_at": seg["created_at"],
                    "message_count": seg["message_count"],
                }
                for seg in db_segments
            ]
        except Exception as e:
            print(f"⚠️ Erreur chargement segments: {e}")
            return []

    def _load_facts_from_db(self) -> Dict[str, List[Dict[str, Any]]]:
        """Charge tous les faits depuis SQLite"""
        try:
            db_facts = self.db.get_facts()
            facts = {
                "entities": [],
                "preferences": [],
                "events": [],
                "relationships": [],
            }
            for fact in db_facts:
                fact_dict = {
                    "category": fact["category"],
                    "content": (
                        json.loads(fact["content"])
                        if isinstance(fact["content"], str)
                        else fact["content"]
                    ),
                    "extracted_at": fact["extracted_at"],
                }
                # Aplatir le contenu dans le dict
                fact_dict.update(fact_dict.pop("content"))
                facts[fact["category"]].append(fact_dict)
            return facts
        except Exception as e:
            print(f"⚠️ Erreur chargement faits: {e}")
            return {
                "entities": [],
                "preferences": [],
                "events": [],
                "relationships": [],
            }

    # ========== STOCKAGE DE CONVERSATIONS ==========

    def add_message(self, role: str, content: str) -> None:
        """
        Ajoute un message à la conversation courante

        Args:
            role: 'user' ou 'assistant'
            content: Contenu du message
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Stocker dans SQLite
        self.db.add_conversation(
            role=role,
            content=content,
            timestamp=message["timestamp"],
            user_id="default",
            metadata=json.dumps({"segment_id": self.current_segment_id}),
        )

        self.current_conversation.append(message)

        # Extraire faits du message utilisateur
        if role == "user":
            self._extract_and_store_facts(content)

        # Vérifier si besoin de résumer/segmenter
        if len(self.current_conversation) >= self.auto_summarize_threshold:
            self._auto_summarize_and_segment()

    def _auto_summarize_and_segment(self) -> None:
        """
        Génère résumé automatique et crée nouveau segment
        """
        if len(self.current_conversation) < self.summarizer.min_messages_for_summary:
            return

        # Générer résumé
        summary_data = self.summarizer.summarize(
            self.current_conversation, include_keypoints=True
        )

        # Créer segment
        segment = {
            "segment_id": self.current_segment_id,
            "messages": self.current_conversation.copy(),
            "summary": summary_data,
            "created_at": datetime.utcnow().isoformat(),
            "message_count": len(self.current_conversation),
        }

        # Sauvegarder dans SQLite
        start_ts = (
            self.current_conversation[0]["timestamp"]
            if self.current_conversation
            else datetime.utcnow().isoformat()
        )
        end_ts = (
            self.current_conversation[-1]["timestamp"]
            if self.current_conversation
            else datetime.utcnow().isoformat()
        )

        self.db.add_segment(
            summary=summary_data.get("summary", ""),
            message_count=len(self.current_conversation),
            start_timestamp=start_ts,
            end_timestamp=end_ts,
            topics=summary_data.get("keypoints", []),
            metadata={
                "segment_id": self.current_segment_id,
                "full_summary": summary_data,
            },
        )

        # Mettre à jour cache
        self.conversations["segments"].append(segment)

        # Générer embedding du résumé
        if self.embedding_model and summary_data.get("summary"):
            self._generate_and_store_embedding(
                text=summary_data["summary"],
                segment_id=self.current_segment_id,
                metadata={"type": "segment_summary"},
            )

        # Réinitialiser conversation courante
        self.current_conversation = []
        self.current_segment_id = self._get_next_segment_id()

        print(f"✅ Segment auto-créé avec résumé ({len(segment['messages'])} messages)")

    def force_segment_creation(self) -> Dict[str, Any]:
        """
        Force la création d'un segment même si seuil non atteint

        Returns:
            Données du segment créé
        """
        if not self.current_conversation:
            return {"error": "Aucun message dans conversation courante"}

        self._auto_summarize_and_segment()
        return (
            self.conversations["segments"][-1] if self.conversations["segments"] else {}
        )

    # ========== EXTRACTION DE FAITS ==========

    def _extract_and_store_facts(self, message: str) -> None:
        """
        Extrait faits d'un message et les stocke

        Args:
            message: Message utilisateur à analyser
        """
        facts = self.fact_extractor.extract_all_facts(message)

        # Ajouter timestamp à tous les faits
        timestamp = datetime.utcnow().isoformat()

        # Stocker entités
        for entity in facts["entities"]:
            entity["extracted_at"] = timestamp
            self._add_or_update_entity(entity)
            # Sauver dans SQLite
            self.db.add_fact(
                category="entities",
                type_=entity.get("entity_type", "unknown"),
                data=entity,
                timestamp=timestamp,
            )

        # Stocker préférences
        for pref in facts["preferences"]:
            pref["extracted_at"] = timestamp
            self.facts["preferences"].append(pref)
            self.db.add_fact(
                category="preferences",
                type_=pref.get("category", "general"),
                data=pref,
                timestamp=timestamp,
            )

        # Stocker événements
        for event in facts["events"]:
            event["extracted_at"] = timestamp
            self.facts["events"].append(event)
            self.db.add_fact(
                category="events",
                type_=event.get("event_type", "general"),
                data=event,
                timestamp=timestamp,
            )

        # Stocker relations
        for rel in facts["relationships"]:
            rel["extracted_at"] = timestamp
            self.facts["relationships"].append(rel)
            self.db.add_fact(
                category="relationships",
                type_=rel.get("relationship_type", "general"),
                data=rel,
                timestamp=timestamp,
            )

    def _add_or_update_entity(self, entity: Dict[str, Any]) -> None:
        """
        Ajoute ou met à jour une entité (incrémente occurrences si existe)

        Args:
            entity: Dictionnaire entité
        """
        # Chercher entité existante
        for existing in self.facts["entities"]:
            if (
                existing["entity_type"] == entity["entity_type"]
                and existing["value"].lower() == entity["value"].lower()
            ):
                # Incrémenter occurrences
                existing["occurrences"] += 1
                existing["last_seen"] = entity.get(
                    "first_seen", datetime.utcnow().isoformat()
                )
                return

        # Nouvelle entité
        self.facts["entities"].append(entity)

    # ========== RECHERCHE SÉMANTIQUE ==========

    def _generate_and_store_embedding(
        self,
        text: str,
        segment_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Génère embedding d'un texte et le stocke

        Args:
            text: Texte à encoder
            segment_id: ID du segment associé (optionnel)
            metadata: Métadonnées supplémentaires
        """
        if not self.embedding_model:
            return

        # Générer embedding
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)

        # Stocker dans SQLite
        self.db.add_embedding(
            conversation_id=None,  # Pas de lien direct avec message
            embedding=embedding,  # numpy array
            text=text[:200],  # Préview
            timestamp=datetime.utcnow().isoformat(),
        )

    def search_relevant_context(
        self, query: str, top_k: int = 3, min_similarity: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        Recherche contexte pertinent pour une requête

        Args:
            query: Requête utilisateur
            top_k: Nombre de résultats à retourner
            min_similarity: Seuil de similarité minimale (0-1)

        Returns:
            Liste de segments/faits pertinents triés par similarité
        """
        # Charger embeddings depuis SQLite
        db_embeddings = self.db.get_embeddings()

        if not self.embedding_model or not db_embeddings:
            # Fallback : retourner derniers segments
            return self._get_recent_segments(top_k)

        # Générer embedding de la requête
        query_embedding = self.embedding_model.encode(query, convert_to_numpy=True)

        # Calculer similarités cosinus
        results = []
        for entry in db_embeddings:
            stored_embedding = entry["embedding"]  # déjà numpy array

            # Similarité cosinus
            similarity = self._cosine_similarity(query_embedding, stored_embedding)

            if similarity >= min_similarity:
                results.append(
                    {
                        "similarity": float(similarity),
                        "segment_id": entry.get("segment_id", "unknown"),
                        "text_preview": entry["text"],
                        "metadata": {},  # Pas de metadata dans le format actuel
                    }
                )

        # Trier par similarité décroissante
        results.sort(key=lambda x: x["similarity"], reverse=True)

        # Limiter au top_k
        return results[:top_k]

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calcule similarité cosinus entre 2 vecteurs

        Args:
            vec1, vec2: Vecteurs numpy

        Returns:
            Score de similarité (0-1)
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _get_recent_segments(self, count: int) -> List[Dict[str, Any]]:
        """
        Récupère les N derniers segments

        Args:
            count: Nombre de segments à retourner

        Returns:
            Liste de segments récents
        """
        segments = self.conversations.get("segments", [])
        recent = segments[-count:] if len(segments) > count else segments

        # Formater pour compatibilité avec search_relevant_context
        return [
            {
                "similarity": 1.0,  # Placeholder
                "segment_id": seg["segment_id"],
                "text_preview": seg["summary"].get("summary", "")[:200],
                "metadata": {"type": "recent_segment"},
            }
            for seg in recent
        ]

    # ========== RÉCUPÉRATION DE CONTEXTE ==========

    def get_context_for_prompt(
        self,
        query: str,
        include_facts: bool = True,
        include_segments: bool = True,
        max_tokens: int = 1000,
    ) -> str:
        """
        Construit contexte enrichi pour un prompt

        Args:
            query: Requête utilisateur
            include_facts: Inclure faits extraits
            include_segments: Inclure segments pertinents
            max_tokens: Budget de tokens approximatif

        Returns:
            Contexte formaté prêt pour prompt
        """
        context_parts = []

        # 1. Segments pertinents (via recherche sémantique)
        if include_segments:
            relevant_segments = self.search_relevant_context(query, top_k=2)

            if relevant_segments:
                context_parts.append("=== Conversations Précédentes ===")
                for seg_data in relevant_segments:
                    segment = self._get_segment_by_id(seg_data["segment_id"])
                    if segment and segment.get("summary"):
                        formatted = self.summarizer.format_summary_for_context(
                            segment["summary"]
                        )
                        context_parts.append(formatted)

        # 2. Faits pertinents
        if include_facts:
            facts_context = self._format_relevant_facts(query)
            if facts_context:
                context_parts.append("\n=== Faits Mémorisés ===")
                context_parts.append(facts_context)

        # 3. Conversation courante (aperçu)
        if self.current_conversation:
            context_parts.append("\n=== Conversation Actuelle ===")
            recent_msgs = self.current_conversation[-3:]  # 3 derniers messages
            for msg in recent_msgs:
                role = msg["role"].capitalize()
                content = msg["content"][:100]
                context_parts.append(f"{role}: {content}...")

        # Joindre et limiter taille
        full_context = "\n\n".join(context_parts)

        # Approximation tokens (1 token ≈ 4 chars)
        if len(full_context) > max_tokens * 4:
            full_context = full_context[: max_tokens * 4] + "\n[...contexte tronqué...]"

        return full_context

    def _format_relevant_facts(self, query: str) -> str:
        """
        Formate faits pertinents pour une requête

        Args:
            query: Requête utilisateur

        Returns:
            Faits formatés en texte
        """
        facts_text = []
        query_lower = query.lower()

        # Préférences
        prefs = self.facts.get("preferences", [])
        if prefs:
            facts_text.append("Préférences :")
            for pref in prefs[-5:]:  # 5 dernières
                sentiment = "aime" if pref["sentiment"] == "positive" else "n'aime pas"
                facts_text.append(
                    f"  - {sentiment} {pref['subject']} ({pref['category']})"
                )

        # Entités fréquentes
        entities = self.facts.get("entities", [])
        if entities:
            # Trier par occurrences
            top_entities = sorted(
                entities, key=lambda e: e.get("occurrences", 1), reverse=True
            )[:5]
            facts_text.append("\nEntités mentionnées :")
            for ent in top_entities:
                facts_text.append(
                    f"  - {ent['value']} ({ent['entity_type']}, {ent.get('occurrences', 1)}x)"
                )

        # Événements récents
        events = self.facts.get("events", [])
        if events:
            recent_events = events[-3:]  # 3 derniers
            facts_text.append("\nÉvénements récents :")
            for evt in recent_events:
                facts_text.append(f"  - {evt['description']}")

        return "\n".join(facts_text) if facts_text else ""

    def _get_segment_by_id(self, segment_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un segment par son ID

        Args:
            segment_id: ID du segment

        Returns:
            Segment ou None si non trouvé
        """
        for segment in self.conversations.get("segments", []):
            if segment["segment_id"] == segment_id:
                return segment
        return None

    # ========== GESTION DE FICHIERS JSON ==========

    def _load_json(self, filepath: str, default: Any = None) -> Any:
        """
        Charge un fichier JSON

        Args:
            filepath: Chemin du fichier
            default: Valeur par défaut si fichier absent

        Returns:
            Données chargées ou default
        """
        if not os.path.exists(filepath):
            return default if default is not None else {}

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Erreur chargement {filepath}: {e}")
            return default if default is not None else {}

    def _save_json(self, filepath: str, data: Any) -> None:
        """
        Sauvegarde données en JSON

        Args:
            filepath: Chemin du fichier
            data: Données à sauvegarder
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde {filepath}: {e}")

    def _get_next_segment_id(self) -> str:
        """
        Génère ID pour prochain segment

        Returns:
            ID unique (format: segment_YYYYMMDD_HHMMSS_XXX)
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        segment_count = len(self.conversations.get("segments", []))
        return f"segment_{timestamp}_{segment_count:03d}"

    # ========== STATS & DEBUG ==========

    def get_stats(self) -> Dict[str, Any]:
        """
        Retourne statistiques sur la mémoire

        Returns:
            Dict avec stats (segments, faits, embeddings, etc.)
        """
        return {
            "segments_count": len(self.conversations.get("segments", [])),
            "current_conversation_length": len(self.current_conversation),
            "entities_count": len(self.facts.get("entities", [])),
            "preferences_count": len(self.facts.get("preferences", [])),
            "events_count": len(self.facts.get("events", [])),
            "relationships_count": len(self.facts.get("relationships", [])),
            "embeddings_count": len(self.db.get_embeddings()),
            "embedding_model": self.embedding_model_name,
            "embedding_available": self.embedding_model is not None,
            "storage_dir": self.storage_dir,
            "database": "SQLite (workly.db)",
        }


# --- Exemple d'utilisation ---
if __name__ == "__main__":
    # Mock LLM callback pour test
    def mock_llm(prompt: str) -> str:
        return "Résumé de test : discussion sur l'IA et la mémoire long-terme."

    # Test basique
    print("=== Test MemoryManager ===\n")

    manager = MemoryManager(storage_dir="data/memory_test", llm_callback=mock_llm)

    # Ajouter messages
    print("1. Ajout de messages:")
    manager.add_message("user", "J'adore la programmation Python !")
    manager.add_message(
        "assistant", "C'est génial ! Qu'est-ce que tu aimes particulièrement ?"
    )
    manager.add_message(
        "user", "Les libraries comme numpy et pandas sont super utiles."
    )
    print("   ✅ 3 messages ajoutés\n")

    # Stats
    print("2. Statistiques:")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print()

    # Contexte
    print("3. Contexte pour prompt:")
    context = manager.get_context_for_prompt("Parle-moi de Python", max_tokens=500)
    print(context[:300] + "..." if len(context) > 300 else context)
