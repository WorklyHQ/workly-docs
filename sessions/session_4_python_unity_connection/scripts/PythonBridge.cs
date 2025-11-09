using System;
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
    
    // Composants réseau
    private TcpListener server;
    private TcpClient client;
    private NetworkStream stream;
    private Thread listenThread;
    private bool isRunning = false;
    
    // Buffer pour les messages
    private string messageBuffer = "";
    
    void Start()
    {
        Debug.Log($"[PythonBridge] Démarrage du serveur sur {host}:{port}");
        StartServer();
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
                else if (jsonMessage.Contains("\"set_expression\""))
                {
                    Debug.Log("[PythonBridge] 😊 Commande : Changer l'expression");
                    // TODO: Implémenter le changement d'expression
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