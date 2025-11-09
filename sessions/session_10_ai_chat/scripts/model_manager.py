"""
Model Manager pour Desktop-Mate (Kira)

Gestion du modèle LLM (Zephyr-7B) avec :
- Chargement modèle avec llama-cpp-python
- Détection GPU NVIDIA avec pynvml
- Application profils GPU adaptatifs
- Génération texte avec contexte
- Gestion erreurs (OOM, modèle introuvable)
"""

import os
from typing import Optional, Dict, List, Any
import logging
from dataclasses import dataclass

# Import llama-cpp-python
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    Llama = None

# Import pynvml (GPU monitoring)
try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False
    pynvml = None

from .config import AIConfig, get_config

logger = logging.getLogger(__name__)


@dataclass
class GPUInfo:
    """Informations sur le GPU NVIDIA"""
    available: bool
    name: Optional[str] = None
    vram_total: Optional[int] = None  # En bytes
    vram_free: Optional[int] = None   # En bytes
    vram_used: Optional[int] = None   # En bytes
    driver_version: Optional[str] = None
    cuda_version: Optional[str] = None


class ModelManager:
    """
    Gestionnaire du modèle LLM avec support GPU
    
    Gère le cycle de vie du modèle :
    - Détection GPU
    - Chargement modèle avec profil GPU
    - Génération texte
    - Déchargement modèle
    """
    
    def __init__(self, config: Optional[AIConfig] = None):
        """
        Initialise le gestionnaire de modèle
        
        Args:
            config: Configuration IA (si None, charge depuis config.json)
        """
        self.config = config or get_config()
        self.model: Optional[Llama] = None
        self.is_loaded = False
        self.gpu_info: Optional[GPUInfo] = None
        
        # Vérifier disponibilité llama-cpp-python
        if not LLAMA_CPP_AVAILABLE:
            logger.error(
                "❌ llama-cpp-python non disponible ! "
                "Installez-le avec : pip install llama-cpp-python"
            )
            raise ImportError("llama-cpp-python est requis pour ModelManager")
        
        logger.info("✅ ModelManager initialisé")
    
    def detect_gpu(self) -> GPUInfo:
        """
        Détecte le GPU NVIDIA et récupère ses informations
        
        Returns:
            GPUInfo avec informations GPU (ou available=False si pas de GPU)
        """
        if not PYNVML_AVAILABLE:
            logger.warning(
                "⚠️ pynvml non disponible. Impossible de détecter le GPU. "
                "Installez-le avec : pip install pynvml"
            )
            return GPUInfo(available=False)
        
        try:
            pynvml.nvmlInit()
            
            # Compter les GPUs
            device_count = pynvml.nvmlDeviceGetCount()
            
            if device_count == 0:
                logger.warning("⚠️ Aucun GPU NVIDIA détecté")
                return GPUInfo(available=False)
            
            # Prendre le premier GPU (index 0)
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            
            # Récupérer infos
            name = pynvml.nvmlDeviceGetName(handle)
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            driver_version = pynvml.nvmlSystemGetDriverVersion()
            
            # CUDA version (peut échouer sur certains systèmes)
            try:
                cuda_version = pynvml.nvmlSystemGetCudaDriverVersion()
                cuda_version_str = f"{cuda_version // 1000}.{(cuda_version % 1000) // 10}"
            except:
                cuda_version_str = "Unknown"
            
            gpu_info = GPUInfo(
                available=True,
                name=name,
                vram_total=memory_info.total,
                vram_free=memory_info.free,
                vram_used=memory_info.used,
                driver_version=driver_version,
                cuda_version=cuda_version_str
            )
            
            logger.info(
                f"🎮 GPU détecté : {name} | "
                f"VRAM: {memory_info.total / (1024**3):.1f} GB "
                f"(Libre: {memory_info.free / (1024**3):.1f} GB)"
            )
            
            pynvml.nvmlShutdown()
            
            self.gpu_info = gpu_info
            return gpu_info
            
        except Exception as e:
            logger.error(f"❌ Erreur détection GPU : {e}")
            return GPUInfo(available=False)
    
    def load_model(self, force_profile: Optional[str] = None) -> bool:
        """
        Charge le modèle LLM avec le profil GPU configuré
        
        Args:
            force_profile: Force un profil spécifique (ignore config)
        
        Returns:
            True si chargement réussi
        
        Raises:
            FileNotFoundError: Si le modèle n'existe pas
            RuntimeError: Si erreur de chargement (OOM, etc.)
        """
        if self.is_loaded:
            logger.warning("⚠️ Modèle déjà chargé. Utilisez unload_model() d'abord.")
            return True
        
        # Vérifier existence du modèle
        model_path = self.config.model_path
        if not os.path.exists(model_path):
            error_msg = f"Modèle introuvable : {model_path}"
            logger.error(f"❌ {error_msg}")
            raise FileNotFoundError(error_msg)
        
        # Détecter GPU
        gpu_info = self.detect_gpu()
        
        # Choisir profil
        if force_profile:
            self.config.switch_profile(force_profile)
        
        profile_name = self.config.gpu_profile
        gpu_params = self.config.get_gpu_params()
        
        logger.info(
            f"🔄 Chargement modèle : {os.path.basename(model_path)} "
            f"(profil: {profile_name})"
        )
        
        try:
            # Charger modèle avec llama-cpp-python
            self.model = Llama(
                model_path=model_path,
                n_gpu_layers=gpu_params["n_gpu_layers"],
                n_ctx=gpu_params["n_ctx"],
                n_batch=gpu_params["n_batch"],
                n_threads=gpu_params["n_threads"],
                use_mlock=gpu_params["use_mlock"],
                verbose=False  # Désactiver logs verbeux
            )
            
            self.is_loaded = True
            
            logger.info(
                f"✅ Modèle chargé avec succès ! "
                f"(profil: {profile_name}, "
                f"GPU layers: {gpu_params['n_gpu_layers']}, "
                f"context: {gpu_params['n_ctx']})"
            )
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            
            # Détecter erreur OOM (Out Of Memory)
            if "out of memory" in error_msg.lower() or "oom" in error_msg.lower():
                logger.error(
                    f"❌ Erreur VRAM insuffisante ! "
                    f"Profil actuel : {profile_name}. "
                    f"Essayez un profil moins gourmand (balanced ou cpu_fallback)."
                )
                
                # Auto-fallback vers CPU si erreur OOM
                if profile_name != "cpu_fallback":
                    logger.warning("⚠️ Tentative de fallback vers cpu_fallback...")
                    return self.load_model(force_profile="cpu_fallback")
            
            logger.error(f"❌ Erreur chargement modèle : {error_msg}")
            raise RuntimeError(f"Échec chargement modèle : {error_msg}")
    
    def unload_model(self):
        """Décharge le modèle de la mémoire"""
        if not self.is_loaded:
            logger.warning("⚠️ Aucun modèle chargé")
            return
        
        self.model = None
        self.is_loaded = False
        
        logger.info("✅ Modèle déchargé")
    
    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop: Optional[List[str]] = None
    ) -> str:
        """
        Génère une réponse texte à partir d'un prompt
        
        Args:
            prompt: Texte d'entrée (peut contenir historique + question)
            temperature: Créativité (0.0-2.0). Si None, utilise config.
            top_p: Nucleus sampling (0.0-1.0). Si None, utilise config.
            max_tokens: Nombre max de tokens générés. Si None, utilise config.
            stop: Liste de séquences d'arrêt (ex: ["\n\n", "User:"])
        
        Returns:
            Texte généré par le modèle
        
        Raises:
            RuntimeError: Si le modèle n'est pas chargé
        """
        if not self.is_loaded or self.model is None:
            raise RuntimeError(
                "Modèle non chargé ! Appelez load_model() d'abord."
            )
        
        # Utiliser paramètres config si non spécifiés
        temperature = temperature if temperature is not None else self.config.temperature
        top_p = top_p if top_p is not None else self.config.top_p
        max_tokens = max_tokens if max_tokens is not None else self.config.max_tokens
        
        logger.debug(
            f"🤖 Génération : "
            f"temp={temperature}, top_p={top_p}, max_tokens={max_tokens}"
        )
        
        try:
            # Générer avec llama-cpp-python
            response = self.model(
                prompt,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                stop=stop or [],
                echo=False  # Ne pas répéter le prompt dans la sortie
            )
            
            # Extraire le texte généré
            generated_text = response["choices"][0]["text"].strip()
            
            logger.debug(f"✅ Génération terminée : {len(generated_text)} caractères")
            
            return generated_text
            
        except Exception as e:
            logger.error(f"❌ Erreur génération : {e}")
            raise RuntimeError(f"Échec génération : {e}")
    
    def get_gpu_status(self) -> Dict[str, Any]:
        """
        Récupère le statut actuel du GPU
        
        Returns:
            Dictionnaire avec infos GPU actuelles
        """
        if not PYNVML_AVAILABLE:
            return {"available": False, "error": "pynvml non installé"}
        
        try:
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            
            memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            
            status = {
                "available": True,
                "vram_used_gb": memory_info.used / (1024**3),
                "vram_free_gb": memory_info.free / (1024**3),
                "vram_total_gb": memory_info.total / (1024**3),
                "vram_percent": (memory_info.used / memory_info.total) * 100,
                "gpu_utilization_percent": utilization.gpu,
                "temperature_celsius": temperature
            }
            
            pynvml.nvmlShutdown()
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération statut GPU : {e}")
            return {"available": False, "error": str(e)}
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Récupère les informations sur le modèle chargé
        
        Returns:
            Dictionnaire avec infos modèle
        """
        return {
            "is_loaded": self.is_loaded,
            "model_path": self.config.model_path,
            "model_name": os.path.basename(self.config.model_path),
            "gpu_profile": self.config.gpu_profile,
            "gpu_params": self.config.get_gpu_params() if self.is_loaded else None,
            "gpu_info": {
                "available": self.gpu_info.available if self.gpu_info else False,
                "name": self.gpu_info.name if self.gpu_info else None,
                "vram_gb": (
                    self.gpu_info.vram_total / (1024**3)
                    if self.gpu_info and self.gpu_info.vram_total
                    else None
                )
            }
        }
    
    def __repr__(self) -> str:
        """Représentation string du ModelManager"""
        status = "chargé" if self.is_loaded else "déchargé"
        model_name = os.path.basename(self.config.model_path)
        return f"ModelManager({model_name}, {status}, profil={self.config.gpu_profile})"


# Instance globale (optionnel, pour usage singleton)
_model_manager_instance: Optional[ModelManager] = None


def get_model_manager(config: Optional[AIConfig] = None) -> ModelManager:
    """
    Récupère l'instance globale de ModelManager (singleton)
    
    Args:
        config: Configuration IA (optionnel)
    
    Returns:
        Instance ModelManager
    """
    global _model_manager_instance
    
    if _model_manager_instance is None:
        _model_manager_instance = ModelManager(config)
    
    return _model_manager_instance


# Pour tests et usage direct
if __name__ == "__main__":
    # Test rapide du ModelManager
    print("🧪 Test du ModelManager...\n")
    
    # Test 1 : Détection GPU
    print("1. Détection GPU...")
    manager = ModelManager()
    gpu_info = manager.detect_gpu()
    
    if gpu_info.available:
        print(f"   ✅ GPU détecté : {gpu_info.name}")
        print(f"   VRAM : {gpu_info.vram_total / (1024**3):.1f} GB")
        print(f"   Driver : {gpu_info.driver_version}")
    else:
        print("   ⚠️ Aucun GPU détecté (mode CPU)")
    
    print()
    
    # Test 2 : Info modèle (sans charger)
    print("2. Informations modèle...")
    info = manager.get_model_info()
    print(f"   Modèle : {info['model_name']}")
    print(f"   Profil : {info['gpu_profile']}")
    print(f"   Chargé : {info['is_loaded']}")
    
    print()
    
    # Test 3 : Chargement modèle (optionnel - peut être long)
    print("3. Test chargement modèle...")
    print("   (Décommentez le code ci-dessous pour tester)")
    print("   ⚠️ Attention : Le chargement prend 20-30 secondes\n")
    
    # Décommenter pour tester le chargement complet :
    # try:
    #     manager.load_model()
    #     print("   ✅ Modèle chargé avec succès !")
    #     
    #     # Test 4 : Génération simple
    #     print("\n4. Test génération...")
    #     response = manager.generate("Dis bonjour en une phrase.")
    #     print(f"   Réponse : {response}")
    #     
    #     # Décharger
    #     manager.unload_model()
    #     print("\n   ✅ Modèle déchargé")
    #     
    # except Exception as e:
    #     print(f"   ❌ Erreur : {e}")
    
    print("✅ Tests manuels terminés !")
