using System.Collections;
using UnityEngine;
using VRM;

/// <summary>
/// Contrôle le clignement automatique des yeux de l'avatar VRM.
/// Utilise le système Lerp existant de VRMBlendshapeController pour des transitions smooth.
/// 
/// Version: 1.0
/// Date: 21 octobre 2025
/// Session: 8 - Clignement automatique
/// </summary>
public class VRMAutoBlinkController : MonoBehaviour
{
    [Header("Références")]
    [Tooltip("Référence au VRMBlendshapeController pour contrôler les expressions")]
    public VRMBlendshapeController blendshapeController;

    [Header("Paramètres de clignement")]
    [Tooltip("Active ou désactive le clignement automatique")]
    public bool isEnabled = false;

    [Tooltip("Intervalle minimum entre deux clignements (en secondes)")]
    [Range(1.0f, 5.0f)]
    public float minInterval = 2.0f;

    [Tooltip("Intervalle maximum entre deux clignements (en secondes)")]
    [Range(3.0f, 10.0f)]
    public float maxInterval = 5.0f;

    [Tooltip("Durée du clignement (yeux fermés) en secondes")]
    [Range(0.01f, 0.5f)]
    public float blinkDuration = 0.03f;

    [Header("Debug")]
    [Tooltip("Afficher les logs de debug")]
    public bool showDebugLogs = false;

    // Coroutine actuelle (pour pouvoir l'arrêter)
    private Coroutine blinkCoroutine;

    /// <summary>
    /// Initialisation au démarrage
    /// </summary>
    void Start()
    {
        // Trouver automatiquement le VRMBlendshapeController s'il n'est pas assigné
        if (blendshapeController == null)
        {
            blendshapeController = FindObjectOfType<VRMBlendshapeController>();
            
            if (blendshapeController == null)
            {
                Debug.LogError("[VRMAutoBlinkController] VRMBlendshapeController introuvable ! Le clignement automatique ne fonctionnera pas.");
                return;
            }
        }

        // Démarrer le clignement si activé par défaut
        if (isEnabled)
        {
            StartBlinking();
        }

        if (showDebugLogs)
        {
            Debug.Log("[VRMAutoBlinkController] Initialisé. Enabled: " + isEnabled);
        }
    }

    /// <summary>
    /// Active ou désactive le clignement automatique
    /// Appelé depuis PythonBridge via commande IPC
    /// </summary>
    /// <param name="enabled">True pour activer, False pour désactiver</param>
    public void SetAutoBlinkEnabled(bool enabled)
    {
        isEnabled = enabled;

        if (enabled)
        {
            StartBlinking();
            if (showDebugLogs)
            {
                Debug.Log("[VRMAutoBlinkController] Clignement automatique ACTIVÉ");
            }
        }
        else
        {
            StopBlinking();
            if (showDebugLogs)
            {
                Debug.Log("[VRMAutoBlinkController] Clignement automatique DÉSACTIVÉ");
            }
        }
    }

    /// <summary>
    /// Démarre la coroutine de clignement
    /// </summary>
    private void StartBlinking()
    {
        // Arrêter la coroutine précédente si elle existe
        if (blinkCoroutine != null)
        {
            StopCoroutine(blinkCoroutine);
        }

        // Démarrer une nouvelle coroutine
        blinkCoroutine = StartCoroutine(BlinkLoop());
    }

    /// <summary>
    /// Arrête la coroutine de clignement et ouvre les yeux
    /// </summary>
    private void StopBlinking()
    {
        // Arrêter la coroutine si elle existe
        if (blinkCoroutine != null)
        {
            StopCoroutine(blinkCoroutine);
            blinkCoroutine = null;
        }

        // Rouvrir les yeux (mettre Blink à 0)
        if (blendshapeController != null)
        {
            blendshapeController.SetExpression("Blink", 0.0f);
        }
    }

    /// <summary>
    /// Boucle principale du clignement automatique
    /// </summary>
    private IEnumerator BlinkLoop()
    {
        while (isEnabled)
        {
            // Attendre un intervalle aléatoire
            float waitTime = Random.Range(minInterval, maxInterval);
            
            if (showDebugLogs)
            {
                Debug.Log($"[VRMAutoBlinkController] Attente de {waitTime:F2}s avant prochain clignement");
            }

            yield return new WaitForSeconds(waitTime);

            // Effectuer un clignement
            Debug.Log("[VRMAutoBlinkController] 🚀 Lancement PerformBlink()");
            yield return StartCoroutine(PerformBlink());
            Debug.Log("[VRMAutoBlinkController] ✅ PerformBlink() terminé");
        }
    }

    /// <summary>
    /// Effectue un seul clignement (fermer puis ouvrir les yeux)
    /// Version ultra-naturelle : fermeture très rapide, pause minimale, ouverture douce
    /// </summary>
    private IEnumerator PerformBlink()
    {
        if (blendshapeController == null)
        {
            Debug.LogWarning("[VRMAutoBlinkController] ❌ BlendshapeController est null");
            yield break;
        }

        // Récupérer le VRMBlendShapeProxy directement
        VRMBlendShapeProxy proxy = blendshapeController.GetBlendShapeProxy();
        if (proxy == null)
        {
            Debug.LogWarning("[VRMAutoBlinkController] ❌ BlendShapeProxy est null");
            yield break;
        }

        if (showDebugLogs)
        {
            Debug.Log("[VRMAutoBlinkController] 👁️ Clignement !");
        }

        BlendShapeKey blinkKey = BlendShapeKey.CreateFromPreset(BlendShapePreset.Blink);

        // PHASE 1 : Fermeture TRÈS rapide (0 → 1) - Les paupières tombent vite
        float closeDuration = 0.05f;
        float elapsed = 0f;
        
        while (elapsed < closeDuration)
        {
            elapsed += Time.deltaTime;
            float t = Mathf.Clamp01(elapsed / closeDuration);
            // SmoothStep pour une accélération naturelle
            float smoothValue = Mathf.SmoothStep(0f, 1f, t);
            proxy.ImmediatelySetValue(blinkKey, smoothValue);
            proxy.Apply();
            yield return null;
        }

        // S'assurer qu'on est bien à 1.0
        proxy.ImmediatelySetValue(blinkKey, 1.0f);
        proxy.Apply();

        // PHASE 2 : Pause MINIMALE yeux fermés
        yield return new WaitForSeconds(blinkDuration);

        // PHASE 3 : Ouverture douce (1 → 0) - Réouverture progressive
        float openDuration = 0.08f;
        elapsed = 0f;
        
        while (elapsed < openDuration)
        {
            elapsed += Time.deltaTime;
            float t = Mathf.Clamp01(elapsed / openDuration);
            // SmoothStep inversé pour une décélération naturelle
            float smoothValue = Mathf.SmoothStep(1f, 0f, t);
            proxy.ImmediatelySetValue(blinkKey, smoothValue);
            proxy.Apply();
            yield return null;
        }

        // S'assurer que les yeux sont complètement ouverts
        proxy.ImmediatelySetValue(blinkKey, 0.0f);
        proxy.Apply();
    }

    /// <summary>
    /// Méthode publique pour déclencher un clignement manuel (pour tests)
    /// </summary>
    public void TriggerManualBlink()
    {
        if (blendshapeController != null)
        {
            StartCoroutine(PerformBlink());
        }
    }

    /// <summary>
    /// Nettoyage lors de la destruction du composant
    /// </summary>
    void OnDestroy()
    {
        // Arrêter la coroutine si elle tourne encore
        if (blinkCoroutine != null)
        {
            StopCoroutine(blinkCoroutine);
        }
    }

    /// <summary>
    /// Méthode appelée quand les valeurs changent dans l'Inspector Unity (debug)
    /// </summary>
    void OnValidate()
    {
        // S'assurer que les intervalles sont cohérents
        if (minInterval > maxInterval)
        {
            maxInterval = minInterval + 1.0f;
        }
    }
}
