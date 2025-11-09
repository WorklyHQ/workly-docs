"""
Emotion Analyzer Avancé - Desktop-Mate (Kira)

Analyseur émotionnel contextuel pour détecter les émotions dans les réponses
et les mapper vers des expressions VRM.

Fonctionnalités :
- Analyse contextuelle avec historique
- Intensité émotionnelle (0-100)
- Historique émotionnel par utilisateur
- Transitions émotionnelles douces
- Mapping complet vers Blendshapes VRM
"""

import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class EmotionResult:
    """Résultat de l'analyse émotionnelle"""
    emotion: str                # Émotion détectée ('joy', 'angry', etc.)
    intensity: float            # Intensité 0-100
    confidence: float           # Confiance 0-100
    keywords_found: List[str]   # Mots-clés détectés
    context_score: float        # Score contextuel 0-100
    timestamp: datetime         # Horodatage de l'analyse


class EmotionAnalyzer:
    """
    Analyseur émotionnel avancé avec analyse contextuelle
    
    Améliore le EmotionDetector basique avec :
    - Analyse contextuelle (historique des émotions)
    - Calcul d'intensité basé sur la densité de mots-clés
    - Historique émotionnel par utilisateur
    - Transitions douces entre émotions
    - Mapping vers Blendshapes VRM
    """
    
    # Mots-clés par émotion avec poids (importance)
    EMOTION_KEYWORDS = {
        'joy': {
            # Poids 3 : Très fort
            'heureux': 3, 'heureuse': 3, 'super': 3, 'génial': 3, 
            'excellent': 3, 'parfait': 3, 'merveilleux': 3, 'magnifique': 3,
            '🎉': 3, '✨': 3, '🥰': 3, '😍': 3,
            
            # Poids 2 : Fort
            'content': 2, 'contente': 2, 'cool': 2, 'top': 2, 'joie': 2,
            'réjoui': 2, 'enchanté': 2, 'ravi': 2, 'formidable': 2,
            '😊': 2, '😄': 2, '😁': 2, '🤗': 2,
            
            # Poids 1 : Modéré
            'bien': 1, 'sympa': 1, 'agréable': 1, 'plaisant': 1,
            '🙂': 1, '😌': 1
        },
        'angry': {
            # Poids 3 : Très fort
            'furieux': 3, 'furieuse': 3, 'rage': 3, 'colère': 3,
            '😡': 3, '🤬': 3, 'inacceptable': 3, 'insupportable': 3,
            
            # Poids 2 : Fort
            'énervé': 2, 'énervée': 2, 'agacé': 2, 'irrité': 2,
            'fâché': 2, 'mécontent': 2, 'contrarié': 2,
            '😠': 2, 'grrr': 2, 'argh': 2,
            
            # Poids 1 : Modéré
            'agaçant': 1, 'frustré': 1, 'problème': 1, 'erreur': 1,
            'pfff': 1
        },
        'sorrow': {
            # Poids 3 : Très fort
            'désespéré': 3, 'horrible': 3, 'terrible': 3, 'affreux': 3,
            '😭': 3, 'chagrin': 3, 'peine': 3,
            
            # Poids 2 : Fort
            'triste': 2, 'désolé': 2, 'désolée': 2, 'malheureux': 2,
            'mélancolique': 2, 'attristé': 2, 'déçu': 2,
            '😢': 2, '😔': 2, '😞': 2,
            
            # Poids 1 : Modéré
            'dommage': 1, 'malheureusement': 1, 'hélas': 1,
            'navré': 1, 'regret': 1, '😟': 1
        },
        'surprised': {
            # Poids 3 : Très fort
            'stupéfait': 3, 'ébahi': 3, 'ahurissant': 3, 'incroyable': 3,
            '🤯': 3, 'extraordinaire': 3,
            
            # Poids 2 : Fort
            'wow': 2, 'surprenant': 2, 'étonnant': 2, 'impressionnant': 2,
            'stupéfiant': 2, 'waouh': 2, 'inattendu': 2,
            '😲': 2, '😮': 2, '😯': 2,
            
            # Poids 1 : Modéré
            'ooh': 1, 'oh': 1, 'ah': 1, '😳': 1
        },
        'fun': {
            # Poids 3 : Très fort
            'hilarant': 3, 'mdr': 3, 'mort de rire': 3,
            '🤣': 3, '😂': 3, 'ptdr': 3,
            
            # Poids 2 : Fort
            'drôle': 2, 'rigolo': 2, 'amusant': 2, 'marrant': 2,
            'comique': 2, 'blague': 2, 'humour': 2,
            'lol': 2, 'haha': 2, 'hehe': 2, '😆': 2,
            
            # Poids 1 : Modéré
            'hihi': 1, 'cocasse': 1, 'plaisant': 1
        },
        'neutral': {
            # Poids 1 uniquement pour neutral
            'ok': 1, 'bien': 1, 'voilà': 1, 'alors': 1, 'donc': 1,
            'effectivement': 1, 'd\'accord': 1, 'entendu': 1
        }
    }
    
    # Mapping émotions → Blendshapes VRM
    EMOTION_TO_VRM = {
        'joy': {
            'blendshape': 'Joy',
            'intensity_multiplier': 1.0,      # 100% de l'intensité détectée
            'min_threshold': 30,              # Seuil minimum pour activer
            'optimal_range': (50, 85)         # Range optimal d'intensité
        },
        'angry': {
            'blendshape': 'Angry',
            'intensity_multiplier': 0.8,      # 80% (colère plus subtile)
            'min_threshold': 40,
            'optimal_range': (55, 80)
        },
        'sorrow': {
            'blendshape': 'Sorrow',
            'intensity_multiplier': 0.9,      # 90%
            'min_threshold': 35,
            'optimal_range': (50, 80)
        },
        'surprised': {
            'blendshape': 'Surprised',
            'intensity_multiplier': 1.2,      # 120% (surprise marquée)
            'min_threshold': 25,
            'optimal_range': (45, 90)
        },
        'fun': {
            'blendshape': 'Fun',
            'intensity_multiplier': 1.1,      # 110%
            'min_threshold': 30,
            'optimal_range': (50, 95)
        },
        'neutral': {
            'blendshape': 'Neutral',
            'intensity_multiplier': 0.5,      # 50% (neutre doux)
            'min_threshold': 0,
            'optimal_range': (0, 30)
        }
    }
    
    def __init__(self, smoothing_factor: float = 0.3, history_size: int = 5):
        """
        Initialise l'analyseur émotionnel
        
        Args:
            smoothing_factor: Facteur de lissage pour transitions (0-1)
                            0 = changement brutal, 1 = très lisse
            history_size: Taille de l'historique émotionnel par utilisateur
        """
        self.smoothing_factor = max(0.0, min(1.0, smoothing_factor))
        self.history_size = history_size
        
        # Historique émotionnel par utilisateur
        # Format : {user_id: deque([EmotionResult, ...])}
        self.emotion_history: Dict[str, deque] = {}
        
        logger.info(
            f"✅ EmotionAnalyzer initialisé "
            f"(smoothing={self.smoothing_factor}, history={self.history_size})"
        )
    
    def _calculate_intensity(
        self,
        text: str,
        keywords_with_weights: Dict[str, int]
    ) -> Tuple[float, List[str]]:
        """
        Calcule l'intensité émotionnelle basée sur les mots-clés trouvés
        
        Args:
            text: Texte à analyser
            keywords_with_weights: Dictionnaire {mot-clé: poids}
        
        Returns:
            (intensité 0-100, liste des mots-clés trouvés)
        """
        text_lower = text.lower()
        
        total_weight = 0
        keywords_found = []
        
        for keyword, weight in keywords_with_weights.items():
            if keyword in text_lower:
                total_weight += weight
                keywords_found.append(keyword)
        
        # Calcul intensité (normalisation empirique)
        # Poids total typique : 1-10 → Intensité : 0-100
        raw_intensity = min(100, total_weight * 15)  # 15 = facteur de normalisation
        
        # Bonus si plusieurs mots-clés (contexte renforcé)
        keyword_count = len(keywords_found)
        if keyword_count >= 3:
            raw_intensity = min(100, raw_intensity * 1.2)  # +20%
        elif keyword_count >= 2:
            raw_intensity = min(100, raw_intensity * 1.1)  # +10%
        
        return raw_intensity, keywords_found
    
    def _calculate_confidence(
        self,
        intensity: float,
        keywords_count: int,
        context_score: float
    ) -> float:
        """
        Calcule la confiance de la détection émotionnelle
        
        Args:
            intensity: Intensité détectée (0-100)
            keywords_count: Nombre de mots-clés trouvés
            context_score: Score contextuel (0-100)
        
        Returns:
            Confiance 0-100
        """
        # Confiance basée sur :
        # - 40% intensité
        # - 30% nombre de mots-clés
        # - 30% contexte
        
        intensity_factor = intensity / 100.0
        keyword_factor = min(1.0, keywords_count / 3.0)  # Max 3 mots-clés
        context_factor = context_score / 100.0
        
        confidence = (
            intensity_factor * 0.4 +
            keyword_factor * 0.3 +
            context_factor * 0.3
        ) * 100
        
        return min(100, confidence)
    
    def _calculate_context_score(
        self,
        current_emotion: str,
        user_id: str
    ) -> float:
        """
        Calcule un score contextuel basé sur l'historique émotionnel
        
        Args:
            current_emotion: Émotion actuelle détectée
            user_id: ID utilisateur
        
        Returns:
            Score contextuel 0-100
        """
        if user_id not in self.emotion_history:
            return 50.0  # Score neutre si pas d'historique
        
        history = self.emotion_history[user_id]
        
        if len(history) == 0:
            return 50.0
        
        # Vérifier cohérence avec émotions précédentes
        recent_emotions = [result.emotion for result in history]
        
        # Si émotion identique récente → Score élevé (cohérence)
        if current_emotion in recent_emotions[-2:]:  # 2 dernières
            return 80.0
        
        # Si émotions similaires (joie-fun, triste-angry) → Score moyen
        similar_emotions = {
            'joy': ['fun'],
            'fun': ['joy'],
            'angry': ['sorrow'],
            'sorrow': ['angry'],
            'surprised': []
        }
        
        for recent in recent_emotions[-2:]:
            if current_emotion in similar_emotions.get(recent, []):
                return 65.0
        
        # Transition émotionnelle normale
        return 50.0
    
    def _apply_smoothing(
        self,
        current_result: EmotionResult,
        user_id: str
    ) -> EmotionResult:
        """
        Applique un lissage des transitions émotionnelles
        
        Args:
            current_result: Résultat émotionnel actuel
            user_id: ID utilisateur
        
        Returns:
            Résultat émotionnel lissé
        """
        if user_id not in self.emotion_history or len(self.emotion_history[user_id]) == 0:
            return current_result  # Pas de lissage si pas d'historique
        
        previous_result = self.emotion_history[user_id][-1]
        
        # Si émotion identique, lisser l'intensité
        if current_result.emotion == previous_result.emotion:
            smoothed_intensity = (
                self.smoothing_factor * previous_result.intensity +
                (1 - self.smoothing_factor) * current_result.intensity
            )
            
            current_result.intensity = smoothed_intensity
            
            logger.debug(
                f"🎚️ Intensité lissée : {previous_result.intensity:.1f} → "
                f"{current_result.intensity:.1f}"
            )
        
        # Sinon, appliquer transition douce d'intensité
        else:
            # Réduire légèrement l'intensité lors du changement d'émotion
            current_result.intensity *= 0.9
            
            logger.debug(
                f"🔄 Transition émotionnelle : {previous_result.emotion} → "
                f"{current_result.emotion}"
            )
        
        return current_result
    
    def analyze(
        self,
        text: str,
        user_id: str = "desktop_user",
        context: Optional[List[str]] = None
    ) -> EmotionResult:
        """
        Analyse le texte et retourne un résultat émotionnel détaillé
        
        Args:
            text: Texte à analyser (réponse du bot)
            user_id: ID utilisateur pour historique émotionnel
            context: Contexte conversationnel (optionnel, futur)
        
        Returns:
            EmotionResult avec émotion, intensité, confiance, etc.
        """
        if not text or not text.strip():
            # Texte vide → Neutral
            return EmotionResult(
                emotion='neutral',
                intensity=0.0,
                confidence=100.0,
                keywords_found=[],
                context_score=100.0,
                timestamp=datetime.now()
            )
        
        # 1. Analyser chaque émotion et calculer scores
        emotion_scores = {}
        emotion_details = {}
        
        for emotion, keywords_with_weights in self.EMOTION_KEYWORDS.items():
            intensity, keywords_found = self._calculate_intensity(text, keywords_with_weights)
            
            if intensity > 0:
                context_score = self._calculate_context_score(emotion, user_id)
                confidence = self._calculate_confidence(
                    intensity,
                    len(keywords_found),
                    context_score
                )
                
                # Score final pondéré (intensité + contexte)
                final_score = (intensity * 0.7) + (context_score * 0.3)
                
                emotion_scores[emotion] = final_score
                emotion_details[emotion] = {
                    'intensity': intensity,
                    'confidence': confidence,
                    'keywords': keywords_found,
                    'context_score': context_score
                }
        
        # 2. Déterminer émotion dominante
        if not emotion_scores:
            dominant_emotion = 'neutral'
            details = {
                'intensity': 0.0,
                'confidence': 100.0,
                'keywords': [],
                'context_score': 100.0
            }
        else:
            dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
            details = emotion_details[dominant_emotion]
        
        # 3. Créer résultat
        result = EmotionResult(
            emotion=dominant_emotion,
            intensity=details['intensity'],
            confidence=details['confidence'],
            keywords_found=details['keywords'],
            context_score=details['context_score'],
            timestamp=datetime.now()
        )
        
        # 4. Appliquer lissage
        result = self._apply_smoothing(result, user_id)
        
        # 5. Sauvegarder dans historique
        self._save_to_history(user_id, result)
        
        logger.info(
            f"🎭 Émotion analysée : {result.emotion} "
            f"(intensité={result.intensity:.1f}, confiance={result.confidence:.1f})"
        )
        
        return result
    
    def _save_to_history(self, user_id: str, result: EmotionResult):
        """
        Sauvegarde le résultat dans l'historique émotionnel
        
        Args:
            user_id: ID utilisateur
            result: Résultat émotionnel
        """
        if user_id not in self.emotion_history:
            self.emotion_history[user_id] = deque(maxlen=self.history_size)
        
        self.emotion_history[user_id].append(result)
        
        logger.debug(
            f"📚 Historique émotionnel : {len(self.emotion_history[user_id])} "
            f"entrées pour {user_id[:8]}..."
        )
    
    def get_emotion_history(self, user_id: str) -> List[EmotionResult]:
        """
        Récupère l'historique émotionnel d'un utilisateur
        
        Args:
            user_id: ID utilisateur
        
        Returns:
            Liste des résultats émotionnels (chronologique)
        """
        if user_id not in self.emotion_history:
            return []
        
        return list(self.emotion_history[user_id])
    
    def get_vrm_blendshape(
        self,
        emotion: str,
        intensity: float
    ) -> Dict[str, Any]:
        """
        Convertit une émotion en paramètres Blendshape VRM
        
        Args:
            emotion: Émotion détectée ('joy', 'angry', etc.)
            intensity: Intensité 0-100
        
        Returns:
            Dictionnaire avec paramètres VRM :
            {
                'blendshape': str,          # Nom du Blendshape
                'value': float,             # Valeur 0.0-1.0
                'recommended': bool,        # True si dans range optimal
                'raw_intensity': float      # Intensité brute 0-100
            }
        """
        vrm_config = self.EMOTION_TO_VRM.get(emotion, self.EMOTION_TO_VRM['neutral'])
        
        # Appliquer multiplicateur
        adjusted_intensity = intensity * vrm_config['intensity_multiplier']
        adjusted_intensity = min(100, adjusted_intensity)
        
        # Convertir en valeur 0.0-1.0 pour Unity
        vrm_value = adjusted_intensity / 100.0
        vrm_value = max(0.0, min(1.0, vrm_value))
        
        # Vérifier si dans range optimal
        min_optimal, max_optimal = vrm_config['optimal_range']
        is_recommended = min_optimal <= adjusted_intensity <= max_optimal
        
        return {
            'blendshape': vrm_config['blendshape'],
            'value': vrm_value,
            'recommended': is_recommended,
            'raw_intensity': intensity,
            'adjusted_intensity': adjusted_intensity,
            'min_threshold': vrm_config['min_threshold']
        }
    
    def clear_user_history(self, user_id: str):
        """
        Efface l'historique émotionnel d'un utilisateur
        
        Args:
            user_id: ID utilisateur
        """
        if user_id in self.emotion_history:
            del self.emotion_history[user_id]
            logger.info(f"🗑️ Historique émotionnel effacé pour {user_id[:8]}...")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Récupère des statistiques sur l'analyseur
        
        Returns:
            Dictionnaire avec statistiques globales
        """
        total_users = len(self.emotion_history)
        total_emotions = sum(len(history) for history in self.emotion_history.values())
        
        # Répartition des émotions
        emotion_counts = {}
        for history in self.emotion_history.values():
            for result in history:
                emotion_counts[result.emotion] = emotion_counts.get(result.emotion, 0) + 1
        
        return {
            'total_users': total_users,
            'total_emotions_analyzed': total_emotions,
            'emotion_distribution': emotion_counts,
            'smoothing_factor': self.smoothing_factor,
            'history_size': self.history_size
        }


# Instance globale (optionnel, pour usage singleton)
_emotion_analyzer_instance: Optional[EmotionAnalyzer] = None


def get_emotion_analyzer(
    smoothing_factor: float = 0.3,
    history_size: int = 5
) -> EmotionAnalyzer:
    """
    Récupère l'instance globale de EmotionAnalyzer (singleton)
    
    Args:
        smoothing_factor: Facteur de lissage (0-1)
        history_size: Taille historique par utilisateur
    
    Returns:
        Instance EmotionAnalyzer
    """
    global _emotion_analyzer_instance
    
    if _emotion_analyzer_instance is None:
        _emotion_analyzer_instance = EmotionAnalyzer(smoothing_factor, history_size)
    
    return _emotion_analyzer_instance


# Pour tests et usage direct
if __name__ == "__main__":
    # Test rapide de l'EmotionAnalyzer
    print("🧪 Test de l'EmotionAnalyzer avancé...\n")
    
    # Test 1 : Initialisation
    print("1. Initialisation...")
    analyzer = EmotionAnalyzer(smoothing_factor=0.3, history_size=5)
    print(f"   ✅ Analyzer initialisé\n")
    
    # Test 2 : Analyse basique
    print("2. Analyses basiques...")
    tests = [
        ("Je suis super heureux et content ! 😊 C'est génial !", "joy"),
        ("C'est vraiment triste et dommage... 😢", "sorrow"),
        ("Wow ! C'est incroyable et stupéfiant ! 😲", "surprised"),
        ("Haha, trop drôle et hilarant ! 😂 lol mdr", "fun"),
        ("Je suis très en colère et furieux ! 😠", "angry"),
    ]
    
    for text, expected in tests:
        result = analyzer.analyze(text, "test_user")
        status = "✅" if result.emotion == expected else "❌"
        print(
            f"   {status} '{text[:40]}...'\n"
            f"      → {result.emotion} "
            f"(intensité={result.intensity:.1f}, confiance={result.confidence:.1f})"
        )
    
    print()
    
    # Test 3 : Historique émotionnel
    print("3. Historique émotionnel...")
    history = analyzer.get_emotion_history("test_user")
    print(f"   ✅ {len(history)} émotions dans l'historique")
    for i, result in enumerate(history, 1):
        print(f"      {i}. {result.emotion} (intensité={result.intensity:.1f})")
    
    print()
    
    # Test 4 : Mapping VRM
    print("4. Mapping VRM Blendshapes...")
    vrm_tests = [
        ("joy", 75),
        ("angry", 60),
        ("sorrow", 50),
        ("surprised", 85),
        ("fun", 90)
    ]
    
    for emotion, intensity in vrm_tests:
        vrm_data = analyzer.get_vrm_blendshape(emotion, intensity)
        recommended = "✅" if vrm_data['recommended'] else "⚠️"
        print(
            f"   {recommended} {emotion.capitalize():10} ({intensity:3}%) "
            f"→ {vrm_data['blendshape']:10} = {vrm_data['value']:.2f} "
            f"(ajusté: {vrm_data['adjusted_intensity']:.1f}%)"
        )
    
    print()
    
    # Test 5 : Statistiques
    print("5. Statistiques globales...")
    stats = analyzer.get_stats()
    print(f"   ✅ Utilisateurs : {stats['total_users']}")
    print(f"   ✅ Émotions analysées : {stats['total_emotions_analyzed']}")
    print(f"   ✅ Distribution : {stats['emotion_distribution']}")
    
    print()
    print("✅ Tests manuels terminés !")
