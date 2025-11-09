"""
Benchmark IPC - Mesure des performances de communication Python ↔ Unity

Ce script mesure :
1. Latence round-trip (Python → Unity → Python)
2. Latence moyenne sur plusieurs messages
3. Impact de la taille des messages
4. Throughput maximum (messages/seconde)

Usage:
    python scripts/benchmark_ipc.py
    
Prérequis:
    - Unity doit être lancé avec la scène Desktop-Mate
    - Le serveur PythonBridge doit être actif (port 5555)
"""

import sys
import os
import time
import statistics
import json

# Ajouter le dossier racine au path pour importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ipc.unity_bridge import UnityBridge


class IPCBenchmark:
    """Classe pour benchmarker les performances IPC."""
    
    def __init__(self):
        """Initialise le benchmark."""
        self.bridge = UnityBridge()
        self.results = {}
        
    def setup(self) -> bool:
        """Configure la connexion Unity.
        
        Returns:
            True si connexion réussie, False sinon
        """
        print("=" * 70)
        print("🔌 BENCHMARK IPC - Communication Python ↔ Unity")
        print("=" * 70)
        print()
        
        print("📡 Connexion à Unity...")
        if not self.bridge.connect():
            print("❌ Échec de connexion à Unity !")
            print()
            print("⚠️  Vérifiez que :")
            print("   1. Unity est lancé")
            print("   2. La scène Desktop-Mate est ouverte")
            print("   3. Le GameObject avec PythonBridge est actif")
            print("   4. Le port 5555 est disponible")
            return False
        
        print("✅ Connecté à Unity !")
        print()
        
        # Petit délai pour stabiliser la connexion
        time.sleep(0.5)
        
        return True
    
    def teardown(self):
        """Nettoie les ressources."""
        print()
        print("🔌 Déconnexion de Unity...")
        self.bridge.disconnect()
        print("✅ Déconnecté")
    
    def benchmark_simple_commands(self, n_messages: int = 100) -> dict:
        """Benchmark 1 : Mesure la latence de commandes simples.
        
        Args:
            n_messages: Nombre de messages à envoyer
            
        Returns:
            Dictionnaire avec les statistiques
        """
        print(f"📊 Benchmark 1 : Latence commandes simples ({n_messages} messages)")
        print("-" * 70)
        
        latencies = []
        
        # Warmup (ignorer les premiers messages)
        print("🔥 Warmup (10 messages)...")
        for _ in range(10):
            self.bridge.send_command("ping", {})
            time.sleep(0.01)
        
        print(f"⏱️  Envoi de {n_messages} commandes 'ping'...")
        
        for i in range(n_messages):
            start = time.perf_counter()
            
            # Envoyer une commande simple
            success = self.bridge.send_command("ping", {"id": i})
            
            end = time.perf_counter()
            latency_ms = (end - start) * 1000
            
            if success:
                latencies.append(latency_ms)
            
            # Petit délai pour ne pas saturer
            time.sleep(0.001)
            
            # Progress bar
            if (i + 1) % 10 == 0:
                print(f"   Envoyé {i + 1}/{n_messages} messages...", end='\r')
        
        print(f"   Envoyé {n_messages}/{n_messages} messages... ✅")
        
        # Calculer les statistiques
        stats = {
            "count": len(latencies),
            "mean_ms": statistics.mean(latencies),
            "median_ms": statistics.median(latencies),
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "stdev_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0
        }
        
        # Affichage
        print()
        print("📈 Résultats :")
        print(f"   Messages envoyés : {stats['count']}")
        print(f"   Latence moyenne  : {stats['mean_ms']:.3f} ms")
        print(f"   Latence médiane  : {stats['median_ms']:.3f} ms")
        print(f"   Latence min      : {stats['min_ms']:.3f} ms")
        print(f"   Latence max      : {stats['max_ms']:.3f} ms")
        print(f"   Écart-type       : {stats['stdev_ms']:.3f} ms")
        print()
        
        self.results["simple_commands"] = stats
        return stats
    
    def benchmark_message_sizes(self) -> dict:
        """Benchmark 2 : Impact de la taille des messages.
        
        Returns:
            Dictionnaire avec les statistiques par taille
        """
        print("📊 Benchmark 2 : Impact de la taille des messages")
        print("-" * 70)
        
        # Différentes tailles de payload
        sizes = {
            "tiny": 10,      # 10 caractères
            "small": 100,    # 100 caractères
            "medium": 1000,  # 1 KB
            "large": 10000   # 10 KB
        }
        
        results = {}
        
        for size_name, size_bytes in sizes.items():
            print(f"⏱️  Test avec payload '{size_name}' ({size_bytes} bytes)...")
            
            # Générer un payload de la taille demandée
            payload = "x" * size_bytes
            
            latencies = []
            
            for i in range(20):  # 20 messages par taille
                start = time.perf_counter()
                
                self.bridge.send_command("test", {"payload": payload})
                
                end = time.perf_counter()
                latency_ms = (end - start) * 1000
                latencies.append(latency_ms)
                
                time.sleep(0.01)
            
            # Statistiques
            stats = {
                "size_bytes": size_bytes,
                "mean_ms": statistics.mean(latencies),
                "median_ms": statistics.median(latencies)
            }
            
            print(f"   Latence moyenne : {stats['mean_ms']:.3f} ms")
            
            results[size_name] = stats
        
        print()
        print("📈 Résumé par taille :")
        for size_name, stats in results.items():
            print(f"   {size_name:8s} ({stats['size_bytes']:5d} bytes) : {stats['mean_ms']:.3f} ms")
        print()
        
        self.results["message_sizes"] = results
        return results
    
    def benchmark_throughput(self, duration_seconds: int = 5) -> dict:
        """Benchmark 3 : Throughput maximum (messages/seconde).
        
        Args:
            duration_seconds: Durée du test en secondes
            
        Returns:
            Dictionnaire avec les statistiques de throughput
        """
        print(f"📊 Benchmark 3 : Throughput maximum ({duration_seconds}s)")
        print("-" * 70)
        
        print(f"⏱️  Envoi de messages pendant {duration_seconds} secondes...")
        
        start_time = time.perf_counter()
        end_time = start_time + duration_seconds
        
        count = 0
        
        while time.perf_counter() < end_time:
            self.bridge.send_command("burst", {"id": count})
            count += 1
            
            # Progress
            elapsed = time.perf_counter() - start_time
            if int(elapsed) != int(elapsed - 0.1):  # Afficher chaque seconde
                print(f"   {elapsed:.1f}s - {count} messages envoyés...", end='\r')
        
        elapsed_total = time.perf_counter() - start_time
        
        # Calculer le throughput
        throughput = count / elapsed_total
        
        print(f"   {elapsed_total:.1f}s - {count} messages envoyés... ✅")
        print()
        print("📈 Résultats :")
        print(f"   Messages envoyés    : {count}")
        print(f"   Durée totale        : {elapsed_total:.2f} s")
        print(f"   Throughput moyen    : {throughput:.2f} messages/seconde")
        print(f"   Intervalle moyen    : {(1000 / throughput):.3f} ms/message")
        print()
        
        stats = {
            "total_messages": count,
            "duration_s": elapsed_total,
            "throughput_msg_per_sec": throughput,
            "interval_ms": 1000 / throughput
        }
        
        self.results["throughput"] = stats
        return stats
    
    def benchmark_expression_commands(self, n_expressions: int = 50) -> dict:
        """Benchmark 4 : Commandes d'expression réalistes.
        
        Args:
            n_expressions: Nombre d'expressions à envoyer
            
        Returns:
            Dictionnaire avec les statistiques
        """
        print(f"📊 Benchmark 4 : Commandes d'expression réalistes ({n_expressions} expressions)")
        print("-" * 70)
        
        # Liste d'expressions VRM typiques
        expressions = ["neutral", "joy", "angry", "sorrow", "fun", "surprised"]
        
        latencies = []
        
        print(f"⏱️  Envoi de {n_expressions} commandes set_expression...")
        
        for i in range(n_expressions):
            # Choisir une expression
            expr = expressions[i % len(expressions)]
            value = 0.5 + (i % 5) * 0.1  # Valeurs entre 0.5 et 0.9
            
            start = time.perf_counter()
            
            # Utiliser la vraie méthode set_expression
            success = self.bridge.set_expression(expr, value)
            
            end = time.perf_counter()
            latency_ms = (end - start) * 1000
            
            if success:
                latencies.append(latency_ms)
            
            time.sleep(0.05)  # 50ms entre expressions (réaliste)
            
            # Progress
            if (i + 1) % 10 == 0:
                print(f"   Envoyé {i + 1}/{n_expressions} expressions...", end='\r')
        
        print(f"   Envoyé {n_expressions}/{n_expressions} expressions... ✅")
        
        # Statistiques
        stats = {
            "count": len(latencies),
            "mean_ms": statistics.mean(latencies),
            "median_ms": statistics.median(latencies),
            "stdev_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0
        }
        
        print()
        print("📈 Résultats :")
        print(f"   Expressions envoyées : {stats['count']}")
        print(f"   Latence moyenne      : {stats['mean_ms']:.3f} ms")
        print(f"   Latence médiane      : {stats['median_ms']:.3f} ms")
        print(f"   Écart-type           : {stats['stdev_ms']:.3f} ms")
        print()
        
        self.results["expression_commands"] = stats
        return stats
    
    def save_results(self, filename: str = "ipc_benchmark_results.txt"):
        """Sauvegarde les résultats dans un fichier.
        
        Args:
            filename: Nom du fichier de sortie
        """
        filepath = os.path.join("scripts", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("🔌 RÉSULTATS BENCHMARK IPC - Python ↔ Unity\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"📅 Date : {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"🖥️  Système : Windows\n")
            f.write(f"🐍 Python : {sys.version.split()[0]}\n\n")
            
            # Benchmark 1
            if "simple_commands" in self.results:
                stats = self.results["simple_commands"]
                f.write("=" * 70 + "\n")
                f.write("Benchmark 1 : Commandes simples\n")
                f.write("=" * 70 + "\n")
                f.write(f"Messages envoyés : {stats['count']}\n")
                f.write(f"Latence moyenne  : {stats['mean_ms']:.3f} ms\n")
                f.write(f"Latence médiane  : {stats['median_ms']:.3f} ms\n")
                f.write(f"Latence min      : {stats['min_ms']:.3f} ms\n")
                f.write(f"Latence max      : {stats['max_ms']:.3f} ms\n")
                f.write(f"Écart-type       : {stats['stdev_ms']:.3f} ms\n\n")
            
            # Benchmark 2
            if "message_sizes" in self.results:
                f.write("=" * 70 + "\n")
                f.write("Benchmark 2 : Impact de la taille des messages\n")
                f.write("=" * 70 + "\n")
                for size_name, stats in self.results["message_sizes"].items():
                    f.write(f"{size_name:8s} ({stats['size_bytes']:5d} bytes) : ")
                    f.write(f"{stats['mean_ms']:.3f} ms\n")
                f.write("\n")
            
            # Benchmark 3
            if "throughput" in self.results:
                stats = self.results["throughput"]
                f.write("=" * 70 + "\n")
                f.write("Benchmark 3 : Throughput maximum\n")
                f.write("=" * 70 + "\n")
                f.write(f"Messages envoyés    : {stats['total_messages']}\n")
                f.write(f"Durée totale        : {stats['duration_s']:.2f} s\n")
                f.write(f"Throughput moyen    : {stats['throughput_msg_per_sec']:.2f} msg/s\n")
                f.write(f"Intervalle moyen    : {stats['interval_ms']:.3f} ms/msg\n\n")
            
            # Benchmark 4
            if "expression_commands" in self.results:
                stats = self.results["expression_commands"]
                f.write("=" * 70 + "\n")
                f.write("Benchmark 4 : Commandes d'expression réalistes\n")
                f.write("=" * 70 + "\n")
                f.write(f"Expressions envoyées : {stats['count']}\n")
                f.write(f"Latence moyenne      : {stats['mean_ms']:.3f} ms\n")
                f.write(f"Latence médiane      : {stats['median_ms']:.3f} ms\n")
                f.write(f"Écart-type           : {stats['stdev_ms']:.3f} ms\n\n")
            
            f.write("=" * 70 + "\n")
            f.write("FIN DU RAPPORT\n")
            f.write("=" * 70 + "\n")
        
        print(f"💾 Résultats sauvegardés dans : {filepath}")
    
    def run_all_benchmarks(self):
        """Exécute tous les benchmarks."""
        if not self.setup():
            return
        
        try:
            # Benchmark 1 : Commandes simples
            self.benchmark_simple_commands(n_messages=100)
            time.sleep(1)
            
            # Benchmark 2 : Taille des messages
            self.benchmark_message_sizes()
            time.sleep(1)
            
            # Benchmark 3 : Throughput
            self.benchmark_throughput(duration_seconds=5)
            time.sleep(1)
            
            # Benchmark 4 : Expressions réalistes
            self.benchmark_expression_commands(n_expressions=50)
            
            # Sauvegarder les résultats
            print()
            self.save_results()
            
            # Résumé final
            print()
            print("=" * 70)
            print("🏆 RÉSUMÉ DES BENCHMARKS")
            print("=" * 70)
            
            if "simple_commands" in self.results:
                mean = self.results["simple_commands"]["mean_ms"]
                print(f"📊 Latence moyenne (commandes simples) : {mean:.3f} ms")
            
            if "throughput" in self.results:
                throughput = self.results["throughput"]["throughput_msg_per_sec"]
                print(f"🚀 Throughput maximum               : {throughput:.2f} msg/s")
            
            if "expression_commands" in self.results:
                mean = self.results["expression_commands"]["mean_ms"]
                print(f"😊 Latence moyenne (expressions)    : {mean:.3f} ms")
            
            print("=" * 70)
            
        finally:
            self.teardown()


def main():
    """Point d'entrée principal."""
    benchmark = IPCBenchmark()
    benchmark.run_all_benchmarks()


if __name__ == "__main__":
    main()
