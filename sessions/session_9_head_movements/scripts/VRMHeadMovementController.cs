using System.Collections;
using UnityEngine;

/// <summary>
/// Contrôleur de mouvements de tête subtils pour modèles VRM
/// Gère les rotations procédurales (head bobbing, head tilt) pour rendre l'avatar vivant
/// Utilise des coroutines et SmoothStep pour des animations naturelles
/// 
/// Session 9 : Mouvements de Tête Subtils 🎭
/// Date : 22 octobre 2025
/// </summary>
public class VRMHeadMovementController : MonoBehaviour
{
    #region Paramètres Publics (Inspector)
    
    [Header("Activation")]
    [Tooltip("Active/désactive les mouvements de tête automatiques")]
    public bool autoHeadMovement = true;
    
    [Header("Timing")]
    [Tooltip("Intervalle minimum entre les mouvements (secondes)")]
    [Range(2.0f, 10.0f)]
    public float minInterval = 3.0f;
    
    [Tooltip("Intervalle maximum entre les mouvements (secondes)")]
    [Range(3.0f, 15.0f)]
    public float maxInterval = 7.0f;
    
    [Tooltip("Durée totale d'un mouvement (aller + retour en secondes)")]
    [Range(1.0f, 5.0f)]
    public float movementDuration = 2.0f;
    
    [Header("Amplitude")]
    [Tooltip("Angle maximum de rotation gauche/droite (Yaw en degrés)")]
    [Range(2.0f, 15.0f)]
    public float maxRotationAngle = 5.0f;
    
    [Tooltip("Angle maximum de rotation haut/bas (Pitch en degrés) - Plus subtil que Yaw")]
    [Range(1.0f, 10.0f)]
    public float maxPitchAngle = 2.5f;
    
    [Header("Debug")]
    [Tooltip("Afficher les logs de debug dans la console")]
    public bool enableDebugLogs = true;
    
    #endregion
    
    #region Variables Privées
    
    private GameObject headBone;
    private Quaternion initialRotation;
    private Coroutine movementCoroutine;
    private bool isInitialized = false;
    
    #endregion
    
    #region Unity Lifecycle
    
    void Start()
    {
        StartCoroutine(InitializeWithDelay());
    }
    
    void OnDestroy()
    {
        StopMovement();
    }
    
    #endregion
    
    #region Initialisation
    
    /// <summary>
    /// Initialisation avec délai pour attendre le chargement du modèle VRM
    /// </summary>
    private IEnumerator InitializeWithDelay()
    {
        Debug.Log("[VRMHeadMovementController] Attente du chargement du modèle VRM...");
        
        // Attendre activement jusqu'à ce qu'un modèle VRM soit chargé (max 30s)
        GameObject vrmModel = null;
        float timeoutDuration = 30f;
        float elapsedTime = 0f;
        
        while (vrmModel == null && elapsedTime < timeoutDuration)
        {
            yield return new WaitForSeconds(0.5f); // Vérifier toutes les 0.5s
            elapsedTime += 0.5f;
            
            vrmModel = FindVRMModel();
            
            if (vrmModel == null)
            {
                Debug.Log($"[VRMHeadMovementController] ⏳ Recherche du modèle VRM... ({elapsedTime:F1}s)");
            }
        }
        
        if (vrmModel == null)
        {
            Debug.LogWarning("[VRMHeadMovementController] ⚠️ Timeout : Aucun modèle VRM trouvé après 30s !");
            Debug.LogWarning("[VRMHeadMovementController] 💡 Assurez-vous de charger un modèle VRM depuis Python");
            isInitialized = false;
            yield break;
        }
        
        Debug.Log($"[VRMHeadMovementController] ✅ Modèle VRM trouvé : {vrmModel.name}");
        
        // DEBUG : Afficher toute la hiérarchie du modèle VRM (TOUJOURS, même si debug désactivé)
        Debug.Log("[VRMHeadMovementController] 🔍 DEBUG - Hiérarchie complète du modèle :");
        LogHierarchy(vrmModel.transform);
        Debug.Log("[VRMHeadMovementController] 🔍 --- Fin de la hiérarchie ---");
        
        // Rechercher le bone "Head" dans le modèle VRM
        headBone = FindHeadBone(vrmModel.transform);
        
        if (headBone != null)
        {
            // Sauvegarder la rotation initiale
            initialRotation = headBone.transform.localRotation;
            isInitialized = true;
            
            Debug.Log($"[VRMHeadMovementController] ✅ Head bone trouvé : {headBone.name}");
            Debug.Log($"[VRMHeadMovementController] 📍 Rotation initiale : {initialRotation.eulerAngles}");
            
            // Démarrer les mouvements si activés
            if (autoHeadMovement)
            {
                StartMovement();
            }
        }
        else
        {
            Debug.LogWarning("[VRMHeadMovementController] ⚠️ Impossible de trouver le Head bone !");
            Debug.LogWarning("[VRMHeadMovementController] 💡 Vérifiez la hiérarchie ci-dessus et ajoutez le nom correct dans FindHeadBone()");
            isInitialized = false;
        }
    }
    
    /// <summary>
    /// Recherche le GameObject du modèle VRM dans la scène
    /// </summary>
    private GameObject FindVRMModel()
    {
        // Chercher un GameObject dont le nom contient "Model" et "Clone"
        GameObject[] allObjects = FindObjectsOfType<GameObject>();
        
        foreach (GameObject obj in allObjects)
        {
            string nameLower = obj.name.ToLower();
            if (nameLower.Contains("model") && nameLower.Contains("clone"))
            {
                Debug.Log($"[VRMHeadMovementController] 🔍 Modèle VRM candidat : {obj.name}");
                return obj;
            }
        }
        
        // Fallback : chercher juste "Model"
        foreach (GameObject obj in allObjects)
        {
            if (obj.name.ToLower().Contains("model"))
            {
                Debug.Log($"[VRMHeadMovementController] 🔍 Modèle VRM candidat (fallback) : {obj.name}");
                return obj;
            }
        }
        
        return null;
    }
    
    /// <summary>
    /// Recherche récursive du GameObject contenant "Head" dans son nom
    /// Essaie plusieurs variantes de noms possibles
    /// </summary>
    private GameObject FindHeadBone(Transform parent)
    {
        string nameLower = parent.name.ToLower();
        
        // Liste des noms possibles pour le head bone
        string[] possibleNames = { "head", "j_bip_c_head", "bip_head", "neck" };
        
        // Vérifier si le nom correspond à un des patterns
        foreach (string pattern in possibleNames)
        {
            if (nameLower.Contains(pattern))
            {
                Debug.Log($"[VRMHeadMovementController] 🔍 Bone candidat trouvé : {parent.name}");
                return parent.gameObject;
            }
        }
        
        // Recherche récursive dans les enfants
        foreach (Transform child in parent)
        {
            GameObject result = FindHeadBone(child);
            if (result != null)
            {
                return result;
            }
        }
        
        return null;
    }
    
    /// <summary>
    /// Affiche la hiérarchie complète pour debug
    /// </summary>
    private void LogHierarchy(Transform parent, int depth = 0)
    {
        string indent = new string(' ', depth * 2);
        Debug.Log($"{indent}→ {parent.name}");
        
        foreach (Transform child in parent)
        {
            LogHierarchy(child, depth + 1);
        }
    }
    
    #endregion
    
    #region Contrôle des Mouvements
    
    /// <summary>
    /// Démarre la boucle de mouvements automatiques
    /// </summary>
    public void StartMovement()
    {
        if (!isInitialized)
        {
            LogDebug("[VRMHeadMovementController] ⚠️ Impossible de démarrer : non initialisé");
            return;
        }
        
        if (movementCoroutine != null)
        {
            LogDebug("[VRMHeadMovementController] ⚠️ Mouvements déjà actifs");
            return;
        }
        
        autoHeadMovement = true;
        movementCoroutine = StartCoroutine(HeadMovementLoop());
        LogDebug("[VRMHeadMovementController] ▶️ Mouvements de tête démarrés");
    }
    
    /// <summary>
    /// Arrête la boucle de mouvements automatiques
    /// </summary>
    public void StopMovement()
    {
        if (movementCoroutine != null)
        {
            StopCoroutine(movementCoroutine);
            movementCoroutine = null;
            LogDebug("[VRMHeadMovementController] ⏸️ Mouvements de tête arrêtés");
        }
        
        autoHeadMovement = false;
        
        // Réinitialiser la rotation à la position initiale
        if (headBone != null && isInitialized)
        {
            headBone.transform.localRotation = initialRotation;
        }
    }
    
    /// <summary>
    /// Active ou désactive les mouvements automatiques
    /// </summary>
    public void SetAutoHeadMovement(bool enabled)
    {
        if (enabled)
        {
            StartMovement();
        }
        else
        {
            StopMovement();
        }
    }
    
    /// <summary>
    /// Met à jour les paramètres de timing
    /// </summary>
    public void UpdateTimingParameters(float min, float max, float duration)
    {
        minInterval = Mathf.Clamp(min, 2.0f, 10.0f);
        maxInterval = Mathf.Clamp(max, 3.0f, 15.0f);
        movementDuration = Mathf.Clamp(duration, 1.0f, 5.0f);
        
        LogDebug($"[VRMHeadMovementController] 🔧 Timing mis à jour : [{minInterval}-{maxInterval}]s, durée {movementDuration}s");
    }
    
    /// <summary>
    /// Met à jour les paramètres d'amplitude
    /// </summary>
    public void UpdateAmplitudeParameters(float maxYaw, float maxPitch)
    {
        maxRotationAngle = Mathf.Clamp(maxYaw, 2.0f, 15.0f);
        maxPitchAngle = Mathf.Clamp(maxPitch, 1.0f, 10.0f);
        
        LogDebug($"[VRMHeadMovementController] 🔧 Amplitude mise à jour : Yaw ±{maxRotationAngle}°, Pitch ±{maxPitchAngle}°");
    }
    
    #endregion
    
    #region Coroutines d'Animation
    
    /// <summary>
    /// Boucle principale des mouvements de tête
    /// </summary>
    private IEnumerator HeadMovementLoop()
    {
        LogDebug("[VRMHeadMovementController] 🔄 Boucle de mouvements démarrée");
        
        while (autoHeadMovement && isInitialized)
        {
            // Attendre un intervalle aléatoire
            float waitTime = Random.Range(minInterval, maxInterval);
            LogDebug($"[VRMHeadMovementController] ⏱️ Attente de {waitTime:F1}s avant prochain mouvement...");
            yield return new WaitForSeconds(waitTime);
            
            // Exécuter un mouvement de tête
            if (autoHeadMovement) // Re-vérifier au cas où désactivé pendant l'attente
            {
                yield return StartCoroutine(PerformHeadMovement());
            }
        }
        
        LogDebug("[VRMHeadMovementController] 🔄 Boucle de mouvements terminée");
    }
    
    /// <summary>
    /// Effectue un mouvement de tête complet (rotation + retour)
    /// Utilise SmoothStep pour des transitions naturelles
    /// </summary>
    private IEnumerator PerformHeadMovement()
    {
        // Choisir une direction aléatoire
        float targetYaw = Random.Range(-maxRotationAngle, maxRotationAngle);
        float targetPitch = Random.Range(-maxPitchAngle, maxPitchAngle);
        
        LogDebug($"[VRMHeadMovementController] 🎭 Début mouvement : Yaw {targetYaw:F1}°, Pitch {targetPitch:F1}°");
        
        // Créer la rotation cible (combinaison Pitch + Yaw)
        Quaternion targetRotation = initialRotation * Quaternion.Euler(targetPitch, targetYaw, 0f);
        
        // Durée de chaque phase (aller = 50%, retour = 50%)
        float halfDuration = movementDuration / 2f;
        
        // PHASE 1 : Rotation vers la cible (SmoothStep)
        yield return StartCoroutine(AnimateRotation(initialRotation, targetRotation, halfDuration));
        
        // PHASE 2 : Retour à la position initiale (SmoothStep)
        yield return StartCoroutine(AnimateRotation(targetRotation, initialRotation, halfDuration));
        
        // Assurer le retour exact à la position initiale
        headBone.transform.localRotation = initialRotation;
        
        LogDebug($"[VRMHeadMovementController] ✅ Mouvement terminé, retour à position initiale");
    }
    
    /// <summary>
    /// Anime une rotation entre deux quaternions avec interpolation SmoothStep
    /// </summary>
    private IEnumerator AnimateRotation(Quaternion from, Quaternion to, float duration)
    {
        float elapsed = 0f;
        
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float t = Mathf.Clamp01(elapsed / duration);
            
            // Appliquer SmoothStep pour interpolation douce
            float smoothT = SmoothStep(t);
            
            // Interpolation sphérique (meilleure pour les rotations)
            headBone.transform.localRotation = Quaternion.Slerp(from, to, smoothT);
            
            yield return null;
        }
        
        // Assurer la rotation finale exacte
        headBone.transform.localRotation = to;
    }
    
    #endregion
    
    #region Fonctions Mathématiques
    
    /// <summary>
    /// Fonction SmoothStep (courbe de Hermite cubique)
    /// Fournit une interpolation douce avec accélération/décélération
    /// f(t) = 3t² - 2t³
    /// 
    /// Propriétés :
    /// - f(0) = 0
    /// - f(1) = 1
    /// - f'(0) = 0 (dérivée nulle au début)
    /// - f'(1) = 0 (dérivée nulle à la fin)
    /// </summary>
    private float SmoothStep(float t)
    {
        return t * t * (3f - 2f * t);
    }
    
    #endregion
    
    #region Utilitaires Debug
    
    private void LogDebug(string message)
    {
        if (enableDebugLogs)
        {
            Debug.Log(message);
        }
    }
    
    #endregion
}
