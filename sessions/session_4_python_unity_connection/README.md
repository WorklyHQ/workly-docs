# Session 4 : Connexion Python ↔ Unity

**Mise en place de la communication IPC (Inter-Process Communication)**

---

## 📋 Contenu de cette session

### 📄 UNITY_PYTHONBRIDGE_SETUP.md
Guide de création du script PythonBridge.cs dans Unity

### 📄 TEST_CONNECTION.md
Procédure de test de la connexion Python → Unity

### 📄 DEBUG_CONNECTION.md
Guide de résolution des problèmes de connexion

### 📄 FIX_SCRIPT_NOT_RUNNING.md ⚠️ IMPORTANT
Solution au problème du script Unity qui ne démarre pas (checkbox)

---

## ✅ Objectifs de la session

1. Créer le serveur socket dans Unity (PythonBridge.cs)
2. Créer le client socket en Python (unity_bridge.py)
3. Établir la connexion TCP sur le port 5555
4. Tester l'envoi de messages JSON bidirectionnel

---

## 🔧 Architecture IPC

```
┌─────────────────┐         TCP Socket          ┌─────────────────┐
│  Python Client  │  ←→  127.0.0.1:5555  ←→     │  Unity Server   │
│                 │                              │                 │
│  unity_bridge   │      JSON Messages           │  PythonBridge   │
│  send_command() │  ─────────────────→          │  HandleMessage()│
│                 │  ←─────────────────          │  SendMessage()  │
└─────────────────┘                              └─────────────────┘
```

---

## 🐛 Problèmes courants

### ❌ "Connexion refusée"
- Unity n'est pas en mode Play
- Le script PythonBridge n'est pas activé (checkbox décochée)
- Le port 5555 est utilisé par une autre application

### ❌ "Script ne démarre pas"
- **Solution :** Vérifier que la checkbox du script est cochée dans l'Inspector
- Voir : `FIX_SCRIPT_NOT_RUNNING.md`

### ❌ "Pas de logs dans Unity"
- La Console Unity doit être visible
- Le script doit être attaché à un GameObject actif
- Unity doit être en mode Play

---

## 🎯 Résultat attendu

À la fin de cette session, tu as :
- ✅ PythonBridge.cs fonctionnel dans Unity
- ✅ unity_bridge.py fonctionnel en Python
- ✅ Connexion établie (message "Client Python connecté !")
- ✅ Bouton "Connect to Unity" dans l'interface Python
- ✅ Status de connexion visible dans Unity et Python

---

## 🔗 Session suivante

👉 **Session 5 : Chargement VRM** pour afficher les avatars 3D
