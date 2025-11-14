"""
Benchmark CPU Threads - Session 11 Phase 4

Test de performance avec différents nombres de threads CPU :
- 1, 2, 4, 6, 8, 12, 16 threads
- "auto" (détection automatique)
- Mesure : tokens/sec, latency, temps génération

Objectif :
- Valider l'heuristique get_optimal_threads()
- Identifier le sweet spot CPU pour votre hardware
- Mesurer gain de performance vs baseline (6 threads fixes)

Usage :
    python scripts/benchmark_cpu_threads.py
"""

import os
import sys
import time
import json
from typing import List, Dict, Any
from dataclasses import dataclass

# Ajouter src/ au path pour imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil non disponible. Installez-le : pip install psutil")

from src.ai.model_manager import ModelManager
from src.ai.config import AIConfig, get_optimal_threads


@dataclass
class BenchmarkResult:
    """Résultat d'un benchmark pour un nombre de threads"""
    n_threads: int
    is_auto: bool
    tokens_generated: int
    duration_sec: float
    tokens_per_sec: float
    avg_latency_ms: float
    cpu_percent: float
    ram_used_gb: float


class CPUBenchmark:
    """
    Benchmark CPU threads pour Workly (Kira)
    
    Test différentes configurations n_threads et compare les performances
    """
    
    def __init__(self, model_path: str = "models/zephyr-7b-beta.Q5_K_M.gguf"):
        """
        Initialise le benchmark
        
        Args:
            model_path: Chemin vers le modèle LLM
        """
        self.model_path = model_path
        self.results: List[BenchmarkResult] = []
        
        # Vérifier modèle existe
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modèle introuvable : {model_path}")
        
        print(f"📊 Benchmark CPU Threads - Session 11 Phase 4\n")
        print(f"Modèle : {os.path.basename(model_path)}")
        
        # Afficher infos CPU
        if PSUTIL_AVAILABLE:
            physical = psutil.cpu_count(logical=False)
            logical = psutil.cpu_count(logical=True)
            print(f"CPU : {physical} cores physiques, {logical} threads logiques")
        
        print()
    
    def run_single_benchmark(
        self,
        n_threads: int,
        is_auto: bool = False,
        gpu_profile: str = "balanced"
    ) -> BenchmarkResult:
        """
        Exécute un benchmark pour un nombre de threads donné
        
        Args:
            n_threads: Nombre de threads CPU (ou valeur auto-détectée)
            is_auto: True si n_threads vient de l'auto-détection
            gpu_profile: Profil GPU à utiliser
        
        Returns:
            BenchmarkResult avec métriques
        """
        print(f"🧪 Test avec {n_threads} threads {'(auto)' if is_auto else ''}...")
        
        # Créer config custom
        config = AIConfig(
            model_path=self.model_path,
            gpu_profile=gpu_profile,
            temperature=0.0,  # Déterministe pour benchmark
            max_tokens=256
        )
        
        # Override n_threads dans profil (hack temporaire)
        from src.ai.config import GPU_PROFILES
        original_threads = GPU_PROFILES[gpu_profile]["n_threads"]
        GPU_PROFILES[gpu_profile]["n_threads"] = n_threads
        
        # Créer ModelManager
        manager = ModelManager(config)
        
        try:
            # Charger modèle (sans warming cache pour benchmark pur)
            print("   Chargement modèle...")
            load_start = time.time()
            manager.load_model(warm_cache=False)
            load_duration = time.time() - load_start
            print(f"   ✅ Modèle chargé en {load_duration:.1f}s")
            
            # Prompt de test (représentatif d'une conversation)
            test_prompt = """<|system|>
Tu es Kira, un assistant virtuel amical et compétent.</s>
<|user|>
Explique-moi en 2-3 phrases ce qu'est l'apprentissage automatique.</s>
<|assistant|>
"""
            
            # Monitorer ressources avant
            if PSUTIL_AVAILABLE:
                process = psutil.Process()
                cpu_before = psutil.cpu_percent(interval=0.1)
                ram_before_gb = process.memory_info().rss / (1024**3)
            
            # Génération (3 runs pour moyenne)
            print("   Génération...")
            durations = []
            tokens_counts = []
            
            for i in range(3):
                start = time.time()
                response = manager.generate(
                    prompt=test_prompt,
                    max_tokens=256,
                    temperature=0.0
                )
                duration = time.time() - start
                
                durations.append(duration)
                # Approximation : ~0.25 token par caractère français
                tokens_counts.append(len(response) // 4)
                
                print(f"      Run {i+1}/3: {duration:.2f}s ({len(response)} chars)")
            
            # Monitorer ressources après
            if PSUTIL_AVAILABLE:
                cpu_after = psutil.cpu_percent(interval=0.1)
                ram_after_gb = process.memory_info().rss / (1024**3)
                cpu_percent = (cpu_before + cpu_after) / 2
                ram_used_gb = ram_after_gb
            else:
                cpu_percent = 0.0
                ram_used_gb = 0.0
            
            # Calculer métriques
            avg_duration = sum(durations) / len(durations)
            avg_tokens = sum(tokens_counts) / len(tokens_counts)
            tokens_per_sec = avg_tokens / avg_duration
            avg_latency_ms = (avg_duration / avg_tokens) * 1000 if avg_tokens > 0 else 0
            
            result = BenchmarkResult(
                n_threads=n_threads,
                is_auto=is_auto,
                tokens_generated=int(avg_tokens),
                duration_sec=avg_duration,
                tokens_per_sec=tokens_per_sec,
                avg_latency_ms=avg_latency_ms,
                cpu_percent=cpu_percent,
                ram_used_gb=ram_used_gb
            )
            
            print(f"   ✅ {tokens_per_sec:.1f} tok/s | latency: {avg_latency_ms:.1f}ms")
            print()
            
            return result
            
        finally:
            # Décharger modèle
            manager.unload_model()
            
            # Restaurer profil original
            GPU_PROFILES[gpu_profile]["n_threads"] = original_threads
    
    def run_full_benchmark(
        self,
        threads_list: List[int] = None,
        include_auto: bool = True
    ):
        """
        Exécute benchmark complet avec différentes configurations
        
        Args:
            threads_list: Liste des n_threads à tester (None = défaut)
            include_auto: Si True, teste aussi "auto"
        """
        if threads_list is None:
            # Configuration par défaut
            threads_list = [1, 2, 4, 6, 8]
            
            # Ajouter 12, 16 si CPU le permet
            if PSUTIL_AVAILABLE:
                logical = psutil.cpu_count(logical=True) or 8
                if logical >= 12:
                    threads_list.append(12)
                if logical >= 16:
                    threads_list.append(16)
        
        print(f"🚀 Démarrage benchmark : {len(threads_list)} configurations\n")
        
        # Tester chaque configuration
        for n_threads in threads_list:
            try:
                result = self.run_single_benchmark(n_threads)
                self.results.append(result)
            except Exception as e:
                print(f"   ❌ Erreur : {e}\n")
        
        # Tester "auto"
        if include_auto:
            try:
                auto_threads = get_optimal_threads()
                print(f"🤖 Test configuration AUTO (détecté : {auto_threads} threads)...")
                result = self.run_single_benchmark(auto_threads, is_auto=True)
                self.results.append(result)
            except Exception as e:
                print(f"   ❌ Erreur auto : {e}\n")
    
    def display_results(self):
        """Affiche les résultats du benchmark"""
        if not self.results:
            print("❌ Aucun résultat disponible")
            return
        
        print("\n" + "="*80)
        print("📊 RÉSULTATS BENCHMARK CPU THREADS")
        print("="*80 + "\n")
        
        # Trier par tokens/sec décroissant
        sorted_results = sorted(
            self.results,
            key=lambda r: r.tokens_per_sec,
            reverse=True
        )
        
        # Afficher tableau
        print(f"{'Threads':<10} {'Auto?':<8} {'Tok/s':<12} {'Latency':<15} {'CPU%':<10} {'RAM GB':<10}")
        print("-" * 80)
        
        best_result = sorted_results[0]
        
        for result in sorted_results:
            # Marquer le meilleur
            marker = "🏆" if result == best_result else "  "
            auto_mark = "✅" if result.is_auto else "  "
            
            print(
                f"{marker} {result.n_threads:<7} {auto_mark:<7} "
                f"{result.tokens_per_sec:<10.1f}  "
                f"{result.avg_latency_ms:<13.1f}ms  "
                f"{result.cpu_percent:<8.0f}%  "
                f"{result.ram_used_gb:<8.1f} GB"
            )
        
        print()
        
        # Statistiques
        print("📈 ANALYSE :\n")
        print(f"🏆 Meilleur : {best_result.n_threads} threads")
        print(f"   → {best_result.tokens_per_sec:.1f} tokens/sec")
        print(f"   → {best_result.avg_latency_ms:.1f}ms latency")
        
        # Comparer avec baseline (6 threads)
        baseline = next((r for r in self.results if r.n_threads == 6 and not r.is_auto), None)
        if baseline:
            gain_percent = ((best_result.tokens_per_sec - baseline.tokens_per_sec) / baseline.tokens_per_sec) * 100
            print(f"\n📊 Gain vs baseline (6 threads) : {gain_percent:+.1f}%")
        
        # Trouver résultat auto
        auto_result = next((r for r in self.results if r.is_auto), None)
        if auto_result:
            auto_gain = ((auto_result.tokens_per_sec - baseline.tokens_per_sec) / baseline.tokens_per_sec) * 100 if baseline else 0
            print(f"\n🤖 Configuration AUTO ({auto_result.n_threads} threads) :")
            print(f"   → {auto_result.tokens_per_sec:.1f} tok/s")
            print(f"   → Gain vs baseline : {auto_gain:+.1f}%")
            
            if auto_result == best_result:
                print("   ✅ AUTO = Optimal ! Heuristique parfaite 🎯")
            else:
                efficiency = (auto_result.tokens_per_sec / best_result.tokens_per_sec) * 100
                print(f"   ⚠️ AUTO = {efficiency:.0f}% de l'optimal (acceptable si >90%)")
        
        print()
    
    def save_results(self, output_file: str = "scripts/benchmark_cpu_results.json"):
        """
        Sauvegarde les résultats au format JSON
        
        Args:
            output_file: Chemin fichier de sortie
        """
        results_dict = {
            "benchmark": "cpu_threads",
            "model": os.path.basename(self.model_path),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": [
                {
                    "n_threads": r.n_threads,
                    "is_auto": r.is_auto,
                    "tokens_generated": r.tokens_generated,
                    "duration_sec": r.duration_sec,
                    "tokens_per_sec": r.tokens_per_sec,
                    "avg_latency_ms": r.avg_latency_ms,
                    "cpu_percent": r.cpu_percent,
                    "ram_used_gb": r.ram_used_gb
                }
                for r in self.results
            ]
        }
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_dict, f, indent=4, ensure_ascii=False)
        
        print(f"💾 Résultats sauvegardés : {output_file}\n")


def main():
    """Point d'entrée du benchmark"""
    print("🎯 Benchmark CPU Threads - Workly (Session 11 Phase 4)\n")
    
    # Vérifier psutil
    if not PSUTIL_AVAILABLE:
        print("⚠️ AVERTISSEMENT : psutil non disponible")
        print("   Auto-détection désactivée. Installez-le : pip install psutil\n")
    
    # Créer benchmark
    benchmark = CPUBenchmark()
    
    # Choix configuration
    print("Configuration à tester :")
    print("1. Rapide (1, 2, 4, 6, 8, auto)")
    print("2. Complète (1, 2, 4, 6, 8, 12, 16, auto)")
    print("3. Custom")
    
    choice = input("\nChoix [1]: ").strip() or "1"
    
    if choice == "1":
        threads_list = [1, 2, 4, 6, 8]
    elif choice == "2":
        threads_list = [1, 2, 4, 6, 8, 12, 16]
    elif choice == "3":
        threads_input = input("Liste de threads (ex: 2,4,6,8) : ").strip()
        threads_list = [int(t.strip()) for t in threads_input.split(',')]
    else:
        threads_list = [1, 2, 4, 6, 8]
    
    print()
    
    try:
        # Exécuter benchmark
        benchmark.run_full_benchmark(threads_list=threads_list)
        
        # Afficher résultats
        benchmark.display_results()
        
        # Sauvegarder
        benchmark.save_results()
        
        print("✅ Benchmark terminé avec succès !")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Benchmark interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
