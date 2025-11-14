"""
Benchmark GPU Profiling - Session 11 Phase 5

Profiling GPU NVIDIA pour optimiser n_gpu_layers :
- Teste différents nombres de layers GPU (0, 10, 20, 30, 35, 40, 43, -1)
- Mesure VRAM utilisée par configuration
- Mesure tokens/sec, latency
- Génère profils dynamiques selon VRAM disponible

Objectif :
- Identifier sweet spot GPU layers vs VRAM
- Créer profils adaptatifs (auto-détection VRAM)
- Optimiser balance GPU/CPU selon hardware

Usage :
    python scripts/benchmark_gpu_profiling.py
"""

import os
import sys
import time
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Ajouter src/ au path pour imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False
    print("⚠️ pynvml non disponible. Installez-le : pip install pynvml")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from src.ai.model_manager import ModelManager
from src.ai.config import AIConfig, GPU_PROFILES


@dataclass
class GPUBenchmarkResult:
    """Résultat d'un benchmark pour une config GPU"""
    n_gpu_layers: int
    vram_used_gb: float
    vram_total_gb: float
    vram_percent: float
    tokens_generated: int
    duration_sec: float
    tokens_per_sec: float
    avg_latency_ms: float
    gpu_utilization: float
    temperature_celsius: int
    success: bool
    error_message: Optional[str] = None


class GPUProfiler:
    """
    Profiling GPU pour Workly (Kira)
    
    Teste différentes configurations n_gpu_layers et génère profils adaptatifs
    """
    
    def __init__(self, model_path: str = "models/zephyr-7b-beta.Q5_K_M.gguf"):
        """
        Initialise le profiler GPU
        
        Args:
            model_path: Chemin vers le modèle LLM
        """
        self.model_path = model_path
        self.results: List[GPUBenchmarkResult] = []
        self.gpu_info: Optional[Dict] = None
        
        # Vérifier modèle existe
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modèle introuvable : {model_path}")
        
        print(f"🎮 Benchmark GPU Profiling - Session 11 Phase 5\n")
        print(f"Modèle : {os.path.basename(model_path)}")
        
        # Détecter GPU
        self._detect_gpu()
        print()
    
    def _detect_gpu(self):
        """Détecte et affiche infos GPU"""
        if not PYNVML_AVAILABLE:
            print("❌ pynvml requis pour profiling GPU !")
            return
        
        try:
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            
            name = pynvml.nvmlDeviceGetName(handle)
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            driver = pynvml.nvmlSystemGetDriverVersion()
            
            self.gpu_info = {
                "name": name,
                "vram_total_gb": memory_info.total / (1024**3),
                "vram_free_gb": memory_info.free / (1024**3),
                "driver": driver
            }
            
            print(f"GPU : {name}")
            print(f"VRAM : {self.gpu_info['vram_total_gb']:.1f} GB total, "
                  f"{self.gpu_info['vram_free_gb']:.1f} GB libre")
            print(f"Driver : {driver}")
            
            pynvml.nvmlShutdown()
            
        except Exception as e:
            print(f"❌ Erreur détection GPU : {e}")
    
    def _get_gpu_stats(self) -> Dict[str, float]:
        """Récupère stats GPU actuelles"""
        if not PYNVML_AVAILABLE:
            return {
                "vram_used_gb": 0.0,
                "vram_percent": 0.0,
                "utilization": 0.0,
                "temperature": 0
            }
        
        try:
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            temperature = pynvml.nvmlDeviceGetTemperature(
                handle, 
                pynvml.NVML_TEMPERATURE_GPU
            )
            
            stats = {
                "vram_used_gb": memory_info.used / (1024**3),
                "vram_total_gb": memory_info.total / (1024**3),
                "vram_percent": (memory_info.used / memory_info.total) * 100,
                "utilization": utilization.gpu,
                "temperature": temperature
            }
            
            pynvml.nvmlShutdown()
            
            return stats
            
        except Exception as e:
            print(f"⚠️ Erreur récupération stats GPU : {e}")
            return {
                "vram_used_gb": 0.0,
                "vram_total_gb": 0.0,
                "vram_percent": 0.0,
                "utilization": 0.0,
                "temperature": 0
            }
    
    def run_single_benchmark(
        self,
        n_gpu_layers: int
    ) -> GPUBenchmarkResult:
        """
        Exécute un benchmark pour un nombre de layers GPU donné
        
        Args:
            n_gpu_layers: Nombre de layers GPU (0 = CPU only, -1 = all)
        
        Returns:
            GPUBenchmarkResult avec métriques
        """
        print(f"🧪 Test avec {n_gpu_layers} GPU layers "
              f"{'(all)' if n_gpu_layers == -1 else ''}...")
        
        # Créer config custom avec profil "balanced" de base
        config = AIConfig(
            model_path=self.model_path,
            gpu_profile="balanced",
            temperature=0.0,  # Déterministe
            max_tokens=256
        )
        
        # Override n_gpu_layers (hack temporaire)
        original_layers = GPU_PROFILES["balanced"]["n_gpu_layers"]
        GPU_PROFILES["balanced"]["n_gpu_layers"] = n_gpu_layers
        
        # Créer ModelManager
        manager = ModelManager(config)
        
        try:
            # Charger modèle
            print("   Chargement modèle...")
            load_start = time.time()
            manager.load_model(warm_cache=False)
            load_duration = time.time() - load_start
            print(f"   ✅ Chargé en {load_duration:.1f}s")
            
            # Attendre stabilisation (1 seconde)
            time.sleep(1.0)
            
            # Mesurer VRAM après chargement
            gpu_stats_load = self._get_gpu_stats()
            print(f"   VRAM : {gpu_stats_load['vram_used_gb']:.2f} GB "
                  f"({gpu_stats_load['vram_percent']:.0f}%)")
            
            # Prompt de test
            test_prompt = """<|system|>
Tu es Kira, un assistant virtuel amical.</s>
<|user|>
Explique-moi en 2-3 phrases ce qu'est l'apprentissage automatique.</s>
<|assistant|>
"""
            
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
                tokens_counts.append(len(response) // 4)  # Approximation
                
                print(f"      Run {i+1}/3: {duration:.2f}s")
            
            # Mesurer VRAM/GPU après génération
            gpu_stats_gen = self._get_gpu_stats()
            
            # Calculer métriques
            avg_duration = sum(durations) / len(durations)
            avg_tokens = sum(tokens_counts) / len(tokens_counts)
            tokens_per_sec = avg_tokens / avg_duration
            avg_latency_ms = (avg_duration / avg_tokens) * 1000 if avg_tokens > 0 else 0
            
            result = GPUBenchmarkResult(
                n_gpu_layers=n_gpu_layers,
                vram_used_gb=gpu_stats_gen['vram_used_gb'],
                vram_total_gb=gpu_stats_gen['vram_total_gb'],
                vram_percent=gpu_stats_gen['vram_percent'],
                tokens_generated=int(avg_tokens),
                duration_sec=avg_duration,
                tokens_per_sec=tokens_per_sec,
                avg_latency_ms=avg_latency_ms,
                gpu_utilization=gpu_stats_gen['utilization'],
                temperature_celsius=gpu_stats_gen['temperature'],
                success=True
            )
            
            print(f"   ✅ {tokens_per_sec:.1f} tok/s | "
                  f"VRAM: {gpu_stats_gen['vram_used_gb']:.2f} GB | "
                  f"GPU: {gpu_stats_gen['utilization']:.0f}% | "
                  f"Temp: {gpu_stats_gen['temperature']}°C")
            print()
            
            return result
            
        except Exception as e:
            # Erreur (probablement OOM)
            print(f"   ❌ Erreur : {e}")
            print()
            
            gpu_stats = self._get_gpu_stats()
            
            return GPUBenchmarkResult(
                n_gpu_layers=n_gpu_layers,
                vram_used_gb=gpu_stats['vram_used_gb'],
                vram_total_gb=gpu_stats['vram_total_gb'],
                vram_percent=gpu_stats['vram_percent'],
                tokens_generated=0,
                duration_sec=0.0,
                tokens_per_sec=0.0,
                avg_latency_ms=0.0,
                gpu_utilization=0.0,
                temperature_celsius=0,
                success=False,
                error_message=str(e)
            )
            
        finally:
            # Décharger modèle
            manager.unload_model()
            
            # Restaurer profil original
            GPU_PROFILES["balanced"]["n_gpu_layers"] = original_layers
            
            # Attendre libération VRAM (2 secondes)
            time.sleep(2.0)
    
    def run_full_profiling(
        self,
        layers_list: List[int] = None
    ):
        """
        Exécute profiling complet GPU
        
        Args:
            layers_list: Liste des n_gpu_layers à tester (None = défaut)
        """
        if layers_list is None:
            # Configuration par défaut : Progressive jusqu'à limite
            layers_list = [0, 10, 20, 30, 35, 40, 43, -1]
        
        print(f"🚀 Démarrage profiling : {len(layers_list)} configurations\n")
        
        # Tester chaque configuration
        for n_layers in layers_list:
            try:
                result = self.run_single_benchmark(n_layers)
                self.results.append(result)
                
                # Arrêter si OOM détecté
                if not result.success and "out of memory" in str(result.error_message).lower():
                    print("⚠️ VRAM insuffisante détectée. Arrêt du profiling.")
                    break
                    
            except KeyboardInterrupt:
                print("\n⚠️ Profiling interrompu par l'utilisateur")
                break
            except Exception as e:
                print(f"❌ Erreur inattendue : {e}\n")
    
    def display_results(self):
        """Affiche les résultats du profiling"""
        if not self.results:
            print("❌ Aucun résultat disponible")
            return
        
        print("\n" + "="*90)
        print("🎮 RÉSULTATS PROFILING GPU")
        print("="*90 + "\n")
        
        # Filtrer succès uniquement
        successful = [r for r in self.results if r.success]
        
        if not successful:
            print("❌ Aucune configuration réussie")
            return
        
        # Trier par tokens/sec décroissant
        sorted_results = sorted(
            successful,
            key=lambda r: r.tokens_per_sec,
            reverse=True
        )
        
        # Afficher tableau
        print(f"{'Layers':<10} {'VRAM GB':<12} {'VRAM %':<10} {'Tok/s':<12} "
              f"{'GPU %':<10} {'Temp°C':<10}")
        print("-" * 90)
        
        best_result = sorted_results[0]
        
        for result in sorted_results:
            marker = "🏆" if result == best_result else "  "
            layers_str = "All" if result.n_gpu_layers == -1 else str(result.n_gpu_layers)
            
            print(
                f"{marker} {layers_str:<8} "
                f"{result.vram_used_gb:<10.2f}  "
                f"{result.vram_percent:<8.0f}%  "
                f"{result.tokens_per_sec:<10.1f}  "
                f"{result.gpu_utilization:<8.0f}%  "
                f"{result.temperature_celsius:<8}°C"
            )
        
        print()
        
        # Analyse
        print("📈 ANALYSE :\n")
        print(f"🏆 Optimal : {best_result.n_gpu_layers} layers")
        print(f"   → {best_result.tokens_per_sec:.1f} tokens/sec")
        print(f"   → {best_result.vram_used_gb:.2f} GB VRAM "
              f"({best_result.vram_percent:.0f}%)")
        
        # Trouver config 0 layers (CPU baseline)
        cpu_result = next((r for r in successful if r.n_gpu_layers == 0), None)
        if cpu_result:
            speedup = best_result.tokens_per_sec / cpu_result.tokens_per_sec
            print(f"\n⚡ Speedup vs CPU : {speedup:.1f}x")
        
        # Recommandations profils
        self._generate_profile_recommendations(successful)
    
    def _generate_profile_recommendations(self, results: List[GPUBenchmarkResult]):
        """Génère recommandations de profils selon VRAM"""
        print("\n💡 PROFILS RECOMMANDÉS :\n")
        
        if not self.gpu_info:
            print("⚠️ Infos GPU non disponibles")
            return
        
        vram_total = self.gpu_info['vram_total_gb']
        
        # Trouver configs selon budget VRAM
        configs_by_vram = {}
        for r in results:
            if r.vram_percent < 90:  # Garder 10% marge
                configs_by_vram[r.n_gpu_layers] = r
        
        # Recommandations
        print(f"GPU : {self.gpu_info['name']} ({vram_total:.1f} GB VRAM)\n")
        
        # Profil "fast" (< 50% VRAM)
        fast_configs = [r for r in results if r.vram_percent < 50 and r.success]
        if fast_configs:
            fast = max(fast_configs, key=lambda r: r.tokens_per_sec)
            print(f"🚀 Profil FAST (< 50% VRAM) :")
            print(f"   n_gpu_layers: {fast.n_gpu_layers}")
            print(f"   VRAM: {fast.vram_used_gb:.2f} GB ({fast.vram_percent:.0f}%)")
            print(f"   Perf: {fast.tokens_per_sec:.1f} tok/s")
        
        # Profil "balanced" (50-70% VRAM)
        balanced_configs = [r for r in results if 50 <= r.vram_percent < 70 and r.success]
        if balanced_configs:
            balanced = max(balanced_configs, key=lambda r: r.tokens_per_sec)
            print(f"\n⚖️ Profil BALANCED (50-70% VRAM) :")
            print(f"   n_gpu_layers: {balanced.n_gpu_layers}")
            print(f"   VRAM: {balanced.vram_used_gb:.2f} GB ({balanced.vram_percent:.0f}%)")
            print(f"   Perf: {balanced.tokens_per_sec:.1f} tok/s")
        
        # Profil "performance" (70-85% VRAM)
        perf_configs = [r for r in results if 70 <= r.vram_percent < 85 and r.success]
        if perf_configs:
            perf = max(perf_configs, key=lambda r: r.tokens_per_sec)
            print(f"\n🔥 Profil PERFORMANCE (70-85% VRAM) :")
            print(f"   n_gpu_layers: {perf.n_gpu_layers}")
            print(f"   VRAM: {perf.vram_used_gb:.2f} GB ({perf.vram_percent:.0f}%)")
            print(f"   Perf: {perf.tokens_per_sec:.1f} tok/s")
        
        print()
    
    def save_results(self, output_file: str = "scripts/benchmark_gpu_results.json"):
        """
        Sauvegarde les résultats au format JSON
        
        Args:
            output_file: Chemin fichier de sortie
        """
        results_dict = {
            "benchmark": "gpu_profiling",
            "model": os.path.basename(self.model_path),
            "gpu_info": self.gpu_info,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": [
                {
                    "n_gpu_layers": r.n_gpu_layers,
                    "vram_used_gb": r.vram_used_gb,
                    "vram_percent": r.vram_percent,
                    "tokens_generated": r.tokens_generated,
                    "duration_sec": r.duration_sec,
                    "tokens_per_sec": r.tokens_per_sec,
                    "avg_latency_ms": r.avg_latency_ms,
                    "gpu_utilization": r.gpu_utilization,
                    "temperature_celsius": r.temperature_celsius,
                    "success": r.success,
                    "error": r.error_message
                }
                for r in self.results
            ]
        }
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_dict, f, indent=4, ensure_ascii=False)
        
        print(f"💾 Résultats sauvegardés : {output_file}\n")


def main():
    """Point d'entrée du profiling"""
    print("🎯 Benchmark GPU Profiling - Workly (Session 11 Phase 5)\n")
    
    # Vérifier pynvml
    if not PYNVML_AVAILABLE:
        print("❌ ERREUR : pynvml requis pour profiling GPU")
        print("   Installez-le : pip install pynvml\n")
        return
    
    # Créer profiler
    profiler = GPUProfiler()
    
    if not profiler.gpu_info:
        print("❌ Aucun GPU détecté. Profiling impossible.")
        return
    
    # Choix configuration
    print("\nConfiguration à tester :")
    print("1. Rapide (0, 20, 35, 43)")
    print("2. Complète (0, 10, 20, 30, 35, 40, 43, -1)")
    print("3. Custom")
    
    choice = input("\nChoix [1]: ").strip() or "1"
    
    if choice == "1":
        layers_list = [0, 20, 35, 43]
    elif choice == "2":
        layers_list = [0, 10, 20, 30, 35, 40, 43, -1]
    elif choice == "3":
        layers_input = input("Liste de layers (ex: 0,20,35,43) : ").strip()
        layers_list = [int(l.strip()) if l.strip() != '-1' else -1 
                       for l in layers_input.split(',')]
    else:
        layers_list = [0, 20, 35, 43]
    
    print()
    
    try:
        # Exécuter profiling
        profiler.run_full_profiling(layers_list=layers_list)
        
        # Afficher résultats
        profiler.display_results()
        
        # Sauvegarder
        profiler.save_results()
        
        print("✅ Profiling terminé avec succès !")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Profiling interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
