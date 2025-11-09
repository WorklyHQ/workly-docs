# 🎭 Chargement du Modèle VRM dans Unity

On va maintenant charger ton avatar `Mura Mura - Model.vrm` dans Unity !

---

## 🎯 Étapes

### Étape 1 : Importer le Modèle dans Unity

1. **Dans Unity**, panneau **Project** (en bas)
2. **Clique droit** sur **Assets**
3. **Create > Folder** → Nomme-le `Models`
4. **Ouvre le dossier Models** (double-clic)

Maintenant, on va copier ton fichier VRM :

5. **Ouvre l'Explorateur Windows** et va dans :
   ```
   C:\Dev\desktop-mate\assets\
   ```
6. **Copie** le fichier `Mura Mura - Model.vrm`
7. **Retourne dans Unity**, dans le dossier **Assets/Models**
8. **Colle** le fichier (Ctrl+V) ou glisse-dépose-le

Unity va **importer le modèle** (ça prend quelques secondes).

---

### Étape 2 : Créer le Script VRMLoader.cs

On va créer un script pour charger dynamiquement les modèles VRM :

1. **Dans Unity**, panneau **Project**
2. Va dans **Assets/Scripts/** (pas dans IPC cette fois)
3. **Clique droit** → **Create > C# Script**
4. Nomme-le : `VRMLoader`
5. **Double-clique** pour l'ouvrir

Copie ce code dans le fichier :

```csharp
using System;
using System.IO;
using UnityEngine;

/// <summary>
/// VRMLoader - Charge et gère les modèles VRM (Version simplifiée - Import Assets uniquement)
/// </summary>
public class VRMLoader : MonoBehaviour
{
    [Header("VRM Model")]
    [Tooltip("Modèle VRM actuellement chargé (glisse depuis Assets/Models)")]
    public GameObject vrmPrefab;
    
    [Tooltip("Instance du modèle actuellement affichée")]
    public GameObject currentModel;
    
    [Tooltip("Position de spawn du modèle")]
    public Vector3 spawnPosition = new Vector3(0, 0, 0);
    
    private string lastLoadedPath = "";
    
    /// <summary>
    /// Charge le modèle VRM depuis le prefab assigné dans l'Inspector
    /// </summary>
    public void LoadVRMModel()
    {
        try
        {
            Debug.Log($"[VRMLoader] 📂 Tentative de chargement du modèle");
            
            // Vérifier qu'un prefab est assigné
            if (vrmPrefab == null)
            {
                Debug.LogError($"[VRMLoader] ❌ Aucun prefab VRM assigné ! Glisse un modèle VRM depuis Assets/Models dans l'Inspector.");
                return;
            }
            
            // Détruire le modèle précédent s'il existe
            if (currentModel != null)
            {
                Debug.Log("[VRMLoader] 🗑️ Suppression du modèle précédent");
                Destroy(currentModel);
                currentModel = null;
            }
            
            Debug.Log("[VRMLoader] ⏳ Instanciation du modèle VRM...");
            
            // Instancier le prefab
            currentModel = Instantiate(vrmPrefab, spawnPosition, Quaternion.identity);
            currentModel.transform.localScale = Vector3.one;
            
            Debug.Log($"[VRMLoader] ✅ Modèle chargé avec succès : {currentModel.name}");
            Debug.Log($"[VRMLoader] 📍 Position : {currentModel.transform.position}");
            
            // Logger les informations du modèle
            LogModelInfo();
        }
        catch (Exception e)
        {
            Debug.LogError($"[VRMLoader] ❌ Erreur lors du chargement : {e.Message}");
            Debug.LogError($"[VRMLoader] Stack trace : {e.StackTrace}");
        }
    }
    
    /// <summary>
    /// Charge un modèle VRM depuis un chemin de fichier (pour Python)
    /// </summary>
    public void LoadVRMFromPath(string filePath)
    {
        Debug.LogWarning($"[VRMLoader] ⚠️ Le chargement depuis un fichier n'est pas encore implémenté.");
        Debug.LogWarning($"[VRMLoader] Pour l'instant, utilise LoadVRMModel() avec un prefab assigné dans l'Inspector.");
        Debug.LogWarning($"[VRMLoader] Chemin demandé : {filePath}");
        
        // Pour l'instant, on charge le modèle par défaut
        LoadVRMModel();
    }
    
    /// <summary>
    /// Charge le modèle par défaut depuis les Assets
    /// </summary>
    public void LoadDefaultModel()
    {
        // Chercher le modèle dans Assets/Models
        string projectPath = Application.dataPath;
        string modelPath = Path.Combine(projectPath, "Models", "Mura Mura - Model.vrm");
        
        Debug.Log($"[VRMLoader] 🎭 Chargement du modèle par défaut : {modelPath}");
        LoadVRMFromPath(modelPath);
    }
    
    /// <summary>
    /// Affiche les informations du modèle chargé
    /// </summary>
    private void LogModelInfo()
    {
        if (currentModel == null) return;
        
        Debug.Log($"[VRMLoader] ℹ️ Informations du modèle :");
        Debug.Log($"  - Nom : {currentModel.name}");
        Debug.Log($"  - Position : {currentModel.transform.position}");
        Debug.Log($"  - Échelle : {currentModel.transform.localScale}");
        
        // Chercher le composant VRM
        var vrmMeta = currentModel.GetComponent<VRMMeta>();
        if (vrmMeta != null)
        {
            Debug.Log($"  - VRM Meta trouvé !");
        }
        
        // Lister les blendshapes disponibles
        var skinnedMeshRenderers = currentModel.GetComponentsInChildren<SkinnedMeshRenderer>();
        Debug.Log($"  - Nombre de SkinnedMeshRenderer : {skinnedMeshRenderers.Length}");
        
        foreach (var smr in skinnedMeshRenderers)
        {
            if (smr.sharedMesh != null && smr.sharedMesh.blendShapeCount > 0)
            {
                Debug.Log($"    • {smr.name} : {smr.sharedMesh.blendShapeCount} blendshapes");
            }
        }
    }
    
    /// <summary>
    /// Supprime le modèle actuel
    /// </summary>
    public void UnloadModel()
    {
        if (currentModel != null)
        {
            Debug.Log("[VRMLoader] 🗑️ Suppression du modèle");
            Destroy(currentModel);
            currentModel = null;
            lastLoadedPath = "";
        }
    }
    
    /// <summary>
    /// Retourne le chemin du dernier modèle chargé
    /// </summary>
    public string GetLastLoadedPath()
    {
        return lastLoadedPath;
    }
}
```

6. **Sauvegarde** (Ctrl+S)
7. **Retourne dans Unity** et attends la compilation

---

### Étape 3 : Attacher le Script au GameObject PythonBridge

1. **Dans la Hierarchy**, sélectionne **PythonBridge**
2. **Dans l'Inspector**, clique sur **Add Component**
3. Tape `VRMLoader` et sélectionne le script
4. Tu devrais maintenant voir "VRM Loader (Script)" dans l'Inspector

---

### Étape 4 : Modifier PythonBridge pour Utiliser VRMLoader

On va maintenant connecter le VRMLoader au PythonBridge.

**Dis-moi quand tu as terminé les étapes 1-3**, et je te donnerai le code pour modifier `PythonBridge.cs` ! 🚀

---

**Commence par les étapes 1-3 et dis-moi quand c'est fait !** 😊
