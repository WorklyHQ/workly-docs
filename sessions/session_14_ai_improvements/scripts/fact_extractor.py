"""
fact_extractor.py - Module d'extraction de faits depuis les conversations

Ce module analyse les messages de conversation pour extraire des informations structurées :
- Entités (noms, lieux, dates, organisations)
- Préférences (aime/n'aime pas)
- Événements (actions, projets, objectifs)
- Relations (entre personnes, concepts)

Utilise des patterns regex et des mots-clés pour l'extraction.
"""

import re
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import json


@dataclass
class Entity:
    """Entité extraite (nom, lieu, date, organisation)"""
    entity_type: str  # 'person', 'location', 'date', 'organization'
    value: str
    context: str
    confidence: float  # 0.0 - 1.0
    first_seen: str  # ISO timestamp
    occurrences: int = 1
    
    def to_dict(self) -> Dict:
        """Convertit en dictionnaire pour JSON"""
        return asdict(self)


@dataclass
class Preference:
    """Préférence utilisateur (aime/n'aime pas)"""
    category: str  # 'food', 'hobby', 'music', 'color', 'general'
    subject: str  # ex: "pizza", "programming", "jazz"
    sentiment: str  # 'positive', 'negative', 'neutral'
    intensity: float  # 0.0 - 1.0 (force de la préférence)
    context: str  # phrase originale
    timestamp: str  # ISO timestamp
    
    def to_dict(self) -> Dict:
        """Convertit en dictionnaire pour JSON"""
        return asdict(self)


@dataclass
class Event:
    """Événement mentionné (action passée, projet, objectif)"""
    event_type: str  # 'past_action', 'current_project', 'future_goal'
    description: str
    participants: List[str]
    location: Optional[str]
    time_reference: Optional[str]  # "hier", "la semaine prochaine", date précise
    status: str  # 'completed', 'ongoing', 'planned'
    context: str  # phrase originale
    timestamp: str  # ISO timestamp
    
    def to_dict(self) -> Dict:
        """Convertit en dictionnaire pour JSON"""
        return asdict(self)


@dataclass
class Relationship:
    """Relation entre entités (personnes, concepts)"""
    subject: str
    relation_type: str  # 'family', 'friend', 'colleague', 'owns', 'works_at', etc.
    object: str
    context: str
    confidence: float
    timestamp: str
    
    def to_dict(self) -> Dict:
        """Convertit en dictionnaire pour JSON"""
        return asdict(self)


class FactExtractor:
    """
    Extracteur de faits depuis conversations
    
    Analyse les messages pour identifier et extraire des informations structurées.
    Utilise des patterns regex et des listes de mots-clés pour l'extraction.
    """
    
    def __init__(self):
        """Initialise l'extracteur avec patterns et mots-clés"""
        # Patterns regex pour extraction d'entités
        self.patterns = {
            'person': r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Noms propres
            'location': r'\b(?:à|en|dans|vers)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            'date': r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|lundi|mardi|mercredi|jeudi|vendredi|samedi|dimanche|hier|aujourd\'hui|demain|la semaine prochaine|le mois prochain)\b',
            'organization': r'\b(?:chez|pour)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
        }
        
        # Mots-clés pour détection de préférences
        self.preference_keywords = {
            'positive': [
                'aime', 'adore', 'préfère', 'apprécie', 'raffole',
                'fan de', 'passionné', 'favori', 'excellent', 'génial',
                'j\'aime', 'je préfère', 'c\'est super', 'c\'est bien'
            ],
            'negative': [
                'déteste', 'n\'aime pas', 'horreur de', 'pas fan',
                'je n\'aime pas', 'c\'est nul', 'c\'est mauvais',
                'insupportable', 'horrible', 'désagréable'
            ]
        }
        
        # Catégories de préférences
        self.preference_categories = {
            'food': ['pizza', 'burger', 'salade', 'viande', 'poisson', 'végétarien', 
                     'chocolat', 'gâteau', 'cuisine', 'restaurant', 'plat', 'nourriture'],
            'hobby': ['sport', 'lecture', 'jeux vidéo', 'musique', 'film', 'série',
                      'voyage', 'randonnée', 'natation', 'football', 'basket', 'tennis'],
            'music': ['rock', 'pop', 'jazz', 'classique', 'rap', 'électro', 'métal',
                      'chanson', 'artiste', 'groupe', 'concert', 'album'],
            'work': ['programmation', 'développement', 'design', 'marketing',
                     'gestion', 'projet', 'équipe', 'bureau', 'réunion'],
            'color': ['rouge', 'bleu', 'vert', 'jaune', 'noir', 'blanc', 'rose',
                      'violet', 'orange', 'gris', 'couleur']
        }
        
        # Mots-clés pour événements
        self.event_keywords = {
            'past_action': ['ai fait', 'j\'ai', 'était', 'hier', 'la semaine dernière',
                            'le mois dernier', 'il y a', 'c\'était', 'avais'],
            'current_project': ['actuellement', 'en ce moment', 'travaille sur',
                                'suis en train de', 'occupe de', 'fais'],
            'future_goal': ['veux', 'voudrais', 'compte', 'projet de', 'prévois',
                            'envisage', 'demain', 'bientôt', 'plus tard', 'va']
        }
        
        # Mots-clés pour relations
        self.relationship_keywords = {
            'family': ['père', 'mère', 'frère', 'sœur', 'fils', 'fille', 'cousin',
                       'oncle', 'tante', 'grand-père', 'grand-mère', 'parent', 'famille'],
            'friend': ['ami', 'amie', 'copain', 'copine', 'pote', 'meilleur ami'],
            'colleague': ['collègue', 'patron', 'chef', 'manager', 'équipe', 'travaille avec'],
            'owns': ['a un', 'a une', 'possède', 'propriétaire de'],
            'works_at': ['travaille à', 'travaille chez', 'employé de', 'chez']
        }
    
    def extract_entities(self, message: str) -> List[Entity]:
        """
        Extrait les entités (noms, lieux, dates, organisations)
        
        Args:
            message: Message à analyser
            
        Returns:
            Liste d'entités extraites avec contexte
        """
        entities = []
        timestamp = datetime.utcnow().isoformat()
        
        # Extraction pour chaque type d'entité
        for entity_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, message, re.IGNORECASE)
            for match in matches:
                value = match.group(1) if match.lastindex else match.group(0)
                value = value.strip()
                
                # Filtrer les faux positifs (mots trop courts, mots communs)
                if len(value) < 2:
                    continue
                
                # Calculer confiance basée sur contexte
                confidence = self._calculate_entity_confidence(entity_type, value, message)
                
                entity = Entity(
                    entity_type=entity_type,
                    value=value,
                    context=message,
                    confidence=confidence,
                    first_seen=timestamp,
                    occurrences=1
                )
                entities.append(entity)
        
        return entities
    
    def extract_preferences(self, message: str) -> List[Preference]:
        """
        Extrait les préférences (aime/n'aime pas)
        
        Args:
            message: Message à analyser
            
        Returns:
            Liste de préférences extraites
        """
        preferences = []
        timestamp = datetime.utcnow().isoformat()
        message_lower = message.lower()
        
        # Détecter sentiment
        sentiment = 'neutral'
        intensity = 0.5
        
        for keyword in self.preference_keywords['positive']:
            if keyword in message_lower:
                sentiment = 'positive'
                intensity = 0.7 if 'adore' in message_lower or 'raffole' in message_lower else 0.6
                break
        
        for keyword in self.preference_keywords['negative']:
            if keyword in message_lower:
                sentiment = 'negative'
                intensity = 0.7 if 'déteste' in message_lower or 'horreur' in message_lower else 0.6
                break
        
        # Si aucun sentiment détecté, pas de préférence
        if sentiment == 'neutral':
            return []
        
        # Identifier catégorie et sujet
        category = 'general'
        subject = None
        
        for cat_name, keywords in self.preference_categories.items():
            for keyword in keywords:
                if keyword in message_lower:
                    category = cat_name
                    subject = keyword
                    break
            if subject:
                break
        
        # Si sujet trouvé, créer préférence
        if subject:
            preference = Preference(
                category=category,
                subject=subject,
                sentiment=sentiment,
                intensity=intensity,
                context=message,
                timestamp=timestamp
            )
            preferences.append(preference)
        
        return preferences
    
    def extract_events(self, message: str) -> List[Event]:
        """
        Extrait les événements (actions passées, projets, objectifs)
        
        Args:
            message: Message à analyser
            
        Returns:
            Liste d'événements extraits
        """
        events = []
        timestamp = datetime.utcnow().isoformat()
        message_lower = message.lower()
        
        # Détecter type d'événement
        event_type = None
        status = 'ongoing'
        
        for evt_type, keywords in self.event_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    event_type = evt_type
                    if evt_type == 'past_action':
                        status = 'completed'
                    elif evt_type == 'future_goal':
                        status = 'planned'
                    break
            if event_type:
                break
        
        # Si type détecté, créer événement
        if event_type:
            # Extraire participants (noms propres)
            participants = []
            person_matches = re.finditer(self.patterns['person'], message)
            for match in person_matches:
                participants.append(match.group(0))
            
            # Extraire lieu si présent
            location = None
            location_match = re.search(self.patterns['location'], message)
            if location_match:
                location = location_match.group(1)
            
            # Extraire référence temporelle
            time_reference = None
            date_match = re.search(self.patterns['date'], message, re.IGNORECASE)
            if date_match:
                time_reference = date_match.group(0)
            
            event = Event(
                event_type=event_type,
                description=message[:100] + '...' if len(message) > 100 else message,
                participants=participants,
                location=location,
                time_reference=time_reference,
                status=status,
                context=message,
                timestamp=timestamp
            )
            events.append(event)
        
        return events
    
    def extract_relationships(self, message: str) -> List[Relationship]:
        """
        Extrait les relations entre entités
        
        Args:
            message: Message à analyser
            
        Returns:
            Liste de relations extraites
        """
        relationships = []
        timestamp = datetime.utcnow().isoformat()
        message_lower = message.lower()
        
        # Détecter type de relation
        for rel_type, keywords in self.relationship_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    # Trouver sujet et objet autour du mot-clé
                    subject, object_entity = self._extract_relation_entities(message, keyword)
                    
                    if subject and object_entity:
                        confidence = 0.7  # Confiance moyenne pour relations
                        relationship = Relationship(
                            subject=subject,
                            relation_type=rel_type,
                            object=object_entity,
                            context=message,
                            confidence=confidence,
                            timestamp=timestamp
                        )
                        relationships.append(relationship)
                        break
        
        return relationships
    
    def extract_all_facts(self, message: str) -> Dict[str, List]:
        """
        Extrait tous les types de faits d'un message
        
        Args:
            message: Message à analyser
            
        Returns:
            Dictionnaire contenant toutes les extractions
        """
        return {
            'entities': [e.to_dict() for e in self.extract_entities(message)],
            'preferences': [p.to_dict() for p in self.extract_preferences(message)],
            'events': [e.to_dict() for e in self.extract_events(message)],
            'relationships': [r.to_dict() for r in self.extract_relationships(message)]
        }
    
    # --- Méthodes utilitaires privées ---
    
    def _calculate_entity_confidence(self, entity_type: str, value: str, context: str) -> float:
        """
        Calcule confiance pour une entité basée sur contexte
        
        Args:
            entity_type: Type d'entité ('person', 'location', etc.)
            value: Valeur extraite
            context: Contexte original
            
        Returns:
            Score de confiance 0.0-1.0
        """
        confidence = 0.5  # Confiance de base
        
        # Augmenter confiance si majuscule au début
        if value[0].isupper():
            confidence += 0.1
        
        # Augmenter si plusieurs mots (nom complet)
        if ' ' in value:
            confidence += 0.1
        
        # Augmenter si présence de mots indicateurs dans contexte
        indicators = {
            'person': ['rencontré', 'parlé avec', 'ami', 'collègue'],
            'location': ['visité', 'habite', 'voyage', 'ville'],
            'organization': ['travaille', 'entreprise', 'société', 'boîte']
        }
        
        if entity_type in indicators:
            for indicator in indicators[entity_type]:
                if indicator in context.lower():
                    confidence += 0.1
                    break
        
        return min(confidence, 1.0)  # Cap à 1.0
    
    def _extract_relation_entities(self, message: str, keyword: str) -> tuple:
        """
        Extrait sujet et objet autour d'un mot-clé de relation
        
        Args:
            message: Message complet
            keyword: Mot-clé de relation trouvé
            
        Returns:
            Tuple (sujet, objet) ou (None, None)
        """
        # Chercher mot-clé dans message
        keyword_index = message.lower().find(keyword.lower())
        if keyword_index == -1:
            return None, None
        
        # Extraire contexte avant/après mot-clé
        before = message[:keyword_index].strip()
        after = message[keyword_index + len(keyword):].strip()
        
        # Extraire dernier mot avant (sujet)
        subject_match = re.findall(r'\b(\w+)\s*$', before)
        subject = subject_match[0] if subject_match else None
        
        # Extraire premier mot après (objet)
        object_match = re.findall(r'^\s*(\w+)', after)
        object_entity = object_match[0] if object_match else None
        
        return subject, object_entity


# --- Exemple d'utilisation ---
if __name__ == "__main__":
    # Test basique
    extractor = FactExtractor()
    
    test_messages = [
        "J'adore la pizza et je déteste les brocolis.",
        "Hier j'ai rencontré Marie à Paris pour discuter du projet.",
        "Je travaille actuellement sur un nouveau système d'IA.",
        "Mon frère Pierre travaille chez Google à Londres."
    ]
    
    print("=== Test FactExtractor ===\n")
    for msg in test_messages:
        print(f"Message: {msg}")
        facts = extractor.extract_all_facts(msg)
        print(json.dumps(facts, indent=2, ensure_ascii=False))
        print("\n" + "-" * 50 + "\n")
