#!/usr/bin/env python3
"""
Memory Profiling Script for Desktop-Mate

Mesure l'utilisation RAM/VRAM à différents points du cycle de vie de l'application.

Usage:
    python scripts/profile_memory.py
    
Outputs:
    - Console : Métriques en temps réel
    - Fichier : memory_profile_results.txt
"""

import psutil
import os
import sys
import time
from pathlib import Path

# Ajouter src/ au path pour imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    import pynvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False
    print("⚠️  pynvml non disponible - Pas de monitoring VRAM GPU")


class MemoryProfiler:
    """Profileur mémoire RAM et VRAM"""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.gpu_available = False
        self.gpu_handle = None
        
        if NVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                self.gpu_available = True
                print("✅ GPU monitoring activé")
            except Exception as e:
                print(f"⚠️  GPU monitoring indisponible : {e}")
        
        self.measurements = []
    
    def get_ram_usage(self):
        """Retourne l'utilisation RAM en MB"""
        mem_info = self.process.memory_info()
        return mem_info.rss / 1024 / 1024  # Convertir bytes → MB
    
    def get_vram_usage(self):
        """Retourne l'utilisation VRAM en MB (si GPU disponible)"""
        if not self.gpu_available:
            return None
        
        try:
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(self.gpu_handle)
            return mem_info.used / 1024 / 1024  # Convertir bytes → MB
        except Exception as e:
            print(f"⚠️  Erreur lecture VRAM : {e}")
            return None
    
    def get_system_ram(self):
        """Retourne RAM système totale/utilisée en MB"""
        mem = psutil.virtual_memory()
        return {
            'total': mem.total / 1024 / 1024,
            'available': mem.available / 1024 / 1024,
            'used': mem.used / 1024 / 1024,
            'percent': mem.percent
        }
    
    def measure(self, label: str):
        """Prend une mesure et l'enregistre"""
        ram_mb = self.get_ram_usage()
        vram_mb = self.get_vram_usage()
        sys_ram = self.get_system_ram()
        
        measurement = {
            'label': label,
            'timestamp': time.time(),
            'ram_process_mb': ram_mb,
            'vram_gpu_mb': vram_mb,
            'system_ram': sys_ram
        }
        
        self.measurements.append(measurement)
        
        # Afficher en temps réel
        print(f"\n📊 {label}")
        print(f"  RAM Process : {ram_mb:.2f} MB")
        if vram_mb is not None:
            print(f"  VRAM GPU    : {vram_mb:.2f} MB")
        print(f"  RAM Système : {sys_ram['used']:.2f}/{sys_ram['total']:.2f} MB ({sys_ram['percent']:.1f}%)")
        
        return measurement
    
    def save_results(self, filename="memory_profile_results.txt"):
        """Sauvegarde les résultats dans un fichier"""
        output_path = Path(__file__).parent.parent / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("MEMORY PROFILING RESULTS - Desktop-Mate\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Date : {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Nombre de mesures : {len(self.measurements)}\n\n")
            
            # Tableau des mesures
            f.write("-" * 80 + "\n")
            f.write(f"{'Label':<30} {'RAM Process (MB)':<20} {'VRAM GPU (MB)':<20}\n")
            f.write("-" * 80 + "\n")
            
            for m in self.measurements:
                vram_str = f"{m['vram_gpu_mb']:.2f}" if m['vram_gpu_mb'] is not None else "N/A"
                f.write(f"{m['label']:<30} {m['ram_process_mb']:<20.2f} {vram_str:<20}\n")
            
            f.write("-" * 80 + "\n\n")
            
            # Analyse différences
            if len(self.measurements) >= 2:
                f.write("ANALYSE DES DIFFÉRENCES\n")
                f.write("-" * 80 + "\n")
                
                baseline = self.measurements[0]
                for i, m in enumerate(self.measurements[1:], 1):
                    ram_diff = m['ram_process_mb'] - baseline['ram_process_mb']
                    f.write(f"\n{m['label']} vs {baseline['label']}\n")
                    f.write(f"  RAM : +{ram_diff:.2f} MB\n")
                    
                    if m['vram_gpu_mb'] is not None and baseline['vram_gpu_mb'] is not None:
                        vram_diff = m['vram_gpu_mb'] - baseline['vram_gpu_mb']
                        f.write(f"  VRAM : +{vram_diff:.2f} MB\n")
        
        print(f"\n✅ Résultats sauvegardés : {output_path}")
    
    def cleanup(self):
        """Nettoie les ressources"""
        if self.gpu_available:
            try:
                pynvml.nvmlShutdown()
            except:
                pass


def profile_basic_startup():
    """Profile 1 : Démarrage basique (imports seulement)"""
    print("\n" + "="*80)
    print("PROFILING 1 : DÉMARRAGE BASIQUE")
    print("="*80)
    
    profiler = MemoryProfiler()
    
    # Mesure 1 : Baseline
    profiler.measure("1. Baseline (script vide)")
    
    # Mesure 2 : Imports Python
    print("\n⏳ Import des modules Python...")
    from utils.config import Config
    from ipc.unity_bridge import UnityBridge
    profiler.measure("2. Après imports Python")
    
    # Mesure 3 : Imports Qt
    print("\n⏳ Import PySide6...")
    from PySide6.QtWidgets import QApplication
    profiler.measure("3. Après imports Qt")
    
    profiler.save_results("memory_profile_basic.txt")
    profiler.cleanup()


def profile_llm_loading():
    """Profile 2 : Chargement du modèle LLM"""
    print("\n" + "="*80)
    print("PROFILING 2 : CHARGEMENT LLM")
    print("="*80)
    
    profiler = MemoryProfiler()
    
    # Mesure 1 : Baseline
    profiler.measure("1. Baseline (avant LLM)")
    
    # Mesure 2 : Import AI
    print("\n⏳ Import modules IA...")
    from ai.config import AIConfig
    from ai.model_manager import ModelManager
    profiler.measure("2. Après imports IA")
    
    # Mesure 3 : Chargement modèle
    print("\n⏳ Chargement du modèle LLM (Zephyr-7B)...")
    print("⚠️  Cela peut prendre 10-30 secondes...")
    
    try:
        ai_config = AIConfig()
        model_manager = ModelManager(ai_config)
        
        # Charger le modèle d'abord !
        print("⏳ Chargement du modèle...")
        model_manager.load_model()
        profiler.measure("3. Après chargement LLM")
        
        # Mesure 4 : Première génération (warming)
        print("\n⏳ Première génération (warming cache)...")
        test_prompt = "Bonjour"
        response = model_manager.generate(test_prompt, max_tokens=50)
        profiler.measure("4. Après première génération")
        
        # Mesure 5 : Deuxième génération
        print("\n⏳ Deuxième génération...")
        response = model_manager.generate(test_prompt, max_tokens=50)
        profiler.measure("5. Après deuxième génération")
        
    except Exception as e:
        print(f"❌ Erreur chargement LLM : {e}")
        import traceback
        traceback.print_exc()
    
    profiler.save_results("memory_profile_llm.txt")
    profiler.cleanup()


def profile_conversation():
    """Profile 3 : Conversation longue (10-50-100 messages)"""
    print("\n" + "="*80)
    print("PROFILING 3 : CONVERSATION LONGUE")
    print("="*80)
    
    profiler = MemoryProfiler()
    
    # Baseline
    profiler.measure("1. Baseline")
    
    print("\n⏳ Initialisation ChatEngine...")
    try:
        from ai.config import AIConfig
        from ai.chat_engine import ChatEngine
        
        ai_config = AIConfig()
        chat_engine = ChatEngine(ai_config)
        profiler.measure("2. Après init ChatEngine")
        
        # IMPORTANT : Charger le modèle avant de discuter !
        print("\n⏳ Chargement du modèle LLM...")
        chat_engine.model_manager.load_model()
        profiler.measure("2b. Après chargement modèle")
        
        # Séquence de messages
        test_messages = [
            "Bonjour !",
            "Comment vas-tu ?",
            "Parle-moi de toi",
            "Quelle est ta fonction ?",
            "Merci pour tes réponses"
        ]
        
        # 10 messages
        print("\n⏳ Envoi de 10 messages...")
        for i in range(10):
            msg = test_messages[i % len(test_messages)]
            # chat() retourne un ChatResponse
            chat_response = chat_engine.chat(msg)
            if (i + 1) % 5 == 0:
                print(f"  {i+1}/10 messages traités...")
        
        profiler.measure("3. Après 10 messages")
        
        # 50 messages (40 de plus)
        print("\n⏳ Envoi de 40 messages supplémentaires (total 50)...")
        for i in range(40):
            msg = test_messages[i % len(test_messages)]
            chat_response = chat_engine.chat(msg)
            if (i + 1) % 10 == 0:
                print(f"  {10 + i+1}/50 messages traités...")
        
        profiler.measure("4. Après 50 messages")
        
        # 100 messages (50 de plus)
        print("\n⏳ Envoi de 50 messages supplémentaires (total 100)...")
        for i in range(50):
            msg = test_messages[i % len(test_messages)]
            chat_response = chat_engine.chat(msg)
            if (i + 1) % 10 == 0:
                print(f"  {50 + i+1}/100 messages traités...")
        
        profiler.measure("5. Après 100 messages")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
    
    profiler.save_results("memory_profile_conversation.txt")
    profiler.cleanup()


def main():
    """Menu principal"""
    print("\n" + "="*80)
    print("MEMORY PROFILER - Desktop-Mate")
    print("="*80)
    
    # Vérifier si argument CLI fourni
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print("\nChoisissez un profil :\n")
        print("1. Démarrage basique (imports seulement)")
        print("2. Chargement LLM (avec warming)")
        print("3. Conversation longue (10-50-100 messages)")
        print("4. Tous les profils (séquence complète)")
        print("0. Quitter")
        
        choice = input("\nVotre choix : ").strip()
    
    if choice == "1":
        profile_basic_startup()
    elif choice == "2":
        profile_llm_loading()
    elif choice == "3":
        profile_conversation()
    elif choice == "4":
        print("\n🚀 Exécution de tous les profils...\n")
        profile_basic_startup()
        time.sleep(2)
        profile_llm_loading()
        time.sleep(2)
        profile_conversation()
        print("\n✅ Tous les profils terminés !")
    elif choice == "0":
        print("Au revoir !")
    else:
        print("❌ Choix invalide")


if __name__ == "__main__":
    main()
