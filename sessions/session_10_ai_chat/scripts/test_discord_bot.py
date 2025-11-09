"""
Tests unitaires pour le Bot Discord (Kira)

Tests avec mocks pour simuler Discord sans connexion réelle.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import asyncio
from datetime import datetime

from src.discord_bot.bot import KiraDiscordBot, get_discord_bot
from src.ai.chat_engine import ChatResponse


# === Fixtures ===

@pytest.fixture
def mock_chat_engine():
    """Mock du ChatEngine"""
    engine = Mock()
    engine.chat = Mock(return_value=ChatResponse(
        response="Salut ! Comment ça va ? 😊",
        emotion="joy",
        tokens_used=10,
        context_messages=0,
        processing_time=0.5
    ))
    return engine


@pytest.fixture
def mock_emotion_analyzer():
    """Mock de l'EmotionAnalyzer"""
    analyzer = Mock()
    
    # Mock de la méthode analyze
    emotion_result = Mock()
    emotion_result.emotion = "joy"
    emotion_result.intensity = 75.0
    emotion_result.confidence = 85.0
    analyzer.analyze = Mock(return_value=emotion_result)
    
    # Mock de get_vrm_blendshape
    analyzer.get_vrm_blendshape = Mock(return_value={
        'blendshape': 'Joy',
        'value': 0.75,
        'recommended': True
    })
    
    return analyzer


@pytest.fixture
def mock_unity_bridge():
    """Mock du UnityBridge"""
    bridge = Mock()
    bridge.is_connected = Mock(return_value=True)
    bridge.set_expression = Mock(return_value=True)
    return bridge


@pytest.fixture
def mock_config():
    """Mock de la Config"""
    config = Mock()
    config.get = Mock(return_value={
        'auto_reply_enabled': True,
        'auto_reply_channels': [123456789],
        'rate_limit_seconds': 3
    })
    return config


@pytest.fixture
def bot(mock_chat_engine, mock_emotion_analyzer, mock_unity_bridge, mock_config):
    """Fixture du bot Discord mocké"""
    with patch('discord.Client.login', new_callable=AsyncMock):
        bot = KiraDiscordBot(
            chat_engine=mock_chat_engine,
            emotion_analyzer=mock_emotion_analyzer,
            unity_bridge=mock_unity_bridge,
            config=mock_config
        )
        # Patch bot.user (read-only property)
        mock_user = Mock()
        mock_user.id = 999999999
        mock_user.name = "Kira"
        with patch.object(type(bot), 'user', property(lambda self: mock_user)):
            yield bot


@pytest.fixture
def mock_message():
    """Mock d'un message Discord"""
    message = Mock()
    message.author = Mock()
    message.author.id = 123456
    message.author.name = "TestUser"
    message.author.bot = False
    message.channel = Mock()
    message.channel.id = 123456789
    message.channel.name = "general"
    message.channel.send = AsyncMock()
    message.channel.typing = Mock()
    message.channel.typing.return_value.__aenter__ = AsyncMock()
    message.channel.typing.return_value.__aexit__ = AsyncMock()
    message.content = "Bonjour Kira !"
    return message


# === Tests Initialisation ===

def test_bot_initialization(mock_chat_engine, mock_emotion_analyzer, mock_unity_bridge, mock_config):
    """Test initialisation du bot"""
    bot = KiraDiscordBot(
        chat_engine=mock_chat_engine,
        emotion_analyzer=mock_emotion_analyzer,
        unity_bridge=mock_unity_bridge,
        config=mock_config
    )
    
    assert bot.chat_engine == mock_chat_engine
    assert bot.emotion_analyzer == mock_emotion_analyzer
    assert bot.unity_bridge == mock_unity_bridge
    assert bot.auto_reply_enabled is True
    assert 123456789 in bot.auto_reply_channels
    assert bot.rate_limit_seconds == 3


def test_bot_initialization_defaults():
    """Test initialisation avec valeurs par défaut (singletons)"""
    with patch('src.discord_bot.bot.get_chat_engine'):
        with patch('src.discord_bot.bot.get_emotion_analyzer'):
            with patch('src.discord_bot.bot.UnityBridge'):
                with patch('src.discord_bot.bot.Config'):
                    bot = KiraDiscordBot()
                    assert bot.chat_engine is not None
                    assert bot.emotion_analyzer is not None


# === Tests on_ready ===

@pytest.mark.asyncio
async def test_on_ready(bot):
    """Test event on_ready"""
    # Mock guilds (read-only)
    mock_guilds = [Mock(name="Test Server", id=111)]
    bot.change_presence = AsyncMock()
    
    with patch.object(type(bot), 'guilds', property(lambda self: mock_guilds)):
        await bot.on_ready()
        
        # Vérifier que change_presence a été appelé
        bot.change_presence.assert_called_once()


# === Tests on_message ===

@pytest.mark.asyncio
async def test_on_message_ignores_own_messages(bot, mock_message):
    """Test que le bot ignore ses propres messages"""
    mock_message.author = bot.user
    
    await bot.on_message(mock_message)
    
    # Aucune réponse envoyée
    mock_message.channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_on_message_ignores_bot_messages(bot, mock_message):
    """Test que le bot ignore les messages d'autres bots"""
    mock_message.author.bot = True
    
    await bot.on_message(mock_message)
    
    mock_message.channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_on_message_with_mention(bot, mock_message):
    """Test réponse à une mention @Kira"""
    # Simuler mention
    bot.user.mentioned_in = Mock(return_value=True)
    mock_message.content = f"<@{bot.user.id}> Bonjour !"
    
    await bot.on_message(mock_message)
    
    # Vérifier que réponse envoyée
    mock_message.channel.send.assert_called_once()
    
    # Vérifier que ChatEngine appelé
    bot.chat_engine.chat.assert_called_once()


@pytest.mark.asyncio
async def test_on_message_auto_reply_in_configured_channel(bot, mock_message):
    """Test auto-reply dans canal configuré"""
    bot.auto_reply_enabled = True
    bot.auto_reply_channels = [mock_message.channel.id]
    bot.user.mentioned_in = Mock(return_value=False)
    
    await bot.on_message(mock_message)
    
    # Vérifier que réponse envoyée
    mock_message.channel.send.assert_called_once()


@pytest.mark.asyncio
async def test_on_message_no_reply_in_non_configured_channel(bot, mock_message):
    """Test pas de réponse dans canal non configuré"""
    bot.auto_reply_enabled = True
    bot.auto_reply_channels = [999999]  # Autre canal
    bot.user.mentioned_in = Mock(return_value=False)
    mock_message.channel.id = 111111
    
    await bot.on_message(mock_message)
    
    # Aucune réponse
    mock_message.channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_on_message_rate_limiting(bot, mock_message):
    """Test rate limiting entre messages"""
    bot.user.mentioned_in = Mock(return_value=True)
    bot.rate_limit_seconds = 10  # 10 secondes
    
    # Premier message → OK
    await bot.on_message(mock_message)
    assert mock_message.channel.send.call_count == 1
    
    # Deuxième message immédiat → Ignoré (rate limit)
    mock_message.channel.send.reset_mock()
    await bot.on_message(mock_message)
    mock_message.channel.send.assert_not_called()


# === Tests Méthodes Privées ===

def test_should_reply_to_message_with_mention(bot, mock_message):
    """Test _should_reply_to_message avec mention"""
    bot.user.mentioned_in = Mock(return_value=True)
    
    assert bot._should_reply_to_message(mock_message) is True


def test_should_reply_to_message_auto_reply(bot, mock_message):
    """Test _should_reply_to_message avec auto-reply"""
    bot.user.mentioned_in = Mock(return_value=False)
    bot.auto_reply_enabled = True
    bot.auto_reply_channels = [mock_message.channel.id]
    
    assert bot._should_reply_to_message(mock_message) is True


def test_should_reply_to_message_no_reason(bot, mock_message):
    """Test _should_reply_to_message sans raison"""
    bot.user.mentioned_in = Mock(return_value=False)
    bot.auto_reply_enabled = False
    
    assert bot._should_reply_to_message(mock_message) is False


def test_check_rate_limit_first_message(bot):
    """Test rate limit pour premier message"""
    user_id = 123
    
    assert bot._check_rate_limit(user_id) is True
    assert user_id in bot.last_response_time


def test_check_rate_limit_too_fast(bot):
    """Test rate limit message trop rapide"""
    user_id = 123
    bot.rate_limit_seconds = 10
    
    # Premier message
    assert bot._check_rate_limit(user_id) is True
    
    # Deuxième immédiat
    assert bot._check_rate_limit(user_id) is False


def test_clean_prompt(bot):
    """Test nettoyage du prompt"""
    bot.user.id = 999
    
    # Avec mention
    content = f"<@{bot.user.id}> Bonjour Kira !"
    cleaned = bot._clean_prompt(content)
    assert "Bonjour Kira !" in cleaned
    assert "<@" not in cleaned


@pytest.mark.asyncio
async def test_generate_response(bot):
    """Test génération de réponse complète"""
    response = await bot._generate_response(
        prompt="Bonjour",
        user_id="123",
        username="TestUser"
    )
    
    assert response == "Salut ! Comment ça va ? 😊"
    
    # Vérifier appels
    bot.chat_engine.chat.assert_called_once()
    bot.emotion_analyzer.analyze.assert_called_once()


def test_send_emotion_to_unity_connected(bot):
    """Test envoi émotion à Unity (connecté)"""
    bot._send_emotion_to_unity("joy", 75.0)
    
    # Vérifier appels
    bot.unity_bridge.is_connected.assert_called_once()
    bot.emotion_analyzer.get_vrm_blendshape.assert_called_once_with("joy", 75.0)
    bot.unity_bridge.set_expression.assert_called_once()


def test_send_emotion_to_unity_not_connected(bot):
    """Test envoi émotion à Unity (non connecté)"""
    bot.unity_bridge.is_connected = Mock(return_value=False)
    
    bot._send_emotion_to_unity("joy", 75.0)
    
    # Pas d'appel set_expression
    bot.unity_bridge.set_expression.assert_not_called()


# === Tests Statistiques ===

def test_get_stats(bot):
    """Test récupération statistiques"""
    bot.messages_processed = 10
    bot.responses_sent = 8
    
    # Mock guilds (read-only) et is_ready
    mock_guilds = [Mock(), Mock()]
    with patch.object(type(bot), 'guilds', property(lambda self: mock_guilds)):
        with patch.object(bot, 'is_ready', return_value=True):
            stats = bot.get_stats()
            
            assert stats['messages_processed'] == 10
            assert stats['responses_sent'] == 8
            assert stats['guilds'] == 2
            assert stats['auto_reply_enabled'] is True
            assert 'uptime_seconds' in stats


# === Tests Singleton ===

def test_get_discord_bot_singleton():
    """Test que get_discord_bot retourne singleton"""
    with patch('src.discord_bot.bot.KiraDiscordBot'):
        bot1 = get_discord_bot()
        bot2 = get_discord_bot()
        
        # Même instance
        assert bot1 is bot2


# === Tests Erreurs ===

@pytest.mark.asyncio
async def test_on_message_handles_chat_engine_error(bot, mock_message):
    """Test gestion erreur ChatEngine"""
    bot.user.mentioned_in = Mock(return_value=True)
    bot.chat_engine.chat = Mock(side_effect=Exception("Erreur test"))
    
    await bot.on_message(mock_message)
    
    # Message d'erreur envoyé
    mock_message.channel.send.assert_called_once()
    sent_message = mock_message.channel.send.call_args[0][0]
    assert "erreur" in sent_message.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
