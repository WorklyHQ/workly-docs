"""
ContextAnalyzer - Analyse contextuelle avancée des conversations

Ce module fait partie de la Session 14 Phase 4 : Analyse Contextuelle
Il détecte les intentions, sentiments, sujets et propose des actions proactives.

Architecture:
    - Détection d'intentions (8+ types)
    - Analyse sentiment (positif/négatif/neutre)
    - Extraction topics conversation
    - Suggestions actions proactives
    - Intégration avec ChatEngine

Author: Workly Team
Date: 17 novembre 2025
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from collections import Counter

logger = logging.getLogger(__name__)


@dataclass
class ContextAnalysis:
    """Résultat d'analyse contextuelle."""
    
    intent: str  # Type d'intention détectée
    intent_confidence: float  # Confiance 0.0-1.0
    sentiment: str  # "positive", "negative", "neutral"
    sentiment_score: float  # -1.0 à 1.0
    topics: List[str]  # Sujets identifiés
    entities: List[str]  # Entités nommées détectées
    requires_action: bool  # Nécessite action proactive
    suggested_actions: List[str]  # Actions suggérées
    complexity: str  # "simple", "medium", "complex"
    timestamp: datetime


class ContextAnalyzer:
    """
    Analyseur contextuel avancé pour comprendre intentions et contexte.
    
    Fonctionnalités:
        - Détection intentions (question, commande, casual, gratitude, etc.)
        - Analyse sentiment (positif/négatif/neutre avec score)
        - Extraction topics et entités
        - Suggestions actions proactives
        - Analyse complexité message
    
    Usage:
        analyzer = ContextAnalyzer()
        analysis = analyzer.analyze("Comment ça marche ?")
        print(f"Intent: {analysis.intent}, Sentiment: {analysis.sentiment}")
    """
    
    # Définition des intentions détectables
    INTENTS = {
        "question": ["comment", "pourquoi", "quoi", "où", "quand", "qui", "quel", "?"],
        "command": ["fais", "fait", "lance", "démarre", "arrête", "ouvre", "ferme", "!"],
        "casual": ["salut", "bonjour", "bonsoir", "coucou", "hey", "hello"],
        "gratitude": ["merci", "remercie", "thanks", "cool", "super", "génial"],
        "complaint": ["problème", "bug", "marche pas", "fonctionne pas", "erreur", "crash"],
        "feedback": ["j'aime", "j'adore", "j'aime pas", "je déteste", "préfère"],
        "request_help": ["aide", "aidez", "help", "stp", "s'il te plaît", "peux-tu"],
        "statement": [],  # Par défaut si rien d'autre
    }
    
    # Mots-clés sentiment positif
    POSITIVE_KEYWORDS = [
        "bien", "super", "génial", "excellent", "parfait", "top", "cool",
        "merci", "content", "heureux", "joyeux", "satisfait", "adore",
        "aime", "bravo", "félicitations", "réussi", "succès", "😊", "😃",
        "🎉", "👍", "❤️", "💚", "✅", "🙂", "😄", "😁"
    ]
    
    # Mots-clés sentiment négatif
    NEGATIVE_KEYWORDS = [
        "mal", "mauvais", "nul", "problème", "bug", "erreur", "crash",
        "triste", "déçu", "frustré", "énervé", "mécontent", "déteste",
        "n'aime pas", "pas content", "dommage", "pire", "échec", "😢",
        "😞", "😠", "😡", "❌", "😔", "😟", "😥", "💔"
    ]
    
    # Topics communs à détecter
    TOPIC_KEYWORDS = {
        "technique": ["code", "bug", "erreur", "développement", "programmation", "script"],
        "ia": ["intelligence", "artificiel", "llm", "model", "ai", "chatbot"],
        "avatar": ["vrm", "modèle", "avatar", "3d", "animation", "expression"],
        "python": ["python", "pip", "venv", "import", "fonction", "classe"],
        "unity": ["unity", "gameobject", "script", "scene", "build"],
        "personnel": ["nom", "prénom", "j'aime", "j'adore", "préfère", "moi"],
        "aide": ["aide", "comment", "tuto", "guide", "expliquer", "comprendre"],
    }
    
    def __init__(self):
        """Initialise l'analyseur contextuel."""
        logger.info("Initialisation ContextAnalyzer")
        self.analysis_history: List[ContextAnalysis] = []
    
    def analyze(self, text: str, conversation_history: Optional[List[str]] = None) -> ContextAnalysis:
        """
        Analyse complète du contexte d'un message.
        
        Args:
            text: Texte à analyser
            conversation_history: Historique conversation (optionnel)
        
        Returns:
            ContextAnalysis avec toutes les informations détectées
        """
        text_lower = text.lower().strip()
        
        # 1. Détection intention
        intent, intent_confidence = self._detect_intent(text_lower)
        
        # 2. Analyse sentiment
        sentiment, sentiment_score = self._analyze_sentiment(text_lower)
        
        # 3. Extraction topics
        topics = self._extract_topics(text_lower)
        
        # 4. Extraction entités (noms, lieux, etc.)
        entities = self._extract_entities(text)
        
        # 5. Analyse complexité
        complexity = self._analyze_complexity(text)
        
        # 6. Suggestions actions proactives
        requires_action, suggested_actions = self._suggest_actions(
            intent, sentiment, topics, text_lower
        )
        
        analysis = ContextAnalysis(
            intent=intent,
            intent_confidence=intent_confidence,
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            topics=topics,
            entities=entities,
            requires_action=requires_action,
            suggested_actions=suggested_actions,
            complexity=complexity,
            timestamp=datetime.now()
        )
        
        # Stocker dans historique
        self.analysis_history.append(analysis)
        if len(self.analysis_history) > 100:
            self.analysis_history.pop(0)
        
        logger.debug(f"Analyse: intent={intent}({intent_confidence:.2f}), "
                    f"sentiment={sentiment}({sentiment_score:.2f}), "
                    f"topics={topics}, complexity={complexity}")
        
        return analysis
    
    def _detect_intent(self, text: str) -> Tuple[str, float]:
        """
        Détecte l'intention principale du message.
        
        Args:
            text: Texte en minuscules
        
        Returns:
            (intent_name, confidence_score)
        """
        scores: Dict[str, float] = {}
        
        for intent_name, keywords in self.INTENTS.items():
            if not keywords:  # statement par défaut
                continue
            
            # Compter occurrences mots-clés
            count = sum(1 for keyword in keywords if keyword in text)
            
            # Bonus si début de phrase
            if keywords and any(text.startswith(kw) for kw in keywords):
                count += 2
            
            scores[intent_name] = count
        
        # Intent avec score maximum
        if scores and max(scores.values()) > 0:
            best_intent = max(scores, key=scores.get)
            max_score = scores[best_intent]
            # Normaliser confidence (max 5 mots-clés = 1.0)
            confidence = min(max_score / 5.0, 1.0)
            return best_intent, confidence
        
        # Défaut : statement
        return "statement", 0.5
    
    def _analyze_sentiment(self, text: str) -> Tuple[str, float]:
        """
        Analyse le sentiment du message.
        
        Args:
            text: Texte en minuscules
        
        Returns:
            (sentiment_label, sentiment_score)
            sentiment_label: "positive", "negative", "neutral"
            sentiment_score: -1.0 (très négatif) à 1.0 (très positif)
        """
        positive_count = sum(1 for word in self.POSITIVE_KEYWORDS if word in text)
        negative_count = sum(1 for word in self.NEGATIVE_KEYWORDS if word in text)
        
        # Score brut
        raw_score = positive_count - negative_count
        
        # Normaliser entre -1 et 1 (max 5 mots = score 1.0)
        sentiment_score = max(-1.0, min(1.0, raw_score / 5.0))
        
        # Label
        if sentiment_score > 0.2:
            sentiment_label = "positive"
        elif sentiment_score < -0.2:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"
        
        return sentiment_label, sentiment_score
    
    def _extract_topics(self, text: str) -> List[str]:
        """
        Extrait les topics (sujets) du message.
        
        Args:
            text: Texte en minuscules
        
        Returns:
            Liste des topics détectés
        """
        detected_topics = []
        
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics
    
    def _extract_entities(self, text: str) -> List[str]:
        """
        Extrait les entités nommées (noms propres, etc.).
        
        Args:
            text: Texte original (avec majuscules)
        
        Returns:
            Liste des entités détectées
        """
        entities = []
        
        # Pattern : mots commençant par majuscule (hors début phrase)
        words = text.split()
        for i, word in enumerate(words):
            # Nettoyer ponctuation
            clean_word = re.sub(r'[^\w]', '', word)
            
            # Si majuscule ET pas début de phrase
            if clean_word and clean_word[0].isupper() and i > 0:
                entities.append(clean_word)
        
        return entities
    
    def _analyze_complexity(self, text: str) -> str:
        """
        Analyse la complexité du message.
        
        Args:
            text: Texte original
        
        Returns:
            "simple", "medium", "complex"
        """
        # Critères complexité
        word_count = len(text.split())
        sentence_count = text.count('.') + text.count('!') + text.count('?')
        if sentence_count == 0:
            sentence_count = 1
        
        avg_words_per_sentence = word_count / sentence_count
        
        # Classification
        if word_count <= 5:
            return "simple"
        elif word_count <= 20 or avg_words_per_sentence <= 12:
            return "medium"
        else:
            return "complex"
    
    def _suggest_actions(self, intent: str, sentiment: str, 
                        topics: List[str], text: str) -> Tuple[bool, List[str]]:
        """
        Suggère des actions proactives basées sur le contexte.
        
        Args:
            intent: Intention détectée
            sentiment: Sentiment détecté
            topics: Topics identifiés
            text: Texte original en minuscules
        
        Returns:
            (requires_action, suggested_actions_list)
        """
        suggested_actions = []
        
        # Actions selon intention
        if intent == "question":
            suggested_actions.append("provide_detailed_answer")
            if "comment" in text:
                suggested_actions.append("offer_tutorial")
        
        elif intent == "command":
            suggested_actions.append("execute_command")
            suggested_actions.append("confirm_action")
        
        elif intent == "complaint":
            suggested_actions.append("show_empathy")
            suggested_actions.append("offer_solution")
            if "bug" in text or "erreur" in text:
                suggested_actions.append("request_details")
        
        elif intent == "gratitude":
            suggested_actions.append("acknowledge_thanks")
            suggested_actions.append("offer_further_help")
        
        elif intent == "request_help":
            suggested_actions.append("provide_step_by_step")
            suggested_actions.append("ask_clarification")
        
        # Actions selon sentiment
        if sentiment == "negative":
            suggested_actions.append("adjust_tone_empathetic")
        elif sentiment == "positive":
            suggested_actions.append("maintain_positive_tone")
        
        # Actions selon topics
        if "technique" in topics or "aide" in topics:
            suggested_actions.append("provide_code_example")
        
        if "ia" in topics:
            suggested_actions.append("explain_ai_features")
        
        # Dédupliquer
        suggested_actions = list(set(suggested_actions))
        
        requires_action = len(suggested_actions) > 0
        
        return requires_action, suggested_actions
    
    def get_conversation_summary(self, window: int = 10) -> Dict[str, Any]:
        """
        Résume les N dernières analyses de conversation.
        
        Args:
            window: Nombre d'analyses à considérer
        
        Returns:
            Dictionnaire avec statistiques conversation
        """
        recent = self.analysis_history[-window:] if self.analysis_history else []
        
        if not recent:
            return {
                "total_messages": 0,
                "dominant_intent": None,
                "dominant_sentiment": None,
                "common_topics": [],
                "average_complexity": None,
            }
        
        # Compter intents
        intents = [a.intent for a in recent]
        intent_counts = Counter(intents)
        dominant_intent = intent_counts.most_common(1)[0][0] if intent_counts else None
        
        # Compter sentiments
        sentiments = [a.sentiment for a in recent]
        sentiment_counts = Counter(sentiments)
        dominant_sentiment = sentiment_counts.most_common(1)[0][0] if sentiment_counts else None
        
        # Topics communs
        all_topics = []
        for a in recent:
            all_topics.extend(a.topics)
        topic_counts = Counter(all_topics)
        common_topics = [topic for topic, _ in topic_counts.most_common(3)]
        
        # Complexité moyenne
        complexities = [a.complexity for a in recent]
        complexity_counts = Counter(complexities)
        average_complexity = complexity_counts.most_common(1)[0][0] if complexity_counts else None
        
        return {
            "total_messages": len(recent),
            "dominant_intent": dominant_intent,
            "dominant_sentiment": dominant_sentiment,
            "common_topics": common_topics,
            "average_complexity": average_complexity,
            "intent_distribution": dict(intent_counts),
            "sentiment_distribution": dict(sentiment_counts),
        }
    
    def get_context_for_prompt(self, window: int = 5) -> str:
        """
        Génère un contexte textuel pour injection dans prompt LLM.
        
        Args:
            window: Nombre d'analyses récentes à considérer
        
        Returns:
            Texte décrivant le contexte conversationnel
        """
        summary = self.get_conversation_summary(window)
        
        if summary["total_messages"] == 0:
            return ""
        
        # Construire description contextuelle
        parts = []
        
        # Intent dominant
        if summary["dominant_intent"]:
            intent_fr = {
                "question": "pose souvent des questions",
                "command": "donne des commandes",
                "casual": "converse de manière décontractée",
                "gratitude": "exprime de la gratitude",
                "complaint": "exprime des plaintes",
                "feedback": "donne du feedback",
                "request_help": "demande de l'aide",
                "statement": "fait des déclarations",
            }
            parts.append(f"L'utilisateur {intent_fr.get(summary['dominant_intent'], 'communique')}")
        
        # Sentiment dominant
        if summary["dominant_sentiment"]:
            sentiment_fr = {
                "positive": "semble de bonne humeur",
                "negative": "semble frustré ou mécontent",
                "neutral": "est neutre émotionnellement",
            }
            parts.append(sentiment_fr.get(summary["dominant_sentiment"], ""))
        
        # Topics
        if summary["common_topics"]:
            topics_str = ", ".join(summary["common_topics"])
            parts.append(f"et s'intéresse à : {topics_str}")
        
        if not parts:
            return ""
        
        context = ". ".join(p for p in parts if p) + "."
        return context
    
    def clear_history(self) -> None:
        """Vide l'historique des analyses."""
        self.analysis_history.clear()
        logger.info("Historique analyses contextuelles vidé")
    
    def __repr__(self) -> str:
        return f"<ContextAnalyzer: {len(self.analysis_history)} analyses>"


# ============================================================================
# TEST STANDALONE
# ============================================================================

if __name__ == "__main__":
    print("\n🧪 Test ContextAnalyzer standalone\n")
    print("=" * 60)
    
    # Créer analyseur
    analyzer = ContextAnalyzer()
    
    # Messages de test
    test_messages = [
        "Comment ça marche ?",
        "Super merci beaucoup ! 😊",
        "J'ai un bug avec Unity, ça crash tout le temps 😡",
        "Bonjour Kira !",
        "Peux-tu m'aider avec Python ?",
        "Lance l'application maintenant !",
    ]
    
    print("\n📝 Analyse de 6 messages de test :\n")
    
    for i, msg in enumerate(test_messages, 1):
        print(f"\n{i}. Message: \"{msg}\"")
        analysis = analyzer.analyze(msg)
        
        print(f"   Intent: {analysis.intent} (conf: {analysis.intent_confidence:.2f})")
        print(f"   Sentiment: {analysis.sentiment} (score: {analysis.sentiment_score:+.2f})")
        print(f"   Topics: {analysis.topics if analysis.topics else 'Aucun'}")
        print(f"   Complexité: {analysis.complexity}")
        print(f"   Actions suggérées: {', '.join(analysis.suggested_actions) if analysis.suggested_actions else 'Aucune'}")
    
    # Résumé conversation
    print("\n" + "=" * 60)
    print("\n📊 Résumé conversation (6 derniers messages) :\n")
    
    summary = analyzer.get_conversation_summary(window=6)
    print(f"Total messages: {summary['total_messages']}")
    print(f"Intent dominant: {summary['dominant_intent']}")
    print(f"Sentiment dominant: {summary['dominant_sentiment']}")
    print(f"Topics communs: {summary['common_topics']}")
    print(f"Complexité moyenne: {summary['average_complexity']}")
    
    # Contexte pour prompt
    print("\n" + "=" * 60)
    print("\n💬 Contexte généré pour prompt LLM :\n")
    
    context = analyzer.get_context_for_prompt(window=6)
    print(f"\"{context}\"")
    
    print("\n" + "=" * 60)
    print("\n✅ Test ContextAnalyzer terminé !")
