// ============================================================
// VERSION 1.6 - SURPRISED FIX - MODIFIÉ 2025-10-19 16:45
// ============================================================
using UnityEngine;
using System;
using System.Collections.Generic;
using VRM;

/// <summary>
/// Contrôleur des blendshapes VRM pour gérer les expressions faciales
/// Thread-safe avec Queue<Action> pour Unity main thread
/// Version 1.3 - BlendShapePreset au lieu de CreateUnknown
/// </summary>
public class VRMBlendshapeController : MonoBehaviour
{
    [Header("Configuration")]
    [Tooltip("Référence au GameObject VRM chargé (auto-détecté si null)")]
    public GameObject vrmInstance;

    // Proxy UniVRM pour contrôler les blendshapes
    private VRMBlendShapeProxy blendShapeProxy;

    // Queue d'actions pour thread-safety (comme VRMLoader)
    private Queue<Action> mainThreadActions = new Queue<Action>();

    // Flag d'initialisation
    private bool isInitialized = false;

    /// <summary>
    /// Initialisation au démarrage
    /// </summary>
    void Start()
    {
        Debug.Log("[VRMBlendshape] 🎭 VRMBlendshapeController démarré (VERSION 1.6 - SURPRISED FIX)");

        if (vrmInstance != null)
        {
            InitializeBlendShapeProxy();
        }
        else
        {
            Debug.Log("[VRMBlendshape] ⏳ VRM instance non assignée, détection automatique au premier usage");
        }
    }

    /// <summary>
    /// Initialise le VRMBlendShapeProxy depuis le modèle VRM
    /// </summary>
    void InitializeBlendShapeProxy()
    {
        if (vrmInstance == null)
        {
            // Tenter de trouver automatiquement le VRM dans la scène
            vrmInstance = GameObject.Find("Mura Mura - Model(Clone)");
            if (vrmInstance == null)
            {
                // Chercher n'importe quel GameObject avec VRMBlendShapeProxy
                VRMBlendShapeProxy[] proxies = FindObjectsOfType<VRMBlendShapeProxy>();
                if (proxies.Length > 0)
                {
                    blendShapeProxy = proxies[0];
                    vrmInstance = blendShapeProxy.gameObject;
                    Debug.Log($"[VRMBlendshape] ✅ VRM détecté automatiquement : {vrmInstance.name}");
                }
                else
                {
                    Debug.LogError("[VRMBlendshape] ❌ Aucun VRM trouvé dans la scène !");
                    return;
                }
            }
        }

        // Récupérer le component VRMBlendShapeProxy
        blendShapeProxy = vrmInstance.GetComponent<VRMBlendShapeProxy>();

        if (blendShapeProxy == null)
        {
            Debug.LogError($"[VRMBlendshape] ❌ VRMBlendShapeProxy introuvable sur {vrmInstance.name} !");
            return;
        }

        Debug.Log($"[VRMBlendshape] ✅ VRMBlendShapeProxy initialisé pour {vrmInstance.name}");
        isInitialized = true;

        // Lister les expressions disponibles
        ListAvailableExpressions();
    }

    /// <summary>
    /// Liste toutes les expressions disponibles dans le modèle VRM (debug)
    /// </summary>
    void ListAvailableExpressions()
    {
        if (blendShapeProxy != null && blendShapeProxy.BlendShapeAvatar != null)
        {
            Debug.Log("[VRMBlendshape] 📋 Expressions disponibles :");
            foreach (var clip in blendShapeProxy.BlendShapeAvatar.Clips)
            {
                Debug.Log($"  - {clip.BlendShapeName} (Preset: {clip.Preset})");
            }
        }
    }

    /// <summary>
    /// Définit une expression faciale (thread-safe)
    /// Appelé depuis le thread réseau IPC
    /// </summary>
    /// <param name="expressionName">Nom de l'expression (ex: "joy", "angry")</param>
    /// <param name="value">Intensité de 0.0 à 1.0</param>
    public void SetExpression(string expressionName, float value)
    {
        Debug.Log($"[VRMBlendshape] 📨 Demande SetExpression : {expressionName} = {value:F2}");

        lock (mainThreadActions)
        {
            mainThreadActions.Enqueue(() => SetExpressionInternal(expressionName, value));
        }
    }

    /// <summary>
    /// Exécute réellement le changement d'expression (main thread Unity)
    /// </summary>
    private void SetExpressionInternal(string expressionName, float value)
    {
        // Vérifier initialisation
        if (!isInitialized)
        {
            Debug.LogWarning("[VRMBlendshape] ⚠️ Tentative d'initialisation...");
            InitializeBlendShapeProxy();
            if (!isInitialized)
            {
                Debug.LogError("[VRMBlendshape] ❌ Impossible de définir l'expression : non initialisé");
                return;
            }
        }

        if (blendShapeProxy == null)
        {
            Debug.LogError("[VRMBlendshape] ❌ blendShapeProxy est null !");
            return;
        }

        try
        {
            // Clamper la valeur entre 0 et 1
            value = Mathf.Clamp01(value);

            // Essayer d'abord avec le preset si disponible
            BlendShapeKey key;
            BlendShapePreset preset = BlendShapePreset.Unknown;

            // Mapper les noms vers les presets VRM standards
            switch (expressionName.ToLower())
            {
                case "joy": preset = BlendShapePreset.Joy; break;
                case "angry": preset = BlendShapePreset.Angry; break;
                case "sorrow": preset = BlendShapePreset.Sorrow; break;
                case "fun": preset = BlendShapePreset.Fun; break;
                case "surprised": preset = BlendShapePreset.Unknown; break; // Pas de preset standard
                default: preset = BlendShapePreset.Unknown; break;
            }

            // Créer la clé appropriée
            if (preset != BlendShapePreset.Unknown)
            {
                key = BlendShapeKey.CreateFromPreset(preset);
                Debug.Log($"[VRMBlendshape] 🔑 Utilisation du preset : {preset}");
            }
            else
            {
                // Pour les expressions sans preset (Surprised), essayer avec le nom capitalisé
                string capitalizedName = char.ToUpper(expressionName[0]) + expressionName.Substring(1).ToLower();
                key = BlendShapeKey.CreateUnknown(capitalizedName);
                Debug.Log($"[VRMBlendshape] 🔑 Utilisation de Unknown (capitalisé) : '{capitalizedName}'");
            }

            // Appliquer la valeur
            blendShapeProxy.ImmediatelySetValue(key, value);

            // Vérifier si la valeur a bien été définie
            float actualValue = blendShapeProxy.GetValue(key);
            Debug.Log($"[VRMBlendshape] 🔍 Valeur stockée après ImmediatelySetValue : {actualValue:F2}");

            // Si la valeur est 0 alors qu'on voulait mettre autre chose, essayer avec le nom capitalisé
            if (actualValue == 0.0f && value > 0.0f && preset != BlendShapePreset.Unknown)
            {
                Debug.LogWarning($"[VRMBlendshape] ⚠️ Le preset {preset} semble ne pas exister, tentative avec le nom capitalisé...");

                // Essayer avec la première lettre en majuscule
                string capitalizedName = char.ToUpper(expressionName[0]) + expressionName.Substring(1).ToLower();
                key = BlendShapeKey.CreateUnknown(capitalizedName);
                blendShapeProxy.ImmediatelySetValue(key, value);
                actualValue = blendShapeProxy.GetValue(key);

                Debug.Log($"[VRMBlendshape] 🔍 Nouvelle tentative avec '{capitalizedName}' : {actualValue:F2}");
            }

            // IMPORTANT : Apply() rend le changement visible sur le mesh !
            blendShapeProxy.Apply();

            Debug.Log($"[VRMBlendshape] ✅ Expression '{expressionName}' (preset: {preset}) appliquée à {value:F2}");
        }
        catch (Exception e)
        {
            Debug.LogError($"[VRMBlendshape] ❌ Erreur lors de l'application de '{expressionName}' : {e.Message}");
        }
    }

    /// <summary>
    /// Réinitialise toutes les expressions à neutre (thread-safe)
    /// </summary>
    public void ResetExpressions()
    {
        Debug.Log("[VRMBlendshape] 🔄 Demande ResetExpressions");

        lock (mainThreadActions)
        {
            mainThreadActions.Enqueue(() => ResetExpressionsInternal());
        }
    }

    /// <summary>
    /// Exécute le reset des expressions (main thread Unity)
    /// </summary>
    private void ResetExpressionsInternal()
    {
        if (!isInitialized || blendShapeProxy == null)
        {
            Debug.LogError("[VRMBlendshape] ❌ Impossible de reset : non initialisé");
            return;
        }

        try
        {
            // Définir toutes les expressions principales à 0
            string[] mainExpressions = { "joy", "angry", "sorrow", "fun", "surprised" };

            foreach (string expr in mainExpressions)
            {
                BlendShapeKey key = BlendShapeKey.CreateUnknown(expr);
                blendShapeProxy.ImmediatelySetValue(key, 0.0f);
            }

            // Optionnel : définir Neutral à 1.0
            BlendShapeKey neutralKey = BlendShapeKey.CreateUnknown("neutral");
            blendShapeProxy.ImmediatelySetValue(neutralKey, 1.0f);

            // IMPORTANT : Apply() rend le changement visible !
            blendShapeProxy.Apply();

            Debug.Log("[VRMBlendshape] ✅ Toutes les expressions réinitialisées");
        }
        catch (Exception e)
        {
            Debug.LogError($"[VRMBlendshape] ❌ Erreur lors du reset : {e.Message}");
        }
    }

    /// <summary>
    /// Update est appelé à chaque frame sur le main thread Unity
    /// On exécute ici toutes les actions en queue
    /// </summary>
    void Update()
    {
        // Exécuter toutes les actions en attente
        lock (mainThreadActions)
        {
            while (mainThreadActions.Count > 0)
            {
                try
                {
                    mainThreadActions.Dequeue()?.Invoke();
                }
                catch (Exception e)
                {
                    Debug.LogError($"[VRMBlendshape] ❌ Erreur dans l'exécution d'une action : {e.Message}");
                }
            }
        }
    }

    /// <summary>
    /// LateUpdate est appelé après Update, idéal pour appliquer les blendshapes
    /// Cela garantit que Apply() est appelé après tous les changements de la frame
    /// </summary>
    void LateUpdate()
    {
        // Forcer Apply() à chaque frame pour garantir le rendu visuel
        if (blendShapeProxy != null)
        {
            blendShapeProxy.Apply();
        }
    }

    /// <summary>
    /// Méthode publique pour assigner le VRM manuellement (appelée par VRMLoader par exemple)
    /// </summary>
    public void SetVRMInstance(GameObject vrm)
    {
        Debug.Log($"[VRMBlendshape] 📌 VRM instance assignée : {vrm.name}");
        vrmInstance = vrm;
        InitializeBlendShapeProxy();
    }

    // === Méthodes de test (optionnel) ===

    /// <summary>
    /// Test manuel dans Unity Inspector (clic droit sur le script → Test Joy)
    /// </summary>
    [ContextMenu("Test Joy Expression")]
    void TestJoyExpression()
    {
        SetExpression("joy", 1.0f);
    }

    [ContextMenu("Test Angry Expression")]
    void TestAngryExpression()
    {
        SetExpression("angry", 1.0f);
    }

    [ContextMenu("Test Reset")]
    void TestReset()
    {
        ResetExpressions();
    }
}
