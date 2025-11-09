# 📖 Guide Utilisateur : Contrôle Bot Discord Desktop-Mate

**Version** : Desktop-Mate v0.10.0-alpha  
**Date** : 24 octobre 2025

---

## 🎯 À Quoi Sert le Bot Discord ?

Le **bot Discord Kira** permet à votre avatar VRM Desktop-Mate de :
- ✅ **Discuter sur Discord** avec vos amis/communauté
- ✅ **Réagir émotionnellement** (expressions faciales en temps réel)
- ✅ **Utiliser l'IA Zephyr-7B** pour générer des réponses intelligentes
- ✅ **Se souvenir** des conversations passées
- ✅ **Auto-répondre** dans des salons configurés

---

## 📋 Prérequis

Avant de configurer le bot Discord, vous devez :

1. ✅ **Desktop-Mate installé** et fonctionnel
2. ✅ **IA chargée** (onglet "🔌 Connexion" → "Charger IA")
3. ✅ **Unity optionnel** (pour les réactions VRM)
4. ✅ **Compte Discord** (gratuit)
5. ✅ **Application Discord Bot** créée (voir ci-dessous)

---

## 🚀 Étape 1 : Créer un Bot Discord

### 1.1 Accéder au Developer Portal

1. Ouvrir le navigateur
2. Aller sur [https://discord.com/developers/applications](https://discord.com/developers/applications)
3. Se connecter avec votre compte Discord

### 1.2 Créer une Nouvelle Application

1. Cliquer sur **"New Application"** (en haut à droite)
2. Entrer un nom pour votre bot (ex: "Kira Desktop-Mate")
3. Accepter les conditions d'utilisation
4. Cliquer sur **"Create"**

### 1.3 Créer le Bot

1. Dans le menu de gauche, cliquer sur **"Bot"**
2. Cliquer sur **"Add Bot"**
3. Confirmer en cliquant **"Yes, do it!"**
4. ✅ Votre bot est créé !

### 1.4 Obtenir le Token

1. Dans la section **"Token"**, cliquer sur **"Reset Token"**
2. Confirmer l'action
3. **COPIER LE TOKEN** (bouton "Copy")
4. ⚠️ **NE JAMAIS PARTAGER CE TOKEN** (c'est comme un mot de passe)

### 1.5 Configurer les Intents

Dans la section **"Privileged Gateway Intents"** :

1. ✅ Activer **"MESSAGE CONTENT INTENT"** (IMPORTANT)
2. ✅ Activer **"SERVER MEMBERS INTENT"** (optionnel)
3. Cliquer sur **"Save Changes"**

---

## 🎪 Étape 2 : Inviter le Bot sur Votre Serveur

### 2.1 Générer l'URL d'Invitation

1. Dans le menu de gauche, cliquer sur **"OAuth2"** → **"URL Generator"**
2. Dans **"Scopes"**, cocher :
   - ✅ `bot`
   - ✅ `applications.commands`
3. Dans **"Bot Permissions"**, cocher :
   - ✅ `Send Messages`
   - ✅ `Read Message History`
   - ✅ `View Channels`
   - ✅ `Use Slash Commands` (optionnel)

### 2.2 Inviter le Bot

1. Copier l'**URL générée** (en bas de la page)
2. Ouvrir cette URL dans un navigateur
3. Sélectionner le **serveur** où inviter le bot
4. Cliquer sur **"Continuer"** puis **"Autoriser"**
5. ✅ Le bot est maintenant sur votre serveur !

---

## ⚙️ Étape 3 : Configurer Desktop-Mate

### 3.1 Lancer Desktop-Mate

```powershell
cd C:\Dev\desktop-mate
.\venv\Scripts\Activate.ps1
python main.py
```

### 3.2 Charger l'IA (OBLIGATOIRE)

1. Aller dans l'onglet **"🔌 Connexion"**
2. Cliquer sur **"Charger IA"**
3. Attendre "✅ IA chargée : Zephyr-7B prêt" (~10-30 secondes)

### 3.3 Configurer le Token Discord

1. Aller dans l'onglet **"🤖 Discord"**
2. Coller le **token Discord** dans le champ "Token Discord"
3. Le token s'affiche en `******` (mode password)

### 3.4 Configurer les Salons Auto-Reply

#### Obtenir l'ID d'un Salon Discord

1. Sur Discord, activer le **Mode Développeur** :
   - Paramètres Utilisateur → Avancés → Mode Développeur : **ON**
2. Clic droit sur le **salon** → **"Copier l'identifiant"**
3. Vous obtenez un nombre (ex: `1430901193571569754`)

#### Ajouter le Salon dans Desktop-Mate

1. Dans Desktop-Mate, cliquer sur **"➕ Ajouter Salon"**
2. Coller l'**ID du salon** (ex: `1430901193571569754`)
3. Cliquer sur **"OK"**
4. Le salon apparaît dans la liste

#### Retirer un Salon

1. Sélectionner le salon dans la liste
2. Cliquer sur **"➖ Retirer Salon"**

### 3.5 Configurer le Rate Limit

Le **rate limit** empêche le bot de spammer (répondre trop vite).

1. Ajuster le **QSpinBox "Délai Rate Limit"**
   - Valeur recommandée : **3 secondes**
   - Min : 1 seconde
   - Max : 60 secondes
2. Le bot attendra X secondes avant de répondre à nouveau au même utilisateur

### 3.6 Sauvegarder la Configuration

1. Cliquer sur **"💾 Sauvegarder Configuration"**
2. Message de confirmation : "Configuration sauvegardée avec succès"
3. La config est enregistrée dans `data/config.json`

---

## ▶️ Étape 4 : Démarrer le Bot

### 4.1 Lancer le Bot

1. Cliquer sur **"▶️ Démarrer Bot Discord"**
2. Le statut passe à "🟡 Connexion en cours..."
3. Après quelques secondes : "🟢 Connecté : BotName#1234"
4. ✅ Le bot est maintenant **actif** sur Discord !

### 4.2 Vérifier la Connexion

Sur Discord, le bot apparaît **en ligne** (point vert).

### 4.3 États Visuels

| Icône | Statut | Description |
|-------|--------|-------------|
| 🔴 | Déconnecté | Bot inactif |
| 🟡 | Connexion... | Bot en cours de connexion |
| 🟢 | Connecté | Bot actif sur Discord |

---

## 💬 Étape 5 : Utiliser le Bot sur Discord

### 5.1 Mentionner le Bot

Tapez : `@BotName Bonjour !`

Le bot répondra avec une réponse générée par l'IA Zephyr-7B.

### 5.2 Auto-Reply dans un Salon Configuré

Si vous avez ajouté un salon dans la liste auto-reply :

1. Écrire **n'importe quel message** dans ce salon
2. Le bot **répondra automatiquement** (sans mention nécessaire)
3. Rate limit : Le bot attendra X secondes avant de répondre à nouveau

### 5.3 Voir les Messages dans Desktop-Mate

Dans l'onglet "🤖 Discord", section **"Derniers Messages Discord"** :

```
[12:34:56] User123: Bonjour Kira !
[12:35:02] User456: Comment ça va ?
```

Format : `[HH:MM:SS] Username: message`

Limite : **50 derniers messages** affichés.

### 5.4 Voir les Statistiques

Section **"Statistiques Discord"** :

```
Messages reçus: 42 | Réponses envoyées: 35 | Serveurs: 2 | Uptime: 3600s
```

- **Messages reçus** : Total de messages traités
- **Réponses envoyées** : Total de réponses générées
- **Serveurs** : Nombre de serveurs où le bot est présent
- **Uptime** : Temps depuis le démarrage du bot (en secondes)

---

## ⏹️ Étape 6 : Arrêter le Bot

1. Cliquer sur **"⏹️ Arrêter Bot Discord"**
2. Le statut passe à "🟡 Déconnexion en cours..."
3. Après quelques secondes : "🔴 Déconnecté"
4. Sur Discord, le bot apparaît **hors ligne** (point gris)

---

## 🎭 Intégration avec l'Avatar VRM

Si Unity est connecté, le bot envoie automatiquement les **émotions détectées** à l'avatar VRM.

### Émotions Supportées

| Émotion Discord | Expression VRM |
|----------------|----------------|
| Joie, bonheur | 😊 Joy |
| Colère, frustration | 😠 Angry |
| Tristesse | 😢 Sorrow |
| Surprise | 😲 Surprised |
| Amusement, rire | 😄 Fun |
| Neutre | 😐 Neutral |

### Exemple

1. Utilisateur Discord : "Wow c'est incroyable !"
2. Bot détecte : **Émotion "surprise"** (intensité 80%)
3. Avatar VRM : Affiche l'expression **"😲 Surprised"**
4. Bot répond : "Je suis ravie que ça te plaise ! ..."

---

## 🔧 Dépannage

### ❌ Problème : "IA Non Disponible"

**Erreur** : Message "Le bot Discord nécessite que l'IA soit chargée."

**Solution** :
1. Aller dans l'onglet "🔌 Connexion"
2. Cliquer sur "Charger IA"
3. Attendre "✅ IA chargée"
4. Retourner dans Discord et démarrer le bot

---

### ❌ Problème : "Token Manquant"

**Erreur** : Message "Veuillez entrer votre token Discord."

**Solution** :
1. Obtenir le token Discord (voir Étape 1)
2. Coller le token dans le champ
3. Sauvegarder la configuration
4. Redémarrer le bot

---

### ❌ Problème : Bot ne répond pas

**Cause possible 1** : Le bot n'est pas dans le bon salon

**Solution** : Vérifier que le salon est dans la liste auto-reply.

**Cause possible 2** : Permissions manquantes

**Solution** : Vérifier les permissions du bot sur le serveur Discord.

**Cause possible 3** : Rate limiting

**Solution** : Attendre X secondes (délai configuré) avant de réessayer.

---

### ❌ Problème : Erreur "403 Forbidden"

**Cause** : Le bot n'a pas les permissions nécessaires.

**Solution** :
1. Sur Discord, clic droit sur le bot → "Gérer les permissions"
2. Activer : "Envoyer des messages", "Lire l'historique"
3. Redémarrer le bot

---

### ❌ Problème : Token invalide

**Erreur** : Message "Improper token has been passed."

**Causes** :
- Token copié incorrectement (espaces, caractères manquants)
- Token désactivé/régénéré sur Discord

**Solution** :
1. Aller sur Discord Developer Portal
2. Bot → Reset Token
3. Copier le nouveau token
4. Coller dans Desktop-Mate
5. Sauvegarder et redémarrer

---

### ❌ Problème : "MESSAGE CONTENT INTENT" manquant

**Erreur** : Le bot ne voit pas le contenu des messages.

**Solution** :
1. Discord Developer Portal → Bot
2. Activer "MESSAGE CONTENT INTENT"
3. Sauvegarder
4. Redémarrer le bot Desktop-Mate

---

## 🔒 Sécurité

### ⚠️ RÈGLES IMPORTANTES

1. **NE JAMAIS** partager votre token Discord
2. **NE JAMAIS** commit le token dans Git
3. **NE JAMAIS** publier screenshots avec le token visible
4. Si le token est compromis : **Révoquer immédiatement** (Discord Developer Portal)

### Stockage Sécurisé

Desktop-Mate stocke le token dans :
- `data/config.json` (local uniquement)
- Affiché en mode **password** dans l'UI (`*****`)
- **PAS** inclus dans les commits Git (.gitignore)

### Variable d'Environnement (Alternative)

Au lieu de stocker le token dans config.json :

1. Créer un fichier `.env` :
   ```env
   DISCORD_TOKEN=votre_token_ici
   ```
2. Desktop-Mate chargera automatiquement depuis `.env`
3. ⚠️ Ajouter `.env` dans `.gitignore`

---

## 💡 Conseils & Astuces

### Optimiser la Vitesse de Réponse

1. **GPU CUDA** : Utiliser le profil "performance" (35-43 layers)
   - Onglet Connexion → Profil GPU : "Performance"
   - Génération : ~2-3 secondes

2. **Reduce Context** : Limiter l'historique de conversation
   - Éditer `data/config.json`
   - `"context_limit": 5` (au lieu de 10)

### Rate Limiting Optimal

- **Salon calme** : 1-2 secondes
- **Salon actif** : 3-5 secondes
- **Salon très actif** : 10-15 secondes

### Salons Auto-Reply

**Recommandations** :
- ✅ Salon dédié au bot (ex: #bot-kira)
- ✅ Salon de test/debug
- ❌ Éviter les salons généraux (spam)
- ❌ Éviter les salons avec d'autres bots

### Tester le Bot

Commandes utiles (sur Discord) :

```
@BotName Bonjour !
@BotName Raconte-moi une blague
@BotName Comment ça va ?
```

---

## 📊 Limites Actuelles

| Limite | Valeur | Note |
|--------|--------|------|
| Messages affichés | 50 max | GUI Desktop-Mate |
| Historique conversation | 10 messages | Par utilisateur |
| Rate limit min | 1 seconde | Configurable |
| Rate limit max | 60 secondes | Configurable |
| Longueur réponse | ~200 tokens | ~150 mots |
| Serveurs Discord | Illimité | Supporté |
| Salons auto-reply | Illimité | Configurable |

---

## 🎯 Cas d'Usage

### 1. Bot Personnel (Communauté Discord)

- Ajouter le bot sur votre serveur privé
- Configurer 1-2 salons auto-reply
- Laisser Desktop-Mate tourner sur votre PC
- Le bot répond automatiquement à vos amis

### 2. Assistant Discord

- Créer un salon dédié "#demande-à-kira"
- Configurer ce salon en auto-reply
- Utilisateurs posent des questions
- Kira répond intelligemment

### 3. Bot de Test/Développement

- Créer un serveur Discord de test
- Tester les réponses de l'IA
- Ajuster les paramètres (temperature, top_p)
- Vérifier les émotions VRM

---

## 📚 Ressources

### Documentation

- [Discord.py Docs](https://discordpy.readthedocs.io/)
- [Discord Developer Portal](https://discord.com/developers/docs)
- [Desktop-Mate README](../../README.md)

### Aide

- **Issues GitHub** : [github.com/Xyon15/desktop-mate/issues](https://github.com/Xyon15/desktop-mate/issues)
- **Discord Server** : (à créer)

---

## ✅ Checklist Configuration

Avant de démarrer le bot, vérifier :

- [ ] IA chargée (onglet Connexion)
- [ ] Token Discord copié et collé
- [ ] Au moins 1 salon auto-reply ajouté
- [ ] Rate limit configuré (3 secondes recommandé)
- [ ] Configuration sauvegardée
- [ ] Bot invité sur le serveur Discord
- [ ] Permissions bot OK (Send Messages, Read History)
- [ ] MESSAGE CONTENT INTENT activé

---

**🎊 Vous êtes maintenant prêt à utiliser le bot Discord Kira avec Desktop-Mate ! 🤖✨**

**Amusez-vous bien et n'hésitez pas à personnaliser les réponses de Kira ! 🎭💬**

---

**Dernière mise à jour** : 24 octobre 2025  
**Version** : Desktop-Mate v0.10.0-alpha
