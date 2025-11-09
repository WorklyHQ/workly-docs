# 📦 Installation de UniVRM - Méthode Alternative (Plus Simple)

L'installation par Git URL ne fonctionne pas ? Pas de panique ! On va utiliser la méthode manuelle avec le fichier `.unitypackage`.

---

## 🎯 Méthode Alternative : Installation Manuelle (Recommandée)

### Étape 1 : Télécharger UniVRM

Je vais t'ouvrir la page de téléchargement :

**Lien direct** : https://github.com/vrm-c/UniVRM/releases

1. Sur la page, cherche la **dernière version** (en haut de la liste)
2. Télécharge le fichier qui s'appelle :
   ```
   UniVRM-x.xx.x_xxxx.unitypackage
   ```
   (Exemple : `UniVRM-0.115.0_26fe.unitypackage`)

3. **⚠️ IMPORTANT** : Télécharge le fichier qui contient **"UniVRM"** dans le nom, PAS "VRM-1.0"

---

### Étape 2 : Importer dans Unity

Une fois le fichier téléchargé :

1. **Dans Unity**, va dans le menu :
   ```
   Assets > Import Package > Custom Package...
   ```

2. **Sélectionne** le fichier `.unitypackage` que tu viens de télécharger

3. Une fenêtre s'ouvre avec une liste de fichiers :
   - ✅ **Coche tout** (clique sur "All" en bas à gauche si nécessaire)
   - Clique sur **"Import"** (en bas à droite)

4. ⏳ **Attends l'importation** (peut prendre 2-5 minutes)
   - Unity va compiler les scripts
   - Une barre de progression s'affiche en bas

---

### Étape 3 : Vérifier l'Installation

Une fois l'importation terminée :

1. **Vérifie le menu** :
   - Tu devrais voir un nouveau menu **"VRM"** dans la barre de menu (en haut)
   - Si tu vois "VRM", c'est gagné ! ✅

2. **Vérifie le dossier Assets** :
   - Dans le panneau "Project" (en bas), ouvre le dossier **"Assets"**
   - Tu devrais voir des dossiers : "VRM", "UniGLTF", "VRMShaders", etc.

3. **Console** (en bas) :
   - Vérifie qu'il n'y a **pas d'erreurs rouges**
   - Des warnings jaunes (⚠️) sont normaux et OK

---

## ✅ Vérification Finale

**Installation réussie si :**

✅ Menu **"VRM"** visible dans la barre de menu Unity  
✅ Dossiers "VRM", "UniGLTF", "VRMShaders" dans Assets  
✅ **Aucune erreur rouge** dans la Console  

---

## 🆘 Problèmes Possibles

### Je ne trouve pas le fichier .unitypackage

Sur la page GitHub :
- Descends un peu sur la page des releases
- Cherche la section **"Assets"** (elle peut être repliée, clique pour ouvrir)
- Télécharge le fichier `.unitypackage`

### Erreurs après l'import

Si tu vois des erreurs rouges :
1. **Attends 1-2 minutes** : Unity compile
2. **Menu** : `Assets > Reimport All` (pour tout recompiler)
3. **Redémarre Unity** si nécessaire

### Le menu "VRM" n'apparaît pas

- Vérifie que l'import s'est bien terminé
- Redémarre Unity
- Vérifie la Console pour des erreurs

---

## 🎯 Prochaine Étape

Une fois UniVRM installé avec succès :

**Dis-moi "UniVRM est installé"** et on continuera avec :
1. ✅ Créer le script PythonBridge.cs
2. ✅ Configurer la scène
3. ✅ Tester le chargement de ton modèle VRM
4. ✅ Tester la connexion avec Python

---

**Télécharge le fichier .unitypackage et importe-le dans Unity !** 🚀

Je t'attends ! 😊
