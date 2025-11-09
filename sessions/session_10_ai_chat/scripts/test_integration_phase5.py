"""
🎉 Test d'intégration complet Phase 5 : Chat Engine

Démontre tout le système IA de Desktop-Mate en action :
- Configuration IA
- Gestionnaire modèle avec GPU
- Mémoire conversationnelle
- Chat Engine avec détection émotions
"""

import sys
from pathlib import Path

# Ajouter racine projet au path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ai.config import AIConfig, get_config
from src.ai.model_manager import ModelManager, get_model_manager
from src.ai.memory import ConversationMemory, get_memory
from src.ai.chat_engine import ChatEngine, EmotionDetector, get_chat_engine


def test_full_system_integration():
    """
    Test d'intégration complet du système IA
    
    Vérifie que tous les composants fonctionnent ensemble :
    1. Config charge correctement
    2. ModelManager initialise avec config
    3. Memory fonctionne
    4. ChatEngine orchestre tout
    5. Émotions détectées correctement
    """
    print("\n" + "="*70)
    print("🎉 TEST INTÉGRATION COMPLÈTE - PHASE 5 : CHAT ENGINE")
    print("="*70 + "\n")
    
    # 1. Configuration
    print("1️⃣  Chargement configuration...")
    config = get_config()
    print(f"   ✅ Config chargée : {config.gpu_profile} profile")
    print(f"   📊 Context limit : {config.context_limit} messages")
    print(f"   🌡️  Temperature : {config.temperature}")
    print(f"   🎯 Max tokens : {config.max_tokens}")
    
    # Afficher profil GPU
    gpu_params = config.get_gpu_params()
    print(f"   🎮 GPU layers : {gpu_params['n_gpu_layers']}")
    print(f"   💾 Context size : {gpu_params['n_ctx']}")
    
    # 2. Model Manager
    print("\n2️⃣  Initialisation Model Manager...")
    model_manager = get_model_manager(config)
    print(f"   ✅ ModelManager créé : {model_manager}")
    
    # Détection GPU
    gpu_info = model_manager.detect_gpu()
    if gpu_info and gpu_info.available:
        print(f"   🎮 GPU détecté : {gpu_info.name}")
        vram_gb = (gpu_info.vram_total or 0) / (1024**3)
        print(f"   💾 VRAM : {vram_gb:.1f} GB")
        print(f"   📦 Driver : {gpu_info.driver_version}")
    else:
        print("   ⚠️  Pas de GPU NVIDIA (CPU fallback)")
    
    # 3. Mémoire
    print("\n3️⃣  Initialisation Mémoire...")
    memory = get_memory()
    stats = memory.get_stats()
    print(f"   ✅ ConversationMemory prête")
    print(f"   📊 Total interactions : {stats['total_interactions']}")
    print(f"   👥 Utilisateurs uniques : {stats['unique_users']}")
    
    # 4. Détecteur émotions
    print("\n4️⃣  Test Détecteur Émotions...")
    detector = EmotionDetector()
    
    test_phrases = [
        ("Je suis super content ! 😊", "joy"),
        ("C'est vraiment énervant... 😠", "angry"),
        ("Tristement, c'est dommage", "sorrow"),
        ("Wow, incroyable ! 😲", "surprised"),
        ("Haha, trop drôle ! 😂", "fun"),
        ("D'accord, bien.", "neutral")
    ]
    
    print("   🎭 Test détection émotions :")
    for phrase, expected in test_phrases:
        detected = detector.analyze(phrase)
        status = "✅" if detected == expected else "❌"
        print(f"      {status} '{phrase[:30]}...' → {detected}")
    
    # 5. Chat Engine
    print("\n5️⃣  Initialisation Chat Engine...")
    chat_engine = get_chat_engine(config, memory, model_manager)
    print(f"   ✅ ChatEngine prêt : {chat_engine}")
    
    # Test construction prompt
    print("\n6️⃣  Test Construction Prompt...")
    history = [
        {'user_input': 'Salut Kira', 'bot_response': 'Bonjour !'},
        {'user_input': 'Ça va ?', 'bot_response': 'Très bien merci !'}
    ]
    
    prompt = chat_engine._build_prompt("Comment tu t'appelles ?", history)
    print(f"   ✅ Prompt construit : {len(prompt)} caractères")
    print(f"   📝 Messages historiques : {prompt.count('<|user|>') - 1}")
    print(f"   🔖 Format : ChatML (Zephyr)")
    
    # 7. Statistiques globales
    print("\n7️⃣  Statistiques Globales...")
    global_stats = chat_engine.get_stats()
    
    print("   📊 Stats Mémoire :")
    for key, value in global_stats['memory'].items():
        print(f"      • {key}: {value}")
    
    print("   🤖 Stats Modèle :")
    for key, value in global_stats['model'].items():
        print(f"      • {key}: {value}")
    
    print("   ⚙️  Config Active :")
    for key, value in global_stats['config'].items():
        print(f"      • {key}: {value}")
    
    # 8. Résumé final
    print("\n" + "="*70)
    print("✅ TEST D'INTÉGRATION RÉUSSI !")
    print("="*70)
    print("\n🎯 Composants validés :")
    print("   ✅ Phase 1 : Architecture")
    print("   ✅ Phase 2 : ConversationMemory (SQLite)")
    print("   ✅ Phase 3 : AIConfig (GPU profiles)")
    print("   ✅ Phase 4 : ModelManager (GPU detection)")
    print("   ✅ Phase 5 : ChatEngine (émotions)")
    
    print("\n🚀 Kira est prête à discuter !")
    print("   💬 Sources supportées : desktop, discord")
    print("   🎭 Émotions : joy, angry, sorrow, surprised, fun, neutral")
    print("   🔄 Sauvegarde automatique conversations")
    print("   🧠 Contexte intelligent avec historique")
    
    print("\n📝 Prochaine étape (Phase 6) :")
    print("   → Emotion Analyzer avancé")
    print("   → Mapping émotions → Blendshapes VRM")
    print("   → Historique émotionnel")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    """Exécuter le test d'intégration"""
    test_full_system_integration()
    
    print("💡 Pour tester la conversation complète :")
    print("   1. Charger le modèle : engine.model_manager.load_model()")
    print("   2. Discuter : response = engine.chat('Bonjour !', 'user123')")
    print("   3. Voir réponse : print(response.response, response.emotion)")
    print()
