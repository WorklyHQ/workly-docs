# 🔧 Guide de Configuration Unity - Session 6

**Configuration pas-à-pas pour implémenter les expressions faciales**

---

## 📋 Vue d'ensemble

Tu vas devoir :
1. ✅ Créer le script `VRMBlendshapeController.cs` dans Unity
2. ✅ Modifier `PythonBridge.cs` pour ajouter les nouvelles commandes
3. ✅ Configurer les références dans Unity Inspector
4. ✅ Tester les expressions avec Python

**Temps estimé** : 10-15 minutes

---

## 🛠️ Étape 1 : Créer VRMBlendshapeController.cs

### 1.1 - Ouvrir Unity

1. Ouvrir **Unity Hub**
2. Charger le projet `unity/DesktopMateUnity/`
3. Attendre que Unity charge complètement

### 1.2 - Créer le script

1. Dans Unity, **Project window** en bas
2. Naviguer vers `Assets/Scripts/`
3. **Clic droit** dans le dossier → **Create** → **C# Script**
4. Nommer le fichier : `VRMBlendshapeController`
5. **Double-cliquer** sur le fichier pour l'ouvrir dans Visual Studio/VS Code

### 1.3 - Copier le code

1. Ouvrir le fichier de référence : `docs/sessions/session_6_expressions/scripts/VRMBlendshapeController.cs`
2. **Copier tout le contenu** (Ctrl+A, Ctrl+C)
3. **Coller dans Unity** (remplacer tout le contenu existant)
4. **Sauvegarder** (Ctrl+S)
5. Retourner dans Unity (le script va compiler automatiquement)

### 1.4 - Vérifier la compilation

1. Dans Unity, **Console window** (en bas)
2. Vérifier qu'il n'y a **aucune erreur rouge**
3. Si erreurs → vérifier que tout le code a bien été copié

---

## 🔄 Étape 2 : Modifier PythonBridge.cs

### 2.1 - Ouvrir le script

1. Dans Unity Project window : `Assets/Scripts/IPC/PythonBridge.cs`
2. **Double-cliquer** pour ouvrir

### 2.2 - Ajouter la référence VRMBlendshapeController

Chercher cette section (vers ligne 20) :
```csharp
[Header("VRM Loader")]
[Tooltip("Référence au VRMLoader pour charger les modèles")]
public VRMLoader vrmLoader;
```

**Ajouter juste en dessous** :
```csharp
[Header("VRM Blendshapes")]
[Tooltip("Référence au VRMBlendshapeController pour les expressions")]
public VRMBlendshapeController blendshapeController;
```

### 2.3 - Ajouter les commandes expressions

Chercher la méthode `HandleMessage()` (vers ligne 150).

Trouve cette section :
```csharp
else if (jsonMessage.Contains("\"set_expression\""))
{
    Debug.Log("[PythonBridge] 😊 Commande : Changer l'expression");
    // TODO: Implémenter le changement d'expression
}
```

**Remplacer par** (copier depuis le fichier actuel `PythonBridge.cs` dans le projet) :
```csharp
else if (jsonMessage.Contains("\"set_expression\""))
{
    Debug.Log("[PythonBridge] 😊 Commande : Changer l'expression");
    
    // Extraire le nom de l'expression et la valeur
    string expressionName = ExtractStringValue(jsonMessage, "name");
    float expressionValue = ExtractFloatValue(jsonMessage, "value");

    // Appeler le BlendshapeController
    if (blendshapeController != null)
    {
        Debug.Log($"[PythonBridge] 🎭 Expression : {expressionName} = {expressionValue:F2}");
        blendshapeController.SetExpression(expressionName, expressionValue);

        SendMessage(new
        {
            type = "response",
            command = "set_expression",
            status = "success",
            message = $"Expression '{expressionName}' appliquée à {expressionValue:F2}"
        });
    }
    else
    {
        Debug.LogError("[PythonBridge] ❌ VRMBlendshapeController non assigné !");
    }
}
else if (jsonMessage.Contains("\"reset_expressions\""))
{
    Debug.Log("[PythonBridge] 🔄 Commande : Reset expressions");

    if (blendshapeController != null)
    {
        blendshapeController.ResetExpressions();

        SendMessage(new
        {
            type = "response",
            command = "reset_expressions",
            status = "success",
            message = "Toutes les expressions réinitialisées"
        });
    }
    else
    {
        Debug.LogError("[PythonBridge] ❌ VRMBlendshapeController non assigné !");
    }
}
```

### 2.4 - Ajouter les méthodes helper

À la fin du fichier `PythonBridge.cs`, **avant le dernier `}`**, ajouter :

```csharp
/// <summary>
/// Extrait une valeur string depuis le JSON
/// </summary>
private string ExtractStringValue(string json, string key)
{
    try
    {
        string searchKey = $"\"{key}\"";
        int keyStart = json.IndexOf(searchKey);
        if (keyStart == -1) return "";

        int valueStart = json.IndexOf("\"", keyStart + searchKey.Length + 1);
        if (valueStart == -1) return "";

        int valueEnd = json.IndexOf("\"", valueStart + 1);
        if (valueEnd == -1) return "";

        return json.Substring(valueStart + 1, valueEnd - valueStart - 1);
    }
    catch (Exception e)
    {
        Debug.LogError($"[PythonBridge] ❌ Erreur extraction '{key}' : {e.Message}");
        return "";
    }
}

/// <summary>
/// Extrait une valeur float depuis le JSON
/// </summary>
private float ExtractFloatValue(string json, string key)
{
    try
    {
        string searchKey = $"\"{key}\"";
        int keyStart = json.IndexOf(searchKey);
        if (keyStart == -1) return 0.0f;

        int colonIndex = json.IndexOf(":", keyStart);
        if (colonIndex == -1) return 0.0f;

        int valueStart = colonIndex + 1;
        while (valueStart < json.Length && (json[valueStart] == ' ' || json[valueStart] == '\t'))
            valueStart++;

        int valueEnd = valueStart;
        while (valueEnd < json.Length && json[valueEnd] != ',' && json[valueEnd] != '}' && json[valueEnd] != '\n')
            valueEnd++;

        string valueStr = json.Substring(valueStart, valueEnd - valueStart).Trim();
        
        if (float.TryParse(valueStr, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float result))
        {
            return result;
        }

        return 0.0f;
    }
    catch (Exception e)
    {
        Debug.LogError($"[PythonBridge] ❌ Erreur extraction float '{key}' : {e.Message}");
        return 0.0f;
    }
}
```

### 2.5 - Sauvegarder

1. **Sauvegarder** le fichier (Ctrl+S)
2. Retourner dans Unity
3. Attendre la compilation
4. Vérifier qu'il n'y a **pas d'erreurs** dans la Console

---

## 🎯 Étape 3 : Configurer Unity Inspector

### 3.1 - Sélectionner PythonBridge

1. Dans Unity **Hierarchy** window (à gauche)
2. Cliquer sur le GameObject **PythonBridge**
3. Regarder l'**Inspector** window (à droite)

### 3.2 - Ajouter VRMBlendshapeController

**Option A - Sur le même GameObject (recommandé) :**

1. Avec **PythonBridge** sélectionné
2. Dans l'Inspector, cliquer **Add Component** (en bas)
3. Taper `VRMBlendshapeController`
4. Cliquer sur le script pour l'ajouter

**Option B - GameObject séparé :**

1. Dans Hierarchy, clic droit → **Create Empty**
2. Nommer : `BlendshapeController`
3. Add Component → `VRMBlendshapeController`

### 3.3 - Assigner les références

**Dans VRMBlendshapeController :**
- Champ `VRM Instance` : **Laisser vide** (auto-détection)  
  *(Ou glisser-déposer l'avatar VRM si déjà chargé)*

**Dans PythonBridge :**
1. Trouver le champ **Blendshape Controller**
2. **Glisser-déposer** le GameObject qui a VRMBlendshapeController
3. Vérifier que le champ n'affiche **pas "None"**

### 3.4 - Vérifier VRMLoader (déjà configuré normalement)

Dans PythonBridge, vérifier que :
- Champ `Vrm Loader` : référence au GameObject avec VRMLoader

**Si "None" :**
- Glisser-déposer le GameObject qui a VRMLoader attaché

---

## ✅ Étape 4 : Tester dans Unity

### 4.1 - Charger un modèle VRM

1. Cliquer **Play** ▶️ en haut de Unity
2. Attendre que la console affiche : `[PythonBridge] Serveur démarré`
3. Dans Python, cliquer **"Connect to Unity"**
4. Cliquer **"Load VRM Model"**
5. Sélectionner `assets/Mura Mura - Model.vrm`
6. Vérifier que l'avatar s'affiche dans Unity **Game window**

### 4.2 - Tester les expressions

**Méthode 1 - Via Python (recommandé) :**
1. Dans l'interface Python, aller dans l'onglet **"Expressions"**
2. Bouger le slider **"Joy"** (😊)
3. Observer l'avatar dans Unity → **Il devrait sourire !**
4. Tester les autres sliders (Angry, Sorrow, etc.)
5. Cliquer **"Reset All Expressions"** → avatar revient à neutre

**Méthode 2 - Test manuel Unity :**
1. Dans Unity, **arrêter Play** (⏹️)
2. Sélectionner le GameObject avec VRMBlendshapeController
3. Dans Inspector, **clic droit** sur le script → **Test Joy Expression**
4. Cliquer Play ▶️
5. L'avatar devrait sourire directement

### 4.3 - Vérifier les logs Unity

Dans Unity **Console**, tu devrais voir :
```
[VRMBlendshape] 🎭 VRMBlendshapeController démarré
[VRMBlendshape] ✅ VRMBlendShapeProxy initialisé pour Mura Mura - Model(Clone)
[VRMBlendshape] 📋 Expressions disponibles :
  - joy (Preset: Joy)
  - angry (Preset: Angry)
  - sorrow (Preset: Sorrow)
  ...
[PythonBridge] 😊 Commande : Changer l'expression
[PythonBridge] 🎭 Expression : joy = 0.80
[VRMBlendshape] ✅ Expression 'joy' appliquée à 0.80
```

---

## 🐛 Dépannage

### Problème 1 : "VRMBlendshapeController non assigné !"

**Cause :** Référence non configurée dans PythonBridge

**Solution :**
1. Arrêter Play (⏹️)
2. Sélectionner PythonBridge dans Hierarchy
3. Inspector → Vérifier champ **Blendshape Controller**
4. Doit pointer vers un GameObject (pas "None")
5. Si "None", glisser-déposer le bon GameObject

### Problème 2 : Avatar ne réagit pas

**Cause 1 :** VRM Instance non détecté

**Solution :**
- Vérifier logs Unity : `[VRMBlendshape] VRM détecté automatiquement`
- Si erreur, assigner manuellement dans Inspector

**Cause 2 :** Modèle VRM ne supporte pas ces expressions

**Solution :**
- Vérifier logs : `[VRMBlendshape] 📋 Expressions disponibles :`
- Si la liste est vide, le modèle VRM ne contient pas de blendshapes

### Problème 3 : Erreurs de compilation

**Erreur :** `VRM does not exist in the namespace`

**Solution :**
- Vérifier que UniVRM est bien installé
- File → Build Settings → Player Settings → Scripting Define Symbols → doit contenir `VRM`

**Erreur :** `SetExpression does not exist`

**Solution :**
- Vérifier que VRMBlendshapeController.cs compile sans erreurs
- Vérifier que le code a été copié intégralement

### Problème 4 : Sliders Python ne font rien

**Cause :** Unity pas connecté

**Solution :**
1. Vérifier status "Connected" dans interface Python
2. Reconnecter avec bouton "Connect to Unity"
3. Vérifier que Unity est en mode Play ▶️

---

## 📝 Checklist finale

Avant de dire "C'est bon !" :

- [ ] VRMBlendshapeController.cs créé et compile sans erreurs
- [ ] PythonBridge.cs modifié avec nouvelles commandes
- [ ] ExtractStringValue() et ExtractFloatValue() ajoutées
- [ ] Référence blendshapeController assignée dans Unity Inspector
- [ ] Avatar VRM chargé et visible dans Unity
- [ ] Slider "Joy" dans Python fait sourire l'avatar
- [ ] Les 5 expressions fonctionnent (joy, angry, sorrow, surprised, fun)
- [ ] Bouton "Reset All" fonctionne
- [ ] Logs Unity montrent les commandes reçues
- [ ] Aucune erreur dans Console Unity

---

## 🎉 Succès !

Si tout fonctionne, tu as maintenant :
- ✅ Un système d'expressions faciales complet
- ✅ 5 émotions contrôlables via Python
- ✅ Interface utilisateur intuitive avec sliders
- ✅ Communication IPC robuste
- ✅ Thread-safety Unity respecté

**Prochaine étape :** Session 7 - Animations automatiques ! 🎬

---

**Besoin d'aide ?** Consulte `docs/sessions/session_6_expressions/BLENDSHAPES_GUIDE.md` pour plus de détails techniques.
