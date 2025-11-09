using System;
using System.IO;
using System.Collections.Generic;
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
    private Queue<Action> mainThreadActions = new Queue<Action>();

    /// <summary>
    /// Update - Exécute les actions sur le thread principal
    /// </summary>
    void Update()
    {
        // Exécuter toutes les actions en attente sur le thread principal
        lock (mainThreadActions)
        {
            while (mainThreadActions.Count > 0)
            {
                var action = mainThreadActions.Dequeue();
                action?.Invoke();
            }
        }
    }

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

            // Notifier le VRMBlendshapeController qu'un nouveau modèle est chargé
            VRMBlendshapeController blendshapeController = FindObjectOfType<VRMBlendshapeController>();
            if (blendshapeController != null)
            {
                blendshapeController.SetVRMInstance(currentModel);
                Debug.Log("[VRMLoader] 🎭 VRMBlendshapeController notifié du nouveau modèle");
            }
            else
            {
                Debug.LogWarning("[VRMLoader] ⚠️ VRMBlendshapeController introuvable");
            }

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
    /// IMPORTANT: Peut être appelé depuis n'importe quel thread
    /// </summary>
    public void LoadVRMFromPath(string filePath)
    {
        Debug.Log($"[VRMLoader] 📋 Demande de chargement reçue : {filePath}");

        // Enqueue l'action pour l'exécuter sur le thread principal
        lock (mainThreadActions)
        {
            mainThreadActions.Enqueue(() => {
                Debug.Log($"[VRMLoader] 🎭 Exécution du chargement sur le thread principal");
                LoadVRMModel();
            });
        }
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

        // Lister les SkinnedMeshRenderers
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
