# 📝 Conventions de Commits - Workly Docs

## 🎯 Convention : **Semi-Strict**

Ce repo utilise une convention **semi-strict** : utiliser `docs:` pour la documentation technique, mais accepter des commits libres pour les notes et brainstorming.

## 📋 Format

### Pour la documentation technique (préféré)

```
docs: <description courte>
```

### Pour les notes et brainstorming (accepté)

```
Description libre
```

## ✅ Quand utiliser `docs:` ?

Utilise le préfixe `docs:` pour les **commits structurés** :

| Type de changement | Utilise `docs:` | Exemple |
|-------------------|-----------------|---------|
| Ajout de session complète | ✅ Oui | `docs: add session 12 website guide` |
| Mise à jour d'un guide technique | ✅ Oui | `docs: update IPC optimization guide` |
| Création de CURRENT_STATE | ✅ Oui | `docs: update current state for chat 11` |
| Mise à jour d'INDEX.md | ✅ Oui | `docs: update index with session 12` |
| Documentation d'architecture | ✅ Oui | `docs: document Unity threading model` |

## 🎨 Quand utiliser un commit libre ?

Utilise des commits **libres** pour les **notes rapides** :

| Type de changement | Format libre OK | Exemple |
|-------------------|-----------------|---------|
| Notes de brainstorming | ✅ Oui | `Notes session 12 - idées features` |
| TODO temporaire | ✅ Oui | `TODO: vérifier Unity version` |
| Notes de debug | ✅ Oui | `Debug notes - problème IPC` |
| Résumé de chat | ✅ Oui | `Résumé chat 10 - optimisations` |

## 📝 Types de commits `docs:`

### Types principaux

| Type | Usage | Exemple |
|------|-------|---------|
| `docs: add` | Ajout de nouvelle documentation | `docs: add session 12 complete guide` |
| `docs: update` | Mise à jour de doc existante | `docs: update README with new sessions` |
| `docs: fix` | Correction de doc (typo, erreurs) | `docs: fix typos in session 10 guide` |
| `docs: reorganize` | Réorganisation de structure | `docs: reorganize chat transitions folder` |
| `docs: remove` | Suppression de doc obsolète | `docs: remove outdated session 1 notes` |

### Avec scope (recommandé)

```bash
docs(session-12): add website implementation guide
docs(index): update with sessions 10-12
docs(current-state): update for chat 11
docs(transitions): add chat 10 to 11 prompt
```

## ✅ Exemples valides

### Format strict (préféré pour doc technique)

```bash
docs: add session 12 website implementation
docs: update INDEX.md with new sessions
docs(session-11): add performance optimization guide
docs(transitions): create chat 11 context
docs: fix typos in session 10
```

### Format libre (OK pour notes)

```bash
Notes de brainstorming pour session 13
TODO - vérifier Unity 2022.3 LTS
Résumé chat 10 - phases 1-3
Idées pour améliorer les expressions
Debug notes - problème socket timeout
```

### Format mixte (totalement OK)

Tu peux mélanger les deux styles dans le même repo !

```bash
docs: add session 12 guide
Notes rapides sur les animations
docs(index): update with session 12
Brainstorming - idées audio system
docs: update CURRENT_STATE for chat 11
```

## 🌍 Langue

**Français privilégié** car c'est une doc projet personnel :

```bash
# ✅ Préféré
docs: ajouter guide session 12
Notes session 12 - système audio

# ✅ Accepté aussi
docs: add session 12 guide
Session 12 notes - audio system
```

## 📦 Commits détaillés

Pour les grosses mises à jour, ajoute des détails :

```bash
docs: add session 12 complete documentation

- Website implementation guide
- Technical architecture
- Setup instructions
- Troubleshooting section
- Update INDEX.md and README.md
```

## 🎯 Bonnes pratiques

### ✅ À faire

- Utiliser `docs:` pour les guides structurés et complets
- Être descriptif dans les commits
- Mentionner les sessions/chats concernés
- Commits réguliers (ne pas attendre d'avoir 50 changements)

### ❌ À éviter

- Commits vides : `update`, `fix`, `.`
- Trop vague : `docs` (quel doc ?)
- Commits énormes avec 10 sessions différentes

## 💡 Pourquoi cette convention semi-strict ?

1. **Structure** : `docs:` pour retrouver facilement les commits de doc technique
2. **Flexibilité** : Commits libres pour les notes rapides sans friction
3. **Pragmatique** : Adapté au workflow de développement solo avec IA
4. **Lisibilité** : Historique Git clair et organisé
5. **Rapidité** : Pas de blocage pour les notes rapides

## 🔍 Recherche dans l'historique

Avec cette convention, tu peux facilement :

```bash
# Trouver tous les commits de documentation technique
git log --grep="^docs:"

# Trouver les commits d'une session spécifique
git log --grep="session-12"

# Voir tous les changements (structurés + libres)
git log --oneline
```

## 📚 Exemples concrets

### Scenario 1 : Fin de session

```bash
docs: add session 12 website implementation

- Complete technical guide
- Update INDEX.md with session 12
- Update README.md with new features
- Create CURRENT_STATE.md for chat 11
- Add scripts/ folder with final code
```

### Scenario 2 : Notes rapides pendant debug

```bash
Notes debug - problème Unity threading

- Socket timeout après 5 secondes
- Besoin de vérifier le thread principal
- Tester avec Unity 2022.3.15f1
```

### Scenario 3 : Mise à jour incrémentale

```bash
docs(session-12): update troubleshooting section

Add solution for CSS not loading issue
```

### Scenario 4 : Brainstorming

```bash
Idées session 13 - système audio

- Lip-sync avec visèmes
- Détection de pitch pour émotions
- Intégration avec TTS
- Tests avec sounddevice
```

---

**🎯 Résumé rapide :**
- Format strict : `docs: description` pour doc technique
- Format libre : `Description` pour notes rapides
- Les deux sont acceptés dans le même repo
- Français privilégié
- Commits réguliers et descriptifs
