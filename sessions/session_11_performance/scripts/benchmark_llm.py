#!/usr/bin/env python3
"""
LLM Benchmarking Script for Desktop-Mate

Mesure les latences et performances du modèle LLM dans différentes conditions.

Usage:
    python scripts/benchmark_llm.py
    
Outputs:
    - Console : Métriques en temps réel
    - Fichier : llm_benchmark_results.txt
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple
import statistics

# Ajouter src/ au path pour imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai.config import AIConfig
from ai.model_manager import ModelManager


class LLMBenchmark:
    """Benchmark pour tester les performances du LLM"""
    
    def __init__(self):
        self.results: List[Dict] = []
        self.ai_config = AIConfig()
        self.model_manager = None
    
    def benchmark_cold_start(self) -> Dict:
        """Benchmark 1 : Cold start (chargement + première génération)"""
        print("\n" + "="*80)
        print("BENCHMARK 1 : COLD START")
        print("="*80)
        
        # Mesure chargement modèle
        print("\n⏳ Chargement du modèle...")
        start_load = time.time()
        
        self.model_manager = ModelManager(self.ai_config)
        self.model_manager.load_model()
        
        load_time = time.time() - start_load
        print(f"✅ Modèle chargé en {load_time:.2f}s")
        
        # Mesure première génération (cold cache)
        print("\n⏳ Première génération (cold cache)...")
        test_prompt = "Bonjour, comment vas-tu ?"
        
        start_gen = time.time()
        response = self.model_manager.generate(
            test_prompt,
            max_tokens=50,
            temperature=0.7
        )
        gen_time = time.time() - start_gen
        
        tokens = len(response.split())
        tokens_per_sec = tokens / gen_time if gen_time > 0 else 0
        
        print(f"✅ Génération terminée en {gen_time:.2f}s")
        print(f"   Tokens générés : {tokens}")
        print(f"   Vitesse : {tokens_per_sec:.2f} tokens/sec")
        
        result = {
            'benchmark': 'cold_start',
            'load_time': load_time,
            'first_gen_time': gen_time,
            'tokens': tokens,
            'tokens_per_sec': tokens_per_sec,
            'prompt': test_prompt,
            'response_len': len(response)
        }
        
        self.results.append(result)
        return result
    
    def benchmark_warm_cache(self, num_runs: int = 10) -> Dict:
        """Benchmark 2 : Warm cache (générations suivantes)"""
        print("\n" + "="*80)
        print(f"BENCHMARK 2 : WARM CACHE ({num_runs} runs)")
        print("="*80)
        
        if not self.model_manager or not self.model_manager.is_loaded:
            raise RuntimeError("Modèle non chargé ! Exécutez benchmark_cold_start() d'abord.")
        
        test_prompts = [
            "Bonjour !",
            "Comment vas-tu ?",
            "Parle-moi de toi",
            "Quel temps fait-il ?",
            "Raconte-moi une blague"
        ]
        
        latencies = []
        tokens_per_sec_list = []
        
        print(f"\n⏳ Exécution de {num_runs} générations...")
        
        for i in range(num_runs):
            prompt = test_prompts[i % len(test_prompts)]
            
            start = time.time()
            response = self.model_manager.generate(
                prompt,
                max_tokens=50,
                temperature=0.7
            )
            latency = time.time() - start
            
            tokens = len(response.split())
            tps = tokens / latency if latency > 0 else 0
            
            latencies.append(latency)
            tokens_per_sec_list.append(tps)
            
            if (i + 1) % 5 == 0:
                print(f"  {i+1}/{num_runs} générations terminées...")
        
        # Statistiques
        avg_latency = statistics.mean(latencies)
        median_latency = statistics.median(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        stdev_latency = statistics.stdev(latencies) if len(latencies) > 1 else 0
        
        avg_tps = statistics.mean(tokens_per_sec_list)
        median_tps = statistics.median(tokens_per_sec_list)
        
        print(f"\n✅ Benchmark terminé !")
        print(f"   Latence moyenne : {avg_latency:.3f}s")
        print(f"   Latence médiane : {median_latency:.3f}s")
        print(f"   Latence min/max : {min_latency:.3f}s / {max_latency:.3f}s")
        print(f"   Écart-type : {stdev_latency:.3f}s")
        print(f"   Vitesse moyenne : {avg_tps:.2f} tokens/sec")
        print(f"   Vitesse médiane : {median_tps:.2f} tokens/sec")
        
        result = {
            'benchmark': 'warm_cache',
            'num_runs': num_runs,
            'avg_latency': avg_latency,
            'median_latency': median_latency,
            'min_latency': min_latency,
            'max_latency': max_latency,
            'stdev_latency': stdev_latency,
            'avg_tokens_per_sec': avg_tps,
            'median_tokens_per_sec': median_tps,
            'all_latencies': latencies,
            'all_tps': tokens_per_sec_list
        }
        
        self.results.append(result)
        return result
    
    def benchmark_context_sizes(self) -> Dict:
        """Benchmark 3 : Impact de la taille du contexte"""
        print("\n" + "="*80)
        print("BENCHMARK 3 : IMPACT TAILLE CONTEXTE")
        print("="*80)
        
        if not self.model_manager or not self.model_manager.is_loaded:
            raise RuntimeError("Modèle non chargé ! Exécutez benchmark_cold_start() d'abord.")
        
        # Tester différentes longueurs de prompt
        contexts = {
            'court': "Bonjour",  # ~1 token
            'moyen': "Bonjour, comment vas-tu aujourd'hui ? J'aimerais discuter avec toi.",  # ~15 tokens
            'long': "Bonjour ! Je m'appelle Alice et j'aimerais te poser quelques questions sur l'intelligence artificielle. Peux-tu m'expliquer comment tu fonctionnes et quelles sont tes capacités ? J'aimerais aussi savoir si tu peux m'aider avec différentes tâches."  # ~50 tokens
        }
        
        results_by_context = {}
        
        for context_name, prompt in contexts.items():
            print(f"\n⏳ Test contexte '{context_name}' (~{len(prompt.split())} mots)...")
            
            # 3 runs par contexte
            latencies = []
            for i in range(3):
                start = time.time()
                response = self.model_manager.generate(
                    prompt,
                    max_tokens=50,
                    temperature=0.7
                )
                latency = time.time() - start
                latencies.append(latency)
            
            avg_latency = statistics.mean(latencies)
            print(f"   Latence moyenne : {avg_latency:.3f}s")
            
            results_by_context[context_name] = {
                'prompt_words': len(prompt.split()),
                'avg_latency': avg_latency,
                'latencies': latencies
            }
        
        result = {
            'benchmark': 'context_sizes',
            'results': results_by_context
        }
        
        self.results.append(result)
        return result
    
    def benchmark_different_lengths(self) -> Dict:
        """Benchmark 4 : Impact de max_tokens sur la vitesse"""
        print("\n" + "="*80)
        print("BENCHMARK 4 : IMPACT MAX_TOKENS")
        print("="*80)
        
        if not self.model_manager or not self.model_manager.is_loaded:
            raise RuntimeError("Modèle non chargé ! Exécutez benchmark_cold_start() d'abord.")
        
        max_tokens_list = [25, 50, 100, 150]
        results_by_length = {}
        
        prompt = "Raconte-moi une courte histoire"
        
        for max_tokens in max_tokens_list:
            print(f"\n⏳ Test max_tokens={max_tokens}...")
            
            # 3 runs
            latencies = []
            tokens_generated = []
            
            for i in range(3):
                start = time.time()
                response = self.model_manager.generate(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                latency = time.time() - start
                
                tokens = len(response.split())
                
                latencies.append(latency)
                tokens_generated.append(tokens)
            
            avg_latency = statistics.mean(latencies)
            avg_tokens = statistics.mean(tokens_generated)
            avg_tps = avg_tokens / avg_latency if avg_latency > 0 else 0
            
            print(f"   Latence moyenne : {avg_latency:.3f}s")
            print(f"   Tokens générés : {avg_tokens:.1f}")
            print(f"   Vitesse : {avg_tps:.2f} tokens/sec")
            
            results_by_length[max_tokens] = {
                'avg_latency': avg_latency,
                'avg_tokens': avg_tokens,
                'avg_tps': avg_tps,
                'latencies': latencies,
                'tokens': tokens_generated
            }
        
        result = {
            'benchmark': 'different_lengths',
            'results': results_by_length
        }
        
        self.results.append(result)
        return result
    
    def save_results(self, filename: str = "llm_benchmark_results.txt"):
        """Sauvegarde les résultats dans un fichier"""
        output_path = Path(__file__).parent.parent / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("LLM BENCHMARK RESULTS - Desktop-Mate\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Date : {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Modèle : {self.ai_config.model_path}\n")
            f.write(f"Profil GPU : {self.ai_config.gpu_profile}\n\n")
            
            # Benchmark 1 : Cold Start
            cold_start = next((r for r in self.results if r['benchmark'] == 'cold_start'), None)
            if cold_start:
                f.write("-" * 80 + "\n")
                f.write("BENCHMARK 1 : COLD START\n")
                f.write("-" * 80 + "\n")
                f.write(f"Temps chargement modèle : {cold_start['load_time']:.2f}s\n")
                f.write(f"Temps première génération : {cold_start['first_gen_time']:.2f}s\n")
                f.write(f"Tokens générés : {cold_start['tokens']}\n")
                f.write(f"Vitesse : {cold_start['tokens_per_sec']:.2f} tokens/sec\n\n")
            
            # Benchmark 2 : Warm Cache
            warm_cache = next((r for r in self.results if r['benchmark'] == 'warm_cache'), None)
            if warm_cache:
                f.write("-" * 80 + "\n")
                f.write("BENCHMARK 2 : WARM CACHE\n")
                f.write("-" * 80 + "\n")
                f.write(f"Nombre de runs : {warm_cache['num_runs']}\n")
                f.write(f"Latence moyenne : {warm_cache['avg_latency']:.3f}s\n")
                f.write(f"Latence médiane : {warm_cache['median_latency']:.3f}s\n")
                f.write(f"Latence min/max : {warm_cache['min_latency']:.3f}s / {warm_cache['max_latency']:.3f}s\n")
                f.write(f"Écart-type : {warm_cache['stdev_latency']:.3f}s\n")
                f.write(f"Vitesse moyenne : {warm_cache['avg_tokens_per_sec']:.2f} tokens/sec\n")
                f.write(f"Vitesse médiane : {warm_cache['median_tokens_per_sec']:.2f} tokens/sec\n\n")
            
            # Benchmark 3 : Context Sizes
            context = next((r for r in self.results if r['benchmark'] == 'context_sizes'), None)
            if context:
                f.write("-" * 80 + "\n")
                f.write("BENCHMARK 3 : IMPACT TAILLE CONTEXTE\n")
                f.write("-" * 80 + "\n")
                for ctx_name, ctx_data in context['results'].items():
                    f.write(f"\nContexte '{ctx_name}' (~{ctx_data['prompt_words']} mots)\n")
                    f.write(f"  Latence moyenne : {ctx_data['avg_latency']:.3f}s\n")
                f.write("\n")
            
            # Benchmark 4 : Different Lengths
            lengths = next((r for r in self.results if r['benchmark'] == 'different_lengths'), None)
            if lengths:
                f.write("-" * 80 + "\n")
                f.write("BENCHMARK 4 : IMPACT MAX_TOKENS\n")
                f.write("-" * 80 + "\n")
                for max_tok, data in lengths['results'].items():
                    f.write(f"\nmax_tokens={max_tok}\n")
                    f.write(f"  Latence moyenne : {data['avg_latency']:.3f}s\n")
                    f.write(f"  Tokens générés : {data['avg_tokens']:.1f}\n")
                    f.write(f"  Vitesse : {data['avg_tps']:.2f} tokens/sec\n")
                f.write("\n")
            
            # Comparaison Cold vs Warm
            if cold_start and warm_cache:
                f.write("-" * 80 + "\n")
                f.write("COMPARAISON COLD START vs WARM CACHE\n")
                f.write("-" * 80 + "\n")
                improvement = ((cold_start['first_gen_time'] - warm_cache['avg_latency']) 
                             / cold_start['first_gen_time'] * 100)
                f.write(f"Cold start : {cold_start['first_gen_time']:.3f}s\n")
                f.write(f"Warm cache : {warm_cache['avg_latency']:.3f}s\n")
                f.write(f"Amélioration : {improvement:.1f}%\n\n")
        
        print(f"\n✅ Résultats sauvegardés : {output_path}")


def main():
    """Menu principal"""
    print("\n" + "="*80)
    print("LLM BENCHMARK - Desktop-Mate")
    print("="*80)
    print("\nChoisissez un benchmark :\n")
    print("1. Cold start (chargement + première génération)")
    print("2. Warm cache (10 générations)")
    print("3. Impact taille contexte")
    print("4. Impact max_tokens")
    print("5. Tous les benchmarks (séquence complète)")
    print("0. Quitter")
    
    # Vérifier si argument CLI fourni
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        choice = input("\nVotre choix : ").strip()
    
    benchmark = LLMBenchmark()
    
    if choice == "1":
        benchmark.benchmark_cold_start()
        benchmark.save_results()
    elif choice == "2":
        benchmark.benchmark_cold_start()
        benchmark.benchmark_warm_cache(num_runs=10)
        benchmark.save_results()
    elif choice == "3":
        benchmark.benchmark_cold_start()
        benchmark.benchmark_context_sizes()
        benchmark.save_results()
    elif choice == "4":
        benchmark.benchmark_cold_start()
        benchmark.benchmark_different_lengths()
        benchmark.save_results()
    elif choice == "5":
        print("\n🚀 Exécution de tous les benchmarks...\n")
        benchmark.benchmark_cold_start()
        time.sleep(1)
        benchmark.benchmark_warm_cache(num_runs=10)
        time.sleep(1)
        benchmark.benchmark_context_sizes()
        time.sleep(1)
        benchmark.benchmark_different_lengths()
        benchmark.save_results()
        print("\n✅ Tous les benchmarks terminés !")
    elif choice == "0":
        print("Au revoir !")
    else:
        print("❌ Choix invalide")


if __name__ == "__main__":
    main()
