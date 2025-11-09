using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

/// <summary>
/// PythonBridge - Serveur socket pour communiquer avec l'application Python
/// Place ce script sur un GameObject dans la scène Unity
/// </summary>
public class PythonBridge : MonoBehaviour
{
    [Header("Configuration")]
    [Tooltip("Port d'écoute pour la connexion Python")]
    public int port = 5555;

    [Tooltip("Adresse IP d'écoute (127.0.0.1 = localhost)")]
    public string host = "127.0.0.1";

    [Header("Status")]
    [Tooltip("État de la connexion")]
    public bool isConnected = false;

    [Header("VRM Loader")]
    [Tooltip("Référence au VRMLoader pour charger les modèles")]
    public VRMLoader vrmLoader;

    [Header("VRM Blendshapes")]
    [Tooltip("Référence au VRMBlendshapeController pour les expressions")]
    public VRMBlendshapeController blendshapeController;

    [Header("VRM Auto Blink")]
    [Tooltip("Référence au VRMAutoBlinkController pour le clignement automatique")]
    public VRMAutoBlinkController autoBlinkController;

    [Header("VRM Head Movement")]
    [Tooltip("Référence au VRMHeadMovementController pour les mouvements de tête")]
    public VRMHeadMovementController headMovementController;

    // Composants réseau
    private TcpListener server;
    private TcpClient client;
    private NetworkStream stream;
    private Thread listenThread;
    private bool isRunning = false;

    // Buffer pour les messages
    private string messageBuffer = "";
    
    // Queue pour exécuter les actions sur le thread principal Unity
    private Queue<Action> mainThreadActions = new Queue<Action>();

    void Start()
    {
        Debug.Log($"[PythonBridge] Démarrage du serveur sur {host}:{port}");
        StartServer();
    }
    
    /// <summary>
    /// Update - Exécute les actions en attente sur le thread principal
    /// </summary>
    void Update()
    {
        // Exécuter toutes les actions en attente sur le thread principal
        lock (mainThreadActions)
        {
            while (mainThreadActions.Count > 0)
            {
                var action = mainThreadActions.Dequeue();
                try
                {
                    action?.Invoke();
                }
                catch (Exception e)
                {
                    Debug.LogError($"[PythonBridge] ❌ Erreur lors de l'exécution d'une action : {e.Message}");
                }
            }
        }
    }

    /// <summary>
    /// Démarre le serveur socket
    /// </summary>
    void StartServer()
    {
        try
        {
            // Créer et démarrer le serveur TCP
            IPAddress ipAddress = IPAddress.Parse(host);
            server = new TcpListener(ipAddress, port);
            server.Start();

            isRunning = true;

            // Démarrer le thread d'écoute
            listenThread = new Thread(new ThreadStart(ListenForConnections));
            listenThread.IsBackground = true;
            listenThread.Start();

            Debug.Log($"[PythonBridge] ✅ Serveur démarré avec succès sur {host}:{port}");
            Debug.Log("[PythonBridge] En attente de connexion Python...");
        }
        catch (Exception e)
        {
            Debug.LogError($"[PythonBridge] ❌ Erreur au démarrage du serveur : {e.Message}");
        }
    }

    /// <summary>
    /// Thread d'écoute des connexions entrantes
    /// </summary>
    void ListenForConnections()
    {
        while (isRunning)
        {
            try
            {
                // Attendre une connexion (bloquant)
                client = server.AcceptTcpClient();
                stream = client.GetStream();
                isConnected = true;

                Debug.Log("[PythonBridge] 🔗 Client Python connecté !");

                // Envoyer un message de confirmation
                SendMessage(new
                {
                    type = "response",
                    status = "connected",
                    message = "Unity server ready"
                });

                // Recevoir les messages
                ReceiveMessages();
            }
            catch (SocketException)
            {
                // Le serveur a été arrêté
                break;
            }
            catch (Exception e)
            {
                Debug.LogError($"[PythonBridge] Erreur de connexion : {e.Message}");
            }
        }
    }

    /// <summary>
    /// Reçoit les messages du client Python
    /// </summary>
    void ReceiveMessages()
    {
        byte[] buffer = new byte[4096];

        while (isRunning && client != null && client.Connected)
        {
            try
            {
                // Lire les données
                int bytesRead = stream.Read(buffer, 0, buffer.Length);

                if (bytesRead == 0)
                {
                    // Connexion fermée
                    Debug.Log("[PythonBridge] Client déconnecté");
                    isConnected = false;
                    break;
                }

                // Convertir en string
                string data = Encoding.UTF8.GetString(buffer, 0, bytesRead);
                messageBuffer += data;

                // Traiter les messages complets (séparés par \n)
                ProcessMessages();
            }
            catch (Exception e)
            {
                Debug.LogError($"[PythonBridge] Erreur de réception : {e.Message}");
                isConnected = false;
                break;
            }
        }
    }

    /// <summary>
    /// Traite les messages reçus du buffer
    /// </summary>
    void ProcessMessages()
    {
        while (messageBuffer.Contains("\n"))
        {
            int newlineIndex = messageBuffer.IndexOf("\n");
            string message = messageBuffer.Substring(0, newlineIndex);
            messageBuffer = messageBuffer.Substring(newlineIndex + 1);

            if (!string.IsNullOrWhiteSpace(message))
            {
                HandleMessage(message);
            }
        }
    }

    /// <summary>
    /// Gère un message reçu de Python
    /// </summary>
    void HandleMessage(string jsonMessage)
    {
        try
        {
            Debug.Log($"[PythonBridge] 📨 Reçu : {jsonMessage}");

            // Parser le JSON (simple pour l'instant)
            // TODO: Utiliser JsonUtility ou Newtonsoft.Json pour un parsing complet

            // Pour l'instant, on détecte juste la commande
            if (jsonMessage.Contains("\"command\""))
            {
                if (jsonMessage.Contains("\"load_model\""))
                {
                    Debug.Log("[PythonBridge] 🎭 Commande : Charger un modèle VRM");

                    // Extraire le chemin du fichier (parsing simple)
                    string path = ExtractPathFromJson(jsonMessage);

                    // Appeler le VRMLoader
                    if (vrmLoader != null)
                    {
                        Debug.Log($"[PythonBridge] 📂 Chargement depuis : {path}");
                        vrmLoader.LoadVRMFromPath(path);

                        SendMessage(new
                        {
                            type = "response",
                            command = "load_model",
                            status = "success",
                            message = $"Modèle en cours de chargement : {path}"
                        });
                    }
                    else
                    {
                        Debug.LogError("[PythonBridge] ❌ VRMLoader non assigné !");
                        SendMessage(new
                        {
                            type = "response",
                            command = "load_model",
                            status = "error",
                            message = "VRMLoader non configuré"
                        });
                    }
                }
                else if (jsonMessage.Contains("\"unload_model\""))
                {
                    Debug.Log("[PythonBridge] 🗑️ Commande : Décharger le modèle VRM");

                    // Enqueue l'action pour l'exécuter sur le thread principal
                    lock (mainThreadActions)
                    {
                        mainThreadActions.Enqueue(() => {
                            // Appeler le VRMLoader pour décharger
                            if (vrmLoader != null)
                            {
                                // Note: Pas besoin de ResetExpressions car le modèle sera détruit
                                // Les expressions sont automatiquement perdues avec Destroy(currentModel)
                                vrmLoader.UnloadModel();

                                SendMessage(new
                                {
                                    type = "response",
                                    command = "unload_model",
                                    status = "success",
                                    message = "Modèle déchargé avec succès"
                                });
                            }
                            else
                            {
                                Debug.LogError("[PythonBridge] ❌ VRMLoader non assigné !");
                                SendMessage(new
                                {
                                    type = "response",
                                    command = "unload_model",
                                    status = "error",
                                    message = "VRMLoader non configuré"
                                });
                            }
                        });
                    }
                }
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
                        SendMessage(new
                        {
                            type = "response",
                            command = "set_expression",
                            status = "error",
                            message = "VRMBlendshapeController non configuré"
                        });
                    }
                }
                else if (jsonMessage.Contains("\"reset_expressions\""))
                {
                    Debug.Log("[PythonBridge] 🔄 Commande : Reset expressions");

                    // Appeler le BlendshapeController
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
                        SendMessage(new
                        {
                            type = "response",
                            command = "reset_expressions",
                            status = "error",
                            message = "VRMBlendshapeController non configuré"
                        });
                    }
                }
                else if (jsonMessage.Contains("\"set_transition_speed\""))
                {
                    Debug.Log("[PythonBridge] ⚡ Commande : Changer vitesse de transition");

                    // Extraire la vitesse
                    float speed = ExtractFloatValue(jsonMessage, "speed");

                    // Appeler le BlendshapeController
                    if (blendshapeController != null)
                    {
                        Debug.Log($"[PythonBridge] 🎚️ Vitesse de transition : {speed:F2}");
                        blendshapeController.SetTransitionSpeed(speed);

                        SendMessage(new
                        {
                            type = "response",
                            command = "set_transition_speed",
                            status = "success",
                            message = $"Vitesse de transition définie à {speed:F2}"
                        });
                    }
                    else
                    {
                        Debug.LogError("[PythonBridge] ❌ VRMBlendshapeController non assigné !");
                        SendMessage(new
                        {
                            type = "response",
                            command = "set_transition_speed",
                            status = "error",
                            message = "VRMBlendshapeController non configuré"
                        });
                    }
                }
                else if (jsonMessage.Contains("\"set_auto_blink\""))
                {
                    Debug.Log("[PythonBridge] 👁️ Commande : Changer état clignement automatique");

                    // Extraire l'état enabled
                    bool enabled = ExtractBoolValue(jsonMessage, "enabled");

                    // Enqueue l'action sur le thread principal
                    lock (mainThreadActions)
                    {
                        mainThreadActions.Enqueue(() => {
                            if (autoBlinkController != null)
                            {
                                autoBlinkController.SetAutoBlinkEnabled(enabled);
                                Debug.Log($"[PythonBridge] 👁️ Clignement automatique : {(enabled ? "ACTIVÉ" : "DÉSACTIVÉ")}");
                                
                                SendMessage(new
                                {
                                    type = "response",
                                    command = "set_auto_blink",
                                    status = "success",
                                    message = $"Clignement automatique {(enabled ? "activé" : "désactivé")}"
                                });
                            }
                            else
                            {
                                Debug.LogError("[PythonBridge] ❌ VRMAutoBlinkController non assigné !");
                                SendMessage(new
                                {
                                    type = "response",
                                    command = "set_auto_blink",
                                    status = "error",
                                    message = "VRMAutoBlinkController non configuré"
                                });
                            }
                        });
                    }
                }
                else if (jsonMessage.Contains("\"set_auto_head_movement\""))
                {
                    Debug.Log("[PythonBridge] 🎭 Commande : Changer état mouvements de tête automatiques");

                    // Extraire les paramètres
                    bool enabled = ExtractBoolValue(jsonMessage, "enabled");
                    float minInterval = ExtractFloatValue(jsonMessage, "min_interval");
                    float maxInterval = ExtractFloatValue(jsonMessage, "max_interval");
                    float maxAngle = ExtractFloatValue(jsonMessage, "max_angle");

                    // Enqueue l'action sur le thread principal
                    lock (mainThreadActions)
                    {
                        mainThreadActions.Enqueue(() => {
                            if (headMovementController != null)
                            {
                                headMovementController.SetAutoHeadMovement(enabled);
                                
                                // Mettre à jour les paramètres de timing (min, max, duration)
                                // Note: duration est fixé à 2.0s (1s aller + 1s retour)
                                headMovementController.UpdateTimingParameters(minInterval, maxInterval, 2.0f);
                                
                                // Mettre à jour les paramètres d'amplitude (yaw, pitch)
                                // Note: pitch = maxAngle / 2 pour des mouvements plus subtils
                                headMovementController.UpdateAmplitudeParameters(maxAngle, maxAngle / 2f);
                                
                                Debug.Log($"[PythonBridge] 🎭 Mouvements de tête : {(enabled ? "ACTIVÉS" : "DÉSACTIVÉS")}");
                                Debug.Log($"[PythonBridge] 🎭 Paramètres : Interval [{minInterval:F1}s-{maxInterval:F1}s], Angle max {maxAngle:F1}°");
                                
                                SendMessage(new
                                {
                                    type = "response",
                                    command = "set_auto_head_movement",
                                    status = "success",
                                    message = $"Mouvements de tête {(enabled ? "activés" : "désactivés")}"
                                });
                            }
                            else
                            {
                                Debug.LogError("[PythonBridge] ❌ VRMHeadMovementController non assigné !");
                                SendMessage(new
                                {
                                    type = "response",
                                    command = "set_auto_head_movement",
                                    status = "error",
                                    message = "VRMHeadMovementController non configuré"
                                });
                            }
                        });
                    }
                }
                else if (jsonMessage.Contains("\"set_blendshape\""))
                {
                    Debug.Log("[PythonBridge] 👄 Commande : Modifier un blendshape");
                    // TODO: Implémenter le contrôle des blendshapes
                }
            }
        }
        catch (Exception e)
        {
            Debug.LogError($"[PythonBridge] ❌ Erreur de traitement du message : {e.Message}");
        }
    }

    /// <summary>
    /// Envoie un message au client Python
    /// </summary>
    public void SendMessage(object data)
    {
        if (stream == null || !isConnected)
        {
            Debug.LogWarning("[PythonBridge] ⚠️ Impossible d'envoyer : pas de connexion");
            return;
        }

        try
        {
            // Convertir en JSON (simple)
            string json = JsonUtility.ToJson(data);
            string message = json + "\n";

            // Convertir en bytes et envoyer
            byte[] bytes = Encoding.UTF8.GetBytes(message);
            stream.Write(bytes, 0, bytes.Length);
            stream.Flush();

            Debug.Log($"[PythonBridge] 📤 Envoyé : {json}");
        }
        catch (Exception e)
        {
            Debug.LogError($"[PythonBridge] ❌ Erreur d'envoi : {e.Message}");
            isConnected = false;
        }
    }

    /// <summary>
    /// Nettoyage à la fermeture de l'application
    /// </summary>
    void OnApplicationQuit()
    {
        Debug.Log("[PythonBridge] Fermeture du serveur...");

        isRunning = false;
        isConnected = false;

        // Fermer les connexions
        if (stream != null)
        {
            stream.Close();
            stream = null;
        }

        if (client != null)
        {
            client.Close();
            client = null;
        }

        if (server != null)
        {
            server.Stop();
            server = null;
        }

        // Arrêter le thread
        if (listenThread != null && listenThread.IsAlive)
        {
            listenThread.Join(1000); // Attendre max 1 seconde
        }

        Debug.Log("[PythonBridge] ✅ Serveur fermé");
    }

    /// <summary>
    /// Extrait le chemin du fichier depuis le JSON (parsing simple)
    /// </summary>
    private string ExtractPathFromJson(string json)
    {
        try
        {
            // Chercher "path": "..."
            int pathStart = json.IndexOf("\"path\"");
            if (pathStart == -1) return "";

            int valueStart = json.IndexOf("\"", pathStart + 6);
            if (valueStart == -1) return "";

            int valueEnd = json.IndexOf("\"", valueStart + 1);
            if (valueEnd == -1) return "";

            string path = json.Substring(valueStart + 1, valueEnd - valueStart - 1);

            // Convertir les slashes si nécessaire
            path = path.Replace("/", "\\");

            return path;
        }
        catch (Exception e)
        {
            Debug.LogError($"[PythonBridge] ❌ Erreur extraction path : {e.Message}");
            return "";
        }
    }

    /// <summary>
    /// Extrait une valeur string depuis le JSON (parsing simple)
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
    /// Extrait une valeur float depuis le JSON (parsing simple)
    /// </summary>
    private float ExtractFloatValue(string json, string key)
    {
        try
        {
            string searchKey = $"\"{key}\"";
            int keyStart = json.IndexOf(searchKey);
            if (keyStart == -1) return 0.0f;

            // Chercher le ':' après la clé
            int colonIndex = json.IndexOf(":", keyStart);
            if (colonIndex == -1) return 0.0f;

            // Trouver le début de la valeur (après ':' et espaces)
            int valueStart = colonIndex + 1;
            while (valueStart < json.Length && (json[valueStart] == ' ' || json[valueStart] == '\t'))
                valueStart++;

            // Trouver la fin de la valeur (avant ',' ou '}')
            int valueEnd = valueStart;
            while (valueEnd < json.Length && json[valueEnd] != ',' && json[valueEnd] != '}' && json[valueEnd] != '\n')
                valueEnd++;

            string valueStr = json.Substring(valueStart, valueEnd - valueStart).Trim();

            // Parser le float
            if (float.TryParse(valueStr, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float result))
            {
                return result;
            }

            Debug.LogWarning($"[PythonBridge] ⚠️ Impossible de parser float '{key}' : '{valueStr}'");
            return 0.0f;
        }
        catch (Exception e)
        {
            Debug.LogError($"[PythonBridge] ❌ Erreur extraction float '{key}' : {e.Message}");
            return 0.0f;
        }
    }

    /// <summary>
    /// Extrait une valeur booléenne depuis un JSON simple
    /// </summary>
    private bool ExtractBoolValue(string json, string key)
    {
        try
        {
            string searchKey = $"\"{key}\"";
            int keyStart = json.IndexOf(searchKey);
            if (keyStart == -1) return false;

            // Chercher le ':' après la clé
            int colonIndex = json.IndexOf(":", keyStart);
            if (colonIndex == -1) return false;

            // Trouver le début de la valeur (après ':' et espaces)
            int valueStart = colonIndex + 1;
            while (valueStart < json.Length && (json[valueStart] == ' ' || json[valueStart] == '\t'))
                valueStart++;

            // Trouver la fin de la valeur (avant ',' ou '}')
            int valueEnd = valueStart;
            while (valueEnd < json.Length && json[valueEnd] != ',' && json[valueEnd] != '}' && json[valueEnd] != '\n')
                valueEnd++;

            string valueStr = json.Substring(valueStart, valueEnd - valueStart).Trim().ToLower();

            // Parser le booléen
            if (valueStr == "true")
            {
                return true;
            }
            else if (valueStr == "false")
            {
                return false;
            }

            Debug.LogWarning($"[PythonBridge] ⚠️ Impossible de parser bool '{key}' : '{valueStr}'");
            return false;
        }
        catch (Exception e)
        {
            Debug.LogError($"[PythonBridge] ❌ Erreur extraction bool '{key}' : {e.Message}");
            return false;
        }
    }

    /// <summary>
    /// Affiche le statut dans l'inspecteur Unity
    /// </summary>
    void OnGUI()
    {
        // Affichage en haut à gauche de la fenêtre Game
        GUIStyle style = new GUIStyle();
        style.fontSize = 14;
        style.normal.textColor = isConnected ? Color.green : Color.red;

        string status = isConnected ? "✅ Python Connecté" : "⏳ En attente de Python...";
        GUI.Label(new Rect(10, 10, 300, 30), status, style);
    }
}

// Classe pour sérialiser les réponses JSON
[Serializable]
public class UnityResponse
{
    public string type;
    public string status;
    public string message;
    public string command;
}
