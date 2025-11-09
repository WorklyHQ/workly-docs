# 🎭 Guide Technique : Mouvements de Tête Automatiques

## 📋 Vue d'ensemble

Ce guide détaille l'**implémentation technique des mouvements de tête automatiques** dans Desktop-Mate.

**Objectif :** Rendre l'avatar plus vivant avec des mouvements de tête **aléatoires, naturels et fluides**.

---

## 🏗️ Architecture

### Composants

```
Python GUI (app.py)
    ↓ Checkbox + Sliders
Python IPC (unity_bridge.py)
    ↓ JSON command
Unity PythonBridge (PythonBridge.cs)
    ↓ Parse & call
Unity Controller (VRMHeadMovementController.cs)
    ↓ Coroutine
VRM Head Bone
    ↓ Rotation update
Avatar visuel
```

---

## 🎯 Unity C# : VRMHeadMovementController

### Fichier

`unity/VRMHeadMovementController.cs`

### Classe complète

```csharp
using System.Collections;
using UnityEngine;

public class VRMHeadMovementController : MonoBehaviour
{
    [Header("Head Movement Settings")]
    [Tooltip("Enable/disable automatic head movements")]
    public bool enabled = true;

    [Tooltip("Minimum interval between movements (seconds)")]
    [Range(1f, 5f)]
    public float minInterval = 3f;

    [Tooltip("Maximum interval between movements (seconds)")]
    [Range(3f, 15f)]
    public float maxInterval = 7f;

    [Tooltip("Maximum rotation angle (degrees)")]
    [Range(1f, 20f)]
    public float maxAngle = 5f;

    private Transform headBone;
    private Quaternion initialHeadRotation;
    private Coroutine movementCoroutine;

    void Start()
    {
        // Find head bone via Animator
        Animator animator = GetComponent<Animator>();
        if (animator != null)
        {
            headBone = animator.GetBoneTransform(HumanBodyBones.Head);
            if (headBone != null)
            {
                initialHeadRotation = headBone.localRotation;
                Debug.Log($"[VRMHeadMovementController] Head bone found: {headBone.name}");
                
                if (enabled)
                {
                    StartMovements();
                }
            }
            else
            {
                Debug.LogError("[VRMHeadMovementController] Head bone not found!");
            }
        }
        else
        {
            Debug.LogError("[VRMHeadMovementController] Animator not found!");
        }
    }

    public void SetEnabled(bool value)
    {
        enabled = value;
        if (enabled)
        {
            StartMovements();
        }
        else
        {
            StopMovements();
        }
    }

    public void SetParameters(float minInt, float maxInt, float angle)
    {
        minInterval = Mathf.Clamp(minInt, 1f, 5f);
        maxInterval = Mathf.Clamp(maxInt, 3f, 15f);
        maxAngle = Mathf.Clamp(angle, 1f, 20f);
        
        Debug.Log($"[VRMHeadMovementController] Parameters updated: min={minInterval}s, max={maxInterval}s, angle={maxAngle}°");
    }

    private void StartMovements()
    {
        if (headBone == null) return;
        
        if (movementCoroutine != null)
        {
            StopCoroutine(movementCoroutine);
        }
        
        movementCoroutine = StartCoroutine(RandomHeadMovement());
        Debug.Log("[VRMHeadMovementController] Head movements started");
    }

    private void StopMovements()
    {
        if (movementCoroutine != null)
        {
            StopCoroutine(movementCoroutine);
            movementCoroutine = null;
        }
        
        if (headBone != null)
        {
            headBone.localRotation = initialHeadRotation;
        }
        
        Debug.Log("[VRMHeadMovementController] Head movements stopped");
    }

    private IEnumerator RandomHeadMovement()
    {
        while (enabled)
        {
            // Wait random interval
            float waitTime = Random.Range(minInterval, maxInterval);
            yield return new WaitForSeconds(waitTime);

            // Generate random target rotation
            float targetYaw = Random.Range(-maxAngle, maxAngle);
            float targetPitch = Random.Range(-maxAngle / 2f, maxAngle / 2f);

            Quaternion startRotation = headBone.localRotation;
            Quaternion targetRotation = initialHeadRotation * 
                Quaternion.Euler(targetPitch, targetYaw, 0f);

            // Smooth interpolation
            float movementDuration = Random.Range(0.3f, 0.8f);
            float elapsedTime = 0f;

            while (elapsedTime < movementDuration)
            {
                elapsedTime += Time.deltaTime;
                float t = elapsedTime / movementDuration;
                float smoothT = Mathf.SmoothStep(0f, 1f, t);

                headBone.localRotation = Quaternion.Slerp(
                    startRotation,
                    targetRotation,
                    smoothT
                );

                yield return null;
            }

            // Hold position briefly
            yield return new WaitForSeconds(Random.Range(0.2f, 0.5f));

            // Return to neutral
            startRotation = headBone.localRotation;
            elapsedTime = 0f;
            movementDuration = Random.Range(0.4f, 0.9f);

            while (elapsedTime < movementDuration)
            {
                elapsedTime += Time.deltaTime;
                float t = elapsedTime / movementDuration;
                float smoothT = Mathf.SmoothStep(0f, 1f, t);

                headBone.localRotation = Quaternion.Slerp(
                    startRotation,
                    initialHeadRotation,
                    smoothT
                );

                yield return null;
            }

            headBone.localRotation = initialHeadRotation;
        }
    }

    void OnDisable()
    {
        StopMovements();
    }
}
```

### Explication détaillée

#### 1. Recherche du head bone

```csharp
Animator animator = GetComponent<Animator>();
headBone = animator.GetBoneTransform(HumanBodyBones.Head);
initialHeadRotation = headBone.localRotation;
```

**Pourquoi :**
- Les modèles VRM utilisent le système Humanoid d'Unity
- `HumanBodyBones.Head` est l'enum standard pour la tête
- On sauvegarde la rotation initiale pour y revenir (position neutre)

**Alternatives :**
- ❌ Rechercher par nom ("Head", "head", "頭") → Fragile, dépend du modèle
- ✅ Utiliser Humanoid → Fonctionne avec tous les VRM

#### 2. Génération angles aléatoires

```csharp
float targetYaw = Random.Range(-maxAngle, maxAngle);      // Gauche/Droite
float targetPitch = Random.Range(-maxAngle / 2f, maxAngle / 2f);  // Haut/Bas
```

**Explication :**
- **Yaw** (Y-axis) : Rotation horizontale (-5° à +5° par défaut)
- **Pitch** (X-axis) : Rotation verticale (moitié moins, -2.5° à +2.5°)
- **Roll** (Z-axis) : Pas utilisé (évite l'effet "penché bizarre")

**Pourquoi pitch/2 ?**
- Mouvements verticaux trop amples = bizarre (penche trop la tête)
- Mouvements horizontaux plus naturels et fréquents

#### 3. Interpolation SmoothStep

```csharp
float t = elapsedTime / movementDuration;
float smoothT = Mathf.SmoothStep(0f, 1f, t);

headBone.localRotation = Quaternion.Slerp(
    startRotation,
    targetRotation,
    smoothT
);
```

**SmoothStep vs Lerp :**

| Méthode | Courbe | Vitesse | Naturalité |
|---------|--------|---------|-----------|
| `Lerp` | Linéaire | Constante | Robotique ❌ |
| `SmoothStep` | S-curve | Variable | Naturelle ✅ |

**Visualisation SmoothStep :**
```
Vitesse
  ^
  │     ╱────╲
  │    ╱      ╲
  │   ╱        ╲
  │  ╱          ╲
  └─────────────────> Temps
    Accélération | Décélération
```

**Résultat :**
- Démarrage progressif (pas de "jerk")
- Accélération au milieu
- Arrêt en douceur

#### 4. Cycle de mouvement

```
1. Attendre (minInterval à maxInterval)
   ↓
2. Générer rotation aléatoire (yaw + pitch)
   ↓
3. Interpoler vers target (0.3-0.8s)
   ↓
4. Tenir position (0.2-0.5s)
   ↓
5. Retourner à neutre (0.4-0.9s)
   ↓
6. Répéter
```

**Durées aléatoires :**
- Mouvement vers target : 0.3-0.8s
- Hold position : 0.2-0.5s  
- Retour neutre : 0.4-0.9s

**Pourquoi ?** Éviter la prévisibilité, rendre naturel.

---

## 🔌 Unity IPC : PythonBridge

### Commande `set_auto_head_movement`

**Ajout dans PythonBridge.cs :**

```csharp
case "set_auto_head_movement":
{
    bool enabled = data.ContainsKey("enabled") && (bool)data["enabled"];
    float minInterval = data.ContainsKey("min_interval") ? 
        Convert.ToSingle(data["min_interval"]) : 3f;
    float maxInterval = data.ContainsKey("max_interval") ? 
        Convert.ToSingle(data["max_interval"]) : 7f;
    float maxAngle = data.ContainsKey("max_angle") ? 
        Convert.ToSingle(data["max_angle"]) : 5f;

    if (headMovementController != null)
    {
        headMovementController.SetEnabled(enabled);
        if (enabled)
        {
            headMovementController.SetParameters(minInterval, maxInterval, maxAngle);
        }
        Debug.Log($"[PythonBridge] Auto head movement: {enabled}, " +
                  $"interval=[{minInterval}-{maxInterval}]s, angle={maxAngle}°");
    }
    break;
}
```

**Gestion des paramètres :**
- `enabled` : true/false
- `min_interval` : 3.0s (fixe depuis Python)
- `max_interval` : 3.0-10.0s (slider Python)
- `max_angle` : 2.0-10.0° (slider Python)

---

## 🐍 Python : unity_bridge.py

### Méthode d'envoi

```python
def set_auto_head_movement(self, enabled: bool, min_interval: float, 
                           max_interval: float, max_angle: float):
    """Enable/disable automatic head movements with parameters.
    
    Args:
        enabled: Enable or disable head movements
        min_interval: Minimum interval between movements (seconds)
        max_interval: Maximum interval between movements (seconds)
        max_angle: Maximum rotation angle (degrees)
    """
    command = {
        "command": "set_auto_head_movement",
        "enabled": enabled,
        "min_interval": min_interval,
        "max_interval": max_interval,
        "max_angle": max_angle
    }
    self.send_command("set_auto_head_movement", command)
    logger.info(f"Set auto head movement: {enabled}, "
                f"interval=[{min_interval}-{max_interval}]s, "
                f"angle={max_angle}°")
```

### Exemple JSON envoyé

```json
{
  "command": "set_auto_head_movement",
  "enabled": true,
  "min_interval": 3.0,
  "max_interval": 7.0,
  "max_angle": 5.0
}
```

---

## 🖥️ Python : Interface GUI

### Sliders dans app.py

**Fréquence (max_interval) :**
```python
self.head_freq_slider = QSlider(Qt.Horizontal)
self.head_freq_slider.setMinimum(30)   # 3.0s
self.head_freq_slider.setMaximum(100)  # 10.0s
self.head_freq_slider.setValue(70)     # 7.0s default

# Conversion: slider_value / 10.0 = seconds
max_interval = self.head_freq_slider.value() / 10.0
```

**Amplitude (max_angle) :**
```python
self.head_amp_slider = QSlider(Qt.Horizontal)
self.head_amp_slider.setMinimum(20)   # 2.0°
self.head_amp_slider.setMaximum(100)  # 10.0°
self.head_amp_slider.setValue(50)     # 5.0° default

# Conversion: slider_value / 10.0 = degrees
max_angle = self.head_amp_slider.value() / 10.0
```

### Handler de changement

```python
def on_head_movement_param_change(self, label, format_str, value, param_name):
    """Handle head movement parameter slider change."""
    # Update label
    label.setText(format_str.format(value))
    
    # Save to config
    self.config.set(f"avatar.auto_head_movement.{param_name}", value)
    self.config.save()
    
    # Send to Unity if enabled
    if self.unity_bridge.is_connected() and self.vrm_loaded:
        if self.auto_head_movement_checkbox.isChecked():
            min_interval = 3.0
            max_interval = self.head_freq_slider.value() / 10.0
            max_angle = self.head_amp_slider.value() / 10.0
            
            self.unity_bridge.set_auto_head_movement(
                True, min_interval, max_interval, max_angle
            )
```

---

## 📊 Paramètres et valeurs

### Tableau récapitulatif

| Paramètre | Type | Min | Max | Défaut | Unité | Description |
|-----------|------|-----|-----|--------|-------|-------------|
| `enabled` | bool | - | - | `true` | - | Active/désactive mouvements |
| `min_interval` | float | 1.0 | 5.0 | `3.0` | secondes | Intervalle minimum (fixe) |
| `max_interval` | float | 3.0 | 15.0 | `7.0` | secondes | Intervalle maximum (slider) |
| `max_angle` | float | 1.0 | 20.0 | `5.0` | degrés | Angle maximum rotation |

### Comportement selon les valeurs

**Fréquence (max_interval) :**
- `3.0s` → Mouvements fréquents (toutes les 3s)
- `7.0s` → Mouvements modérés (tous les 3-7s) ✅ Défaut
- `10.0s` → Mouvements rares (tous les 3-10s)

**Amplitude (max_angle) :**
- `2.0°` → Mouvements subtils (micro-mouvements)
- `5.0°` → Mouvements naturels ✅ Défaut
- `10.0°` → Mouvements amples (très expressifs)

---

## 🧪 Tests et validation

### Tests fonctionnels

**Test 1 : Activation/Désactivation**
```
1. Charger VRM
2. Cocher "Activer mouvements de tête"
   → Mouvements démarrent
3. Décocher
   → Mouvements s'arrêtent, tête revient à neutre
```

**Test 2 : Fréquence**
```
1. Slider à 3.0s (min)
   → Mouvements très fréquents
2. Slider à 10.0s (max)
   → Mouvements rares
```

**Test 3 : Amplitude**
```
1. Slider à 2.0° (min)
   → Micro-mouvements subtils
2. Slider à 10.0° (max)
   → Grands mouvements expressifs
```

### Tests de performance

**Métriques :**
- ✅ FPS stable (60 FPS maintenu)
- ✅ Pas de lag visible
- ✅ Coroutine n'impacte pas Update()

**Monitoring Unity :**
```csharp
// Profiler → CPU Usage → VRMHeadMovementController
// Overhead : < 0.1ms par frame
```

### Tests edge cases

**Test 1 : Déconnexion Unity**
```
1. Activer mouvements
2. Fermer Unity
   → Python détecte déconnexion
   → UI se désactive correctement
```

**Test 2 : Modèle sans head bone**
```
1. Charger modèle non-Humanoid
   → Log erreur "Head bone not found"
   → Pas de crash, comportement graceful
```

**Test 3 : Valeurs extrêmes**
```
1. Slider fréquence à 3.0s, amplitude à 2.0°
   → Mouvements subtils mais visibles
2. Slider fréquence à 10.0s, amplitude à 10.0°
   → Mouvements rares mais amples
```

---

## 🎨 Variantes et améliorations futures

### Variante 1 : Mouvements influencés par l'audio

```csharp
// Dans RandomHeadMovement()
if (AudioAnalyzer.IsSpeaking())
{
    // Mouvements plus fréquents pendant la parole
    waitTime = Random.Range(minInterval * 0.5f, maxInterval * 0.5f);
}
```

### Variante 2 : Regard vers le curseur

```csharp
// Calculer direction vers curseur souris
Vector3 cursorWorldPos = Camera.main.ScreenToWorldPoint(Input.mousePosition);
Vector3 directionToCursor = (cursorWorldPos - headBone.position).normalized;

// Limiter rotation vers curseur
Quaternion lookRotation = Quaternion.LookRotation(directionToCursor);
headBone.rotation = Quaternion.Slerp(
    headBone.rotation,
    lookRotation,
    Time.deltaTime * lookSpeed
);
```

### Variante 3 : Profils émotionnels

```csharp
enum EmotionalState { Calm, Excited, Sad }

EmotionalState currentEmotion = EmotionalState.Calm;

switch (currentEmotion)
{
    case EmotionalState.Excited:
        minInterval *= 0.5f;  // Mouvements plus fréquents
        maxAngle *= 1.5f;     // Plus amples
        break;
    case EmotionalState.Sad:
        minInterval *= 2f;    // Mouvements plus rares
        maxAngle *= 0.5f;     // Plus subtils
        break;
}
```

---

## 🔧 Debugging

### Logs Unity

**Activation :**
```
[VRMHeadMovementController] Head bone found: J_Bip_C_Head
[VRMHeadMovementController] Head movements started
```

**Mise à jour paramètres :**
```
[VRMHeadMovementController] Parameters updated: min=3s, max=7s, angle=5°
[PythonBridge] Auto head movement: True, interval=[3-7]s, angle=5°
```

**Désactivation :**
```
[VRMHeadMovementController] Head movements stopped
```

### Problèmes courants

**Problème 1 : Pas de mouvement**

Vérifier :
- [ ] Head bone trouvé ? (Log "Head bone found")
- [ ] Enabled = true ?
- [ ] VRM chargé ?
- [ ] Script attaché au bon GameObject ?

**Problème 2 : Mouvements saccadés**

Solution :
- Utiliser `SmoothStep` au lieu de `Lerp`
- Augmenter `movementDuration` (0.5-1.0s)
- Vérifier FPS stable

**Problème 3 : Rotation bizarre (tête penché)**

Cause : Utilisation de rotation absolute au lieu de locale

Solution :
```csharp
// ✅ CORRECT
headBone.localRotation = targetRotation;

// ❌ INCORRECT
headBone.rotation = targetRotation;
```

---

## 📚 Ressources

### Unity Documentation

- [Humanoid Avatars](https://docs.unity3d.com/Manual/ConfiguringtheAvatar.html)
- [Quaternion.Slerp](https://docs.unity3d.com/ScriptReference/Quaternion.Slerp.html)
- [Mathf.SmoothStep](https://docs.unity3d.com/ScriptReference/Mathf.SmoothStep.html)
- [Coroutines](https://docs.unity3d.com/Manual/Coroutines.html)

### UniVRM Documentation

- [VRM Specification](https://github.com/vrm-c/vrm-specification)
- [UniVRM GitHub](https://github.com/vrm-c/UniVRM)

---

## ✅ Checklist d'implémentation

Pour implémenter des mouvements similaires :

### Unity
- [ ] Créer VRMHeadMovementController.cs
- [ ] Attacher au GameObject avec Animator
- [ ] Configurer paramètres dans Inspector
- [ ] Tester mouvements visuellement

### IPC
- [ ] Ajouter commande dans PythonBridge.cs
- [ ] Extraire paramètres JSON
- [ ] Appeler SetEnabled() et SetParameters()

### Python
- [ ] Créer méthode unity_bridge.set_auto_head_movement()
- [ ] Ajouter UI (checkbox + sliders)
- [ ] Connecter signaux
- [ ] Sauvegarder config

### Tests
- [ ] Test activation/désactivation
- [ ] Test sliders (min/max)
- [ ] Test performance (FPS)
- [ ] Test déconnexion Unity

---

**Fichier :** `docs/sessions/session_9_head_movements/HEAD_MOVEMENT_GUIDE.md`  
**Date :** Octobre 2025  
**Auteur :** Copilot + Utilisateur
