"""
Tests unitaires pour EmotionAnalyzer

Test de toutes les fonctionnalités :
- Analyse émotionnelle basique
- Calcul d'intensité
- Analyse contextuelle
- Historique émotionnel
- Lissage transitions
- Mapping VRM Blendshapes
"""

import pytest
from datetime import datetime

from src.ai.emotion_analyzer import (
    EmotionAnalyzer,
    EmotionResult,
    get_emotion_analyzer
)


# === Tests Initialisation ===

def test_emotion_analyzer_init():
    """Test initialisation basique"""
    analyzer = EmotionAnalyzer(smoothing_factor=0.5, history_size=10)
    
    assert analyzer.smoothing_factor == 0.5
    assert analyzer.history_size == 10
    assert len(analyzer.emotion_history) == 0


def test_emotion_analyzer_init_defaults():
    """Test initialisation avec valeurs par défaut"""
    analyzer = EmotionAnalyzer()
    
    assert analyzer.smoothing_factor == 0.3
    assert analyzer.history_size == 5


def test_emotion_analyzer_init_clamps_smoothing():
    """Test que smoothing_factor est borné entre 0-1"""
    analyzer1 = EmotionAnalyzer(smoothing_factor=-0.5)
    assert analyzer1.smoothing_factor == 0.0
    
    analyzer2 = EmotionAnalyzer(smoothing_factor=1.5)
    assert analyzer2.smoothing_factor == 1.0


# === Tests Analyse Émotionnelle Basique ===

def test_analyze_joy():
    """Test détection émotion 'joy'"""
    analyzer = EmotionAnalyzer()
    
    result = analyzer.analyze("Je suis super heureux et content ! 😊", "user1")
    
    assert result.emotion == 'joy'
    assert result.intensity > 50  # Intensité significative
    assert result.confidence > 50
    assert len(result.keywords_found) >= 2  # Au moins 2 mots-clés


def test_analyze_angry():
    """Test détection émotion 'angry'"""
    analyzer = EmotionAnalyzer()
    
    result = analyzer.analyze("Je suis furieux et très énervé ! 😠", "user1")
    
    assert result.emotion == 'angry'
    assert result.intensity > 50
    assert result.confidence > 50


def test_analyze_sorrow():
    """Test détection émotion 'sorrow'"""
    analyzer = EmotionAnalyzer()
    
    result = analyzer.analyze("C'est vraiment triste et désolé... 😢", "user1")
    
    assert result.emotion == 'sorrow'
    assert result.intensity > 40
    assert result.confidence > 40


def test_analyze_surprised():
    """Test détection émotion 'surprised'"""
    analyzer = EmotionAnalyzer()
    
    result = analyzer.analyze("Wow ! C'est incroyable et stupéfiant ! 😲", "user1")
    
    assert result.emotion == 'surprised'
    assert result.intensity > 50
    assert result.confidence > 50


def test_analyze_fun():
    """Test détection émotion 'fun'"""
    analyzer = EmotionAnalyzer()
    
    result = analyzer.analyze("Haha trop drôle ! lol mdr 😂", "user1")
    
    assert result.emotion == 'fun'
    assert result.intensity > 50
    assert result.confidence > 50


def test_analyze_neutral_empty():
    """Test texte vide → neutral"""
    analyzer = EmotionAnalyzer()
    
    result = analyzer.analyze("", "user1")
    
    assert result.emotion == 'neutral'
    assert result.intensity == 0.0
    assert result.confidence == 100.0


def test_analyze_neutral_no_keywords():
    """Test texte sans mots-clés → neutral"""
    analyzer = EmotionAnalyzer()
    
    result = analyzer.analyze("Ceci est un texte technique.", "user1")
    
    assert result.emotion == 'neutral'
    assert result.intensity < 30


# === Tests Intensité ===

def test_intensity_increases_with_keywords():
    """Test que l'intensité augmente avec le nombre de mots-clés"""
    analyzer = EmotionAnalyzer()
    
    result1 = analyzer.analyze("Je suis content.", "user1")
    result2 = analyzer.analyze("Je suis super heureux et content !", "user1")
    result3 = analyzer.analyze("Je suis super heureux, content, génial et parfait ! 🎉😊", "user1")
    
    # Intensité croissante
    assert result1.intensity < result2.intensity < result3.intensity


def test_intensity_weighted_keywords():
    """Test que les mots-clés à poids élevé donnent plus d'intensité"""
    analyzer = EmotionAnalyzer()
    
    # "furieux" (poids 3) vs "agaçant" (poids 1)
    result_high = analyzer.analyze("Je suis furieux !", "user1")
    result_low = analyzer.analyze("C'est agaçant.", "user1")
    
    assert result_high.intensity > result_low.intensity


def test_intensity_capped_at_100():
    """Test que l'intensité ne dépasse jamais 100"""
    analyzer = EmotionAnalyzer()
    
    # Texte avec beaucoup de mots-clés très forts
    result = analyzer.analyze(
        "Super génial parfait excellent merveilleux magnifique "
        "heureux content réjoui 😊😄😁🎉✨🥰😍",
        "user1"
    )
    
    assert result.intensity <= 100.0


# === Tests Confiance ===

def test_confidence_high_with_multiple_keywords():
    """Test confiance élevée avec plusieurs mots-clés"""
    analyzer = EmotionAnalyzer()
    
    result = analyzer.analyze("Je suis super heureux, content et génial ! 😊", "user1")
    
    assert result.confidence > 70


def test_confidence_low_with_single_keyword():
    """Test confiance plus basse avec un seul mot-clé"""
    analyzer = EmotionAnalyzer()
    
    result = analyzer.analyze("C'est bien.", "user1")
    
    assert result.confidence < 70


# === Tests Historique Émotionnel ===

def test_emotion_history_saves():
    """Test que l'historique est sauvegardé"""
    analyzer = EmotionAnalyzer(history_size=5)
    
    analyzer.analyze("Je suis content.", "user1")
    analyzer.analyze("C'est triste.", "user1")
    analyzer.analyze("Wow incroyable !", "user1")
    
    history = analyzer.get_emotion_history("user1")
    
    assert len(history) == 3
    assert history[0].emotion == 'joy'
    assert history[1].emotion == 'sorrow'
    assert history[2].emotion == 'surprised'


def test_emotion_history_max_size():
    """Test que l'historique respecte la taille max"""
    analyzer = EmotionAnalyzer(history_size=3)
    
    for i in range(5):
        analyzer.analyze("Je suis content.", "user1")
    
    history = analyzer.get_emotion_history("user1")
    
    assert len(history) == 3  # Max size respectée


def test_emotion_history_per_user():
    """Test que chaque utilisateur a son propre historique"""
    analyzer = EmotionAnalyzer()
    
    analyzer.analyze("Je suis content.", "user1")
    analyzer.analyze("Je suis triste.", "user2")
    
    history1 = analyzer.get_emotion_history("user1")
    history2 = analyzer.get_emotion_history("user2")
    
    assert len(history1) == 1
    assert len(history2) == 1
    assert history1[0].emotion == 'joy'
    assert history2[0].emotion == 'sorrow'


def test_emotion_history_empty_for_new_user():
    """Test historique vide pour nouvel utilisateur"""
    analyzer = EmotionAnalyzer()
    
    history = analyzer.get_emotion_history("new_user")
    
    assert history == []


# === Tests Analyse Contextuelle ===

def test_context_score_increases_for_repeated_emotion():
    """Test que le score contextuel augmente si émotion répétée"""
    analyzer = EmotionAnalyzer()
    
    # Première analyse
    result1 = analyzer.analyze("Je suis content.", "user1")
    context_score1 = result1.context_score
    
    # Deuxième analyse (même émotion)
    result2 = analyzer.analyze("Je suis heureux.", "user1")
    context_score2 = result2.context_score
    
    # Le score contextuel devrait augmenter
    assert context_score2 >= context_score1


def test_context_score_neutral_for_first_emotion():
    """Test score contextuel neutre pour première émotion"""
    analyzer = EmotionAnalyzer()
    
    result = analyzer.analyze("Je suis content.", "user1")
    
    # Premier message → Score neutre (50)
    assert result.context_score == 50.0


# === Tests Lissage (Smoothing) ===

def test_smoothing_reduces_intensity_jumps():
    """Test que le lissage réduit les variations brutales d'intensité"""
    analyzer = EmotionAnalyzer(smoothing_factor=0.5)  # Lissage fort
    
    # Première émotion 'joy' avec intensité modérée
    result1 = analyzer.analyze("Je suis content.", "user1")
    intensity1 = result1.intensity
    
    # Deuxième émotion 'joy' avec intensité très forte
    # Avec lissage, l'intensité devrait être intermédiaire
    result2 = analyzer.analyze("Je suis super heureux génial parfait ! 😊🎉", "user1")
    intensity2 = result2.intensity
    
    # Sans lissage, intensity2 serait beaucoup plus élevée
    # Avec lissage, elle est réduite
    assert intensity2 < 100  # Pas au max grâce au lissage


def test_no_smoothing_for_first_emotion():
    """Test pas de lissage pour la première émotion (pas d'historique)"""
    analyzer = EmotionAnalyzer(smoothing_factor=0.5)
    
    result = analyzer.analyze("Je suis super heureux ! 😊", "user1")
    
    # Pas de lissage appliqué (pas d'historique)
    assert result.intensity > 0


def test_smoothing_on_emotion_transition():
    """Test lissage lors d'un changement d'émotion"""
    analyzer = EmotionAnalyzer(smoothing_factor=0.3)
    
    result1 = analyzer.analyze("Je suis heureux.", "user1")
    result2 = analyzer.analyze("Je suis triste.", "user1")
    
    # Lors d'un changement, l'intensité est légèrement réduite
    assert result2.intensity < 100


# === Tests Mapping VRM Blendshapes ===

def test_vrm_mapping_joy():
    """Test mapping 'joy' vers Blendshape VRM"""
    analyzer = EmotionAnalyzer()
    
    vrm_data = analyzer.get_vrm_blendshape('joy', 70)
    
    assert vrm_data['blendshape'] == 'Joy'
    assert 0.0 <= vrm_data['value'] <= 1.0
    assert vrm_data['raw_intensity'] == 70
    assert 'adjusted_intensity' in vrm_data


def test_vrm_mapping_all_emotions():
    """Test mapping de toutes les émotions"""
    analyzer = EmotionAnalyzer()
    
    emotions = ['joy', 'angry', 'sorrow', 'surprised', 'fun', 'neutral']
    
    for emotion in emotions:
        vrm_data = analyzer.get_vrm_blendshape(emotion, 50)
        
        assert 'blendshape' in vrm_data
        assert 0.0 <= vrm_data['value'] <= 1.0
        assert vrm_data['raw_intensity'] == 50


def test_vrm_intensity_multiplier():
    """Test que le multiplicateur d'intensité est appliqué"""
    analyzer = EmotionAnalyzer()
    
    # 'surprised' a un multiplier de 1.2 (120%)
    vrm_surprised = analyzer.get_vrm_blendshape('surprised', 50)
    
    # 'angry' a un multiplier de 0.8 (80%)
    vrm_angry = analyzer.get_vrm_blendshape('angry', 50)
    
    # Surprised devrait avoir une intensité ajustée plus élevée
    assert vrm_surprised['adjusted_intensity'] > vrm_angry['adjusted_intensity']


def test_vrm_value_clamped():
    """Test que la valeur VRM est bornée entre 0.0 et 1.0"""
    analyzer = EmotionAnalyzer()
    
    # Intensité très forte
    vrm_data = analyzer.get_vrm_blendshape('surprised', 100)  # multiplier 1.2
    
    # Valeur doit rester <= 1.0
    assert vrm_data['value'] <= 1.0


def test_vrm_recommended_range():
    """Test vérification du range optimal"""
    analyzer = EmotionAnalyzer()
    
    # Dans le range optimal (50-85 pour 'joy')
    vrm_optimal = analyzer.get_vrm_blendshape('joy', 70)
    assert vrm_optimal['recommended'] is True
    
    # Hors du range optimal
    vrm_low = analyzer.get_vrm_blendshape('joy', 20)
    assert vrm_low['recommended'] is False


def test_vrm_min_threshold():
    """Test que le seuil minimum est inclus"""
    analyzer = EmotionAnalyzer()
    
    vrm_data = analyzer.get_vrm_blendshape('joy', 50)
    
    assert 'min_threshold' in vrm_data
    assert vrm_data['min_threshold'] > 0


# === Tests Utilitaires ===

def test_clear_user_history():
    """Test effacement historique utilisateur"""
    analyzer = EmotionAnalyzer()
    
    analyzer.analyze("Je suis content.", "user1")
    analyzer.analyze("Je suis triste.", "user1")
    
    assert len(analyzer.get_emotion_history("user1")) == 2
    
    analyzer.clear_user_history("user1")
    
    assert len(analyzer.get_emotion_history("user1")) == 0


def test_get_stats():
    """Test récupération statistiques"""
    analyzer = EmotionAnalyzer()
    
    analyzer.analyze("Je suis content.", "user1")
    analyzer.analyze("Je suis triste.", "user1")
    analyzer.analyze("Je suis content.", "user2")
    
    stats = analyzer.get_stats()
    
    assert stats['total_users'] == 2
    assert stats['total_emotions_analyzed'] == 3
    assert 'emotion_distribution' in stats
    assert stats['smoothing_factor'] == 0.3


# === Tests Singleton ===

def test_get_emotion_analyzer_singleton():
    """Test que get_emotion_analyzer retourne toujours la même instance"""
    analyzer1 = get_emotion_analyzer()
    analyzer2 = get_emotion_analyzer()
    
    assert analyzer1 is analyzer2


# === Tests Cas Limites ===

def test_analyze_with_emojis_only():
    """Test analyse avec uniquement des emojis"""
    analyzer = EmotionAnalyzer()
    
    result = analyzer.analyze("😊😄😁🎉", "user1")
    
    assert result.emotion == 'joy'
    assert result.intensity > 0


def test_analyze_mixed_emotions():
    """Test texte avec émotions mixtes (dominante détectée)"""
    analyzer = EmotionAnalyzer()
    
    # Plus de mots-clés 'joy' que 'sorrow'
    result = analyzer.analyze(
        "Je suis content et heureux, mais un peu triste.",
        "user1"
    )
    
    # Joy devrait dominer
    assert result.emotion == 'joy'


def test_analyze_very_long_text():
    """Test avec texte très long"""
    analyzer = EmotionAnalyzer()
    
    long_text = "Je suis content. " * 100
    
    result = analyzer.analyze(long_text, "user1")
    
    assert result.emotion == 'joy'
    assert result.intensity > 0


def test_analyze_special_characters():
    """Test avec caractères spéciaux"""
    analyzer = EmotionAnalyzer()
    
    result = analyzer.analyze("Je suis content !!! ???", "user1")
    
    assert result.emotion == 'joy'


# === Tests Result Object ===

def test_emotion_result_has_timestamp():
    """Test que EmotionResult contient un timestamp"""
    analyzer = EmotionAnalyzer()
    
    result = analyzer.analyze("Je suis content.", "user1")
    
    assert isinstance(result.timestamp, datetime)


def test_emotion_result_keywords_found():
    """Test que les mots-clés trouvés sont listés"""
    analyzer = EmotionAnalyzer()
    
    result = analyzer.analyze("Je suis heureux et content.", "user1")
    
    assert len(result.keywords_found) >= 2
    assert any('heureux' in kw or 'content' in kw for kw in result.keywords_found)


if __name__ == "__main__":
    # Lancer les tests
    pytest.main([__file__, "-v"])
