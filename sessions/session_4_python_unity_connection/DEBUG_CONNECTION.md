# 🔧 Debug - Connexion Refusée

## ❌ Problème Identifié

Python dit : `Aucune connexion n'a pu être établie car l'ordinateur cible l'a expressément refusée`

Cela signifie que **Unity n'écoute pas sur le port 5555**.

---

## 🔍 Vérifications à Faire dans Unity

### 1️⃣ Unity est-il en Mode Play ?

**Dans Unity** :
- Le bouton Play ▶️ doit être **enfoncé/bleu**
- Si ce n'est pas le cas, clique dessus

### 2️⃣ Vérifie la Console Unity

**Ouvre la Console** : Menu `Window > General > Console`

**Que vois-tu dans la Console ?**

#### ✅ Si tu vois :
```
[PythonBridge] Démarrage du serveur sur 127.0.0.1:5555
[PythonBridge] ✅ Serveur démarré avec succès
[PythonBridge] En attente de connexion Python...
```
➡️ C'est bon ! Le serveur Unity fonctionne. Réessaye la connexion Python.

#### ❌ Si tu vois des ERREURS ROUGES :
Copie-moi **le message d'erreur exact** et je t'aiderai à le corriger.

#### 🤔 Si tu ne vois RIEN :
Le script ne s'exécute pas. Vérifions :

---

## 🔧 Solutions Possibles

### Solution 1 : Vérifier le GameObject

1. **Dans la Hierarchy** (panneau gauche), cherche l'objet **"PythonBridge"**
2. **Clique dessus**
3. **Dans l'Inspector** (panneau droit), vérifie :
   - ✅ Le script **"Python Bridge (Script)"** est bien attaché
   - ✅ Il n'y a pas de texte rouge "Missing Script"
   - ✅ Port = 5555
   - ✅ Host = 127.0.0.1

### Solution 2 : Redémarrer Unity en Mode Play

1. **Clique sur Stop** ⏹️ (si Unity est en Play)
2. **Clique sur Play** ▶️ à nouveau
3. **Regarde la Console** pour les messages de démarrage

### Solution 3 : Vérifier les Erreurs de Compilation

1. **Ouvre la Console Unity**
2. **Clique sur "Clear"** pour effacer
3. **Regarde si des erreurs apparaissent**

Si tu vois des erreurs, copie-les moi !

---

## 🎯 Checklist Complète

Vérifie ces points **un par un** :

- [ ] Unity est ouvert
- [ ] Unity est en mode **Play** ▶️
- [ ] Le GameObject **"PythonBridge"** existe dans la Hierarchy
- [ ] Le script **PythonBridge.cs** est attaché au GameObject
- [ ] La Console Unity affiche "Serveur démarré avec succès"
- [ ] Aucune erreur rouge dans la Console Unity

---

## 💡 Test Rapide

Pour tester si le problème vient de Unity ou de Python :

### Dans Unity (en mode Play), vérifie :

1. **Fenêtre Game** : Tu devrais voir en haut à gauche :
   ```
   ⏳ En attente de Python...
   ```
   (en rouge)

2. Si tu ne vois PAS ce texte :
   - Le script ne s'exécute pas
   - Vérifie qu'il est bien attaché au GameObject

---

## 📸 Si tu es bloqué

Envoie-moi une capture d'écran ou dis-moi :

1. **Unity est-il en mode Play ?** (Oui/Non)
2. **Que dit la Console Unity ?** (Copie les messages)
3. **Le GameObject PythonBridge existe-t-il ?** (Oui/Non)
4. **Y a-t-il des erreurs rouges ?** (Oui/Non + copie l'erreur)

---

**Vérifie ces points et dis-moi ce que tu trouves !** 🔍
