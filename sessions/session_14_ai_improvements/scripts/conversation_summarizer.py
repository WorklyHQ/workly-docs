"""
conversation_summarizer.py - Module de résumé automatique de conversations

Ce module génère des résumés de conversations en utilisant le LLM Zephyr-7B.
Utilise des prompts spécialisés pour créer des résumés concis et informatifs.

Fonctionnalités :
- Résumé de conversations longues (20+ messages)
- Détection de points clés (décisions, questions importantes)
- Formatage contexte pour intégration dans prompts
- Seuils configurables pour déclenchement auto
"""

import re
from typing import List, Dict, Optional, Any
from datetime import datetime


class ConversationSummarizer:
    """
    Générateur de résumés de conversations
    
    Utilise le LLM (Zephyr-7B via ChatEngine) pour générer des résumés
    de conversations basés sur l'historique des messages.
    """
    
    def __init__(self, llm_callback=None, max_tokens: int = 200):
        """
        Initialise le summarizer
        
        Args:
            llm_callback: Fonction callback pour générer texte via LLM
                         Signature: callback(prompt: str) -> str
            max_tokens: Nombre max de tokens pour résumé généré
        """
        self.llm_callback = llm_callback
        self.max_tokens = max_tokens
        
        # Seuils pour déclenchement automatique
        self.auto_summarize_threshold = 20  # messages
        self.min_messages_for_summary = 5   # minimum de messages
        
        # Template de prompt pour résumé
        self.summary_prompt_template = """<|system|>
Tu es un assistant qui génère des résumés concis de conversations.
Ton résumé doit capturer l'essentiel en 3-5 phrases maximum.
Mentionne les sujets principaux, décisions prises, et questions importantes.</|system|>

<|user|>
Voici une conversation à résumer :

{conversation}

Génère un résumé concis (3-5 phrases) de cette conversation.</|user|>

<|assistant|>
"""
        
        # Template pour extraction de points clés
        self.keypoints_prompt_template = """<|system|>
Tu es un assistant qui identifie les points clés d'une conversation.
Liste uniquement les éléments importants : décisions, questions, actions, faits.</|system|>

<|user|>
Conversation :

{conversation}

Liste les points clés sous forme de puces (maximum 5 points).</|user|>

<|assistant|>
"""
    
    def summarize(
        self,
        messages: List[Dict[str, str]],
        include_keypoints: bool = False
    ) -> Dict[str, Any]:
        """
        Génère un résumé de conversation
        
        Args:
            messages: Liste de messages [{'role': ..., 'content': ...}, ...]
            include_keypoints: Si True, inclut aussi liste de points clés
            
        Returns:
            Dict avec 'summary', 'message_count', 'timestamp', 'keypoints' (optionnel)
        """
        if not messages or len(messages) < self.min_messages_for_summary:
            return {
                'summary': "",
                'message_count': len(messages),
                'timestamp': datetime.utcnow().isoformat(),
                'error': "Pas assez de messages pour générer un résumé"
            }
        
        # Formater conversation pour prompt
        formatted_conv = self._format_conversation(messages)
        
        # Générer résumé via LLM
        if self.llm_callback:
            summary_prompt = self.summary_prompt_template.format(
                conversation=formatted_conv
            )
            summary_text = self.llm_callback(summary_prompt)
            summary_text = self._clean_summary(summary_text)
        else:
            # Mode sans LLM (pour tests) - résumé basique
            summary_text = self._generate_basic_summary(messages)
        
        result = {
            'summary': summary_text,
            'message_count': len(messages),
            'timestamp': datetime.utcnow().isoformat(),
            'date_range': {
                'start': messages[0].get('timestamp', 'unknown'),
                'end': messages[-1].get('timestamp', 'unknown')
            }
        }
        
        # Ajouter points clés si demandé
        if include_keypoints:
            keypoints = self._extract_keypoints(messages)
            result['keypoints'] = keypoints
        
        return result
    
    def _format_conversation(self, messages: List[Dict[str, str]]) -> str:
        """
        Formate liste de messages en texte lisible pour LLM
        
        Args:
            messages: Liste de messages avec 'role' et 'content'
            
        Returns:
            Conversation formatée en texte
        """
        formatted = []
        
        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            
            # Nettoyer contenu (supprimer extra whitespace)
            content = ' '.join(content.split())
            
            # Formater selon rôle
            if role == 'user':
                prefix = "Utilisateur:"
            elif role == 'assistant':
                prefix = "Assistant:"
            elif role == 'system':
                prefix = "Système:"
            else:
                prefix = f"{role.capitalize()}:"
            
            formatted.append(f"{prefix} {content}")
        
        return "\n".join(formatted)
    
    def _clean_summary(self, summary: str) -> str:
        """
        Nettoie le résumé généré par LLM
        
        Args:
            summary: Résumé brut du LLM
            
        Returns:
            Résumé nettoyé
        """
        # Supprimer marqueurs de prompt qui pourraient rester
        summary = re.sub(r'<\|.*?\|>', '', summary)
        
        # Supprimer extra whitespace
        summary = ' '.join(summary.split())
        
        # Trim
        summary = summary.strip()
        
        # Limiter taille si trop long
        max_chars = 500
        if len(summary) > max_chars:
            # Couper à la dernière phrase complète
            summary = summary[:max_chars]
            last_period = summary.rfind('.')
            if last_period > 0:
                summary = summary[:last_period + 1]
        
        return summary
    
    def _generate_basic_summary(self, messages: List[Dict[str, str]]) -> str:
        """
        Génère résumé basique sans LLM (fallback)
        
        Args:
            messages: Liste de messages
            
        Returns:
            Résumé simple basé sur comptage
        """
        user_msgs = [m for m in messages if m.get('role') == 'user']
        assistant_msgs = [m for m in messages if m.get('role') == 'assistant']
        
        summary = f"Conversation de {len(messages)} messages "
        summary += f"({len(user_msgs)} de l'utilisateur, {len(assistant_msgs)} de l'assistant). "
        
        # Ajouter aperçu du premier/dernier message
        if user_msgs:
            first_user = user_msgs[0].get('content', '')[:50]
            summary += f"Premier message: '{first_user}...'. "
        
        return summary
    
    def _extract_keypoints(self, messages: List[Dict[str, str]]) -> List[str]:
        """
        Extrait points clés de la conversation
        
        Args:
            messages: Liste de messages
            
        Returns:
            Liste de points clés (strings)
        """
        keypoints = []
        
        if self.llm_callback:
            # Utiliser LLM pour extraction
            formatted_conv = self._format_conversation(messages)
            keypoints_prompt = self.keypoints_prompt_template.format(
                conversation=formatted_conv
            )
            
            keypoints_text = self.llm_callback(keypoints_prompt)
            
            # Parser réponse (format bullet points)
            lines = keypoints_text.split('\n')
            for line in lines:
                line = line.strip()
                # Détecter bullets (-, *, •, numéros)
                if re.match(r'^[-*•]\s+', line) or re.match(r'^\d+\.\s+', line):
                    # Supprimer bullet
                    point = re.sub(r'^[-*•]\s+', '', line)
                    point = re.sub(r'^\d+\.\s+', '', point)
                    if point:
                        keypoints.append(point)
        else:
            # Extraction basique sans LLM
            # Chercher messages avec mots-clés importants
            important_keywords = [
                'important', 'décision', 'problème', 'question',
                'objectif', 'projet', 'urgent', 'attention'
            ]
            
            for msg in messages:
                content_lower = msg.get('content', '').lower()
                for keyword in important_keywords:
                    if keyword in content_lower:
                        snippet = msg.get('content', '')[:80]
                        keypoints.append(snippet + '...')
                        break
                
                if len(keypoints) >= 5:
                    break
        
        return keypoints[:5]  # Max 5 points
    
    def should_summarize(self, message_count: int) -> bool:
        """
        Détermine si une conversation doit être résumée
        
        Args:
            message_count: Nombre de messages dans conversation courante
            
        Returns:
            True si résumé recommandé
        """
        return message_count >= self.auto_summarize_threshold
    
    def detect_key_points(self, message: str) -> List[str]:
        """
        Détecte si un message contient des points clés
        
        Args:
            message: Message à analyser
            
        Returns:
            Liste de types de points clés détectés
        """
        key_point_indicators = {
            'decision': ['décidé', 'choisi', 'opté pour', 'conclusion'],
            'question': ['?', 'comment', 'pourquoi', 'est-ce que'],
            'action': ['vais faire', 'dois', 'faut', 'besoin de'],
            'problem': ['problème', 'bug', 'erreur', 'souci', 'difficulté'],
            'goal': ['objectif', 'but', 'veux', 'souhaite', 'projet']
        }
        
        detected = []
        message_lower = message.lower()
        
        for key_type, indicators in key_point_indicators.items():
            for indicator in indicators:
                if indicator in message_lower:
                    detected.append(key_type)
                    break
        
        return detected
    
    def summarize_batch(
        self,
        conversations: List[List[Dict[str, str]]],
        batch_size: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Résume plusieurs conversations en batch
        
        Args:
            conversations: Liste de listes de messages
            batch_size: Nombre de conversations à traiter en parallèle
            
        Returns:
            Liste de résumés
        """
        summaries = []
        
        # Pour chaque conversation
        for conv in conversations:
            if len(conv) >= self.min_messages_for_summary:
                summary = self.summarize(conv, include_keypoints=True)
                summaries.append(summary)
            else:
                # Skip conversations trop courtes
                summaries.append({
                    'summary': "",
                    'message_count': len(conv),
                    'timestamp': datetime.utcnow().isoformat(),
                    'skipped': True,
                    'reason': "Trop peu de messages"
                })
        
        return summaries
    
    def format_summary_for_context(self, summary_data: Dict[str, Any]) -> str:
        """
        Formate un résumé pour l'inclure dans un contexte de prompt
        
        Args:
            summary_data: Données de résumé (output de summarize())
            
        Returns:
            Texte formaté pour inclusion dans prompt
        """
        if not summary_data.get('summary'):
            return ""
        
        formatted = f"[Résumé conversation précédente ({summary_data.get('message_count', 0)} messages)]\n"
        formatted += summary_data['summary']
        
        # Ajouter points clés si présents
        if 'keypoints' in summary_data and summary_data['keypoints']:
            formatted += "\n\nPoints clés :\n"
            for i, point in enumerate(summary_data['keypoints'], 1):
                formatted += f"{i}. {point}\n"
        
        return formatted


# --- Exemple d'utilisation ---
if __name__ == "__main__":
    # Mock LLM callback pour test
    def mock_llm(prompt: str) -> str:
        return "Cette conversation porte sur le développement d'une application. L'utilisateur demande de l'aide pour implémenter une fonctionnalité. L'assistant propose une solution technique et explique les étapes."
    
    # Test basique
    summarizer = ConversationSummarizer(llm_callback=mock_llm)
    
    test_messages = [
        {'role': 'user', 'content': 'Je veux ajouter une fonctionnalité de mémoire', 'timestamp': '2024-01-01T10:00:00'},
        {'role': 'assistant', 'content': 'Excellente idée ! Je peux t\'aider avec ça.', 'timestamp': '2024-01-01T10:00:05'},
        {'role': 'user', 'content': 'Comment faire pour stocker les conversations ?', 'timestamp': '2024-01-01T10:01:00'},
        {'role': 'assistant', 'content': 'Tu peux utiliser JSON pour persister les données.', 'timestamp': '2024-01-01T10:01:10'},
        {'role': 'user', 'content': 'D\'accord, et pour la recherche sémantique ?', 'timestamp': '2024-01-01T10:02:00'},
        {'role': 'assistant', 'content': 'sentence-transformers est parfait pour ça !', 'timestamp': '2024-01-01T10:02:15'},
    ]
    
    print("=== Test ConversationSummarizer ===\n")
    
    # Test résumé simple
    print("1. Résumé simple:")
    summary = summarizer.summarize(test_messages)
    print(f"   Résumé: {summary['summary']}")
    print(f"   Messages: {summary['message_count']}")
    print()
    
    # Test résumé avec points clés
    print("2. Résumé avec points clés:")
    summary_full = summarizer.summarize(test_messages, include_keypoints=True)
    print(f"   Résumé: {summary_full['summary']}")
    print(f"   Points clés: {summary_full.get('keypoints', [])}")
    print()
    
    # Test détection
    print("3. Détection seuil auto-résumé:")
    print(f"   6 messages: {summarizer.should_summarize(6)}")
    print(f"   25 messages: {summarizer.should_summarize(25)}")
    print()
    
    # Test détection points clés
    print("4. Détection points clés:")
    test_msg = "J'ai décidé d'utiliser Python pour ce projet. Comment faire ?"
    keypoints = summarizer.detect_key_points(test_msg)
    print(f"   Message: {test_msg}")
    print(f"   Points clés détectés: {keypoints}")
