# Session 6 : Expressions Faciales (Blendshapes VRM)

**Date :** 19 octobre 2025  
**Objectif :** Implémenter le contrôle des expressions faciales via blendshapes VRM  
**Status :** ✅ **TERMINÉ !**

---

## 🎯 Objectifs de la Session

### Fonctionnalités à implémenter

1. ✅ **VRMBlendshapeController.cs** (Unity)
   - Contrôle des blendshapes VRM
   - Méthodes SetExpression() et ResetExpressions()
   - Accès au VRMBlendShapeProxy de UniVRM

2. ✅ **Commande IPC `set_expression`**
   - Extension du protocole de communication
   - Format JSON : `{"command": "set_expression", "data": {"name": "joy", "value": 0.8}}`

3. ✅ **Interface Python avec sliders**
   - Onglet "Expressions" dans l'interface Qt
   - Sliders pour chaque expression (0-100%)
   - Bouton "Reset All" pour revenir à neutre

4. ✅ **Documentation complète**
   - Guide technique blendshapes VRM
   - Instructions configuration Unity
   - Tests et validation

---

## 🎭 Expressions VRM Implémentées

### Expressions principales (VRM Standard)

| Expression | Nom VRM | Description | Slider Range |
|------------|---------|-------------|--------------|
| 😊 **Joyeux** | `joy` | Sourire, yeux heureux | 0-100% |
| 😠 **En colère** | `angry` | Sourcils froncés, bouche fermée | 0-100% |
| 😢 **Triste** | `sorrow` | Yeux tristes, bouche baissée | 0-100% |
| 😲 **Surpris** | `surprised` | Yeux grands ouverts, bouche O | 0-100% |
| 😄 **Amusé** | `fun` | Sourire éclatant | 0-100% |

### Expressions secondaires (optionnel)

| Expression | Nom VRM | Description |
|------------|---------|-------------|
| 😐 **Neutre** | `neutral` | Expression par défaut |
| 😉 **Clin d'œil gauche** | `blink_l` | Fermeture œil gauche |
| 😉 **Clin d'œil droit** | `blink_r` | Fermeture œil droit |

### Formes de bouche (phonèmes - pour futur lip-sync)

| Phonème | Nom VRM | Description |
|---------|---------|-------------|
| **A** | `a` | Bouche ouverte (ah) |
| **I** | `i` | Bouche étirée (ii) |
| **U** | `u` | Bouche arrondie (ou) |
| **E** | `e` | Bouche mi-ouverte (eh) |
| **O** | `o` | Bouche ronde (oh) |

---

## 📁 Fichiers créés/modifiés

### Nouveaux fichiers

1. **`unity/DesktopMateUnity/Assets/Scripts/VRMBlendshapeController.cs`**
   - Contrôleur principal des blendshapes
   - Thread-safe avec Queue<Action>
   - Gestion des erreurs

2. **`docs/sessions/session_6_expressions/README.md`** (ce fichier)
   - Vue d'ensemble de la session
   - Liste des expressions implémentées

3. **`docs/sessions/session_6_expressions/BLENDSHAPES_GUIDE.md`**
   - Guide technique détaillé
   - Explications sur les blendshapes VRM
   - Instructions Unity pas-à-pas

3. **`docs/sessions/session_6_expressions/scripts/VRMBlendshapeController.cs`**
   - Script de référence complet VERSION 1.6 (finale)
   - Code commenté en français

4. **`docs/sessions/session_6_expressions/scripts/VRMBlendshapeController_V1.6_BACKUP.cs`**
   - Backup de la VERSION 1.6 (avant Session 7)
   - Sauvegarde avant implémentation transitions smooth

### Fichiers modifiés

1. **`unity/DesktopMateUnity/Assets/Scripts/IPC/PythonBridge.cs`**
   - Ajout référence `VRMBlendshapeController`
   - Nouvelle commande `set_expression`
   - Nouvelle commande `reset_expressions`

2. **`src/ipc/unity_bridge.py`**
   - Méthode `set_expression(name, value)`
   - Méthode `reset_expressions()`

3. **`src/gui/app.py`**
   - Nouvel onglet "Expressions"
   - Sliders pour chaque expression principale
   - Bouton "Reset All Expressions"
   - Labels avec valeurs en temps réel

---

## 🛠️ Architecture Technique

### Communication IPC

```
Python (GUI Qt)
    │
    ├─ Slider "Joy" changé → value = 0.8
    │
    ▼
UnityBridge.set_expression("joy", 0.8)
    │
    ├─ Créer JSON: {"command": "set_expression", "data": {"name": "joy", "value": 0.8}}
    │
    ▼
Socket TCP → Unity (port 5555)
    │
    ▼
PythonBridge.cs HandleMessage()
    │
    ├─ Parser JSON
    ├─ Extraire "joy" et 0.8
    │
    ▼
VRMBlendshapeController.SetExpression("joy", 0.8)
    │
    ├─ Ajouter action à Queue<Action>
    │
    ▼
Update() (main thread Unity)
    │
    ├─ Dépiler Queue
    ├─ Exécuter SetExpressionInternal()
    │
    ▼
VRMBlendShapeProxy.ImmediatelySetValue("joy", 0.8)
    │
    ▼
Avatar VRM affiche expression 😊
```

### Thread Safety Unity

Comme pour le VRMLoader, on utilise le pattern **Queue + Update()** :

```csharp
private Queue<Action> mainThreadActions = new Queue<Action>();

public void SetExpression(string name, float value) {
    lock (mainThreadActions) {
        mainThreadActions.Enqueue(() => SetExpressionInternal(name, value));
    }
}

void Update() {
    lock (mainThreadActions) {
        while (mainThreadActions.Count > 0) {
            mainThreadActions.Dequeue()?.Invoke();
        }
    }
}
```

---

## 🔧 Configuration Unity (Pas-à-pas)

### Étape 1 : Créer le script VRMBlendshapeController.cs

1. Dans Unity : `Assets/Scripts/` → Créer `VRMBlendshapeController.cs`
2. Copier le code fourni dans `scripts/VRMBlendshapeController_CLEAN.cs`
3. Sauvegarder et vérifier compilation (pas d'erreurs)

### Étape 2 : Attacher le script au GameObject

1. Dans Unity Hierarchy, sélectionner **PythonBridge** (ou créer nouveau GameObject)
2. Inspector → **Add Component** → `VRMBlendshapeController`
3. Le component apparaît avec un champ "VRM Instance"

### Étape 3 : Configurer la référence VRM

**Option A - Automatique (recommandé) :**
- Le script détecte automatiquement le modèle VRM chargé

**Option B - Manuel :**
1. Dans la Scene, sélectionner l'avatar VRM (GameObject avec VRMBlendShapeProxy)
2. Glisser-déposer dans le champ "VRM Instance" du VRMBlendshapeController
3. Vérifier que le champ est bien assigné

### Étape 4 : Modifier PythonBridge.cs

1. Ouvrir `Assets/Scripts/IPC/PythonBridge.cs`
2. Ajouter la référence publique :
   ```csharp
   public VRMBlendshapeController blendshapeController;
   ```
3. Dans `HandleMessage()`, ajouter les cas `set_expression` et `reset_expressions`
4. Sauvegarder

### Étape 5 : Assigner la référence dans Unity

1. Sélectionner **PythonBridge** dans la Hierarchy
2. Inspector → Section **PythonBridge (Script)**
3. Trouver le champ "Blendshape Controller"
4. Glisser-déposer le GameObject qui a VRMBlendshapeController
5. Vérifier que la référence est bien assignée (pas "None")

### Étape 6 : Tester dans Unity

1. Cliquer **Play** ▶️
2. Lancer l'application Python
3. Connecter à Unity
4. Utiliser les sliders d'expressions
5. Vérifier que l'avatar réagit dans Unity Game window

---

## 🧪 Tests et Validation

### Test 1 : Connexion de base
```python
# Dans Python
unity_bridge.connect()
# Console Unity devrait afficher : "Client Python connecté !"
```

### Test 2 : Expression simple
```python
# Dans Python
unity_bridge.set_expression("joy", 0.8)
# Avatar devrait sourire à 80%
```

### Test 3 : Plusieurs expressions
```python
# Tester chaque expression individuellement
unity_bridge.set_expression("joy", 1.0)      # Sourire max
unity_bridge.set_expression("angry", 0.5)    # Colère modérée
unity_bridge.set_expression("sorrow", 0.3)   # Légèrement triste
```

### Test 4 : Reset
```python
unity_bridge.reset_expressions()
# Avatar devrait revenir à neutre
```

### Test 5 : Sliders GUI
- Bouger chaque slider et vérifier réaction temps réel
- Vérifier que les labels affichent les valeurs correctes
- Tester le bouton "Reset All"

---

## 🐛 Problèmes potentiels et solutions

### Problème 1 : Avatar ne réagit pas
**Causes possibles :**
- VRM Instance non assignée dans VRMBlendshapeController
- Référence blendshapeController non assignée dans PythonBridge
- Modèle VRM ne contient pas ces blendshapes

**Solution :**
1. Vérifier toutes les références dans Unity Inspector
2. Console Unity → chercher logs VRMBlendshapeController
3. Vérifier que le modèle VRM supporte ces blendshapes

### Problème 2 : Erreurs "EnsureRunningOnMainThread"
**Cause :** Blendshapes appelés depuis thread réseau

**Solution :**
- Vérifier que Queue<Action> + Update() est bien implémenté
- S'assurer que `SetExpressionInternal()` est privée et appelée via Queue

### Problème 3 : Expressions incorrectes
**Cause :** Noms de blendshapes différents selon modèle VRM

**Solution :**
- Consulter la documentation du modèle VRM utilisé
- Ajuster les noms dans le mapping (joy → Joy, Preset.Joy, etc.)

### Problème 4 : Sliders ne répondent pas
**Cause :** Connexion Unity perdue

**Solution :**
- Vérifier status "Connected" dans GUI
- Reconnecter avec bouton "Connect to Unity"
- Vérifier logs Python pour erreurs socket

---

## 📚 Documentation Technique

### Fichiers de référence

- **[BLENDSHAPES_GUIDE.md](BLENDSHAPES_GUIDE.md)** - Guide technique complet
- **[scripts/VRMBlendshapeController.cs](scripts/VRMBlendshapeController.cs)** - Code de référence

### Ressources externes

- [Spécification VRM](https://github.com/vrm-c/vrm-specification) - Standard officiel VRM
- [Documentation UniVRM](https://vrm.dev/univrm/) - API UniVRM
- [BlendShape VRM](https://github.com/vrm-c/vrm-specification/blob/master/specification/0.0/schema/vrm.blendshape.md) - Spec blendshapes

---

## 🎯 Prochaines étapes (Session 7+)

### Animations automatiques
- Idle animations (respiration, clignement automatique)
- Smooth transitions entre expressions
- Animation timeline

### Lip-sync audio
- Capture microphone
- Analyse amplitude → formes bouche (A, I, U, E, O)
- Synchronisation temps réel

### Présets d'émotions
- Boutons quick-action (1 clic = expression complète)
- Sauvegarder/charger des présets
- Interpolation entre émotions

---

## ✅ Checklist de complétion

- [x] VRMBlendshapeController.cs créé et compilé
- [x] PythonBridge.cs modifié avec commandes expressions
- [x] unity_bridge.py avec méthodes set_expression() et reset_expressions()
- [x] Interface GUI avec sliders expressions
- [x] Tests réussis pour toutes les expressions principales
- [x] Documentation complète (README, GUIDE, scripts)
- [x] INDEX.md, README.md, CURRENT_STATE.md mis à jour

---

**🎉 Session 6 terminée avec succès ! 🎭**

**Voir :** [SESSION_SUCCESS.md](SESSION_SUCCESS.md) pour le récapitulatif complet.
