"""
Chat Engine pour Workly (Kira)

Moteur conversationnel unifié qui orchestre :
- Mémoire conversationnelle court-terme (ConversationMemory)
- Mémoire long-terme avancée (MemoryManager) - Phase 1
- Personnalité évolutive (PersonalityEngine) - Phase 2
- Analyse émotionnelle avancée (EmotionAnalyzer) - Phase 3
- Génération LLM (ModelManager)
- Construction prompts avec contexte
- Sauvegarde automatique des conversations

Phases IA :
- Phase 1 : Mémoire long-terme (résumés, faits, recherche sémantique)
- Phase 2 : Personnalité évolutive (6 traits, adaptation contexte)
- Phase 3 : Émotions avancées (composées, mémoire émotionnelle, transitions)
"""

import logging
import os
from typing import Optional, Dict, List, Any
from dataclasses import dataclass

from .memory import ConversationMemory, get_memory
from .model_manager import ModelManager, get_model_manager
from .config import AIConfig, get_config
from .memory_manager import MemoryManager
from .personality_engine import PersonalityEngine
from .emotion_analyzer import EmotionAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class ChatResponse:
    """Réponse du chat engine"""

    response: str  # Texte généré par le modèle
    emotion: str  # Émotion détectée ('joy', 'angry', etc.)
    tokens_used: int  # Nombre approximatif de tokens
    context_messages: int  # Nombre de messages dans le contexte
    processing_time: float  # Temps de traitement en secondes


# EmotionDetector supprimé - remplacé par EmotionAnalyzer (Phase 3)


class ChatEngine:
    """
    Détecteur d'émotions basique par mots-clés

    Analyse le texte généré et retourne l'émotion dominante.
    Version simple mais efficace pour Workly.
    """

    # Mots-clés par émotion (français)
    EMOTION_KEYWORDS = {
        "joy": [
            "heureux",
            "heureuse",
            "content",
            "contente",
            "super",
            "génial",
            "excellent",
            "parfait",
            "cool",
            "top",
            "joie",
            "merveilleux",
            "😊",
            "😄",
            "😁",
            "🎉",
            "✨",
            "🥰",
            "😍",
            "🤗",
            "réjoui",
            "enchanté",
            "ravi",
            "formidable",
            "magnifique",
        ],
        "angry": [
            "énervé",
            "énervée",
            "colère",
            "furieux",
            "furieuse",
            "agacé",
            "irrité",
            "fâché",
            "rage",
            "mécontent",
            "contrarié",
            "agaçant",
            "😠",
            "😡",
            "🤬",
            "grrr",
            "argh",
            "pfff",
            "exaspéré",
            "frustré",
            "indigné",
            "erreur",
            "problème",
        ],
        "sorrow": [
            "triste",
            "désolé",
            "désolée",
            "dommage",
            "malheureusement",
            "hélas",
            "peine",
            "chagrin",
            "malheureux",
            "mélancolique",
            "😢",
            "😭",
            "😔",
            "😞",
            "😟",
            "navré",
            "attristé",
            "déçu",
            "regret",
        ],
        "surprised": [
            "wow",
            "incroyable",
            "surprenant",
            "étonnant",
            "ooh",
            "waouh",
            "oh",
            "ah",
            "stupéfait",
            "ébahi",
            "impressionnant",
            "stupéfiant",
            "😲",
            "😮",
            "🤯",
            "😯",
            "😳",
            "inattendu",
            "extraordinaire",
            "ahurissant",
            "attendais pas",
        ],
        "fun": [
            "drôle",
            "lol",
            "mdr",
            "hilarant",
            "rigolo",
            "amusant",
            "marrant",
            "comique",
            "blague",
            "humour",
            "rire",
            "😆",
            "😂",
            "🤣",
            "😄",
            "haha",
            "hehe",
            "hihi",
            "comique",
            "cocasse",
            "plaisant",
        ],
        "neutral": ["ok", "bien", "voilà", "alors", "donc", "effectivement"],
    }

    def analyze(self, text: str) -> str:
        """
        Analyse le texte et retourne l'émotion dominante

        Args:
            text: Texte à analyser (réponse du bot)

        Returns:
            Émotion détectée : 'joy', 'angry', 'sorrow', 'surprised', 'fun', 'neutral'
        """
        if not text or not text.strip():
            return "neutral"

        text_lower = text.lower()

        # Compter occurrences par émotion
        emotion_scores = {}

        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            if emotion == "neutral":
                continue  # Ne pas compter neutral dans le scoring

            score = sum(1 for keyword in keywords if keyword in text_lower)

            if score > 0:
                emotion_scores[emotion] = score

        # Retourner émotion dominante ou neutral
        if not emotion_scores:
            return "neutral"

        dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]

        logger.debug(
            f"🎭 Émotion détectée : {dominant_emotion} " f"(scores: {emotion_scores})"
        )

        return dominant_emotion


class ChatEngine:
    """
    Moteur conversationnel unifié pour Workly

    Orchestre la mémoire, le modèle LLM et la détection émotionnelle
    pour générer des réponses cohérentes et émotionnelles.

    Utilisable par :
    - Interface GUI Workly (source="desktop")
    - Bot Discord (source="discord")
    """

    def __init__(
        self,
        config: Optional[AIConfig] = None,
        memory: Optional[ConversationMemory] = None,
        model_manager: Optional[ModelManager] = None,
        enable_advanced_ai: bool = False,
        memory_storage_dir: str = "data/memory",
    ):
        """
        Initialise le Chat Engine

        Args:
            config: Configuration IA (si None, charge depuis config.json)
            memory: Gestionnaire mémoire court-terme (si None, utilise singleton)
            model_manager: Gestionnaire modèle (si None, utilise singleton)
            enable_advanced_ai: Active mémoire long-terme et IA avancée
            memory_storage_dir: Dossier stockage mémoire long-terme
        """
        self.config = config or get_config()
        self.memory = memory or get_memory()
        self.model_manager = model_manager or get_model_manager(self.config)
        
        # ⭐ PHASE 3 : EmotionAnalyzer avancé (remplace EmotionDetector basique)
        # Toujours activé pour meilleure détection émotions (avec/sans advanced_ai)
        self.emotion_analyzer = EmotionAnalyzer(
            smoothing_factor=0.3,
            history_size=5,
            enable_emotion_memory=enable_advanced_ai  # Mémoire long-terme si IA avancée
        )

        # Mémoire long-terme (Phase 1)
        self.enable_advanced_ai = enable_advanced_ai
        self.memory_manager: Optional[MemoryManager] = None
        
        # Personnalité évolutive (Phase 2)
        self.personality_engine: Optional[PersonalityEngine] = None

        if enable_advanced_ai:
            # Callback LLM pour résumés
            def llm_callback(prompt: str) -> str:
                if self.model_manager.is_loaded:
                    return self.model_manager.generate(
                        prompt=prompt,
                        temperature=0.3,  # Température basse pour résumés factuels
                        max_tokens=200,
                        stop=["<|user|>", "<|system|>"],
                    )
                return ""

            self.memory_manager = MemoryManager(
                storage_dir=memory_storage_dir, llm_callback=llm_callback
            )
            logger.info("✅ Mémoire long-terme activée (MemoryManager)")
            
            # Initialiser PersonalityEngine
            personality_file = os.path.join(memory_storage_dir, "personality.json")
            self.personality_engine = PersonalityEngine(storage_file=personality_file)
            logger.info("✅ Personnalité évolutive activée (PersonalityEngine)")

        logger.info(
            "✅ ChatEngine initialisé"
            + (" [Mode IA Avancée]" if enable_advanced_ai else "")
        )

    def _build_prompt(self, user_input: str, history: List[Dict[str, Any]]) -> str:
        """
        Construit le prompt complet avec system prompt + historique + question

        Args:
            user_input: Message actuel de l'utilisateur
            history: Historique des conversations (liste de dicts)

        Returns:
            Prompt formaté pour le modèle
        """
        # Format du prompt pour Zephyr-7B (format ChatML)
        prompt_parts = []

        # System prompt
        prompt_parts.append(f"<|system|>\n{self.config.system_prompt}")
        
        # ⭐ PHASE 2 : Injection personnalité (si activée)
        if self.enable_advanced_ai and self.personality_engine:
            personality_prompt = self.personality_engine.generate_personality_prompt()
            prompt_parts.append(f"\n{personality_prompt}")
            logger.debug(f"🎭 Personnalité injectée : {personality_prompt[:80]}...")

        # ⭐ PHASE 1 : Injection contexte long-terme (si activé)
        if self.enable_advanced_ai and self.memory_manager:
            long_term_context = self.memory_manager.get_context_for_prompt(
                query=user_input,
                include_facts=True,
                include_segments=True,
                max_tokens=800,  # ~20% du contexte total
            )

            if long_term_context:
                prompt_parts.append("\n--- CONTEXTE MÉMORISÉ ---")
                prompt_parts.append(long_term_context)
                prompt_parts.append("--- FIN CONTEXTE ---")
                logger.debug(
                    f"📚 Contexte long-terme injecté : {len(long_term_context)} chars"
                )

        prompt_parts.append("</|system|>")

        # Historique des conversations (court-terme)
        for interaction in history:
            user_msg = interaction["user_input"]
            bot_msg = interaction["bot_response"]

            prompt_parts.append(f"<|user|>\n{user_msg}</|user|>")
            prompt_parts.append(f"<|assistant|>\n{bot_msg}</|assistant|>")

        # Question actuelle
        prompt_parts.append(f"<|user|>\n{user_input}</|user|>")
        prompt_parts.append("<|assistant|>")

        prompt = "\n".join(prompt_parts)

        logger.debug(
            f"📝 Prompt construit : {len(prompt)} caractères, "
            f"{len(history)} messages d'historique"
        )

        return prompt

    def chat(
        self, user_input: str, user_id: str = "desktop_user", source: str = "desktop"
    ) -> ChatResponse:
        """
        Génère une réponse conversationnelle

        Args:
            user_input: Message de l'utilisateur
            user_id: ID utilisateur (Discord ID ou "desktop_user")
            source: Source du message ("desktop" ou "discord")

        Returns:
            ChatResponse avec réponse, émotion, stats

        Raises:
            RuntimeError: Si le modèle n'est pas chargé
        """
        import time

        start_time = time.time()

        logger.info(
            f"💬 Chat request : user={user_id[:8]}..., "
            f"source={source}, input_len={len(user_input)}"
        )

        # Vérifier que le modèle est chargé
        if not self.model_manager.is_loaded:
            error_msg = (
                "Modèle LLM non chargé ! " "Appelez model_manager.load_model() d'abord."
            )
            logger.error(f"❌ {error_msg}")
            raise RuntimeError(error_msg)

        # 1. Adapter personnalité au contexte (si activée)
        if self.enable_advanced_ai and self.personality_engine:
            # Déterminer heure du jour
            from datetime import datetime
            current_hour = datetime.now().hour
            if 5 <= current_hour < 12:
                time_of_day = 'morning'
            elif 12 <= current_hour < 18:
                time_of_day = 'afternoon'
            elif 18 <= current_hour < 22:
                time_of_day = 'evening'
            else:
                time_of_day = 'night'
            
            # Récupérer préférences utilisateur
            user_prefs = {}
            if self.memory_manager:
                prefs = self.memory_manager.facts.get('preferences', [])
                if prefs:
                    user_prefs['likes_humor'] = any(
                        p.get('subject') in ['humour', 'blague', 'drôle'] 
                        for p in prefs if p.get('sentiment') == 'positive'
                    )
            
            # Adapter personnalité
            conversation_length = len(self.memory_manager.current_conversation) if self.memory_manager else 0
            self.personality_engine.adapt_to_context(
                time_of_day=time_of_day,
                conversation_length=conversation_length,
                user_preferences=user_prefs
            )

        # 2. Récupérer l'historique
        history = self.memory.get_history(
            user_id=user_id, limit=self.config.context_limit, source=source
        )

        # 3. Construire le prompt
        prompt = self._build_prompt(user_input, history)

        # 4. Générer la réponse
        try:
            response_text = self.model_manager.generate(
                prompt=prompt,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                max_tokens=self.config.max_tokens,
                stop=["<|user|>", "<|system|>"],  # Arrêter aux balises
            )
        except Exception as e:
            logger.error(f"❌ Erreur génération : {e}")
            raise RuntimeError(f"Échec génération réponse : {e}")

        # 5. Analyser l'émotion de l'utilisateur (pour PersonalityEngine)
        user_emotion_result = self.emotion_analyzer.analyze(
            user_input,
            user_id=user_id,
            source='user'
        )
        
        # 6. Analyser l'émotion de la réponse assistant
        assistant_emotion_result = self.emotion_analyzer.analyze(
            response_text,
            user_id=user_id,
            source='assistant'
        )
        
        emotion = assistant_emotion_result.emotion  # Pour compatibilité
        
        # ⭐ PHASE 2 : Analyser feedback utilisateur (personnalité)
        if self.enable_advanced_ai and self.personality_engine:
            self.personality_engine.analyze_user_feedback(
                user_input,
                user_emotion=user_emotion_result.emotion
            )
        
        # ⭐ PHASE 3 : Vérifier si ajustement ton nécessaire
        if self.enable_advanced_ai:
            tone_adjustment = self.emotion_analyzer.should_adjust_response_tone(user_id)
            if tone_adjustment:
                logger.info(f"💡 Suggestion ajustement ton : {tone_adjustment}")

        # 7. Sauvegarder l'interaction (mémoire court-terme)
        self.memory.save_interaction(
            user_id=user_id,
            source=source,
            user_input=user_input,
            bot_response=response_text,
            emotion=emotion,
        )

        # ⭐ PHASE 1 : Sauvegarder dans mémoire long-terme (si activée)
        if self.enable_advanced_ai and self.memory_manager:
            # Ajouter message utilisateur
            self.memory_manager.add_message("user", user_input)

            # Ajouter réponse assistant
            self.memory_manager.add_message("assistant", response_text)

            # Note : L'extraction de faits et résumés automatiques
            # sont gérés automatiquement par MemoryManager.add_message()

        # 8. Calculer stats
        processing_time = time.time() - start_time
        tokens_used = len(response_text.split())  # Approximation

        logger.info(
            f"✅ Réponse générée : {len(response_text)} chars, "
            f"émotion assistant={emotion} ({assistant_emotion_result.intensity:.1f}%), "
            f"émotion user={user_emotion_result.emotion} ({user_emotion_result.intensity:.1f}%), "
            f"temps={processing_time:.2f}s"
        )

        return ChatResponse(
            response=response_text,
            emotion=emotion,
            tokens_used=tokens_used,
            context_messages=len(history),
            processing_time=processing_time,
        )

    def clear_user_history(self, user_id: str, source: Optional[str] = None) -> int:
        """
        Efface l'historique d'un utilisateur

        Args:
            user_id: ID utilisateur
            source: Filtrer par source (optionnel)

        Returns:
            Nombre d'interactions supprimées
        """
        deleted = self.memory.clear_user_history(user_id, source)

        logger.info(
            f"🗑️ Historique effacé : {deleted} interactions "
            f"pour {user_id[:8]}... (source={source or 'all'})"
        )

        return deleted

    def get_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques globales

        Returns:
            Dictionnaire avec stats mémoire + modèle + engine
        """
        memory_stats = self.memory.get_stats()
        model_info = self.model_manager.get_model_info()

        stats = {
            "memory": memory_stats,
            "model": model_info,
            "config": {
                "context_limit": self.config.context_limit,
                "gpu_profile": self.config.gpu_profile,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
            },
        }

        # Ajouter stats mémoire long-terme si activée
        if self.enable_advanced_ai and self.memory_manager:
            stats["long_term_memory"] = self.memory_manager.get_stats()

        return stats

    def __repr__(self) -> str:
        """Représentation string du ChatEngine"""
        status = "prêt" if self.model_manager.is_loaded else "modèle non chargé"
        return (
            f"ChatEngine({status}, "
            f"context={self.config.context_limit}, "
            f"profile={self.config.gpu_profile})"
        )


# Instance globale (optionnel, pour usage singleton)
_chat_engine_instance: Optional[ChatEngine] = None


def get_chat_engine(
    config: Optional[AIConfig] = None,
    memory: Optional[ConversationMemory] = None,
    model_manager: Optional[ModelManager] = None,
) -> ChatEngine:
    """
    Récupère l'instance globale de ChatEngine (singleton)

    Args:
        config: Configuration IA (optionnel)
        memory: Gestionnaire mémoire (optionnel)
        model_manager: Gestionnaire modèle (optionnel)

    Returns:
        Instance ChatEngine
    """
    global _chat_engine_instance

    if _chat_engine_instance is None:
        _chat_engine_instance = ChatEngine(config, memory, model_manager)

    return _chat_engine_instance


# Pour tests et usage direct
if __name__ == "__main__":
    # Test rapide du ChatEngine
    print("🧪 Test du ChatEngine...\n")

    # Test 1 : Initialisation
    print("1. Initialisation ChatEngine...")
    engine = ChatEngine()
    print(f"   ✅ {engine}\n")

    # Test 2 : Détection émotion (EmotionAnalyzer - Phase 3)
    print("2. Test détection émotions...")
    analyzer = EmotionAnalyzer(enable_emotion_memory=False)

    tests = [
        ("Je suis super content ! 😊", "joy"),
        ("C'est vraiment triste... 😢", "sorrow"),
        ("Wow, c'est incroyable ! 😲", "surprised"),
        ("Haha, trop drôle ! 😂", "fun"),
        ("Je suis très en colère ! 😠", "angry"),
        ("Je suis excité et impatient ! 🤩", "excited"),  # Émotion composée
        ("Voilà, c'est fait.", "neutral"),
    ]

    for text, expected in tests:
        result = analyzer.analyze(text, source='user')
        emotion = result.emotion
        status = "✅" if emotion == expected else "⚠️"
        print(f"   {status} '{text[:35]}...' → {emotion} ({result.intensity:.0f}%)")

    print()

    # Test 3 : Construction prompt
    print("3. Test construction prompt...")
    history = [
        {"user_input": "Bonjour", "bot_response": "Salut !"},
        {"user_input": "Ça va ?", "bot_response": "Très bien merci !"},
    ]

    prompt = engine._build_prompt("Comment tu t'appelles ?", history)
    print(f"   ✅ Prompt construit : {len(prompt)} caractères")
    print(f"   (Contient {prompt.count('<|user|>')} messages utilisateur)")

    print()

    # Test 4 : Chat complet (nécessite modèle chargé)
    print("4. Test conversation complète...")
    print("   ⚠️ Nécessite modèle chargé (décommentez ci-dessous)")
    print()

    # Décommenter pour tester avec le vrai modèle :
    # try:
    #     engine.model_manager.load_model()
    #
    #     response = engine.chat(
    #         user_input="Bonjour Kira, présente-toi en une phrase courte.",
    #         user_id="test_user",
    #         source="desktop"
    #     )
    #
    #     print(f"   ✅ Réponse : {response.response}")
    #     print(f"   🎭 Émotion : {response.emotion}")
    #     print(f"   ⏱️ Temps : {response.processing_time:.2f}s")
    #
    #     engine.model_manager.unload_model()
    #
    # except Exception as e:
    #     print(f"   ❌ Erreur : {e}")

    print("✅ Tests manuels terminés !")
