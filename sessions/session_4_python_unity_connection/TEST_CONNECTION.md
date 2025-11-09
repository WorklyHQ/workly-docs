# 🔗 Test de la Connexion Python ↔ Unity

C'est le moment de vérité ! On va tester la communication entre ton application Python et Unity ! 🚀

---

## 🎯 Étapes du Test

### Étape 1 : Lancer Unity en Mode Play

Dans Unity :

1. **Assure-toi que** le GameObject `PythonBridge` est bien dans la Hierarchy
2. **Clique sur le bouton Play** ▶️ (en haut au centre de Unity)
3. **Ouvre la Console Unity** (menu : `Window > General > Console`)
4. **Vérifie** que tu vois ces messages :
   ```
   [PythonBridge] Démarrage du serveur sur 127.0.0.1:5555
   [PythonBridge] ✅ Serveur démarré avec succès sur 127.0.0.1:5555
   [PythonBridge] En attente de connexion Python...
   ```

5. **Dans la fenêtre Game** (onglet à côté de Scene), tu devrais voir en haut à gauche :
   ```
   ⏳ En attente de Python...
   ```
   (écrit en rouge)

✅ **Si tu vois ces messages, Unity est prêt à recevoir la connexion !**

---

### Étape 2 : Lancer l'Application Python

**GARDE Unity en mode Play** (ne le ferme pas !)

Maintenant, dans un terminal PowerShell :

```powershell
cd C:\Dev\desktop-mate
.\venv\Scripts\Activate.ps1
python main.py
```

L'interface Qt de Desktop-Mate s'ouvre.

---

### Étape 3 : Connecter Python à Unity

Dans l'interface Desktop-Mate :

1. **Clique sur le bouton** **"Connect to Unity"**
2. **Regarde ce qui se passe !**

---

## ✅ Ce Qui Devrait se Passer

### Dans Unity (Console) :

Tu devrais voir apparaître :
```
[PythonBridge] 🔗 Client Python connecté !
[PythonBridge] 📤 Envoyé : {"type":"response","status":"connected","message":"Unity server ready"}
```

### Dans Unity (Fenêtre Game) :

Le texte en haut à gauche devrait passer de rouge à **vert** :
```
✅ Python Connecté
```

### Dans l'Application Python :

Le statut devrait changer :
```
Unity Status: Connected ✓
```

Le bouton "Load VRM Model" devrait devenir **actif** (cliquable).

---

## 🎉 SI ÇA MARCHE : BRAVO ! 

**Félicitations !** Tu as réussi à établir la communication entre Python et Unity ! 🎊

Tu as maintenant :
- ✅ Application Python fonctionnelle
- ✅ Unity configuré avec UniVRM
- ✅ Communication IPC établie
- ✅ Base solide pour Desktop-Mate

---

## 🆘 SI ÇA NE MARCHE PAS

### Problème 1 : "Unity Status: Connection Failed ✗"

**Vérifications** :
1. ✅ Unity est bien en mode Play ?
2. ✅ Le GameObject `PythonBridge` est dans la Hierarchy ?
3. ✅ La Console Unity affiche "Serveur démarré" ?
4. ✅ Pas de firewall qui bloque le port 5555 ?

**Solution** :
- Redémarre Unity (Stop puis Play)
- Redémarre l'application Python
- Vérifie la Console Unity pour des erreurs

### Problème 2 : Erreur dans la Console Unity

**Si tu vois une erreur rouge dans Unity** :
- Copie-moi l'erreur exacte
- Vérifie que le script PythonBridge.cs est bien attaché au GameObject

### Problème 3 : Rien ne se passe

**Vérifie** :
1. Unity est bien en mode **Play** (bouton Play enfoncé)
2. L'application Python est bien lancée
3. Tu as bien cliqué sur "Connect to Unity"

---

## 🎯 Prochaines Étapes (Si ça Marche)

Une fois la connexion établie, on pourra :

1. **Charger ton modèle VRM** (`Mura Mura - Model.vrm`)
2. **L'afficher dans Unity**
3. **Contrôler les expressions** depuis Python
4. **Implémenter le lip-sync audio**

---

## 💡 Notes Importantes

- **Unity doit être en Play** pour que le serveur socket fonctionne
- **Python se connecte à Unity** (et non l'inverse)
- Le port utilisé est **5555** (localhost)

---

## 🎬 Résumé des Actions

1. ▶️ **Unity** : Clique sur Play
2. 🐍 **Python** : Lance `python main.py`
3. 🔗 **Interface** : Clique "Connect to Unity"
4. ✅ **Vérifie** : Messages dans la Console Unity + statut vert

---

**Lance le test et dis-moi ce qui se passe !** 🚀

Si ça marche, on fête ça ! 🎉  
Si ça ne marche pas, on va débugger ensemble ! 🔧
