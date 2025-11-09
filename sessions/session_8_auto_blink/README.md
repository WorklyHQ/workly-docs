# 👁️ Session 8 : Clignement Automatique ✅

## 📋 Vue d'ensemble

Cette session implémente le **clignement automatique des yeux** pour ajouter du réalisme à l'avatar VRM avec :
- ✅ **Timer aléatoire** (intervalles 2-5 secondes)
- ✅ **Animation fluide** avec courbes SmoothStep (interpolation Hermite)
- ✅ **Toggle on/off** depuis l'interface Python
- ✅ **Paramètres configurables** (fréquence, durée)
- ✅ **Timing réaliste** (160ms par clignement = vitesse humaine)

**🎉 Session terminée avec succès !**

## 🎯 Objectifs de la session

### Objectifs principaux
1. ⏱️ Créer un système de clignement automatique avec timer aléatoire
2. 👁️ Utiliser le blendshape "Blink" (ou équivalent VRM)
3. 🔄 Réutiliser le système Lerp de la Session 7 pour transitions smooth
4. 🎛️ Permettre l'activation/désactivation depuis Python

### Fonctionnalités bonus
- ⚙️ Paramètres configurables (intervalle min/max, durée)
- 💾 Sauvegarde de l'état (on/off) dans config.json
- 🔧 Ajustement en temps réel des paramètres

## 🏗️ Architecture technique

### VRMAutoBlinkController.cs (Unity)

**Nouveau composant Unity** :
- **Timer aléatoire** : `Random.Range(minInterval, maxInterval)` (2-5 secondes)
- **Coroutines** : `BlinkLoop()` pour le timing, `PerformBlink()` pour l'animation
- **Animation SmoothStep** : Interpolation Hermite pour mouvement naturel
- **Manipulation directe** : Bypass du système Lerp via `VRMBlendShapeProxy`
- **Toggle** : Méthode `SetBlinkEnabled(bool enabled)`

**Logique du clignement (3 phases)** :
```csharp
Phase 1: Fermeture (50ms)
  - Value: 0.0 → 1.0
  - Courbe: Mathf.SmoothStep(0f, 1f, t)
  - Accélération douce → max → décélération

Phase 2: Pause (30ms)
  - Value: 1.0 (maintenu)
  - Yeux complètement fermés

Phase 3: Ouverture (80ms)
  - Value: 1.0 → 0.0
  - Courbe: Mathf.SmoothStep(1f, 0f, t)
  - Accélération douce → max → décélération

Total: 160ms (réalisme humain ✅)
```

### Extension PythonBridge (Unity)

**Nouvelle commande IPC** :
- `set_auto_blink` : Active/désactive le clignement automatique
  - Paramètre : `enabled` (bool)
  - Appelle : `autoBlinkController.SetAutoBlinkEnabled(enabled)`

### Extension unity_bridge.py (Python)

**Nouvelle méthode** :
```python
def set_auto_blink(self, enabled: bool) -> bool:
    return self.send_command("set_auto_blink", {"enabled": enabled})
```

### Interface Python (PySide6)

**Nouveau contrôle dans onglet Expressions** :
- **Checkbox** : "Clignement automatique"
- **Signal** : `stateChanged` → `unity_bridge.set_auto_blink(checked)`
- **Sauvegarde** : État persisté dans `config.json`

### Configuration (config.json)

**Nouveaux champs** :
```json
{
  "avatar": {
    "auto_blink": {
      "enabled": false,
      "min_interval": 2.0,
      "max_interval": 5.0,
      "duration": 0.1
    }
  }
}
```

## 📁 Fichiers créés/modifiés

### Fichiers Unity (à créer/modifier)
```
unity/DesktopMateUnity/Assets/Scripts/
├── VRMAutoBlinkController.cs (NOUVEAU)
└── IPC/PythonBridge.cs (ajout commande set_auto_blink)
```

### Fichiers Python (à modifier)
```
src/
├── gui/app.py (checkbox clignement automatique)
├── ipc/unity_bridge.py (méthode set_auto_blink)
└── utils/config.py (champs auto_blink)
```

### Documentation
```
docs/sessions/session_8_auto_blink/
├── README.md (ce fichier - vue d'ensemble)
├── BLINK_GUIDE.md (guide rapide d'implémentation)
├── TECHNICAL_GUIDE.md (guide technique détaillé ✅)
├── TROUBLESHOOTING.md (résolution de problèmes ✅)
└── scripts/ (scripts finaux ✅)
    ├── VRMAutoBlinkController.cs
    ├── VRMBlendshapeController.cs
    ├── PythonBridge.cs
    ├── unity_bridge.py
    ├── config.py
    └── app.py
```

## 🚀 Guide d'utilisation rapide

### Activation du clignement

1. **Lancer Unity + Python**
2. **Connecter à Unity**
3. **Charger modèle VRM**
4. **Cocher "Clignement automatique"** dans onglet Expressions
5. **Observer** : L'avatar cligne des yeux toutes les 2-5 secondes !

### Désactivation

Décocher la checkbox "Clignement automatique"

## 🎓 Concepts techniques

### Coroutines Unity

Les coroutines permettent d'exécuter du code de manière asynchrone :
```csharp
IEnumerator BlinkSequence()
{
    while (isEnabled)
    {
        yield return new WaitForSeconds(randomInterval);
        // Clignotement
    }
}
```

### Blendshapes VRM pour les yeux

**Blendshapes standards VRM** :
- `Blink` : Fermeture complète des deux yeux
- `Blink_L` : Œil gauche uniquement
- `Blink_R` : Œil droit uniquement

Pour ce système, on utilise `Blink` (les deux yeux).

### Réutilisation du système Lerp

Le système de transitions smooth de la Session 7 est automatiquement utilisé :
- `currentValues["Blink"]` interpolé vers `targetValues["Blink"]`
- Transition naturelle grâce au Lerp dans `Update()`

## 🐛 Problèmes potentiels et solutions

### 1. Blendshape "Blink" inexistant
**Solution** : Vérifier les blendshapes disponibles sur le modèle VRM, utiliser un fallback

### 2. Conflit avec expressions manuelles
**Solution** : Le système Lerp gère automatiquement, pas de conflit

### 3. Clignement trop rapide/lent
**Solution** : Ajuster `min_interval` et `max_interval` dans config

## 📊 Tests effectués

- ✅ Clignement régulier avec intervalles aléatoires (2-5s)
- ✅ Transitions smooth avec courbes SmoothStep (pas de saccades)
- ✅ Toggle on/off fonctionne depuis l'interface Python
- ✅ Sauvegarde de l'état dans config.json
- ✅ Compatibilité avec expressions manuelles (pas de conflit)
- ✅ Animation réaliste (160ms = vitesse humaine)
- ✅ Mapping BlendShape Blink/Blink_L/Blink_R correct
- ✅ Tests unitaires Python : 8/8 passing

## 🔗 Liens utiles

- [Documentation Coroutines Unity](https://docs.unity3d.com/Manual/Coroutines.html)
- [VRM BlendShape Specifications](https://vrm.dev/en/univrm/blendshape/univrm_blendshape/)
- [Session 7 - Système Lerp](../docs/sessions/session_7_animations/TRANSITIONS_GUIDE.md)

## 📈 Prochaines étapes possibles

Après Session 8, options pour Session 9 :

### Option A : Lip-sync audio
- Capture microphone
- Analyse fréquences (FFT)
- Animation bouche temps réel

### Option B : Variations de clignement
- Clins d'œil (un seul œil)
- Double clignement
- Clignement émotionnel (selon expression)

### Option C : Head bobbing
- Mouvement subtil de la tête
- Respiration (mouvement du torse)
- Idle animations

---

## 🎯 Résumé de la session

### Problèmes résolus

1. **Blendshapes non appliqués** → Ajout mapping Blink/Blink_L/Blink_R dans `GetBlendShapeKey()`
2. **Animation trop lente** → Bypass Lerp + manipulation directe VRMBlendShapeProxy
3. **Animation robotique** → Utilisation de courbes SmoothStep au lieu d'interpolation linéaire

### Résultat final

**🎉 Clignement automatique des yeux parfaitement fonctionnel !**

- Animation naturelle et fluide (160ms par clignement)
- Intervalles aléatoires réalistes (2-5 secondes)
- Toggle on/off depuis Python avec sauvegarde config
- Cohabitation pacifique avec le système Lerp d'expressions
- Tests unitaires à 100%

### Références

- 📖 [TECHNICAL_GUIDE.md](./TECHNICAL_GUIDE.md) - Architecture détaillée, algorithmes, diagrammes
- 🐛 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Tous les problèmes rencontrés et leurs solutions
- 📂 [scripts/](./scripts/) - Tous les fichiers créés/modifiés pendant la session

---

**✅ Session 8 terminée avec succès - 21 octobre 2025**
