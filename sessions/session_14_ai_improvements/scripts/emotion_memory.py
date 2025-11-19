"""
emotion_memory.py - Mémoire émotionnelle pour Kira

Ce module gère l'historique émotionnel des interactions :
- Stockage des 100 dernières émotions détectées
- Persistance JSON dans data/memory/emotion_history.json
- Analyse tendances émotionnelles (utilisateur + assistant)
- Détection patterns émotionnels (stress, joie prolongée, etc.)
- Support recherche émotions par période

Architecture :
- Stockage dual : émotions utilisateur + émotions assistant (réponses)
- Métadonnées : timestamp, intensité, contexte message
- Analyse statistique : distribution, tendances, transitions fréquentes
"""

import json
import os
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import deque, Counter
from pathlib import Path


@dataclass
class EmotionEntry:
    """Entrée d'émotion dans l'historique"""
    
    emotion: str  # 'joy', 'angry', 'sorrow', 'surprised', 'fun', 'neutral'
    intensity: float  # 0.0 - 100.0
    confidence: float  # 0.0 - 100.0
    source: str  # 'user' ou 'assistant'
    message_preview: str  # Premiers 100 caractères du message
    timestamp: str  # ISO format
    context: Optional[Dict[str, Any]] = None  # Métadonnées additionnelles
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour JSON"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmotionEntry':
        """Crée EmotionEntry depuis dictionnaire"""
        return cls(**data)


class EmotionMemory:
    """
    Gestionnaire de mémoire émotionnelle
    
    Stocke et analyse l'historique des émotions détectées pour :
    - Comprendre l'état émotionnel général de l'utilisateur
    - Adapter les réponses selon l'historique émotionnel
    - Détecter patterns (ex: utilisateur souvent triste le soir)
    - Fournir contexte émotionnel au ChatEngine
    """
    
    def __init__(
        self,
        storage_file: str = "data/memory/emotion_history.json",
        max_entries: int = 100
    ):
        """
        Initialise la mémoire émotionnelle
        
        Args:
            storage_file: Chemin fichier JSON de persistance
            max_entries: Nombre maximum d'entrées (défaut 100)
        """
        self.storage_file = storage_file
        self.max_entries = max_entries
        
        # Créer dossier si nécessaire
        os.makedirs(os.path.dirname(storage_file), exist_ok=True)
        
        # Historique émotionnel (deque pour performance)
        self.history: deque[EmotionEntry] = deque(maxlen=max_entries)
        
        # Charger historique existant
        self._load_history()
    
    def _load_history(self) -> None:
        """Charge l'historique depuis JSON"""
        if not os.path.exists(self.storage_file):
            return
        
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruire deque depuis liste
            entries = data.get('entries', [])
            for entry_data in entries:
                entry = EmotionEntry.from_dict(entry_data)
                self.history.append(entry)
            
            print(f"✅ Chargé {len(self.history)} émotions depuis {self.storage_file}")
            
        except Exception as e:
            print(f"⚠️ Erreur chargement historique émotionnel : {e}")
    
    def _save_history(self) -> None:
        """Sauvegarde l'historique en JSON"""
        try:
            data = {
                'entries': [entry.to_dict() for entry in self.history],
                'last_modified': datetime.utcnow().isoformat(),
                'total_entries': len(self.history)
            }
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde historique émotionnel : {e}")
    
    def add_emotion(
        self,
        emotion: str,
        intensity: float,
        confidence: float,
        source: str,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Ajoute une émotion à l'historique
        
        Args:
            emotion: Nom de l'émotion
            intensity: Intensité 0-100
            confidence: Confiance 0-100
            source: 'user' ou 'assistant'
            message: Message complet
            context: Métadonnées optionnelles
        """
        # Créer preview (100 premiers caractères)
        preview = message[:100] + "..." if len(message) > 100 else message
        
        entry = EmotionEntry(
            emotion=emotion,
            intensity=intensity,
            confidence=confidence,
            source=source,
            message_preview=preview,
            timestamp=datetime.utcnow().isoformat(),
            context=context or {}
        )
        
        # Ajouter à l'historique (deque gère max_entries automatiquement)
        self.history.append(entry)
        
        # Sauvegarder
        self._save_history()
    
    def get_recent_emotions(
        self,
        count: int = 10,
        source: Optional[str] = None
    ) -> List[EmotionEntry]:
        """
        Récupère les N dernières émotions
        
        Args:
            count: Nombre d'émotions à récupérer
            source: Filtrer par source ('user', 'assistant', None=tous)
            
        Returns:
            Liste d'EmotionEntry (chronologique inversé, plus récent d'abord)
        """
        # Convertir deque en liste (ordre chronologique)
        all_entries = list(self.history)
        
        # Filtrer par source si spécifié
        if source:
            all_entries = [e for e in all_entries if e.source == source]
        
        # Inverser (plus récent d'abord) et limiter
        return list(reversed(all_entries))[:count]
    
    def get_emotions_by_period(
        self,
        hours: int = 24,
        source: Optional[str] = None
    ) -> List[EmotionEntry]:
        """
        Récupère émotions d'une période donnée
        
        Args:
            hours: Nombre d'heures dans le passé
            source: Filtrer par source
            
        Returns:
            Liste d'EmotionEntry dans la période
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        result = []
        for entry in self.history:
            entry_time = datetime.fromisoformat(entry.timestamp)
            if entry_time >= cutoff:
                if source is None or entry.source == source:
                    result.append(entry)
        
        return result
    
    def get_emotion_distribution(
        self,
        source: Optional[str] = None,
        hours: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Calcule la distribution des émotions
        
        Args:
            source: Filtrer par source
            hours: Limiter à N heures (None = tout l'historique)
            
        Returns:
            Dict {emotion: count}
        """
        if hours:
            entries = self.get_emotions_by_period(hours, source)
        else:
            entries = list(self.history)
            if source:
                entries = [e for e in entries if e.source == source]
        
        emotions = [e.emotion for e in entries]
        return dict(Counter(emotions))
    
    def get_dominant_emotion(
        self,
        source: Optional[str] = None,
        hours: Optional[int] = None
    ) -> Optional[str]:
        """
        Retourne l'émotion dominante
        
        Args:
            source: Filtrer par source
            hours: Limiter à N heures
            
        Returns:
            Nom de l'émotion dominante, ou None si vide
        """
        distribution = self.get_emotion_distribution(source, hours)
        
        if not distribution:
            return None
        
        return max(distribution.items(), key=lambda x: x[1])[0]
    
    def get_average_intensity(
        self,
        emotion: Optional[str] = None,
        source: Optional[str] = None,
        hours: Optional[int] = None
    ) -> float:
        """
        Calcule l'intensité moyenne
        
        Args:
            emotion: Filtrer par émotion spécifique
            source: Filtrer par source
            hours: Limiter à N heures
            
        Returns:
            Intensité moyenne 0-100, ou 0.0 si vide
        """
        if hours:
            entries = self.get_emotions_by_period(hours, source)
        else:
            entries = list(self.history)
            if source:
                entries = [e for e in entries if e.source == source]
        
        if emotion:
            entries = [e for e in entries if e.emotion == emotion]
        
        if not entries:
            return 0.0
        
        total = sum(e.intensity for e in entries)
        return total / len(entries)
    
    def detect_emotional_pattern(
        self,
        pattern_type: str = "consecutive",
        emotion: Optional[str] = None,
        threshold: int = 3
    ) -> bool:
        """
        Détecte un pattern émotionnel
        
        Args:
            pattern_type: Type de pattern
                - 'consecutive' : N émotions consécutives identiques
                - 'dominant' : Émotion dominante sur période
            emotion: Émotion à rechercher (None = détection auto)
            threshold: Seuil (ex: 3 occurrences consécutives)
            
        Returns:
            True si pattern détecté
        """
        if pattern_type == "consecutive":
            # Vérifier N dernières émotions identiques
            recent = self.get_recent_emotions(threshold)
            
            if len(recent) < threshold:
                return False
            
            # Si emotion spécifiée, vérifier qu'elles correspondent
            if emotion:
                return all(e.emotion == emotion for e in recent)
            
            # Sinon, vérifier qu'elles sont toutes identiques
            first_emotion = recent[0].emotion
            return all(e.emotion == first_emotion for e in recent)
        
        elif pattern_type == "dominant":
            # Émotion représente >50% des 10 dernières
            recent = self.get_recent_emotions(10)
            
            if len(recent) < threshold:
                return False
            
            dominant = self.get_dominant_emotion(hours=24)
            
            if emotion:
                return dominant == emotion
            
            # Vérifier si dominante est > 50%
            distribution = self.get_emotion_distribution(hours=24)
            if dominant and dominant in distribution:
                percentage = distribution[dominant] / len(recent)
                return percentage > 0.5
        
        return False
    
    def get_emotional_trend(
        self,
        window_size: int = 5
    ) -> str:
        """
        Analyse la tendance émotionnelle récente
        
        Args:
            window_size: Taille de la fenêtre d'analyse
            
        Returns:
            'improving', 'declining', 'stable', 'unknown'
        """
        recent = self.get_recent_emotions(window_size * 2)
        
        if len(recent) < window_size * 2:
            return 'unknown'
        
        # Séparer en 2 fenêtres : récente et ancienne
        recent_window = recent[:window_size]
        older_window = recent[window_size:window_size * 2]
        
        # Calculer scores émotionnels moyens (joie=+, tristesse/colère=-)
        emotion_scores = {
            'joy': 1.0,
            'fun': 0.8,
            'surprised': 0.3,
            'neutral': 0.0,
            'sorrow': -0.8,
            'angry': -1.0
        }
        
        def calc_avg_score(entries: List[EmotionEntry]) -> float:
            if not entries:
                return 0.0
            total = sum(
                emotion_scores.get(e.emotion, 0.0) * (e.intensity / 100.0)
                for e in entries
            )
            return total / len(entries)
        
        recent_score = calc_avg_score(recent_window)
        older_score = calc_avg_score(older_window)
        
        diff = recent_score - older_score
        
        # Seuils
        if diff > 0.2:
            return 'improving'
        elif diff < -0.2:
            return 'declining'
        else:
            return 'stable'
    
    def get_context_for_prompt(self) -> str:
        """
        Génère un contexte émotionnel pour injection dans prompt
        
        Returns:
            Texte décrivant l'état émotionnel récent de l'utilisateur
        """
        # Analyser dernières 10 émotions utilisateur
        recent_user = self.get_recent_emotions(10, source='user')
        
        if len(recent_user) < 3:
            return ""  # Pas assez de données
        
        # Émotion dominante utilisateur
        dominant = self.get_dominant_emotion(source='user', hours=24)
        
        # Tendance
        trend = self.get_emotional_trend()
        
        # Intensité moyenne
        avg_intensity = self.get_average_intensity(source='user', hours=24)
        
        # Générer contexte
        context_parts = []
        
        if dominant:
            emotion_names = {
                'joy': 'joyeux',
                'angry': 'irrité',
                'sorrow': 'triste',
                'surprised': 'surpris',
                'fun': 'amusé',
                'neutral': 'neutre'
            }
            emotion_fr = emotion_names.get(dominant, dominant)
            context_parts.append(f"L'utilisateur semble globalement {emotion_fr}")
        
        if avg_intensity > 70:
            context_parts.append("avec une forte intensité émotionnelle")
        elif avg_intensity < 30:
            context_parts.append("mais de manière subtile")
        
        if trend == 'improving':
            context_parts.append("Son humeur s'améliore")
        elif trend == 'declining':
            context_parts.append("Son humeur décline")
        
        # Patterns spéciaux
        if self.detect_emotional_pattern('consecutive', 'sorrow', 3):
            context_parts.append("Il semble traverser une période difficile")
        elif self.detect_emotional_pattern('consecutive', 'joy', 3):
            context_parts.append("Il est dans une période très positive")
        
        if context_parts:
            return ". ".join(context_parts) + "."
        
        return ""
    
    def clear_history(self) -> None:
        """Efface tout l'historique"""
        self.history.clear()
        self._save_history()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retourne des statistiques sur l'historique émotionnel
        
        Returns:
            Dict avec statistiques complètes
        """
        total = len(self.history)
        
        if total == 0:
            return {
                'total_entries': 0,
                'user_entries': 0,
                'assistant_entries': 0,
                'distribution': {},
                'average_intensity': 0.0,
                'dominant_emotion': None,
                'emotional_trend': 'unknown'
            }
        
        user_count = len([e for e in self.history if e.source == 'user'])
        assistant_count = len([e for e in self.history if e.source == 'assistant'])
        
        return {
            'total_entries': total,
            'user_entries': user_count,
            'assistant_entries': assistant_count,
            'distribution_all': self.get_emotion_distribution(),
            'distribution_user': self.get_emotion_distribution(source='user'),
            'distribution_assistant': self.get_emotion_distribution(source='assistant'),
            'average_intensity_user': self.get_average_intensity(source='user'),
            'average_intensity_assistant': self.get_average_intensity(source='assistant'),
            'dominant_emotion_user': self.get_dominant_emotion(source='user'),
            'dominant_emotion_assistant': self.get_dominant_emotion(source='assistant'),
            'emotional_trend': self.get_emotional_trend(),
            'oldest_entry': self.history[0].timestamp if self.history else None,
            'newest_entry': self.history[-1].timestamp if self.history else None
        }
    
    def __repr__(self) -> str:
        """Représentation string de la mémoire"""
        return f"EmotionMemory({len(self.history)} entries, max={self.max_entries})"


# Exemple d'utilisation
if __name__ == "__main__":
    print("=== Test EmotionMemory ===\n")
    
    # Initialiser
    memory = EmotionMemory(storage_file="data/memory_test/emotion_history.json")
    print(f"1. Mémoire initialisée : {memory}\n")
    
    # Ajouter quelques émotions
    print("2. Ajout d'émotions...")
    test_emotions = [
        ("joy", 80, 85, "user", "Je suis super content !"),
        ("fun", 90, 90, "assistant", "Haha c'est hilarant !"),
        ("joy", 75, 80, "user", "Merci beaucoup, c'est génial !"),
        ("neutral", 30, 95, "assistant", "D'accord, je comprends."),
        ("sorrow", 60, 70, "user", "Je suis un peu triste..."),
        ("sorrow", 55, 75, "user", "C'est vraiment dommage."),
    ]
    
    for emotion, intensity, confidence, source, message in test_emotions:
        memory.add_emotion(emotion, intensity, confidence, source, message)
        print(f"   ✅ {source}: {emotion} ({intensity}%)")
    print()
    
    # Récupérer récentes
    print("3. Émotions récentes (5 dernières) :")
    recent = memory.get_recent_emotions(5)
    for i, entry in enumerate(recent, 1):
        print(f"   {i}. [{entry.source}] {entry.emotion} ({entry.intensity:.0f}%) - {entry.message_preview[:40]}...")
    print()
    
    # Distribution
    print("4. Distribution émotions utilisateur :")
    dist = memory.get_emotion_distribution(source='user')
    for emotion, count in dist.items():
        print(f"   {emotion}: {count}")
    print()
    
    # Émotion dominante
    print("5. Analyse :")
    dominant = memory.get_dominant_emotion(source='user')
    print(f"   Émotion dominante utilisateur : {dominant}")
    
    avg_intensity = memory.get_average_intensity(source='user')
    print(f"   Intensité moyenne utilisateur : {avg_intensity:.1f}%")
    
    trend = memory.get_emotional_trend()
    print(f"   Tendance émotionnelle : {trend}")
    print()
    
    # Pattern
    print("6. Détection patterns :")
    has_consecutive = memory.detect_emotional_pattern('consecutive', 'sorrow', 2)
    print(f"   2 tristesses consécutives ? {has_consecutive}")
    print()
    
    # Contexte pour prompt
    print("7. Contexte pour prompt :")
    context = memory.get_context_for_prompt()
    print(f"   '{context}'\n")
    
    # Statistiques
    print("8. Statistiques complètes :")
    stats = memory.get_statistics()
    print(f"   Total émotions : {stats['total_entries']}")
    print(f"   Utilisateur : {stats['user_entries']}")
    print(f"   Assistant : {stats['assistant_entries']}")
    print(f"   Distribution : {stats['distribution_all']}")
    
    print("\n✅ Tests terminés !")
