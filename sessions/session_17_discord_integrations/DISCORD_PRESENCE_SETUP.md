# 🎮 Configuration Discord Rich Presence - Workly

Ce guide explique comment configurer Discord Rich Presence pour afficher ton activité Workly sur ton profil Discord.

---

## 📋 Prérequis

- Discord installé et ouvert sur ton PC
- Workly desktop application installée
- Compte Discord Developer (gratuit)

---

## 🔧 Étape 1 : Créer une Application Discord

### 1.1 Accéder au Developer Portal

1. Va sur https://discord.com/developers/applications
2. Connecte-toi avec ton compte Discord
3. Clique sur **"New Application"**
4. Nomme ton application **"Workly"**
5. Accepte les conditions et clique **"Create"**

### 1.2 Récupérer le Client ID

1. Sur la page de ton application, va dans **"General Information"**
2. Copie l'**Application ID** (aussi appelé Client ID)
3. ⚠️ **Garde-le précieusement**, tu en auras besoin !

Exemple : `1234567890123456789`

---

## 🎨 Étape 2 : Uploader les Images (Assets)

### 2.1 Accéder à Rich Presence Assets

1. Dans ton application Discord, clique sur **"Rich Presence"** dans le menu latéral
2. Va dans **"Art Assets"**
3. Tu peux maintenant uploader les images

### 2.2 Images requises

Upload les images suivantes (format PNG, 512x512 minimum) :

| Nom de l'asset | Description | Usage |
|----------------|-------------|-------|
| `workly_logo` | Logo principal Workly | Grande image (toujours visible) |
| `vrm_active` | Icône avatar VRM | Badge : Avatar actif |
| `status_talking` | Icône conversation | Badge : En conversation |
| `status_listening` | Icône micro | Badge : En écoute |
| `status_thinking` | Icône cerveau | Badge : IA réfléchit |
| `status_idle` | Icône sommeil | Badge : Inactif |
| `status_loading` | Icône chargement | Badge : Chargement |

### 2.3 Créer les images (si tu n'en as pas)

Tu peux :
- Utiliser des emojis Discord comme images temporaires
- Créer tes propres images avec Canva/Photoshop
- Utiliser des icônes gratuites de sites comme Flaticon
- **Note** : Les images doivent être **carrées** (512x512 recommandé)

---

## ⚙️ Étape 3 : Configurer Workly

### 3.1 Éditer le fichier de configuration

Ouvre le fichier de configuration Workly selon ta situation :

**Option A - Workly jamais lancé** (recommandé) :
- Fichier : `workly-desktop\data\config.json`
- **Avantage** : Configuration prête dès le premier lancement

**Option B - Workly déjà lancé** :
- Fichier : `C:\Users\TON_NOM\.workly\config.json`
- **Note** : Ce fichier est créé automatiquement au premier lancement

⚠️ **Si tu ne trouves pas la section `discord_presence`** : Utilise l'**Option A** (fichier du projet).

### 3.2 Activer Discord Presence

Trouve la section `discord_presence` et modifie-la :

```json
{
  "discord_presence": {
    "enabled": true,
    "client_id": "TON_CLIENT_ID_ICI"
  }
}
```

**Remplace** `TON_CLIENT_ID_ICI` par le Client ID que tu as copié à l'étape 1.2

**Exemple** :
```json
{
  "discord_presence": {
    "enabled": true,
    "client_id": "1234567890123456789"
  }
}
```

### 3.3 Sauvegarder

Sauvegarde le fichier `config.json` et redémarre Workly.

---

## ✅ Étape 4 : Tester

### 4.1 Vérifier que ça fonctionne

1. **Lance Discord** (si pas déjà ouvert)
2. **Lance Workly**
3. Regarde les logs dans l'onglet **Logs** de Workly :
   - Tu devrais voir : `✅ Discord Rich Presence connectée`

4. Ouvre ton profil Discord :
   - Tu devrais voir **"En train d'utiliser Workly"**
   - Avec le logo et le statut actuel

### 4.2 États affichés

| État de Workly | Discord affiche |
|----------------|-----------------|
| Démarrage | "Workly - Avatar en attente" |
| VRM chargé | "Avatar VRM actif - Idle" |
| IA en chargement | "Chargement du modèle IA" |
| Conversation active | "Discute avec Kira - En conversation" |
| IA réfléchit | "Génère une réponse - En réflexion" |

---

## 🐛 Dépannage

### Problème : "Discord n'est pas ouvert, Rich Presence désactivée"

**Solution** :
1. Lance Discord AVANT Workly
2. Redémarre Workly
3. Vérifie que Discord tourne en arrière-plan

### Problème : "Erreur Discord RPC"

**Solutions possibles** :
1. Vérifie que le **Client ID** est correct dans `config.json`
2. Vérifie que l'application Discord existe sur le Developer Portal
3. Redémarre Discord ET Workly
4. Vérifie que Discord n'a pas bloqué les Rich Presence :
   - Paramètres Discord → Activité → "Afficher l'activité en cours"

### Problème : "Les images ne s'affichent pas"

**Solutions** :
1. Vérifie que tu as uploadé les assets sur le Developer Portal
2. Les noms des assets doivent **exactement** correspondre :
   - `workly_logo` (pas `workly-logo` ou `WorklyLogo`)
3. Attends 5-10 minutes après l'upload (cache Discord)
4. Redémarre Workly

### Problème : "Rich Presence se déconnecte"

**Causes possibles** :
- Discord fermé/redémarré
- Workly essaiera de se reconnecter automatiquement
- Vérifie les logs dans l'onglet Logs

---

## 🔒 Confidentialité

### Que voit-on sur ton profil ?

- ✅ "Utilise Workly - Assistant Virtuel"
- ✅ Ton statut actuel (Idle, En conversation, etc.)
- ✅ Temps écoulé depuis le lancement
- ✅ Bouton "En savoir plus" (vers le site Workly)

### Ce qui n'est PAS partagé :

- ❌ Contenu de tes conversations
- ❌ Messages envoyés/reçus
- ❌ Données personnelles
- ❌ Modèle VRM utilisé

**Note** : Tu peux désactiver à tout moment en mettant `"enabled": false` dans `config.json`.

---

## 🎨 Personnalisation avancée (Futur)

Dans une future version, tu pourras :
- Personnaliser les messages affichés
- Choisir quels états afficher
- Ajouter des statistiques (nombre de conversations)
- Créer des boutons personnalisés

---

## 📞 Besoin d'aide ?

- 💬 Discord Workly : https://discord.gg/3Cpyxg29B4
- 🐛 GitHub Issues : https://github.com/WorklyHQ/workly-desktop/issues
- 📧 Email : worklyhq@gmail.com

---

**🎭 Affiche fièrement que tu utilises Workly ! ✨**
