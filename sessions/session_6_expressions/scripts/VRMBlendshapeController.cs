using UnityEngine;
using System;
using System.Collections.Generic;
using VRM;

/// <summary>
/// 🎭 VRMBlendshapeController - Contrôleur des expressions faciales VRM
/// 
/// Ce script permet de contrôler les blendshapes (expressions faciales) d'un modèle VRM
/// depuis Python via IPC. Il utilise le pattern Queue + Update() pour garantir la
/// thread-safety requise par Unity.
/// 
/// UTILISATION :
/// 1. Attacher ce script au GameObject PythonBridge (ou tout GameObject)
/// 2. Assigner le modèle VRM chargé dans le champ "VRM Instance" (ou laisser auto-détection)
/// 3. Depuis Python, appeler unity_bridge.set_expression("joy", 0.8)
/// 4. L'avatar affichera l'expression correspondante
/// 
/// EXPRESSIONS SUPPORTÉES :
/// - joy (joyeux)
/// - angry (colère)
/// - sorrow (triste)
/// - fun (amusé)
/// - surprised (surpris)
/// - neutral (neutre)
/// - blink, blink_l, blink_r (clignements)
/// - a, i, u, e, o (formes bouche pour lip-sync futur)
/// </summary>
public class VRMBlendshapeController : MonoBehaviour
{
    // ==================== CONFIGURATION ====================

    [Header("Configuration")]
    [Tooltip("Référence au GameObject VRM chargé (auto-détecté si null)")]
    public GameObject vrmInstance;

    // ==================== VARIABLES PRIVÉES ====================

    // Proxy UniVRM pour contrôler les blendshapes
    private VRMBlendShapeProxy blendShapeProxy;

    // Queue d'actions pour thread-safety
    // Explication : Unity nécessite que les opérations GameObject soient sur le main thread
    // Le serveur IPC tourne sur un thread secondaire, donc on utilise une Queue
    private Queue<Action> mainThreadActions = new Queue<Action>();

    // Flag d'initialisation
    private bool isInitialized = false;

    // ==================== MÉTHODES UNITY ====================

    /// <summary>
    /// Appelé au démarrage du script
    /// </summary>
    void Start()
    {
        Debug.Log("[VRMBlendshape] 🎭 VRMBlendshapeController démarré");

        if (vrmInstance != null)
        {
            // Si un VRM est déjà assigné, initialiser immédiatement
            InitializeBlendShapeProxy();
        }
        else
        {
            Debug.Log("[VRMBlendshape] ⏳ VRM instance non assignée, détection automatique au premier usage");
        }
    }

    /// <summary>
    /// Appelé à chaque frame par Unity (main thread)
    /// On exécute ici toutes les actions en queue
    /// </summary>
    void Update()
    {
        // Lock pour éviter les race conditions
        lock (mainThreadActions)
        {
            // Exécuter toutes les actions en attente
            while (mainThreadActions.Count > 0)
            {
                try
                {
                    // Dépiler et exécuter l'action
                    mainThreadActions.Dequeue()?.Invoke();
                }
                catch (Exception e)
                {
                    Debug.LogError($"[VRMBlendshape] ❌ Erreur dans l'exécution d'une action : {e.Message}");
                }
            }
        }
    }

    // ==================== INITIALISATION ====================

    /// <summary>
    /// Initialise le VRMBlendShapeProxy depuis le modèle VRM
    /// Cette méthode cherche le component VRMBlendShapeProxy sur le GameObject VRM
    /// </summary>
    void InitializeBlendShapeProxy()
    {
        // Si aucun VRM assigné, tenter détection automatique
        if (vrmInstance == null)
        {
            // Méthode 1 : Chercher par nom (modèle "Mura Mura")
            vrmInstance = GameObject.Find("Mura Mura - Model(Clone)");

            if (vrmInstance == null)
            {
                // Méthode 2 : Chercher n'importe quel GameObject avec VRMBlendShapeProxy
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
        // Ce component est fourni par UniVRM et gère tous les blendshapes
        blendShapeProxy = vrmInstance.GetComponent<VRMBlendShapeProxy>();

        if (blendShapeProxy == null)
        {
            Debug.LogError($"[VRMBlendshape] ❌ VRMBlendShapeProxy introuvable sur {vrmInstance.name} !");
            return;
        }

        Debug.Log($"[VRMBlendshape] ✅ VRMBlendShapeProxy initialisé pour {vrmInstance.name}");
        isInitialized = true;

        // Lister les expressions disponibles (debug)
        ListAvailableExpressions();
    }

    /// <summary>
    /// Liste toutes les expressions disponibles dans le modèle VRM (debug)
    /// Utile pour voir quels blendshapes sont supportés par le modèle
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

    // ==================== API PUBLIQUE (Thread-Safe) ====================

    /// <summary>
    /// Définit une expression faciale (thread-safe)
    /// Cette méthode peut être appelée depuis n'importe quel thread
    /// </summary>
    /// <param name="expressionName">Nom de l'expression (ex: "joy", "angry", "sorrow")</param>
    /// <param name="value">Intensité de 0.0 (0%) à 1.0 (100%)</param>
    public void SetExpression(string expressionName, float value)
    {
        Debug.Log($"[VRMBlendshape] 📨 Demande SetExpression : {expressionName} = {value:F2}");

        // Ajouter l'action à la queue pour exécution sur le main thread
        lock (mainThreadActions)
        {
            mainThreadActions.Enqueue(() => SetExpressionInternal(expressionName, value));
        }
    }

    /// <summary>
    /// Réinitialise toutes les expressions à neutre (thread-safe)
    /// Remet toutes les expressions principales à 0
    /// </summary>
    public void ResetExpressions()
    {
        Debug.Log("[VRMBlendshape] 🔄 Demande ResetExpressions");

        // Ajouter l'action à la queue
        lock (mainThreadActions)
        {
            mainThreadActions.Enqueue(() => ResetExpressionsInternal());
        }
    }

    /// <summary>
    /// Assigne manuellement un VRM (utile si chargé dynamiquement)
    /// Peut être appelé par VRMLoader après chargement d'un modèle
    /// </summary>
    public void SetVRMInstance(GameObject vrm)
    {
        Debug.Log($"[VRMBlendshape] 📌 VRM instance assignée : {vrm.name}");
        vrmInstance = vrm;
        InitializeBlendShapeProxy();
    }

    // ==================== MÉTHODES INTERNES (Main Thread) ====================

    /// <summary>
    /// Exécute réellement le changement d'expression (main thread Unity)
    /// Cette méthode est privée et appelée uniquement via la Queue
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

            // Appliquer immédiatement le blendshape
            // Utiliser BlendShapeKey.CreateUnknown (méthode recommandée UniVRM)
            BlendShapeKey key = BlendShapeKey.CreateUnknown(expressionName.ToLower());
            blendShapeProxy.ImmediatelySetValue(key, value);

            Debug.Log($"[VRMBlendshape] ✅ Expression '{expressionName}' appliquée à {value:F2}");
        }
        catch (Exception e)
        {
            Debug.LogError($"[VRMBlendshape] ❌ Erreur lors de l'application de '{expressionName}' : {e.Message}");
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
            // Liste des expressions principales à reset
            string[] mainExpressions = { "joy", "angry", "sorrow", "fun", "surprised" };

            // Définir chaque expression à 0
            foreach (string expr in mainExpressions)
            {
                BlendShapeKey key = BlendShapeKey.CreateUnknown(expr);
                blendShapeProxy.ImmediatelySetValue(key, 0.0f);
            }

            // Optionnel : définir Neutral à 1.0
            BlendShapeKey neutralKey = BlendShapeKey.CreateUnknown("neutral");
            blendShapeProxy.ImmediatelySetValue(neutralKey, 1.0f);

            Debug.Log("[VRMBlendshape] ✅ Toutes les expressions réinitialisées");
        }
        catch (Exception e)
        {
            Debug.LogError($"[VRMBlendshape] ❌ Erreur lors du reset : {e.Message}");
        }
    }

    // ==================== MÉTHODES DE TEST (Optionnel) ====================

    /// <summary>
    /// Test manuel dans Unity Inspector
    /// Clic droit sur le script dans l'Inspector → "Test Joy Expression"
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

    [ContextMenu("Test Sorrow Expression")]
    void TestSorrowExpression()
    {
        SetExpression("sorrow", 1.0f);
    }

    [ContextMenu("Test Reset")]
    void TestReset()
    {
        ResetExpressions();
    }
}

/*
 * ==================== NOTES TECHNIQUES ====================
 * 
 * 1. THREAD SAFETY
 * Unity nécessite que toutes les opérations GameObject soient sur le main thread.
 * Le serveur IPC (PythonBridge) tourne sur un thread secondaire.
 * Solution : Queue<Action> + Update() pour exécuter sur main thread.
 * 
 * 2. BLENDSHAPE NAMING
 * UniVRM accepte plusieurs formats :
 * - Lowercase string : "joy", "angry", "sorrow"
 * - Preset enum : BlendShapePreset.Joy
 * - BlendShapeKey : new BlendShapeKey("joy")
 * On utilise les strings lowercase pour simplicité Python ↔ Unity.
 * 
 * 3. VALEURS
 * Les blendshapes VRM utilisent des valeurs normalisées 0.0 à 1.0 :
 * - 0.0 = expression à 0% (aucun effet)
 * - 0.5 = expression à 50% (modéré)
 * - 1.0 = expression à 100% (maximum)
 * 
 * 4. EXPRESSIONS VRM STANDARD
 * joy      - Joyeux (sourire)
 * angry    - En colère (sourcils froncés)
 * sorrow   - Triste (yeux baissés)
 * fun      - Amusé (sourire éclatant)
 * surprised - Surpris (yeux/bouche ouverts)
 * neutral  - Neutre (par défaut)
 * blink    - Clignement des deux yeux
 * blink_l  - Clignement œil gauche
 * blink_r  - Clignement œil droit
 * a, i, u, e, o - Formes bouche (phonèmes)
 * 
 * 5. AUTO-DÉTECTION VRM
 * Si vrmInstance n'est pas assigné manuellement :
 * 1. Cherche "Mura Mura - Model(Clone)" par nom
 * 2. Sinon cherche n'importe quel VRMBlendShapeProxy dans la scène
 * 3. Sinon erreur (aucun VRM trouvé)
 * 
 * 6. INTÉGRATION AVEC VRMLoader
 * Après chargement d'un VRM, VRMLoader peut appeler :
 * blendshapeController.SetVRMInstance(loadedVRM);
 * 
 * ==================== EXEMPLE UTILISATION ====================
 * 
 * Python :
 * ```python
 * # Définir une expression
 * unity_bridge.set_expression("joy", 0.8)  # Sourire à 80%
 * 
 * # Reset toutes les expressions
 * unity_bridge.reset_expressions()
 * ```
 * 
 * C# (Unity) :
 * ```csharp
 * // Depuis PythonBridge.cs
 * blendshapeController.SetExpression("joy", 0.8f);
 * blendshapeController.ResetExpressions();
 * ```
 * 
 * ==================== DÉPANNAGE ====================
 * 
 * Problème : Avatar ne réagit pas
 * → Vérifier que vrmInstance est assigné dans Inspector
 * → Vérifier logs Unity pour erreurs d'initialisation
 * → Vérifier que le modèle VRM supporte ces blendshapes
 * 
 * Problème : Erreur "EnsureRunningOnMainThread"
 * → Vérifier que SetExpressionInternal() est bien privée
 * → Vérifier que SetExpression() utilise bien la Queue
 * 
 * Problème : Expression ne correspond pas
 * → Vérifier les noms disponibles avec ListAvailableExpressions()
 * → Essayer différentes variantes (joy, Joy, Preset.Joy)
 */
