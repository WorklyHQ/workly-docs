#!/usr/bin/env python3
"""
Test Warming Cache - Compare avant/après

Mesure l'impact du warming cache sur la latence première génération.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai.config import AIConfig
from ai.model_manager import ModelManager


def test_without_warming():
    """Test sans warming cache"""
    print("\n" + "="*80)
    print("TEST 1 : SANS WARMING CACHE")
    print("="*80)
    
    # Charger modèle SANS warming
    print("\n⏳ Chargement modèle (sans warming)...")
    start_load = time.time()
    
    config = AIConfig()
    manager = ModelManager(config)
    manager.load_model(warm_cache=False)
    
    load_time = time.time() - start_load
    print(f"✅ Modèle chargé en {load_time:.2f}s")
    
    # Première génération utilisateur (cold cache)
    print("\n⏳ Première génération utilisateur (cold cache)...")
    start_gen = time.time()
    
    response = manager.generate(
        "Bonjour, comment vas-tu ?",
        max_tokens=50,
        temperature=0.7
    )
    
    first_gen_time = time.time() - start_gen
    tokens = len(response.split())
    tps = tokens / first_gen_time if first_gen_time > 0 else 0
    
    print(f"✅ Première génération terminée en {first_gen_time:.2f}s")
    print(f"   Tokens : {tokens}, Vitesse : {tps:.2f} tok/s")
    
    # Deuxième génération (warm cache)
    print("\n⏳ Deuxième génération (warm cache)...")
    start_gen2 = time.time()
    
    response2 = manager.generate(
        "Parle-moi de toi",
        max_tokens=50,
        temperature=0.7
    )
    
    second_gen_time = time.time() - start_gen2
    tokens2 = len(response2.split())
    tps2 = tokens2 / second_gen_time if second_gen_time > 0 else 0
    
    print(f"✅ Deuxième génération terminée en {second_gen_time:.2f}s")
    print(f"   Tokens : {tokens2}, Vitesse : {tps2:.2f} tok/s")
    
    # Décharger
    manager.unload_model()
    
    return {
        'load_time': load_time,
        'first_gen_time': first_gen_time,
        'second_gen_time': second_gen_time,
        'tokens_first': tokens,
        'tokens_second': tokens2,
        'tps_first': tps,
        'tps_second': tps2
    }


def test_with_warming():
    """Test avec warming cache"""
    print("\n" + "="*80)
    print("TEST 2 : AVEC WARMING CACHE")
    print("="*80)
    
    # Charger modèle AVEC warming
    print("\n⏳ Chargement modèle (avec warming)...")
    start_load = time.time()
    
    config = AIConfig()
    manager = ModelManager(config)
    manager.load_model(warm_cache=True)  # Warming activé
    
    load_time = time.time() - start_load
    print(f"✅ Modèle chargé en {load_time:.2f}s (inclut warming)")
    
    # Première génération utilisateur (cache déjà warm!)
    print("\n⏳ Première génération utilisateur (cache warm)...")
    start_gen = time.time()
    
    response = manager.generate(
        "Bonjour, comment vas-tu ?",
        max_tokens=50,
        temperature=0.7
    )
    
    first_gen_time = time.time() - start_gen
    tokens = len(response.split())
    tps = tokens / first_gen_time if first_gen_time > 0 else 0
    
    print(f"✅ Première génération terminée en {first_gen_time:.2f}s")
    print(f"   Tokens : {tokens}, Vitesse : {tps:.2f} tok/s")
    
    # Deuxième génération
    print("\n⏳ Deuxième génération...")
    start_gen2 = time.time()
    
    response2 = manager.generate(
        "Parle-moi de toi",
        max_tokens=50,
        temperature=0.7
    )
    
    second_gen_time = time.time() - start_gen2
    tokens2 = len(response2.split())
    tps2 = tokens2 / second_gen_time if second_gen_time > 0 else 0
    
    print(f"✅ Deuxième génération terminée en {second_gen_time:.2f}s")
    print(f"   Tokens : {tokens2}, Vitesse : {tps2:.2f} tok/s")
    
    # Décharger
    manager.unload_model()
    
    return {
        'load_time': load_time,
        'first_gen_time': first_gen_time,
        'second_gen_time': second_gen_time,
        'tokens_first': tokens,
        'tokens_second': tokens2,
        'tps_first': tps,
        'tps_second': tps2
    }


def main():
    print("\n" + "="*80)
    print("TEST WARMING CACHE - Desktop-Mate")
    print("="*80)
    
    # Test 1 : Sans warming
    results_without = test_without_warming()
    
    # Pause
    print("\n⏳ Pause 3s avant test 2...\n")
    time.sleep(3)
    
    # Test 2 : Avec warming
    results_with = test_with_warming()
    
    # Comparaison
    print("\n" + "="*80)
    print("COMPARAISON RÉSULTATS")
    print("="*80)
    
    print("\n📊 Temps Chargement Modèle :")
    print(f"   Sans warming : {results_without['load_time']:.2f}s")
    print(f"   Avec warming : {results_with['load_time']:.2f}s")
    diff_load = results_with['load_time'] - results_without['load_time']
    print(f"   Différence   : +{diff_load:.2f}s ({diff_load/results_without['load_time']*100:+.1f}%)")
    
    print("\n📊 Première Génération Utilisateur :")
    print(f"   Sans warming : {results_without['first_gen_time']:.2f}s")
    print(f"   Avec warming : {results_with['first_gen_time']:.2f}s")
    diff_first = results_with['first_gen_time'] - results_without['first_gen_time']
    improvement = (results_without['first_gen_time'] - results_with['first_gen_time']) / results_without['first_gen_time'] * 100
    print(f"   Différence   : {diff_first:.2f}s ({improvement:+.1f}%)")
    
    if improvement > 0:
        print(f"   🎉 AMÉLIORATION : -{improvement:.1f}% de latence !")
    else:
        print(f"   ⚠️ Pas d'amélioration visible")
    
    print("\n📊 Deuxième Génération :")
    print(f"   Sans warming : {results_without['second_gen_time']:.2f}s")
    print(f"   Avec warming : {results_with['second_gen_time']:.2f}s")
    diff_second = results_with['second_gen_time'] - results_without['second_gen_time']
    print(f"   Différence   : {diff_second:.2f}s ({diff_second/results_without['second_gen_time']*100:+.1f}%)")
    
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    
    # Trade-off warming
    overhead_warming = diff_load  # Temps additionnel au chargement
    gain_first_gen = -diff_first  # Temps gagné sur première génération
    
    print(f"\n💰 Trade-off Warming :")
    print(f"   Coût   : +{overhead_warming:.2f}s au chargement")
    print(f"   Gain   : {gain_first_gen:.2f}s sur 1ère génération")
    print(f"   Net    : {gain_first_gen - overhead_warming:.2f}s")
    
    if gain_first_gen > overhead_warming:
        print(f"\n✅ RECOMMANDATION : Activer warming (gain net positif)")
    else:
        print(f"\n⚠️ RECOMMANDATION : Warming discutable (coût > gain)")
    
    print("\n💡 Conseil :")
    print("   - Activer warming si chargement au démarrage app (une fois)")
    print("   - Désactiver warming si chargement à la demande (fréquent)")


if __name__ == "__main__":
    main()
