# 📦 Installation de UniVRM dans Unity

UniVRM est le package officiel pour charger et utiliser des modèles VRM dans Unity.

---

## 🎯 Méthode Recommandée : Package Manager (Git URL)

### Étape 1 : Ouvrir le Package Manager

Dans Unity, va dans le menu :
```
Window > Package Manager
```

Une fenêtre s'ouvre avec la liste des packages.

---

### Étape 2 : Ajouter les Packages UniVRM

Tu dois installer **3 packages dans cet ordre précis** :

#### 📦 Package 1 : VRMShaders

1. Dans le Package Manager, clique sur le **"+"** en haut à gauche
2. Sélectionne **"Add package from git URL..."**
3. Colle cette URL :
   ```
   https://github.com/vrm-c/UniVRM.git?path=/Assets/VRMShaders
   ```
4. Clique sur **"Add"**
5. **Attends que l'installation se termine** (barre de progression en bas de Unity)

#### 📦 Package 2 : UniGLTF

1. Clique à nouveau sur le **"+"**
2. Sélectionne **"Add package from git URL..."**
3. Colle cette URL :
   ```
   https://github.com/vrm-c/UniVRM.git?path=/Assets/UniGLTF
   ```
4. Clique sur **"Add"**
5. **Attends que l'installation se termine**

#### 📦 Package 3 : VRM

1. Clique encore sur le **"+"**
2. Sélectionne **"Add package from git URL..."**
3. Colle cette URL :
   ```
   https://github.com/vrm-c/UniVRM.git?path=/Assets/VRM
   ```
4. Clique sur **"Add"**
5. **Attends que l'installation se termine**

---

### Étape 3 : Vérifier l'Installation

Une fois les 3 packages installés :

1. **Regarde dans le Package Manager** (à gauche) :
   - Tu devrais voir "VRM", "UniGLTF", et "VRMShaders" dans la liste

2. **Vérifie dans le menu Unity** :
   - Tu devrais maintenant avoir un nouveau menu **"VRM"** dans la barre de menu en haut
   - Si tu vois "VRM" dans les menus, c'est gagné ! ✅

3. **Dans la Console Unity** (en bas) :
   - Vérifie qu'il n'y a **pas d'erreurs rouges**
   - Des warnings (⚠️ jaunes) sont OK

---

## ⚠️ Problèmes Possibles

### "Cannot resolve package" ou erreur Git

**Solution Alternative : Installation Manuelle**

Si les URLs Git ne marchent pas, voici la méthode manuelle :

1. **Télécharge UniVRM** :
   - Va sur : https://github.com/vrm-c/UniVRM/releases
   - Télécharge le fichier `.unitypackage` le plus récent (ex: `UniVRM-0.115.0.unitypackage`)

2. **Importe dans Unity** :
   - Dans Unity : `Assets > Import Package > Custom Package...`
   - Sélectionne le fichier `.unitypackage` téléchargé
   - Clique sur **"Import"** (tout cocher)
   - Attends l'importation

### Erreurs de compilation

Si tu vois des erreurs rouges :
- **Attends 1-2 minutes** : Unity compile les scripts
- **Redémarre Unity** : Ferme et rouvre le projet
- Vérifie que tu as bien installé les 3 packages **dans l'ordre**

### Le menu "VRM" n'apparaît pas

- Vérifie dans le Package Manager que les 3 packages sont bien installés
- Redémarre Unity
- Vérifie la Console pour des erreurs

---

## ✅ Vérification Finale

**Tu as réussi si :**

✅ Le Package Manager affiche "VRM", "UniGLTF", et "VRMShaders"  
✅ Un menu **"VRM"** apparaît dans la barre de menu Unity  
✅ **Aucune erreur rouge** dans la Console  

---

## 🎯 Prochaine Étape

Une fois UniVRM installé sans erreur :

**Dis-moi "UniVRM est installé"** et on passera à :
1. ✅ Créer le script PythonBridge.cs
2. ✅ Configurer la scène
3. ✅ Tester la connexion avec Python

---

## 💡 Astuce

Pendant l'installation des packages, Unity peut sembler "gelé". **C'est normal !**

Regarde la barre de progression en bas de la fenêtre Unity pour suivre l'avancement.

**Sois patient, ça peut prendre 2-3 minutes par package !** ⏳

---

**Lance l'installation et dis-moi si tout se passe bien !** 🚀
