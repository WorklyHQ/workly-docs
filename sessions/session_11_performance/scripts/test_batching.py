"""
Test Batching - Compare les performances avec et sans batching

Ce script mesure l'amélioration apportée par le message batching en comparant :
- Envoi de N commandes séparées (baseline)
- Envoi de N commandes groupées en batch

Usage:
    python scripts/test_batching.py
    
Prérequis:
    - Unity lancé avec PythonBridge actif
"""

import sys
import os
import time
import statistics

# Ajouter le dossier racine au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ipc.unity_bridge import UnityBridge


class BatchingTest:
    """Classe pour tester l'amélioration du batching."""
    
    def __init__(self):
        """Initialise le test."""
        self.bridge = UnityBridge()
        
    def setup(self) -> bool:
        """Configure la connexion Unity."""
        print("=" * 70)
        print("🔬 TEST BATCHING - Comparaison avant/après")
        print("=" * 70)
        print()
        
        print("📡 Connexion à Unity...")
        if not self.bridge.connect():
            print("❌ Échec de connexion à Unity !")
            return False
        
        print("✅ Connecté à Unity !")
        print()
        time.sleep(0.5)
        return True
    
    def teardown(self):
        """Nettoie les ressources."""
        print()
        print("🔌 Déconnexion...")
        self.bridge.disconnect()
    
    def test_without_batching(self, n_commands: int = 100) -> dict:
        """Test SANS batching : envoi de commandes séparées.
        
        Args:
            n_commands: Nombre de commandes à envoyer
            
        Returns:
            Statistiques de performance
        """
        print(f"📊 Test 1 : SANS batching ({n_commands} commandes séparées)")
        print("-" * 70)
        
        # Warmup
        print("🔥 Warmup...")
        for _ in range(10):
            self.bridge.send_command("test", {"id": 0})
            time.sleep(0.001)
        
        print(f"⏱️  Envoi de {n_commands} commandes individuelles...")
        
        latencies = []
        
        start_total = time.perf_counter()
        
        for i in range(n_commands):
            start = time.perf_counter()
            
            self.bridge.send_command("test", {"id": i})
            
            end = time.perf_counter()
            latency_ms = (end - start) * 1000
            latencies.append(latency_ms)
            
            # Petit délai pour ne pas saturer
            time.sleep(0.001)
        
        end_total = time.perf_counter()
        total_time_ms = (end_total - start_total) * 1000
        
        # Statistiques
        stats = {
            "count": len(latencies),
            "mean_ms": statistics.mean(latencies),
            "median_ms": statistics.median(latencies),
            "total_time_ms": total_time_ms,
            "throughput_msg_per_sec": n_commands / (total_time_ms / 1000)
        }
        
        print(f"   ✅ Terminé en {total_time_ms:.2f} ms")
        print()
        print("📈 Résultats SANS batching :")
        print(f"   Latence moyenne      : {stats['mean_ms']:.3f} ms/commande")
        print(f"   Latence médiane      : {stats['median_ms']:.3f} ms/commande")
        print(f"   Temps total          : {stats['total_time_ms']:.2f} ms")
        print(f"   Throughput           : {stats['throughput_msg_per_sec']:.2f} msg/s")
        print()
        
        return stats
    
    def test_with_batching(self, n_commands: int = 100, batch_size: int = 10) -> dict:
        """Test AVEC batching : envoi de commandes groupées.
        
        Args:
            n_commands: Nombre total de commandes
            batch_size: Taille de chaque batch
            
        Returns:
            Statistiques de performance
        """
        print(f"📊 Test 2 : AVEC batching ({n_commands} commandes, batches de {batch_size})")
        print("-" * 70)
        
        # Warmup
        print("🔥 Warmup...")
        test_batch = [{"command": "test", "data": {"id": i}} for i in range(5)]
        self.bridge.send_batch(test_batch)
        time.sleep(0.1)
        
        print(f"⏱️  Envoi de {n_commands // batch_size} batches...")
        
        batch_latencies = []
        
        start_total = time.perf_counter()
        
        for batch_num in range(n_commands // batch_size):
            # Créer un batch
            batch = []
            for i in range(batch_size):
                cmd_id = batch_num * batch_size + i
                batch.append({
                    "command": "test",
                    "data": {"id": cmd_id}
                })
            
            # Envoyer le batch
            start = time.perf_counter()
            
            self.bridge.send_batch(batch)
            
            end = time.perf_counter()
            latency_ms = (end - start) * 1000
            batch_latencies.append(latency_ms)
            
            time.sleep(0.001)
        
        end_total = time.perf_counter()
        total_time_ms = (end_total - start_total) * 1000
        
        # Statistiques
        n_batches = len(batch_latencies)
        latency_per_command = statistics.mean(batch_latencies) / batch_size
        
        stats = {
            "count": n_commands,
            "n_batches": n_batches,
            "batch_size": batch_size,
            "mean_batch_ms": statistics.mean(batch_latencies),
            "mean_per_command_ms": latency_per_command,
            "median_batch_ms": statistics.median(batch_latencies),
            "total_time_ms": total_time_ms,
            "throughput_msg_per_sec": n_commands / (total_time_ms / 1000)
        }
        
        print(f"   ✅ Terminé en {total_time_ms:.2f} ms")
        print()
        print("📈 Résultats AVEC batching :")
        print(f"   Batches envoyés      : {stats['n_batches']}")
        print(f"   Latence par batch    : {stats['mean_batch_ms']:.3f} ms")
        print(f"   Latence par commande : {stats['mean_per_command_ms']:.3f} ms")
        print(f"   Temps total          : {stats['total_time_ms']:.2f} ms")
        print(f"   Throughput           : {stats['throughput_msg_per_sec']:.2f} msg/s")
        print()
        
        return stats
    
    def compare_results(self, without: dict, with_batching: dict):
        """Compare les résultats et calcule l'amélioration."""
        print("=" * 70)
        print("🏆 COMPARAISON FINALE")
        print("=" * 70)
        print()
        
        # Comparaison latence par commande
        latency_without = without["mean_ms"]
        latency_with = with_batching["mean_per_command_ms"]
        latency_improvement = ((latency_without - latency_with) / latency_without) * 100
        
        # Comparaison temps total
        time_without = without["total_time_ms"]
        time_with = with_batching["total_time_ms"]
        time_improvement = ((time_without - time_with) / time_without) * 100
        
        # Comparaison throughput
        throughput_without = without["throughput_msg_per_sec"]
        throughput_with = with_batching["throughput_msg_per_sec"]
        throughput_improvement = ((throughput_with - throughput_without) / throughput_without) * 100
        
        print("📊 Latence par commande :")
        print(f"   SANS batching  : {latency_without:.3f} ms")
        print(f"   AVEC batching  : {latency_with:.3f} ms")
        
        if latency_improvement > 0:
            print(f"   ✅ Amélioration : -{latency_improvement:.1f}% (plus rapide) 🚀")
        else:
            print(f"   ⚠️  Régression  : +{abs(latency_improvement):.1f}% (plus lent)")
        print()
        
        print("⏱️  Temps total :")
        print(f"   SANS batching  : {time_without:.2f} ms")
        print(f"   AVEC batching  : {time_with:.2f} ms")
        
        if time_improvement > 0:
            print(f"   ✅ Amélioration : -{time_improvement:.1f}% (plus rapide) 🚀")
        else:
            print(f"   ⚠️  Régression  : +{abs(time_improvement):.1f}% (plus lent)")
        print()
        
        print("🚀 Throughput :")
        print(f"   SANS batching  : {throughput_without:.2f} msg/s")
        print(f"   AVEC batching  : {throughput_with:.2f} msg/s")
        
        if throughput_improvement > 0:
            print(f"   ✅ Amélioration : +{throughput_improvement:.1f}% (plus rapide) 🚀")
        else:
            print(f"   ⚠️  Régression  : {abs(throughput_improvement):.1f}% (plus lent)")
        print()
        
        print("=" * 70)
        
        # Verdict final
        if latency_improvement > 0 and time_improvement > 0:
            print("🎉 VERDICT : Le batching AMÉLIORE les performances ! ✅")
        elif latency_improvement < -5 or time_improvement < -5:
            print("⚠️  VERDICT : Le batching DÉGRADE les performances")
        else:
            print("🤷 VERDICT : Amélioration marginale, non significative")
        
        print("=" * 70)
        
        # Sauvegarder les résultats
        self.save_comparison(without, with_batching, {
            "latency_improvement_percent": latency_improvement,
            "time_improvement_percent": time_improvement,
            "throughput_improvement_percent": throughput_improvement
        })
    
    def save_comparison(self, without: dict, with_batching: dict, improvements: dict):
        """Sauvegarde la comparaison dans un fichier."""
        filepath = os.path.join("scripts", "batching_comparison_results.txt")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("🔬 COMPARAISON BATCHING - Python ↔ Unity\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"📅 Date : {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("SANS batching (baseline) :\n")
            f.write(f"  Latence moyenne      : {without['mean_ms']:.3f} ms/commande\n")
            f.write(f"  Temps total          : {without['total_time_ms']:.2f} ms\n")
            f.write(f"  Throughput           : {without['throughput_msg_per_sec']:.2f} msg/s\n\n")
            
            f.write("AVEC batching (optimisé) :\n")
            f.write(f"  Latence par commande : {with_batching['mean_per_command_ms']:.3f} ms\n")
            f.write(f"  Temps total          : {with_batching['total_time_ms']:.2f} ms\n")
            f.write(f"  Throughput           : {with_batching['throughput_msg_per_sec']:.2f} msg/s\n\n")
            
            f.write("AMÉLIORATION :\n")
            f.write(f"  Latence : {improvements['latency_improvement_percent']:+.1f}%\n")
            f.write(f"  Temps   : {improvements['time_improvement_percent']:+.1f}%\n")
            f.write(f"  Throughput : {improvements['throughput_improvement_percent']:+.1f}%\n\n")
            
            f.write("=" * 70 + "\n")
        
        print(f"\n💾 Comparaison sauvegardée dans : {filepath}")
    
    def run_comparison(self, n_commands: int = 100, batch_size: int = 10):
        """Exécute la comparaison complète."""
        if not self.setup():
            return
        
        try:
            # Test SANS batching
            stats_without = self.test_without_batching(n_commands)
            time.sleep(1)
            
            # Test AVEC batching
            stats_with = self.test_with_batching(n_commands, batch_size)
            time.sleep(1)
            
            # Comparer
            self.compare_results(stats_without, stats_with)
            
        finally:
            self.teardown()


def main():
    """Point d'entrée principal."""
    test = BatchingTest()
    test.run_comparison(n_commands=100, batch_size=10)


if __name__ == "__main__":
    main()
