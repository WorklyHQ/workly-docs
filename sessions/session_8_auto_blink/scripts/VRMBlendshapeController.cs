// ============================================================
// VERSION 2.0 - SMOOTH TRANSITIONS - MODIFIÉ 2025-10-20
// ============================================================
using UnityEngine;
using System;
using System.Collections.Generic;
using System.Linq;
using VRM;

/// <summary>
/// Contrôleur des blendshapes VRM pour gérer les expressions faciales
/// Thread-safe avec Queue<Action> pour Unity main thread
/// VERSION 2.0 - Transitions smooth avec Lerp
/// </summary>
public class VRMBlendshapeController : MonoBehaviour
{
    [Header("Configuration")]
    [Tooltip("Référence au GameObject VRM chargé (auto-détecté si null)")]
    public GameObject vrmInstance;

    [Header("Transition Settings")]
    [Tooltip("Vitesse de transition (unités/seconde). Plus élevé = plus rapide.")]
    [Range(0.1f, 10.0f)]
    public float transitionSpeed = 2.0f;

    // Proxy UniVRM pour contrôler les blendshapes
    private VRMBlendShapeProxy blendShapeProxy;

    // Queue d'actions pour thread-safety (comme VRMLoader)
    private Queue<Action> mainThreadActions = new Queue<Action>();

    // NOUVEAU : Dictionnaires pour les transitions smooth
    private Dictionary<BlendShapeKey, float> currentValues = new Dictionary<BlendShapeKey, float>();
    private Dictionary<BlendShapeKey, float> targetValues = new Dictionary<BlendShapeKey, float>();

    // Flag d'initialisation
    private bool isInitialized = false;

    /// <summary>
    /// Initialisation au démarrage
    /// </summary>
    void Start()
    {
        Debug.Log("[VRMBlendshape] 🎭 VRMBlendshapeController démarré (VERSION 2.0 - SMOOTH TRANSITIONS)");

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
    /// Définit la vitesse de transition (thread-safe)
    /// </summary>
    /// <param name="speed">Vitesse de 0.1 à 10.0</param>
    public void SetTransitionSpeed(float speed)
    {
        lock (mainThreadActions)
        {
            mainThreadActions.Enqueue(() => SetTransitionSpeedInternal(speed));
        }
    }

    /// <summary>
    /// Exécute le changement de vitesse de transition (main thread Unity)
    /// </summary>
    private void SetTransitionSpeedInternal(float speed)
    {
        transitionSpeed = Mathf.Clamp(speed, 0.1f, 10.0f);
        Debug.Log($"[VRMBlendshape] ⚡ Vitesse de transition définie à {transitionSpeed:F2}");
    }

    /// <summary>
    /// Obtient la BlendShapeKey appropriée pour une expression
    /// </summary>
    private BlendShapeKey GetBlendShapeKey(string expressionName)
    {
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
            case "blink": preset = BlendShapePreset.Blink; break;
            case "blink_l": preset = BlendShapePreset.Blink_L; break;
            case "blink_r": preset = BlendShapePreset.Blink_R; break;
            default: preset = BlendShapePreset.Unknown; break;
        }

        // Créer la clé appropriée
        if (preset != BlendShapePreset.Unknown)
        {
            key = BlendShapeKey.CreateFromPreset(preset);
        }
        else
        {
            // Pour les expressions sans preset (Surprised), utiliser le nom capitalisé
            string capitalizedName = char.ToUpper(expressionName[0]) + expressionName.Substring(1).ToLower();
            key = BlendShapeKey.CreateUnknown(capitalizedName);
        }

        return key;
    }

    /// <summary>
    /// Exécute réellement le changement d'expression (main thread Unity)
    /// VERSION 2.0 : Stocke la valeur CIBLE au lieu d'appliquer immédiatement
    /// </summary>
    private void SetExpressionInternal(string expressionName, float value)
    {
        // Vérifier initialisation
        if (!isInitialized || blendShapeProxy == null)
        {
            Debug.LogWarning("[VRMBlendshape] ⚠️ Tentative d'initialisation...");
            InitializeBlendShapeProxy();
            
            // Si toujours pas initialisé après tentative, abandonner
            if (!isInitialized || blendShapeProxy == null)
            {
                Debug.LogWarning("[VRMBlendshape] ⚠️ VRM pas encore chargé, commande ignorée");
                return;
            }
        }

        try
        {
            // Clamper la valeur entre 0 et 1
            value = Mathf.Clamp01(value);

            // Obtenir la clé BlendShape
            BlendShapeKey key = GetBlendShapeKey(expressionName);

            // NOUVEAU : Stocker la valeur CIBLE (pas appliquer directement)
            targetValues[key] = value;

            // Si c'est la première fois pour cette clé, initialiser currentValues
            if (!currentValues.ContainsKey(key))
            {
                currentValues[key] = 0.0f;
            }

            Debug.Log($"[VRMBlendshape] 🎯 Cible définie : {expressionName} → {value:F2} (actuel: {currentValues[key]:F2})");
        }
        catch (Exception e)
        {
            Debug.LogError($"[VRMBlendshape] ❌ Erreur lors de la définition de '{expressionName}' : {e.Message}");
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
    /// VERSION 2.0 : Met les cibles à 0 (transition smooth vers neutre)
    /// </summary>
    private void ResetExpressionsInternal()
    {
        if (!isInitialized || blendShapeProxy == null)
        {
            // Pas d'erreur si le modèle n'est pas chargé (normal après unload)
            Debug.Log("[VRMBlendshape] ℹ️ Reset ignoré : modèle non chargé");
            return;
        }

        try
        {
            // Définir toutes les expressions principales à 0 (cibles)
            string[] mainExpressions = { "joy", "angry", "sorrow", "fun", "surprised" };

            foreach (string expr in mainExpressions)
            {
                BlendShapeKey key = GetBlendShapeKey(expr);
                targetValues[key] = 0.0f;
                
                if (!currentValues.ContainsKey(key))
                {
                    currentValues[key] = 0.0f;
                }
            }

            Debug.Log("[VRMBlendshape] ✅ Toutes les expressions en cours de réinitialisation (smooth)");
        }
        catch (Exception e)
        {
            Debug.LogError($"[VRMBlendshape] ❌ Erreur lors du reset : {e.Message}");
        }
    }

    /// <summary>
    /// Update est appelé à chaque frame sur le main thread Unity
    /// VERSION 2.0 : Exécute les commandes IPC + Lerp vers les valeurs cibles
    /// </summary>
    void Update()
    {
        // 1. Exécuter toutes les actions IPC en attente
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

        // 2. NOUVEAU : Lerp vers les valeurs cibles
        if (isInitialized && blendShapeProxy != null)
        {
            foreach (var key in currentValues.Keys.ToList())
            {
                float current = currentValues[key];
                float target = targetValues.ContainsKey(key) ? targetValues[key] : 0.0f;

                // Si la différence est négligeable, snap directement
                if (Mathf.Abs(current - target) < 0.001f)
                {
                    currentValues[key] = target;
                }
                else
                {
                    // Lerp vers la cible
                    float newValue = Mathf.Lerp(current, target, Time.deltaTime * transitionSpeed);
                    currentValues[key] = newValue;
                }

                // Appliquer la valeur actuelle au blendshape
                blendShapeProxy.ImmediatelySetValue(key, currentValues[key]);
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

    /// <summary>
    /// Retourne le VRMBlendShapeProxy pour accès direct (utilisé par VRMAutoBlinkController)
    /// </summary>
    public VRMBlendShapeProxy GetBlendShapeProxy()
    {
        return blendShapeProxy;
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

    [ContextMenu("Test Transition Speed Fast (5.0)")]
    void TestFastTransition()
    {
        SetTransitionSpeed(5.0f);
    }

    [ContextMenu("Test Transition Speed Slow (0.5)")]
    void TestSlowTransition()
    {
        SetTransitionSpeed(0.5f);
    }
}
