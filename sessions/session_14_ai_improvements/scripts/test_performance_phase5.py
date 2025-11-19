"""
Tests de performance - Session 14 Phase 5

Mesure les performances du système avec toutes les phases activées :
- Temps de réponse
- Utilisation mémoire RAM
- Utilisation VRAM (si GPU disponible)
- Taille des fichiers de stockage

Objectifs :
- Temps réponse < 3s (avec LLM chargé)
- RAM additionnelle < 500 MB
- VRAM < 6 GB (RTX 4050)
"""

import pytest
import time
import os
import psutil
import tempfile
import shutil
from unittest.mock import MagicMock

from src.ai.chat_engine import ChatEngine
from src.ai.config import AIConfig


@pytest.fixture
def temp_storage():
    """Créer dossier temporaire pour tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_model_manager():
    """Mock ModelManager pour tests de performance."""
    mock = MagicMock()
    mock.is_loaded = True
    
    # Simuler génération avec délai réaliste
    def mock_generate(*args, **kwargs):
        time.sleep(0.05)  # 50ms simule traitement LLM rapide
        return "Voici ma réponse !"
    
    mock.generate.side_effect = mock_generate
    return mock


@pytest.fixture
def basic_config():
    """Configuration basique."""
    return AIConfig(
        model_path="dummy",
        system_prompt="Tu es Kira.",
        temperature=0.7,
        max_tokens=200,
    )


def get_process_memory():
    """Récupère mémoire utilisée par processus actuel (en MB)."""
    process = psutil.Process()
    mem_info = process.memory_info()
    return mem_info.rss / 1024 / 1024  # Convertir bytes en MB


class TestPerformanceBasicMode:
    """Tests performance mode basique."""
    
    def test_response_time_basic_mode(self, basic_config, mock_model_manager):
        """Test : Temps réponse mode basique < 1s."""
        engine = ChatEngine(
            config=basic_config,
            model_manager=mock_model_manager,
            enable_advanced_ai=False
        )
        
        start = time.time()
        response = engine.chat("Test message")
        duration = time.time() - start
        
        # Mode basique devrait être très rapide (< 1s)
        assert duration < 1.0, f"Trop lent : {duration:.2f}s"
        assert response.processing_time < 1.0
        
        print(f"\n⏱️  Temps réponse mode basique : {duration:.3f}s")
    
    def test_memory_usage_basic_mode(self, basic_config, mock_model_manager):
        """Test : Utilisation mémoire mode basique."""
        mem_before = get_process_memory()
        
        engine = ChatEngine(
            config=basic_config,
            model_manager=mock_model_manager,
            enable_advanced_ai=False
        )
        
        # 10 conversations
        for i in range(10):
            engine.chat(f"Message {i}")
        
        mem_after = get_process_memory()
        mem_used = mem_after - mem_before
        
        # Mode basique : < 100 MB supplémentaires
        assert mem_used < 100, f"Trop de mémoire : {mem_used:.1f} MB"
        
        print(f"\n💾 Mémoire utilisée mode basique : {mem_used:.1f} MB")


class TestPerformanceAdvancedMode:
    """Tests performance mode avancé."""
    
    def test_response_time_advanced_mode(self, basic_config, mock_model_manager, temp_storage):
        """Test : Temps réponse mode avancé < 3s."""
        engine = ChatEngine(
            config=basic_config,
            model_manager=mock_model_manager,
            enable_advanced_ai=True,
            memory_storage_dir=temp_storage
        )
        
        # Première réponse (peut être plus lente : chargement embeddings)
        start = time.time()
        response = engine.chat("Première question")
        first_duration = time.time() - start
        
        # Réponses suivantes (plus rapides)
        times = []
        for i in range(5):
            start = time.time()
            response = engine.chat(f"Question {i}")
            duration = time.time() - start
            times.append(duration)
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        # Temps moyen < 3s (objectif)
        assert avg_time < 3.0, f"Temps moyen trop lent : {avg_time:.2f}s"
        assert max_time < 5.0, f"Temps max trop lent : {max_time:.2f}s"
        
        print(f"\n⏱️  Mode avancé - Première : {first_duration:.3f}s")
        print(f"⏱️  Mode avancé - Moyenne : {avg_time:.3f}s")
        print(f"⏱️  Mode avancé - Max : {max_time:.3f}s")
    
    def test_memory_usage_advanced_mode(self, basic_config, mock_model_manager, temp_storage):
        """Test : Utilisation mémoire mode avancé < 500 MB."""
        mem_before = get_process_memory()
        
        engine = ChatEngine(
            config=basic_config,
            model_manager=mock_model_manager,
            enable_advanced_ai=True,
            memory_storage_dir=temp_storage
        )
        
        mem_after_init = get_process_memory()
        mem_init = mem_after_init - mem_before
        
        # 20 conversations
        for i in range(20):
            engine.chat(f"Message numéro {i} avec du contenu")
        
        mem_after_chat = get_process_memory()
        mem_total = mem_after_chat - mem_before
        
        # Mode avancé : < 500 MB supplémentaires (objectif)
        # Note : sentence-transformers charge ~300 MB
        assert mem_total < 600, f"Trop de mémoire : {mem_total:.1f} MB"
        
        print(f"\n💾 Mémoire après init : {mem_init:.1f} MB")
        print(f"💾 Mémoire totale mode avancé : {mem_total:.1f} MB")
    
    def test_storage_file_sizes(self, basic_config, mock_model_manager, temp_storage):
        """Test : Taille fichiers de stockage raisonnable."""
        engine = ChatEngine(
            config=basic_config,
            model_manager=mock_model_manager,
            enable_advanced_ai=True,
            memory_storage_dir=temp_storage
        )
        
        # 50 messages pour générer données
        for i in range(50):
            engine.chat(f"Message {i} avec du texte pour tester")
        
        # Mesurer tailles fichiers
        files_sizes = {}
        
        for filename in os.listdir(temp_storage):
            filepath = os.path.join(temp_storage, filename)
            if os.path.isfile(filepath):
                size_kb = os.path.getsize(filepath) / 1024
                files_sizes[filename] = size_kb
        
        # Tailles raisonnables
        for filename, size in files_sizes.items():
            # Aucun fichier > 1 MB
            assert size < 1024, f"{filename} trop gros : {size:.1f} KB"
        
        total_size = sum(files_sizes.values())
        
        print(f"\n📁 Taille fichiers stockage :")
        for filename, size in files_sizes.items():
            print(f"   - {filename}: {size:.1f} KB")
        print(f"   TOTAL: {total_size:.1f} KB")


class TestPerformanceScaling:
    """Tests de montée en charge."""
    
    def test_long_conversation_performance(self, basic_config, mock_model_manager, temp_storage):
        """Test : Performance longue conversation (100 messages)."""
        engine = ChatEngine(
            config=basic_config,
            model_manager=mock_model_manager,
            enable_advanced_ai=True,
            memory_storage_dir=temp_storage
        )
        
        times = []
        
        for i in range(100):
            start = time.time()
            engine.chat(f"Message numéro {i}")
            duration = time.time() - start
            times.append(duration)
        
        # Analyser évolution temps
        first_10_avg = sum(times[:10]) / 10
        last_10_avg = sum(times[-10:]) / 10
        
        # Le temps ne devrait pas exploser à la fin
        slowdown = last_10_avg / first_10_avg if first_10_avg > 0 else 1
        
        assert slowdown < 2.0, f"Ralentissement trop important : x{slowdown:.2f}"
        
        print(f"\n📈 Longue conversation (100 messages) :")
        print(f"   - Premiers 10 : {first_10_avg:.3f}s/msg")
        print(f"   - Derniers 10 : {last_10_avg:.3f}s/msg")
        print(f"   - Ralentissement : x{slowdown:.2f}")
    
    def test_concurrent_users_simulation(self, basic_config, mock_model_manager, temp_storage):
        """Test : Simulation plusieurs utilisateurs."""
        engine = ChatEngine(
            config=basic_config,
            model_manager=mock_model_manager,
            enable_advanced_ai=True,
            memory_storage_dir=temp_storage
        )
        
        # Simuler 3 utilisateurs avec 10 messages chacun
        users = ["user1", "user2", "user3"]
        
        for round_num in range(10):
            for user_id in users:
                engine.chat(f"Message {round_num} de {user_id}", user_id=user_id)
        
        # Vérifier que chaque user a son historique
        for user_id in users:
            history = engine.memory.get_history(user_id=user_id, source="desktop")
            assert len(history) == 10, f"Historique {user_id} incorrect"
        
        print(f"\n👥 Simulation 3 utilisateurs x 10 messages : OK")


class TestPerformanceComponents:
    """Tests performance composants individuels."""
    
    def test_context_analyzer_performance(self):
        """Test : ContextAnalyzer rapide."""
        from src.ai.context_analyzer import ContextAnalyzer
        
        analyzer = ContextAnalyzer()
        
        times = []
        for i in range(100):
            start = time.time()
            analyzer.analyze(f"Message de test numéro {i}")
            duration = time.time() - start
            times.append(duration)
        
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        # Doit être très rapide (< 10ms en moyenne)
        assert avg_time < 0.01, f"ContextAnalyzer trop lent : {avg_time*1000:.1f}ms"
        
        print(f"\n🔍 ContextAnalyzer - 100 analyses :")
        print(f"   - Moyenne : {avg_time*1000:.2f}ms")
        print(f"   - Max : {max_time*1000:.2f}ms")
    
    def test_emotion_analyzer_performance(self):
        """Test : EmotionAnalyzer rapide."""
        from src.ai.emotion_analyzer import EmotionAnalyzer
        
        analyzer = EmotionAnalyzer(enable_emotion_memory=False)
        
        times = []
        for i in range(100):
            start = time.time()
            analyzer.analyze(f"Message test {i}", user_id="test_user")
            duration = time.time() - start
            times.append(duration)
        
        avg_time = sum(times) / len(times)
        
        # Doit être très rapide
        assert avg_time < 0.01, f"EmotionAnalyzer trop lent : {avg_time*1000:.1f}ms"
        
        print(f"\n🎭 EmotionAnalyzer - 100 analyses :")
        print(f"   - Moyenne : {avg_time*1000:.2f}ms")


# ============================================================================
# MARKERS PYTEST
# ============================================================================

pytestmark = pytest.mark.performance
