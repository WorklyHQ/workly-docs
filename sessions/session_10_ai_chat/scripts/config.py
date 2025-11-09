"""
Configuration IA pour Desktop-Mate (Kira)

Gestion de la configuration IA :
- Profils GPU adaptatifs (Performance, Balanced, CPU Fallback)
- Paramètres LLM (temperature, top_p, max_tokens)
- System prompt personnalisable
- Chargement depuis config.json avec valeurs par défaut
"""

import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


# ============================================
# PROFILS GPU PRÉDÉFINIS
# ============================================

GPU_PROFILES = {
    "performance": {
        "name": "Performance",
        "description": "Maximum GPU - Très rapide, pour conversations courtes",
        "n_gpu_layers": -1,      # Toutes les couches sur GPU
        "n_ctx": 4096,           # Contexte maximum (4096 tokens)
        "n_batch": 512,          # Batch size élevé
        "n_threads": 6,          # Threads CPU
        "use_mlock": True,       # Lock memory pour éviter swap
        "vram_estimate": "5-5.5 GB",
        "speed_estimate": "25-35 tokens/sec",
        "recommended_for": "Réponses ultra-rapides, autres apps fermées"
    },
    "balanced": {
        "name": "Balanced",
        "description": "Équilibre GPU/CPU - Rapide et stable (DÉFAUT)",
        "n_gpu_layers": 35,      # 35 couches GPU sur 43 (Zephyr-7B)
        "n_ctx": 2048,           # Contexte standard (2048 tokens)
        "n_batch": 256,          # Batch size modéré
        "n_threads": 6,          # Threads CPU
        "use_mlock": True,       # Lock memory
        "vram_estimate": "3-4 GB",
        "speed_estimate": "15-25 tokens/sec",
        "recommended_for": "Usage quotidien, conversations longues"
    },
    "cpu_fallback": {
        "name": "CPU Fallback",
        "description": "CPU uniquement - Lent mais toujours fonctionnel",
        "n_gpu_layers": 0,       # Aucune couche GPU (tout sur CPU)
        "n_ctx": 2048,           # Contexte standard
        "n_batch": 128,          # Batch size réduit
        "n_threads": 8,          # Plus de threads CPU
        "use_mlock": False,      # Pas de memory lock
        "vram_estimate": "0 GB (RAM: 4-6 GB)",
        "speed_estimate": "2-5 tokens/sec",
        "recommended_for": "Fallback si erreur VRAM ou sans GPU NVIDIA"
    }
}


@dataclass
class AIConfig:
    """
    Configuration IA pour Desktop-Mate
    
    Attributes:
        model_path: Chemin vers le modèle LLM (gguf)
        context_limit: Nombre de messages d'historique à inclure
        gpu_profile: Profil GPU ("performance", "balanced", "cpu_fallback")
        temperature: Créativité des réponses (0.0-2.0)
        top_p: Nucleus sampling (0.0-1.0)
        max_tokens: Nombre maximum de tokens générés
        system_prompt: Prompt système définissant la personnalité de Kira
    """
    
    model_path: str = "models/zephyr-7b-beta.Q5_K_M.gguf"
    context_limit: int = 10
    gpu_profile: str = "balanced"
    temperature: float = 0.7
    top_p: float = 0.9
    max_tokens: int = 512
    system_prompt: str = field(default="Tu es Kira, un assistant virtuel amical.")
    
    def __post_init__(self):
        """Validation après initialisation"""
        self.validate()
    
    @classmethod
    def from_json(cls, config_path: str = "data/config.json") -> "AIConfig":
        """
        Charge la configuration depuis un fichier JSON
        
        Args:
            config_path: Chemin vers config.json
        
        Returns:
            Instance AIConfig
        
        Raises:
            FileNotFoundError: Si config.json n'existe pas
            ValueError: Si la config est invalide
        """
        if not os.path.exists(config_path):
            logger.warning(
                f"⚠️ Fichier config non trouvé : {config_path}. "
                f"Utilisation de la configuration par défaut."
            )
            return cls()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Extraire la section "ai"
            ai_config = config_data.get("ai", {})
            
            if not ai_config:
                logger.warning(
                    "⚠️ Section 'ai' manquante dans config.json. "
                    "Utilisation de la configuration par défaut."
                )
                return cls()
            
            # Créer instance avec les valeurs du JSON
            instance = cls(
                model_path=ai_config.get("model_path", cls.model_path),
                context_limit=ai_config.get("context_limit", cls.context_limit),
                gpu_profile=ai_config.get("gpu_profile", cls.gpu_profile),
                temperature=ai_config.get("temperature", cls.temperature),
                top_p=ai_config.get("top_p", cls.top_p),
                max_tokens=ai_config.get("max_tokens", cls.max_tokens),
                system_prompt=ai_config.get("system_prompt", cls.system_prompt)
            )
            
            logger.info(
                f"✅ Configuration IA chargée depuis {config_path} "
                f"(profil: {instance.gpu_profile})"
            )
            
            return instance
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erreur parsing JSON : {e}")
            logger.warning("Utilisation de la configuration par défaut.")
            return cls()
        except Exception as e:
            logger.error(f"❌ Erreur chargement config : {e}")
            logger.warning("Utilisation de la configuration par défaut.")
            return cls()
    
    def get_gpu_params(self) -> Dict[str, Any]:
        """
        Retourne les paramètres GPU du profil actuel
        
        Returns:
            Dictionnaire avec paramètres llama-cpp-python
        
        Raises:
            ValueError: Si le profil GPU n'existe pas
        """
        if self.gpu_profile not in GPU_PROFILES:
            logger.error(
                f"❌ Profil GPU invalide : {self.gpu_profile}. "
                f"Utilisation de 'balanced'."
            )
            self.gpu_profile = "balanced"
        
        profile = GPU_PROFILES[self.gpu_profile]
        
        # Extraire uniquement les paramètres techniques (pas description, etc.)
        gpu_params = {
            "n_gpu_layers": profile["n_gpu_layers"],
            "n_ctx": profile["n_ctx"],
            "n_batch": profile["n_batch"],
            "n_threads": profile["n_threads"],
            "use_mlock": profile["use_mlock"]
        }
        
        logger.debug(
            f"🎮 Paramètres GPU ({self.gpu_profile}): "
            f"layers={gpu_params['n_gpu_layers']}, "
            f"ctx={gpu_params['n_ctx']}, "
            f"batch={gpu_params['n_batch']}"
        )
        
        return gpu_params
    
    def get_profile_info(self) -> Dict[str, Any]:
        """
        Retourne les informations complètes du profil GPU actuel
        
        Returns:
            Dictionnaire avec toutes les infos du profil
        """
        if self.gpu_profile not in GPU_PROFILES:
            self.gpu_profile = "balanced"
        
        return GPU_PROFILES[self.gpu_profile]
    
    def validate(self) -> bool:
        """
        Valide les paramètres de configuration
        
        Returns:
            True si valide
        
        Raises:
            ValueError: Si un paramètre est invalide
        """
        # Validation du chemin modèle
        if not self.model_path:
            raise ValueError("model_path ne peut pas être vide")
        
        # Validation context_limit
        if not isinstance(self.context_limit, int) or self.context_limit < 1:
            raise ValueError(
                f"context_limit doit être un entier >= 1 (reçu: {self.context_limit})"
            )
        
        if self.context_limit > 50:
            logger.warning(
                f"⚠️ context_limit très élevé ({self.context_limit}). "
                f"Risque de dépasser la limite de tokens du contexte."
            )
        
        # Validation gpu_profile
        if self.gpu_profile not in GPU_PROFILES:
            raise ValueError(
                f"gpu_profile invalide : {self.gpu_profile}. "
                f"Valeurs valides : {list(GPU_PROFILES.keys())}"
            )
        
        # Validation temperature
        if not isinstance(self.temperature, (int, float)):
            raise ValueError(
                f"temperature doit être un nombre (reçu: {type(self.temperature)})"
            )
        
        if self.temperature < 0.0 or self.temperature > 2.0:
            raise ValueError(
                f"temperature doit être entre 0.0 et 2.0 (reçu: {self.temperature})"
            )
        
        # Validation top_p
        if not isinstance(self.top_p, (int, float)):
            raise ValueError(
                f"top_p doit être un nombre (reçu: {type(self.top_p)})"
            )
        
        if self.top_p < 0.0 or self.top_p > 1.0:
            raise ValueError(
                f"top_p doit être entre 0.0 et 1.0 (reçu: {self.top_p})"
            )
        
        # Validation max_tokens
        if not isinstance(self.max_tokens, int) or self.max_tokens < 1:
            raise ValueError(
                f"max_tokens doit être un entier >= 1 (reçu: {self.max_tokens})"
            )
        
        if self.max_tokens > 2048:
            logger.warning(
                f"⚠️ max_tokens très élevé ({self.max_tokens}). "
                f"Génération peut être longue."
            )
        
        # Validation system_prompt
        if not isinstance(self.system_prompt, str) or not self.system_prompt.strip():
            raise ValueError("system_prompt ne peut pas être vide")
        
        logger.debug("✅ Configuration validée")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit la configuration en dictionnaire
        
        Returns:
            Dictionnaire avec tous les paramètres
        """
        return {
            "model_path": self.model_path,
            "context_limit": self.context_limit,
            "gpu_profile": self.gpu_profile,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
            "system_prompt": self.system_prompt
        }
    
    def save_to_json(self, config_path: str = "data/config.json"):
        """
        Sauvegarde la configuration dans un fichier JSON
        
        Args:
            config_path: Chemin vers config.json
        
        Note:
            Cette méthode met à jour UNIQUEMENT la section "ai"
            dans config.json, préservant les autres sections.
        """
        # Charger config existante
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        else:
            config_data = {}
        
        # Mettre à jour section "ai"
        config_data["ai"] = self.to_dict()
        
        # Sauvegarder
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        
        logger.info(f"💾 Configuration IA sauvegardée dans {config_path}")
    
    def switch_profile(self, new_profile: str):
        """
        Change le profil GPU actuel
        
        Args:
            new_profile: Nouveau profil ("performance", "balanced", "cpu_fallback")
        
        Raises:
            ValueError: Si le profil n'existe pas
        """
        if new_profile not in GPU_PROFILES:
            raise ValueError(
                f"Profil GPU invalide : {new_profile}. "
                f"Valeurs valides : {list(GPU_PROFILES.keys())}"
            )
        
        old_profile = self.gpu_profile
        self.gpu_profile = new_profile
        
        logger.info(
            f"🔄 Profil GPU changé : {old_profile} → {new_profile} "
            f"({GPU_PROFILES[new_profile]['description']})"
        )
    
    def __repr__(self) -> str:
        """Représentation string de la config"""
        return (
            f"AIConfig(model={os.path.basename(self.model_path)}, "
            f"profile={self.gpu_profile}, "
            f"context={self.context_limit}, "
            f"temp={self.temperature})"
        )


# Instance globale (optionnel, pour usage singleton)
_config_instance: Optional[AIConfig] = None


def get_config(config_path: str = "data/config.json") -> AIConfig:
    """
    Récupère l'instance globale de AIConfig (singleton)
    
    Args:
        config_path: Chemin vers config.json
    
    Returns:
        Instance AIConfig
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = AIConfig.from_json(config_path)
    
    return _config_instance


def list_profiles() -> Dict[str, Dict[str, Any]]:
    """
    Liste tous les profils GPU disponibles
    
    Returns:
        Dictionnaire avec tous les profils
    """
    return GPU_PROFILES


# Pour tests et usage direct
if __name__ == "__main__":
    # Test rapide du système de configuration
    print("🧪 Test du système de configuration IA...\n")
    
    # Test 1 : Création avec valeurs par défaut
    print("1. Création config par défaut...")
    config = AIConfig()
    print(f"   ✅ {config}")
    print(f"   Profile info: {config.get_profile_info()['description']}\n")
    
    # Test 2 : Chargement depuis JSON
    print("2. Chargement depuis config.json...")
    config_from_json = AIConfig.from_json("data/config.json")
    print(f"   ✅ {config_from_json}")
    print(f"   System prompt (début): {config_from_json.system_prompt[:50]}...\n")
    
    # Test 3 : Récupération paramètres GPU
    print("3. Paramètres GPU (balanced)...")
    gpu_params = config.get_gpu_params()
    print(f"   ✅ {gpu_params}\n")
    
    # Test 4 : Switch profil
    print("4. Changement de profil...")
    config.switch_profile("performance")
    print(f"   ✅ {config}")
    gpu_params_perf = config.get_gpu_params()
    print(f"   GPU layers: {gpu_params_perf['n_gpu_layers']}\n")
    
    # Test 5 : Liste tous les profils
    print("5. Liste des profils disponibles...")
    profiles = list_profiles()
    for name, info in profiles.items():
        print(f"   - {name}: {info['description']}")
    
    print("\n✅ Tous les tests manuels passés !")
