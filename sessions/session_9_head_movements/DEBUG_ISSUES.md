# 🐛 Debug & Issues Résolus (Session 9)

## 📋 Vue d'ensemble

Ce document liste tous les **problèmes rencontrés et résolus** lors de la Session 9.

---

## 🐛 Issue #1 : Conflit VRMAutoBlinkController

### Symptômes

- Clignement des yeux **trop rapide**
- Ou clignement **double** (deux clignements rapides successifs)
- Comportement erratique

### Cause

**Deux systèmes de clignement actifs simultanément :**

1. **VRMAutoBlinkController** (Unity)
   - Composant automatiquement attaché aux modèles VRM importés
   - Gère le clignement avec ses propres paramètres (2-5s)
   - Actif par défaut

2. **Notre système Python/IPC**
   - Contrôle depuis l'interface Python
   - Envoie des commandes `set_auto_blink` à Unity
   - PythonBridge contrôle VRMBlendshapeController

**Résultat :** Conflit → Les deux systèmes déclenchent le clignement indépendamment.

### Diagnostic

```
Timeline du clignement observé :
├─ 0.0s : Unity VRMAutoBlinkController déclenche blink
├─ 0.5s : Animation termine
├─ 1.2s : Python/IPC déclenche blink
├─ 1.7s : Animation termine
├─ 2.3s : Unity VRMAutoBlinkController déclenche encore
└─ ...

→ Intervalle irrégulier, impression de "trop rapide"
```

### Solution

**Désactiver VRMAutoBlinkController dans Unity :**

1. Sélectionner le modèle VRM chargé dans la Hierarchy
2. Chercher le composant "VRMAutoBlinkController" dans l'Inspector
3. **Décocher la case** à côté du nom du composant

**Résultat :**
- ✅ Un seul système de clignement (Python/IPC)
- ✅ Contrôle complet depuis l'interface
- ✅ Comportement prévisible et normal

### Impact

**Avant :**
```
Clignement contrôlé par:
├─ Unity VRMAutoBlinkController (incontrôlable)
└─ Python IPC (contrôlable mais en conflit)
```

**Après :**
```
Clignement contrôlé par:
└─ Python IPC uniquement ✅
```

### Prévention

Pour les futures features, **toujours vérifier** si Unity n'a pas déjà un système natif actif :
- Auto-blink → VRMAutoBlinkController
- Look-at → VRMLookAtHead
- Etc.

---

## 🐛 Issue #2 : État VRM après déconnexion Unity

### Symptômes

- Unity se ferme/déconnecte
- Le bouton VRM reste sur **"Décharger modèle VRM"**
- Impossible de recharger un modèle après reconnexion
- État incohérent

### Cause

**Dans `update_status()` (app.py) :**

```python
def update_status(self):
    if not self.unity_bridge.is_connected():
        if self.connect_btn.isEnabled() == False:
            self.status_label.setText("Statut Unity : Déconnecté ✗")
            self.connect_btn.setEnabled(True)
            self.load_vrm_btn.setEnabled(False)
            # ❌ MANQUE : Reset vrm_loaded et texte bouton
```

**Problème :**
- On désactive le bouton VRM ✅
- On réactive le bouton connexion ✅
- **MAIS** on ne remet pas `self.vrm_loaded = False` ❌
- **DONC** le texte reste "Décharger modèle VRM" ❌

### Diagnostic

```
État interne Python :
self.vrm_loaded = True  ← INCORRECT après déconnexion

État visuel UI :
Bouton texte = "Décharger modèle VRM"  ← INCORRECT

État réel Unity :
Connexion = None, VRM = Non chargé  ← CORRECT

→ Incohérence entre état interne et réalité
```

### Solution

**Ajouter le reset d'état dans `update_status()` :**

```python
def update_status(self):
    if self.unity_bridge.is_connected():
        self.status_label.setText("Statut Unity : Connecté ✓")
    else:
        if self.connect_btn.isEnabled() == False:
            self.status_label.setText("Statut Unity : Déconnecté ✗")
            self.connect_btn.setEnabled(True)
            self.load_vrm_btn.setEnabled(False)
            
            # ✅ Reset VRM state when Unity disconnects
            if self.vrm_loaded:
                self.vrm_loaded = False
                self.load_vrm_btn.setText("Charger modèle VRM")
                logger.info("Unity disconnected - VRM state reset")
```

### Comportement

**Avant le fix :**
```
1. Charger VRM → Bouton = "Décharger modèle VRM"
2. Fermer Unity
3. Bouton reste = "Décharger modèle VRM" ❌
4. Reconnecter Unity
5. Cliquer bouton → Erreur (essaie de décharger mais rien n'est chargé)
```

**Après le fix :**
```
1. Charger VRM → Bouton = "Décharger modèle VRM"
2. Fermer Unity
3. Bouton redevient = "Charger modèle VRM" ✅
4. Reconnecter Unity
5. Cliquer bouton → Charge correctement le VRM ✅
```

### Impact

- ✅ État cohérent après déconnexion
- ✅ Possibilité de recharger VRM après reconnexion
- ✅ Pas de commandes erronées envoyées
- ✅ Expérience utilisateur fluide

---

## 🐛 Issue #3 : Code dupliqué lors de la réorganisation UI

### Symptômes

- Fichier `app.py` avec ~940 lignes
- Contrôles dupliqués (blink, head movement)
- Confusion dans le code

### Cause

**Lors de la création des nouveaux onglets :**

1. Création de `create_expressions_tab()`
2. Création de `create_animations_tab()` 
3. Création de `create_options_tab()`
4. **MAIS** l'ancien code (lignes 407-543) n'a pas été supprimé immédiatement

**Résultat :**
- Code de blink présent 2 fois (Animations + ancien onglet)
- Code de head movement présent 2 fois
- Ancien bouton reset présent en double

### Diagnostic

```
Lignes 188-330 : create_animations_tab()  ✅ NOUVEAU
    ├─ Blink controls
    └─ Head movement controls

Lignes 407-543 : (ancien code)  ❌ DUPLICATION
    ├─ Blink controls (IDENTIQUE)
    └─ Head movement controls (IDENTIQUE)
```

### Solution

**Suppression complète des duplications :**

```python
# Lignes 407-543 supprimées
# Remplacées par :

# Reset button for options
reset_opt_layout = QHBoxLayout()
reset_opt_btn = QPushButton("⚙️ Réinitialiser les options")
reset_opt_btn.clicked.connect(self.reset_options)
# [...]
self.tabs.addTab(tab, "Options")
```

**Résultat :**
- Suppression de ~137 lignes dupliquées
- Fichier passe de 940 à ~850 lignes
- Code propre et maintenable

### Prévention

**Pour éviter ce type de problème :**

1. **Planifier** la migration avant de coder
2. **Supprimer** l'ancien code en même temps que la création du nouveau
3. **Vérifier** avec `grep` qu'il n'y a pas de duplications :
   ```bash
   grep -n "auto_blink_checkbox" app.py
   ```
4. **Tester** après chaque modification

---

## 📊 Résumé des issues

| Issue | Gravité | Impact | Résolu | Temps |
|-------|---------|--------|--------|-------|
| Conflit VRMAutoBlinkController | 🟠 Moyen | Clignement erratique | ✅ | 5 min |
| État VRM après déconnexion | 🟡 Faible | UX dégradée | ✅ | 10 min |
| Code dupliqué | 🟡 Faible | Maintenabilité | ✅ | 15 min |

**Total temps debug :** ~30 minutes

---

## ✅ Leçons apprises

### 1. Toujours vérifier les systèmes Unity natifs

**Avant d'implémenter une feature :**
- Chercher si Unity/UniVRM a déjà un système similaire
- Désactiver ou remplacer proprement
- Ne pas superposer deux systèmes

### 2. Gérer proprement les déconnexions

**Pattern à suivre :**
```python
def on_disconnect():
    # 1. Reset état interne
    self.vrm_loaded = False
    
    # 2. Reset UI
    self.load_vrm_btn.setText("Charger modèle VRM")
    
    # 3. Log l'action
    logger.info("Disconnected - state reset")
```

### 3. Refactoring par étapes

**Pour une réorganisation UI :**
1. Créer nouveau code
2. Tester nouveau code
3. **Supprimer ancien code immédiatement**
4. Vérifier pas de duplications
5. Commit

**Éviter :**
- Créer tout le nouveau code en une fois
- Garder l'ancien "au cas où"
- Oublier de supprimer l'ancien

### 4. Tests de déconnexion

**Toujours tester :**
- ✅ Déconnexion Unity pendant utilisation
- ✅ Reconnexion après déconnexion
- ✅ États UI cohérents
- ✅ Possibilité de recharger VRM

---

## 🔧 Checklist debug future

Pour débugger un nouveau problème :

### 1. Identification
- [ ] Reproduire le problème de manière cohérente
- [ ] Noter les symptômes exacts
- [ ] Vérifier les logs (Python + Unity)

### 2. Diagnostic
- [ ] Identifier la cause racine
- [ ] Vérifier s'il y a des conflits (systèmes multiples)
- [ ] Analyser le flux de données (Python → Unity)

### 3. Solution
- [ ] Implémenter le fix
- [ ] Tester le fix
- [ ] Vérifier les edge cases

### 4. Documentation
- [ ] Ajouter dans DEBUG_ISSUES.md
- [ ] Expliquer cause + solution
- [ ] Ajouter prévention

### 5. Prévention
- [ ] Ajouter checks dans le code
- [ ] Créer tests si nécessaire
- [ ] Documenter le pattern à suivre

---

## 📚 Ressources debug

### Logs Unity

**Activer verbose logging :**
```csharp
Debug.Log($"[Component] Action: {details}");
```

**Console Unity :**
- Menu > Window > General > Console
- Filtrer par composant : `[VRMHeadMovementController]`

### Logs Python

**Niveau de log :**
```python
logger.setLevel(logging.DEBUG)  # Pour verbose
logger.setLevel(logging.INFO)   # Pour normal
```

**Fichier de log :**
- Emplacement : `~/.desktop-mate/logs/`
- Rotation automatique

### Outils

**Grep pour rechercher duplications :**
```bash
# Rechercher tous les "auto_blink_checkbox"
grep -rn "auto_blink_checkbox" src/gui/

# Rechercher toutes les méthodes create_
grep -rn "def create_.*tab" src/gui/app.py
```

**Git diff pour voir les changements :**
```bash
git diff src/gui/app.py
```

---

**Fichier :** `docs/sessions/session_9_head_movements/DEBUG_ISSUES.md`  
**Date :** Octobre 2025  
**Auteur :** Copilot + Utilisateur
