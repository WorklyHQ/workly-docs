"""
personality_engine.py - Moteur de personnalité évolutive pour Kira

Ce module gère la personnalité de l'assistant virtuel :
- Traits de personnalité configurables (gentillesse, humour, formalité, etc.)
- Évolution basée sur interactions utilisateur
- Adaptation au contexte et préférences utilisateur
- Personnalisation des réponses selon personnalité

Architecture :
- Traits stockés dans SQLite avec scores 0.0-1.0
- Modifieurs contextuels (heure, humeur utilisateur, sujet)
- Historique d'évolution pour traçabilité

Migration Phase 6 : JSON → SQLite (performance + ACID)
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

try:
    from .database import get_database
except ImportError:
    from database import get_database


@dataclass
class PersonalityTrait:
    """Trait de personnalité avec score et évolution"""

    name: str
    score: float  # 0.0 - 1.0
    description: str
    last_updated: str
    evolution_history: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour JSON"""
        return asdict(self)


class PersonalityEngine:
    """
    Moteur de personnalité évolutive

    Gère les traits de personnalité de Kira et leur évolution
    selon les interactions avec l'utilisateur.

    Traits principaux :
    - kindness (gentillesse) : 0.0 (distant) → 1.0 (très chaleureux)
    - humor (humour) : 0.0 (sérieux) → 1.0 (très drôle)
    - formality (formalité) : 0.0 (casual) → 1.0 (formel)
    - enthusiasm (enthousiasme) : 0.0 (calme) → 1.0 (très excité)
    - empathy (empathie) : 0.0 (logique) → 1.0 (très empathique)
    - creativity (créativité) : 0.0 (factuel) → 1.0 (très créatif)
    """

    def __init__(self, storage_file: str = "data/memory/personality.json"):
        """
        Initialise le moteur de personnalité

        Args:
            storage_file: (Obsolète, gardé pour backward compatibility)
        """
        self.storage_file = storage_file  # Gardé pour backward compatibility

        # Base de données SQLite
        storage_dir = os.path.dirname(storage_file) if storage_file else "data/memory"
        os.makedirs(storage_dir, exist_ok=True)
        db_path = os.path.join(storage_dir, "workly.db")
        self.db = get_database(db_path)

        # Définition des traits par défaut
        self.default_traits = {
            "kindness": {
                "score": 0.8,
                "description": "Niveau de chaleur et bienveillance dans les interactions",
            },
            "humor": {
                "score": 0.6,
                "description": "Fréquence et intensité des blagues et références amusantes",
            },
            "formality": {
                "score": 0.3,
                "description": "Niveau de formalité vs casual dans le langage",
            },
            "enthusiasm": {
                "score": 0.7,
                "description": "Niveau d'énergie et d'excitation dans les réponses",
            },
            "empathy": {
                "score": 0.8,
                "description": "Capacité à comprendre et répondre aux émotions",
            },
            "creativity": {
                "score": 0.6,
                "description": "Originalité et imagination dans les réponses",
            },
        }

        # Charger ou initialiser personnalité
        self.personality = self._load_personality()

        # Sauvegarder si initialisée (pour créer le fichier)
        if not os.path.exists(self.storage_file):
            self._save_personality()

        # Modifieurs contextuels temporaires (non persistés)
        self.context_modifiers: Dict[str, float] = {}

    def _load_personality(self) -> Dict[str, PersonalityTrait]:
        """
        Charge la personnalité depuis SQLite ou initialise par défaut

        Returns:
            Dictionnaire de traits de personnalité
        """
        try:
            # Charger depuis SQLite
            traits_db = self.db.get_personality_traits()

            if traits_db:
                # Reconstruire PersonalityTrait objects
                personality = {}
                for trait_data in traits_db:
                    trait_name = trait_data["trait_name"]

                    # Charger l'historique d'évolution depuis personality_evolution
                    evolution_history = self.db.get_personality_evolution(trait_name)

                    personality[trait_name] = PersonalityTrait(
                        name=trait_name,
                        score=trait_data["score"],
                        description=trait_data.get("description", ""),
                        last_updated=trait_data["last_updated"],
                        evolution_history=evolution_history,
                    )

                return personality

        except Exception as e:
            print(f"⚠️ Erreur chargement personnalité depuis SQLite : {e}")

        # Initialiser par défaut si aucune donnée en DB
        return self._initialize_default_personality()

    def _initialize_default_personality(self) -> Dict[str, PersonalityTrait]:
        """
        Initialise personnalité avec valeurs par défaut

        Returns:
            Dictionnaire de traits initialisés
        """
        personality = {}
        timestamp = datetime.utcnow().isoformat()

        for trait_name, trait_info in self.default_traits.items():
            personality[trait_name] = PersonalityTrait(
                name=trait_name,
                score=trait_info["score"],
                description=trait_info["description"],
                last_updated=timestamp,
                evolution_history=[
                    {
                        "timestamp": timestamp,
                        "score": trait_info["score"],
                        "reason": "Initialisation",
                    }
                ],
            )

        # Note : _save_personality() sera appelé après assignation de self.personality
        # dans __init__ pour éviter AttributeError

        return personality

    def _save_personality(self) -> None:
        """Sauvegarde la personnalité dans SQLite"""
        try:
            # Sauvegarder chaque trait dans SQLite
            for trait_name, trait in self.personality.items():
                self.db.set_personality_trait(
                    trait_name=trait_name,
                    score=trait.score,
                    description=trait.description,
                    last_updated=trait.last_updated,
                )

        except Exception as e:
            print(f"⚠️ Erreur sauvegarde personnalité dans SQLite : {e}")

    def get_trait(self, trait_name: str) -> float:
        """
        Récupère le score d'un trait avec modifieurs contextuels

        Args:
            trait_name: Nom du trait

        Returns:
            Score 0.0-1.0 (incluant modifieurs)
        """
        if trait_name not in self.personality:
            return 0.5  # Valeur neutre par défaut

        base_score = self.personality[trait_name].score
        modifier = self.context_modifiers.get(trait_name, 0.0)

        # Appliquer modifieur et clipper
        final_score = max(0.0, min(1.0, base_score + modifier))

        return final_score

    def update_trait(
        self, trait_name: str, delta: float, reason: str = "Évolution naturelle"
    ) -> None:
        """
        Met à jour un trait de personnalité

        Args:
            trait_name: Nom du trait à modifier
            delta: Changement (-1.0 à +1.0)
            reason: Raison de la modification (pour historique)
        """
        if trait_name not in self.personality:
            print(f"⚠️ Trait inconnu : {trait_name}")
            return

        trait = self.personality[trait_name]
        old_score = trait.score

        # Appliquer delta avec clipping
        new_score = max(0.0, min(1.0, old_score + delta))

        # Si changement significatif (>0.01)
        if abs(new_score - old_score) > 0.01:
            trait.score = new_score
            trait.last_updated = datetime.utcnow().isoformat()

            # Ajouter à l'historique local (en mémoire)
            trait.evolution_history.append(
                {
                    "timestamp": trait.last_updated,
                    "old_score": old_score,
                    "new_score": new_score,
                    "delta": delta,
                    "reason": reason,
                }
            )

            # Limiter historique à 100 entrées
            if len(trait.evolution_history) > 100:
                trait.evolution_history = trait.evolution_history[-100:]

            # Sauvegarder dans SQLite
            try:
                # Mettre à jour le trait
                self.db.set_personality_trait(
                    trait_name=trait_name,
                    score=new_score,
                    description=trait.description,
                    last_updated=trait.last_updated,
                )

                # Enregistrer l'évolution dans personality_evolution
                self.db.add_personality_evolution(
                    trait_name=trait_name,
                    old_score=old_score,
                    new_score=new_score,
                    reason=reason,
                )
            except Exception as e:
                print(f"⚠️ Erreur sauvegarde évolution personnalité : {e}")
                # Fallback sur sauvegarde complète
                self._save_personality()

    def set_context_modifier(
        self, trait_name: str, modifier: float, duration: str = "temporary"
    ) -> None:
        """
        Applique un modifieur contextuel temporaire

        Args:
            trait_name: Nom du trait
            modifier: Modifieur -0.5 à +0.5
            duration: "temporary" (une requête) ou "session" (jusqu'à reset)
        """
        self.context_modifiers[trait_name] = max(-0.5, min(0.5, modifier))

    def clear_context_modifiers(self) -> None:
        """Efface tous les modifieurs contextuels"""
        self.context_modifiers.clear()

    def analyze_user_feedback(
        self, user_message: str, user_emotion: Optional[str] = None
    ) -> None:
        """
        Analyse le feedback utilisateur et ajuste personnalité

        Args:
            user_message: Message utilisateur
            user_emotion: Émotion détectée (optionnel)
        """
        message_lower = user_message.lower()

        # Détection de feedback positif → augmenter traits utilisés
        positive_indicators = [
            "merci",
            "génial",
            "super",
            "excellent",
            "parfait",
            "cool",
            "top",
        ]
        negative_indicators = ["arrête", "trop", "moins", "sérieux", "calme", "stop"]

        has_positive = any(ind in message_lower for ind in positive_indicators)
        has_negative = any(ind in message_lower for ind in negative_indicators)

        # Feedback sur humour
        if "drôle" in message_lower or "marrant" in message_lower:
            if has_positive:
                self.update_trait("humor", 0.05, "Feedback positif sur humour")
            elif has_negative:
                self.update_trait("humor", -0.05, "Demande de réduction humour")

        # Feedback sur enthousiasme
        if "calme" in message_lower or "trop excité" in message_lower:
            self.update_trait("enthusiasm", -0.05, "Demande de réduction enthousiasme")

        # Feedback sur empathie
        if user_emotion in ["sorrow", "angry"]:
            # Augmenter empathie si utilisateur triste/en colère
            self.update_trait("empathy", 0.03, f"Réponse à émotion {user_emotion}")

        # Feedback général positif → léger boost tous traits
        if has_positive and not has_negative:
            for trait_name in ["kindness", "enthusiasm"]:
                self.update_trait(trait_name, 0.02, "Feedback général positif")

    def adapt_to_context(
        self,
        time_of_day: Optional[str] = None,
        conversation_length: int = 0,
        user_preferences: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Adapte temporairement la personnalité au contexte

        Args:
            time_of_day: "morning", "afternoon", "evening", "night"
            conversation_length: Nombre de messages dans conversation
            user_preferences: Préférences connues de l'utilisateur
        """
        # Réinitialiser modifieurs
        self.clear_context_modifiers()

        # Adapter selon heure
        if time_of_day == "morning":
            self.set_context_modifier("enthusiasm", 0.1)  # Plus énergique le matin
        elif time_of_day == "night":
            self.set_context_modifier("enthusiasm", -0.1)  # Plus calme la nuit
            self.set_context_modifier("formality", -0.1)  # Plus casual

        # Adapter selon longueur conversation
        if conversation_length > 20:
            # Conversations longues → plus casual et empathique
            self.set_context_modifier("formality", -0.1)
            self.set_context_modifier("empathy", 0.1)

        # Adapter selon préférences utilisateur
        if user_preferences:
            if user_preferences.get("prefers_formal"):
                self.set_context_modifier("formality", 0.2)
            if user_preferences.get("likes_humor"):
                self.set_context_modifier("humor", 0.15)

    def generate_personality_prompt(self) -> str:
        """
        Génère un fragment de prompt décrivant la personnalité actuelle

        Returns:
            Texte à injecter dans le system prompt
        """
        traits = []

        # Kindness
        kindness = self.get_trait("kindness")
        if kindness > 0.7:
            traits.append("très chaleureux et bienveillant")
        elif kindness > 0.5:
            traits.append("aimable et attentionné")
        else:
            traits.append("professionnel et direct")

        # Humor
        humor = self.get_trait("humor")
        if humor > 0.7:
            traits.append("avec un bon sens de l'humour et des références amusantes")
        elif humor > 0.5:
            traits.append("avec des touches d'humour occasionnelles")

        # Formality
        formality = self.get_trait("formality")
        if formality < 0.4:
            traits.append("dans un style décontracté et accessible")
        elif formality > 0.6:
            traits.append("dans un style formel et structuré")

        # Enthusiasm
        enthusiasm = self.get_trait("enthusiasm")
        if enthusiasm > 0.7:
            traits.append("énergique et passionné")
        elif enthusiasm < 0.4:
            traits.append("calme et posé")

        # Empathy
        empathy = self.get_trait("empathy")
        if empathy > 0.7:
            traits.append("très à l'écoute des émotions")

        # Creativity
        creativity = self.get_trait("creativity")
        if creativity > 0.7:
            traits.append("créatif dans tes explications")

        # Construire phrase
        if traits:
            return f"Tu es {', '.join(traits[:3])}. " + (
                ", ".join(traits[3:]) + "." if len(traits) > 3 else ""
            )

        return "Tu es un assistant virtuel équilibré."

    def get_personality_summary(self) -> Dict[str, Any]:
        """
        Retourne un résumé de la personnalité actuelle

        Returns:
            Dict avec scores et descriptions
        """
        summary = {}

        for trait_name, trait in self.personality.items():
            current_score = self.get_trait(trait_name)

            summary[trait_name] = {
                "base_score": trait.score,
                "current_score": current_score,
                "modifier": self.context_modifiers.get(trait_name, 0.0),
                "description": trait.description,
                "last_updated": trait.last_updated,
                "evolution_count": len(trait.evolution_history),
            }

        return summary

    def reset_to_defaults(self) -> None:
        """Réinitialise tous les traits aux valeurs par défaut"""
        self.personality = self._initialize_default_personality()
        self.clear_context_modifiers()

    def get_evolution_history(
        self, trait_name: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Récupère l'historique d'évolution d'un trait

        Args:
            trait_name: Nom du trait
            limit: Nombre d'entrées max

        Returns:
            Liste d'événements d'évolution
        """
        if trait_name not in self.personality:
            return []

        history = self.personality[trait_name].evolution_history
        return history[-limit:]

    def __repr__(self) -> str:
        """Représentation string du moteur"""
        traits_str = ", ".join(
            [
                f"{name}={self.get_trait(name):.2f}"
                for name in ["kindness", "humor", "enthusiasm"]
            ]
        )
        return f"PersonalityEngine({traits_str})"


# --- Exemple d'utilisation ---
if __name__ == "__main__":
    print("=== Test PersonalityEngine ===\n")

    # Initialiser
    engine = PersonalityEngine(storage_file="data/memory_test/personality.json")
    print(f"1. Moteur initialisé : {engine}\n")

    # Résumé personnalité
    print("2. Personnalité actuelle :")
    summary = engine.get_personality_summary()
    for trait_name, info in summary.items():
        print(f"   {trait_name}: {info['current_score']:.2f} - {info['description']}")
    print()

    # Générer prompt
    print("3. Fragment de prompt :")
    prompt = engine.generate_personality_prompt()
    print(f"   {prompt}\n")

    # Adapter contexte
    print("4. Adaptation contexte (soirée, conversation longue) :")
    engine.adapt_to_context(time_of_day="night", conversation_length=25)
    print(f"   Modifieurs : {engine.context_modifiers}")
    print(f"   Enthousiasme : {engine.get_trait('enthusiasm'):.2f}\n")

    # Analyser feedback
    print("5. Analyse feedback utilisateur :")
    engine.analyze_user_feedback("Haha c'est vraiment drôle ! Merci !")
    print(f"   Humour après feedback : {engine.get_trait('humor'):.2f}\n")

    # Historique
    print("6. Historique d'évolution (humor) :")
    history = engine.get_evolution_history("humor", limit=5)
    for entry in history[-3:]:
        if "new_score" in entry:
            print(
                f"   {entry['timestamp'][:19]} : {entry.get('old_score', 0):.2f} → {entry['new_score']:.2f}"
            )
        else:
            print(
                f"   {entry['timestamp'][:19]} : Initialisation à {entry['score']:.2f}"
            )

    print("\n✅ Tests terminés !")
