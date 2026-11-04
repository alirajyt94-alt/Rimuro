import os
import sys
import random
import datetime
import io
import asyncio
import base64
import re
import json
import logging
from typing import cast

from dotenv import load_dotenv
load_dotenv()  # Load settings from a local .env file, if present.

# Now import the modules
import discord
from discord.ext import commands, tasks
import random
import datetime
from discord.ui import Button, View, Select
import wavelink
import io
import aiohttp
from typing import cast
import asyncio
import base64
import re
import json

from music_database import MusicDatabase

# Custom emoji configuration
class EmojiConfig:
    def __init__(self):
        self.load_emojis()

    def load_emojis(self):
        """Load emojis from emoji_config.json"""
        try:
            with open('emoji_config.json', 'r', encoding='utf-8') as f:
                emoji_data = json.load(f)

            # Music Control Emojis
            self.PLAY = emoji_data['music_control']['play']
            self.PAUSE = emoji_data['music_control']['pause']
            self.RESUME = emoji_data['music_control']['resume']
            self.STOP = emoji_data['music_control']['stop']
            self.SKIP = emoji_data['music_control']['skip']
            self.PREVIOUS = emoji_data['music_control']['previous']
            self.REPEAT = emoji_data['music_control']['repeat']
            self.REPEAT_ONE = emoji_data['music_control']['repeat_one']
            self.SHUFFLE = emoji_data['music_control']['shuffle']

            # Volume Emojis
            self.VOLUME_UP = emoji_data['volume']['volume_up']
            self.VOLUME_DOWN = emoji_data['volume']['volume_down']
            self.VOLUME_MUTE = emoji_data['volume']['volume_mute']
            self.VOLUME_LOW = emoji_data['volume']['volume_low']
            self.VOLUME_HIGH = emoji_data['volume']['volume_high']

            # Status Emojis
            self.SUCCESS = emoji_data['status']['success']
            self.ERROR = emoji_data['status']['error']
            self.WARNING = emoji_data['status']['warning']
            self.INFO = emoji_data['status']['info']
            self.LOADING = emoji_data['status']['loading']
            self.SEARCH = emoji_data['status']['search']

            # Music Source Emojis
            self.SPOTIFY = emoji_data['music_sources']['spotify']
            self.YOUTUBE = emoji_data['music_sources']['youtube']
            self.SOUNDCLOUD = emoji_data['music_sources']['soundcloud']

            # Feature Emojis
            self.FILTER = emoji_data['features']['filter']
            self.EQUALIZER = emoji_data['features']['equalizer']
            self.HEADPHONES = emoji_data['features']['headphones']
            self.MICROPHONE = emoji_data['features']['microphone']
            self.MUSICAL_NOTE = emoji_data['features']['musical_note']
            self.MUSICAL_NOTES = emoji_data['features']['musical_notes']
            self.RADIO = emoji_data['features']['radio']
            self.STAR = emoji_data['features']['star']
            self.KEY = emoji_data['features']['key']
            self.QUALITY = emoji_data['features']['quality']

            # Platform Emojis
            self.YOUTUBE_PLATFORM = emoji_data['platforms']['youtube_platform']
            self.SOUNDCLOUD_PLATFORM = emoji_data['platforms']['soundcloud_platform']

            # Control Panel Emojis
            self.SETTINGS = emoji_data['control_panel']['settings']
            self.DASHBOARD = emoji_data['control_panel']['dashboard']
            self.QUEUE = emoji_data['control_panel']['queue']
            self.HISTORY = emoji_data['control_panel']['history']

            # Action Emojis
            self.ADD = emoji_data['actions']['add']
            self.REMOVE = emoji_data['actions']['remove']
            self.CLEAR = emoji_data['actions']['clear']
            self.DOWNLOAD = emoji_data['actions']['download']
            self.UPLOAD = emoji_data['actions']['upload']

            # Time Emojis
            self.CLOCK = emoji_data['time']['clock']
            self.HOURGLASS = emoji_data['time']['hourglass']
            self.TIMER = emoji_data['time']['timer']

            print("✅ Emojis loaded from emoji_config.json")
        except FileNotFoundError:
            print("⚠️ emoji_config.json not found, using default emojis")
            self.load_default_emojis()
        except Exception as e:
            print(f"⚠️ Error loading emojis: {e}, using defaults")
            self.load_default_emojis()

    def load_default_emojis(self):
        """Fallback to default Unicode emojis"""
        # Music Control Emojis
        self.PLAY = "▶️"
        self.PAUSE = "⏸️"
        self.RESUME = "▶️"
        self.STOP = "⏹️"
        self.SKIP = "⏭️"
        self.PREVIOUS = "⏮️"
        self.REPEAT = "🔁"
        self.REPEAT_ONE = "🔂"
        self.SHUFFLE = "🔀"

        # Volume Emojis
        self.VOLUME_UP = "🔊"
        self.VOLUME_DOWN = "🔉"
        self.VOLUME_MUTE = "🔇"
        self.VOLUME_LOW = "🔈"
        self.VOLUME_HIGH = "🔊"

        # Status Emojis
        self.SUCCESS = "✅"
        self.ERROR = "❌"
        self.WARNING = "⚠️"
        self.INFO = "ℹ️"
        self.LOADING = "⏳"
        self.SEARCH = "🔍"

        # Music Source Emojis
        self.SPOTIFY = "🎧"
        self.YOUTUBE = "▶️"
        self.SOUNDCLOUD = "☁️"

        # Feature Emojis
        self.FILTER = "🎛️"
        self.EQUALIZER = "🎚️"
        self.HEADPHONES = "🎧"
        self.MICROPHONE = "🎤"
        self.MUSICAL_NOTE = "🎵"
        self.MUSICAL_NOTES = "🎶"
        self.RADIO = "📻"
        self.STAR = "⭐"
        self.KEY = "🔑"
        self.QUALITY = "💎"

        # Platform Emojis
        self.YOUTUBE_PLATFORM = "▶️"
        self.SOUNDCLOUD_PLATFORM = "☁️"

        # Control Panel Emojis
        self.SETTINGS = "⚙️"
        self.DASHBOARD = "📊"
        self.QUEUE = "📜"
        self.HISTORY = "📋"

        # Action Emojis
        self.ADD = "➕"
        self.REMOVE = "➖"
        self.CLEAR = "🗑️"
        self.DOWNLOAD = "📥"
        self.UPLOAD = "📤"

        # Time Emojis
        self.CLOCK = "🕒"
        self.HOURGLASS = "⏳"
        self.TIMER = "⏰"

# Custom response messages
class ResponseMessages:
    # Success Messages
    TRACK_ADDED = "🎵 **Track Added**\n`{track}` has been added to the queue!"
    TRACK_PLAYING = "🎶 **Now Playing**\n`{track}` is now playing!"
    QUEUE_CLEARED = "🗑️ **Queue Cleared**\nThe queue has been cleared successfully!"
    VOLUME_SET = "🔊 **Volume Adjusted**\nVolume set to `{volume}%`!"
    FILTER_APPLIED = "🎛️ **Filter Applied**\n`{filter}` filter has been enabled!"
    FILTER_REMOVED = "🎛️ **Filter Removed**\nAll filters have been disabled!"

    # Error Messages
    NOT_IN_VOICE = "❌ **Voice Channel Required**\nYou need to be in a voice channel to use this command!"
    BOT_NOT_IN_VOICE = "❌ **Bot Not Connected**\nI'm not connected to any voice channel!"
    DIFFERENT_VOICE_CHANNEL = "❌ **Wrong Voice Channel**\nYou must be in the same voice channel as me!"
    NO_TRACK_PLAYING = "❌ **No Track Playing**\nThere's no music currently playing!"
    QUEUE_EMPTY = "📜 **Queue Empty**\nThe queue is currently empty!"
    NO_RESULTS = "🔍 **No Results Found**\nNo tracks found for your search query!"

    # Info Messages
    QUEUE_INFO = "📊 **Queue Information**\nCurrently `{count}` tracks in queue!"
    NOW_PLAYING = "🎵 **Now Playing**\n`{track}` by `{artist}`"
    PLAYER_PAUSED = "⏸️ **Player Paused**\nPlayback has been paused!"
    PLAYER_RESUMED = "▶️ **Player Resumed**\nPlayback has been resumed!"
    TRACK_SKIPPED = "⏭️ **Track Skipped**\nSkipped to the next track!"

    # Warning Messages
    INACTIVITY_WARNING = "⚠️ **Inactivity Warning**\nI'll disconnect in 2 minutes if no one is listening!"

# YouTube API Key Manager
class YouTubeAPIManager:
    def __init__(self, config_file="bot_config.json"):
        self.config_file = config_file
        self.api_key = None
        self.load_api_key()

    def load_api_key(self):
        """Load YouTube API key from config"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.api_key = config.get('youtube_api_key') or os.environ.get('YOUTUBE_API_KEY')
        except FileNotFoundError:
            self.api_key = os.environ.get('YOUTUBE_API_KEY')
            if not self.api_key:
                print("⚠️ WARNING: YOUTUBE_API_KEY not set in environment variables")

    def save_config(self, config):
        """Save config to file"""
        try:
            existing_config = {}
            try:
                with open(self.config_file, 'r') as f:
                    existing_config = json.load(f)
            except FileNotFoundError:
                pass

            existing_config.update(config)

            with open(self.config_file, 'w') as f:
                json.dump(existing_config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def set_api_key(self, api_key):
        """Set YouTube API key"""
        self.api_key = api_key
        self.save_config({'youtube_api_key': api_key})
        return True

    def get_api_key(self):
        """Get YouTube API key"""
        return self.api_key

    def has_api_key(self):
        """Check if API key is set"""
        return bool(self.api_key and self.api_key.strip())

# Custom imports with fallbacks
try:
    from utils import Paginator, DescriptionEmbedPaginator
    from core import Cog, axon, Context
    from utils.Tools import *
except ImportError:
    # Create basic fallback classes if custom modules aren't available
    class Paginator:
        def __init__(self, source, ctx):
            self.source = source
            self.ctx = ctx

        async def paginate(self):
            await self.ctx.send("Paginator not available - showing first page only")
            entries = self.source.entries[:10]
            embed = discord.Embed(title=self.source.title, description="\n".join(entries), color=self.source.color)
            await self.ctx.send(embed=embed)

    class DescriptionEmbedPaginator:
        def __init__(self, entries, title, description, per_page, color):
            self.entries = entries
            self.title = title
            self.description = description
            self.per_page = per_page
            self.color = color

    class Cog(commands.Cog):
        pass

    class axon(commands.Bot):
        pass

    class Context(commands.Context):
        pass

    def blacklist_check():
        def predicate(ctx):
            return True
        return commands.check(predicate)

    def ignore_check():
        def predicate(ctx):
            return True
        return commands.check(predicate)

# Initialize track histories and YouTube API manager
track_histories = {}
youtube_api = YouTubeAPIManager()

SPOTIFY_TRACK_REGEX = r"https?://open\.spotify\.com/track/([a-zA-Z0-9]+)"
SPOTIFY_PLAYLIST_REGEX = r"https?://open\.spotify\.com/playlist/([a-zA-Z0-9]+)"
SPOTIFY_ALBUM_REGEX = r"https?://open\.spotify\.com/album/([a-zA-Z0-9]+)"

class SpotifyAPI:
    BASE_URL = "https://api.spotify.com/v1"

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None

    async def get_token(self):
        auth_url = "https://accounts.spotify.com/api/token"
        auth_value = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode('utf-8')).decode('utf-8')
        headers = {"Authorization": f"Basic {auth_value}"}
        data = {"grant_type": "client_credentials"}
        async with aiohttp.ClientSession() as session:
            async with session.post(auth_url, headers=headers, data=data) as response:
                text = await response.text()
                if response.status != 200:
                    raise Exception(f"Failed to fetch token: {response.status}, response: {text}")
                result = await response.json()
                self.token = result.get("access_token")

    async def get(self, endpoint, params=None):
        retries = 2
        for attempt in range(retries):
            if not self.token or attempt > 0:
                await self.get_token()

            url = f"{self.BASE_URL}/{endpoint}"
            headers = {"Authorization": f"Bearer {self.token}"}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 401 and attempt < retries - 1:
                        continue
                    elif response.status != 200:
                        raise Exception(f"Failed to fetch data from Spotify: {response.status}")
                    return await response.json()
        raise Exception("Exceeded max retries to fetch Spotify data")

    async def get_track(self, track_id):
        return await self.get(f"tracks/{track_id}")

    async def get_playlist(self, playlist_id):
        return await self.get(f"playlists/{playlist_id}")

# Load Spotify credentials from config or environment
try:
    with open('bot_config.json', 'r') as f:
        config = json.load(f)
        spotify_client_id = config.get('spotify_client_id') or os.environ.get("SPOTIFY_CLIENT_ID")
        spotify_client_secret = config.get('spotify_client_secret') or os.environ.get("SPOTIFY_CLIENT_SECRET")
except FileNotFoundError:
    spotify_client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    spotify_client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")

if not spotify_client_id or not spotify_client_secret:
    print("⚠️ WARNING: SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET not set in config or environment variables")
    print("   Spotify features will be disabled until credentials are provided")
    spotify_api = None
else:
    spotify_api = SpotifyAPI(client_id=spotify_client_id, client_secret=spotify_client_secret)
    print("✅ Spotify API initialized successfully")

# Store active player messages to delete them when new music plays
active_player_messages = {}

# Vote system configuration - REMOVED TOP.GG VOTE SYSTEM
OWNER_ID = 1007467674143571988

class UltraAdvancedMusicControlView(View):
    def __init__(self, player, ctx):
        super().__init__(timeout=300)
        self.player = player
        self.ctx = ctx
        self.emoji = EmojiConfig()
        self.setup_buttons()

    def setup_buttons(self):
        # Row 1: Main Playback Controls (5 buttons) - Clean navigation
        self.add_item(Button(emoji="⏮️", style=discord.ButtonStyle.secondary, custom_id="previous", row=0, label="Previous"))
        self.add_item(Button(emoji="⏸️", style=discord.ButtonStyle.primary, custom_id="pause_resume", row=0, label="Pause/Resume"))
        self.add_item(Button(emoji="⏹️", style=discord.ButtonStyle.danger, custom_id="stop", row=0, label="Stop"))
        self.add_item(Button(emoji="⏭️", style=discord.ButtonStyle.secondary, custom_id="skip", row=0, label="Skip"))
        self.add_item(Button(emoji="🔄", style=discord.ButtonStyle.secondary, custom_id="replay", row=0, label="Replay"))

        # Row 2: Seek & Speed Controls (5 buttons) - Time manipulation
        self.add_item(Button(emoji="⏪", style=discord.ButtonStyle.secondary, custom_id="rewind", row=1, label="-30s"))
        self.add_item(Button(emoji="🐌", style=discord.ButtonStyle.secondary, custom_id="speed_075", row=1, label="0.75x"))
        self.add_item(Button(emoji="⏲️", style=discord.ButtonStyle.primary, custom_id="seek_menu", row=1, label="Seek"))
        self.add_item(Button(emoji="⚡", style=discord.ButtonStyle.secondary, custom_id="speed_125", row=1, label="1.25x"))
        self.add_item(Button(emoji="⏩", style=discord.ButtonStyle.secondary, custom_id="forward", row=1, label="+30s"))

        # Row 3: Volume & Loop Controls (5 buttons) - Audio settings
        self.add_item(Button(emoji="🔇", style=discord.ButtonStyle.secondary, custom_id="mute", row=2, label="Mute"))
        self.add_item(Button(emoji="🔉", style=discord.ButtonStyle.primary, custom_id="vol_down", row=2, label="Vol -"))
        self.add_item(Button(emoji="🔁", style=discord.ButtonStyle.success, custom_id="loop", row=2, label="Loop Queue"))
        self.add_item(Button(emoji="🔊", style=discord.ButtonStyle.primary, custom_id="vol_up", row=2, label="Vol +"))
        self.add_item(Button(emoji="🔂", style=discord.ButtonStyle.success, custom_id="loop_track", row=2, label="Loop Track"))

        # Row 4: Queue Management (5 buttons) - Playlist controls
        self.add_item(Button(emoji="📜", style=discord.ButtonStyle.secondary, custom_id="show_queue", row=3, label="Queue"))
        self.add_item(Button(emoji="🔀", style=discord.ButtonStyle.success, custom_id="shuffle", row=3, label="Shuffle"))
        self.add_item(Button(emoji="🎵", style=discord.ButtonStyle.primary, custom_id="add_track", row=3, label="Add Track"))
        self.add_item(Button(emoji="💾", style=discord.ButtonStyle.success, custom_id="save_playlist", row=3, label="Save"))
        self.add_item(Button(emoji="🗑️", style=discord.ButtonStyle.danger, custom_id="clear_queue", row=3, label="Clear"))

        # Row 5: Effects & Info (5 buttons) - Advanced features
        self.add_item(Button(emoji="🎛️", style=discord.ButtonStyle.secondary, custom_id="filter_menu", row=4, label="Filters"))
        self.add_item(Button(emoji="🧹", style=discord.ButtonStyle.danger, custom_id="clear_effects", row=4, label="Clear Effects"))
        self.add_item(Button(emoji="📊", style=discord.ButtonStyle.primary, custom_id="stats", row=4, label="Stats"))
        self.add_item(Button(emoji="💎", style=discord.ButtonStyle.success, custom_id="quality_info", row=4, label="Quality"))
        self.add_item(Button(emoji="🔧", style=discord.ButtonStyle.secondary, custom_id="settings", row=4, label="Settings"))

        # Attach callbacks to all buttons
        for item in self.children:
            if isinstance(item, Button):
                item.callback = self.button_callback

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not self.ctx.voice_client:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"{self.emoji.ERROR} Player Not Active",
                    description="I'm not currently in a voice channel.",
                    color=0xFF0000
                ), ephemeral=True
            )
            return False
        if interaction.user in self.ctx.voice_client.channel.members:
            return True
        await interaction.response.send_message(
            embed=discord.Embed(
                title=f"{self.emoji.ERROR} Permission Denied",
                description="Only members in the same voice channel can control the player.",
                color=0xFF0000
            ), ephemeral=True
        )
        return False

    async def button_callback(self, interaction: discord.Interaction):
        button_id = interaction.data["custom_id"]

        actions = {
            "pause_resume": self.pause_resume,
            "skip": self.skip,
            "previous": self.previous,
            "rewind": self.rewind,
            "forward": self.forward,
            "loop": self.loop,
            "shuffle": self.shuffle,
            "vol_down": self.volume_down,
            "vol_up": self.volume_up,
            "filter_menu": self.filter_menu,
            "show_queue": self.show_queue,
            "clear_queue": self.clear_queue,
            "equalizer": self.equalizer_menu,
            "save_playlist": self.save_playlist,
            "stop": self.stop,
            "speed_075": self.speed_075,
            "speed_125": self.speed_125,
            "loop_track": self.loop_track,
            "replay": self.replay,
            "stats": self.stats,
            "quality_info": self.quality_info,
            "mute": self.mute,
            "seek_menu": self.seek_menu,
            "add_track": self.add_track,
            "settings": self.settings,
            "clear_effects": self.clear_effects
        }

        if button_id in actions:
            await actions[button_id](interaction)

    async def pause_resume(self, interaction: discord.Interaction):
        if not self.player.playing and not self.player.paused:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"{self.emoji.ERROR} No Music Playing",
                    description="There's no music currently playing!",
                    color=0xFF0000
                ), ephemeral=True
            )
            return
        if self.player.paused:
            await self.player.pause(False)
            embed = discord.Embed(
                title=f"{self.emoji.SUCCESS} Playback Resumed",
                description=f"**{self.player.current.title}** has been resumed!",
                color=0x1DB954
            )
        else:
            await self.player.pause(True)
            embed = discord.Embed(
                title=f"{self.emoji.PAUSE} Playback Paused",
                description=f"**{self.player.current.title}** has been paused!",
                color=0xFFA500
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def skip(self, interaction: discord.Interaction):
        if not self.player.playing:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"{self.emoji.ERROR} No Music Playing",
                    description="There's no music currently playing!",
                    color=0xFF0000
                ), ephemeral=True
            )
            return
        await self.player.stop()
        await interaction.response.send_message(
            embed=discord.Embed(
                title=f"{self.emoji.SKIP} Track Skipped",
                description=f"Skipped by **{interaction.user.display_name}**!",
                color=0x1DB954
            ), ephemeral=True
        )

    async def previous(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id in track_histories and track_histories[guild_id]:
            previous_track = track_histories[guild_id].pop()
            await self.player.play(previous_track)
            embed = discord.Embed(
                title=f"{self.emoji.PREVIOUS} Playing Previous Track",
                description=f"**{previous_track.title}**",
                color=0x1DB954
            )
        else:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} No Previous Track",
                description="There's no previous track in history!",
                color=0xFF0000
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def rewind(self, interaction: discord.Interaction):
        if not self.player.playing:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"{self.emoji.ERROR} No Music Playing",
                    description="There's no music currently playing!",
                    color=0xFF0000
                ), ephemeral=True
            )
            return
        new_position = max(0, self.player.position - 30000)
        await self.player.seek(new_position)
        await interaction.response.send_message(
            embed=discord.Embed(
                title="⏪ Rewinded",
                description=f"Rewinded 30 seconds in **{self.player.current.title}**!",
                color=0x1DB954
            ), ephemeral=True
        )

    async def forward(self, interaction: discord.Interaction):
        if not self.player.playing:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"{self.emoji.ERROR} No Music Playing",
                    description="There's no music currently playing!",
                    color=0xFF0000
                ), ephemeral=True
            )
            return
        new_position = min(self.player.current.length, self.player.position + 30000)
        await self.player.seek(new_position)
        await interaction.response.send_message(
            embed=discord.Embed(
                title="⏩ Forwarded",
                description=f"Forwarded 30 seconds in **{self.player.current.title}**!",
                color=0x1DB954
            ), ephemeral=True
        )

    async def loop(self, interaction: discord.Interaction):
        self.player.queue.mode = wavelink.QueueMode.loop_all if self.player.queue.mode != wavelink.QueueMode.loop_all else wavelink.QueueMode.normal
        mode = "enabled" if self.player.queue.mode == wavelink.QueueMode.loop else "disabled"
        await interaction.response.send_message(
            embed=discord.Embed(
                title=f"{self.emoji.REPEAT} Loop {mode.title()}",
                description=f"Loop mode has been **{mode}**!",
                color=0x1DB954 if mode == "enabled" else 0xFFA500
            ), ephemeral=True
        )

    async def shuffle(self, interaction: discord.Interaction):
        if self.player.queue and not self.player.queue.is_empty:
            queued_tracks = list(self.player.queue)
            random.shuffle(queued_tracks)
            self.player.queue.clear()
            await self.player.queue.put_wait(queued_tracks)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"{self.emoji.SHUFFLE} Queue Shuffled",
                    description=f"Queue has been shuffled!",
                    color=0x1DB954
                ), ephemeral=True
            )
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"{self.emoji.ERROR} Queue Empty",
                    description="The queue is currently empty!",
                    color=0xFF0000
                ), ephemeral=True
            )

    async def volume_down(self, interaction: discord.Interaction):
        current_volume = self.player.volume
        new_volume = max(0, current_volume - 20)
        await self.player.set_volume(new_volume)
        await interaction.response.send_message(
            embed=discord.Embed(
                title=f"{self.emoji.VOLUME_DOWN} Volume Decreased",
                description=f"Volume: `{current_volume}%` → `{new_volume}%`",
                color=0x1DB954
            ), ephemeral=True
        )

    async def volume_up(self, interaction: discord.Interaction):
        current_volume = self.player.volume
        new_volume = min(200, current_volume + 20)
        await self.player.set_volume(new_volume)
        await interaction.response.send_message(
            embed=discord.Embed(
                title=f"{self.emoji.VOLUME_UP} Volume Increased",
                description=f"Volume: `{current_volume}%` → `{new_volume}%`",
                color=0x1DB954
            ), ephemeral=True
        )

    async def filter_menu(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=discord.Embed(
                title=f"{self.emoji.FILTER} Audio Filters",
                description="Select an audio filter to apply:",
                color=0x1DB954
            ),
            view=FilterSelectView(self.player, self.ctx),
            ephemeral=True
        )

    async def equalizer_menu(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=discord.Embed(
                title="🎚️ Equalizer Presets",
                description="Select an equalizer preset:",
                color=0x1DB954
            ),
            view=EqualizerView(self.player, self.ctx),
            ephemeral=True
        )

    async def show_queue(self, interaction: discord.Interaction):
        if not self.player.queue or self.player.queue.is_empty:
            embed = discord.Embed(
                title=f"{self.emoji.QUEUE} Queue Empty",
                description="The queue is currently empty!",
                color=0xFFA500
            )
        else:
            tracks = list(self.player.queue)[:10]
            queue_text = "\n".join([f"`{i+1}.` **{track.title[:40]}**" for i, track in enumerate(tracks)])
            embed = discord.Embed(
                title=f"{self.emoji.QUEUE} Current Queue",
                description=queue_text,
                color=0x1DB954
            )
            if len(self.player.queue) > 10:
                embed.set_footer(text=f"And {len(self.player.queue) - 10} more tracks...")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def clear_queue(self, interaction: discord.Interaction):
        if self.player.queue.is_empty:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"{self.emoji.WARNING} Queue Already Empty",
                    description="The queue is already empty!",
                    color=0xFFA500
                ), ephemeral=True
            )
        else:
            queue_count = len(self.player.queue)
            self.player.queue.clear()
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"{self.emoji.CLEAR} Queue Cleared",
                    description=f"Cleared `{queue_count}` tracks!",
                    color=0x1DB954
                ), ephemeral=True
            )

    async def save_playlist(self, interaction: discord.Interaction):
        if self.player.queue.is_empty:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"{self.emoji.ERROR} Queue Empty",
                    description="There are no tracks in the queue to save!",
                    color=0xFF0000
                ), ephemeral=True
            )
            return
        await interaction.response.send_message(
            embed=discord.Embed(
                title="💾 Save Playlist",
                description="Save the current queue as a playlist:",
                color=0x1DB954
            ),
            view=PlaylistSaveView(self.player.queue, interaction.user.id),
            ephemeral=True
        )

    async def stop(self, interaction: discord.Interaction):
        if self.player:
            guild_id = interaction.guild.id
            if guild_id in active_player_messages:
                try:
                    await active_player_messages[guild_id].delete()
                    del active_player_messages[guild_id]
                except:
                    pass
            await self.player.disconnect()
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"{self.emoji.STOP} Playback Stopped",
                    description="Music playback has been stopped!",
                    color=0x1DB954
                )
            )
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"{self.emoji.ERROR} Not Connected",
                    description="I'm not connected to any voice channel!",
                    color=0xFF0000
                )
            )

    async def speed_075(self, interaction: discord.Interaction):
        filters = wavelink.Filters()
        filters.timescale.set(speed=0.75)
        await self.player.set_filters(filters)
        await interaction.response.send_message(
            embed=discord.Embed(
                title="🐌 Playback Speed Set",
                description="Playback speed set to **0.75x**",
                color=0x1DB954
            ), ephemeral=True
        )

    async def speed_125(self, interaction: discord.Interaction):
        filters = wavelink.Filters()
        filters.timescale.set(speed=1.25)
        await self.player.set_filters(filters)
        await interaction.response.send_message(
            embed=discord.Embed(
                title="⚡ Playback Speed Set",
                description="Playback speed set to **1.25x**",
                color=0x1DB954
            ), ephemeral=True
        )

    async def clear_effects(self, interaction: discord.Interaction):
        filters = wavelink.Filters()
        await self.player.set_filters(filters)
        await interaction.response.send_message(
            embed=discord.Embed(
                title="🧹 All Effects Cleared",
                description="All audio filters and effects have been removed!\nPlayback restored to normal speed and quality.",
                color=0x1DB954
            ), ephemeral=True
        )

    async def loop_track(self, interaction: discord.Interaction):
        self.player.queue.mode = wavelink.QueueMode.loop if self.player.queue.mode != wavelink.QueueMode.loop else wavelink.QueueMode.normal
        mode = "enabled" if self.player.queue.mode == wavelink.QueueMode.loop else "disabled"
        await interaction.response.send_message(
            embed=discord.Embed(
                title=f"🔂 Track Loop {mode.title()}",
                description=f"Current track repeat has been **{mode}**!",
                color=0x1DB954 if mode == "enabled" else 0xFFA500
            ), ephemeral=True
        )

    async def replay(self, interaction: discord.Interaction):
        if not self.player.playing:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"{self.emoji.ERROR} No Music Playing",
                    description="There's no music currently playing!",
                    color=0xFF0000
                ), ephemeral=True
            )
            return
        await self.player.seek(0)
        await interaction.response.send_message(
            embed=discord.Embed(
                title="🔄 Replaying Track",
                description=f"Restarting **{self.player.current.title}**!",
                color=0x1DB954
            ), ephemeral=True
        )

    async def stats(self, interaction: discord.Interaction):
        track = self.player.current
        position = self.player.position / 1000
        length = track.length / 1000
        percentage = (position / length * 100) if length > 0 else 0

        await interaction.response.send_message(
            embed=discord.Embed(
                title="📊 Player Statistics",
                description=f"**Now Playing:** {track.title}\n"
                           f"**Progress:** {percentage:.1f}%\n"
                           f"**Volume:** {self.player.volume}%\n"
                           f"**Queue:** {len(self.player.queue)} tracks\n"
                           f"**Quality:** 384kbps Ultra HD",
                color=0x1DB954
            ), ephemeral=True
        )

    async def quality_info(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=discord.Embed(
                title="💎 Ultra HD Audio Quality",
                description="**Current Quality:** 384kbps Ultra HD\n"
                           "**Bitrate:** 384 kbps\n"
                           "**Sample Rate:** 48 kHz\n"
                           "**Channels:** Stereo (2.0)\n"
                           "**Codec:** Opus/AAC\n"
                           "**Streaming:** Low Latency",
                color=0x1DB954
            ), ephemeral=True
        )

    async def mute(self, interaction: discord.Interaction):
        if not hasattr(self.player, '_pre_mute_volume'):
            self.player._pre_mute_volume = self.player.volume
            await self.player.set_volume(0)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="🔇 Muted",
                    description="Player has been muted!",
                    color=0x1DB954
                ), ephemeral=True
            )
        else:
            await self.player.set_volume(self.player._pre_mute_volume)
            delattr(self.player, '_pre_mute_volume')
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="🔊 Unmuted",
                    description="Player has been unmuted!",
                    color=0x1DB954
                ), ephemeral=True
            )

    async def seek_menu(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=discord.Embed(
                title="⏲️ Seek Controls",
                description="Use the ⏪ (30s back) and ⏩ (30s forward) buttons to seek!",
                color=0x1DB954
            ), ephemeral=True
        )

    async def add_track(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=discord.Embed(
                title="🎵 Add Track",
                description="Use `/play <song name>` or `/play <song name>` to add tracks!",
                color=0x1DB954
            ), ephemeral=True
        )

    async def settings(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=discord.Embed(
                title="🔧 Player Settings",
                description="**Current Configuration:**\n"
                           f"• Volume: {self.player.volume}%\n"
                           f"• Loop: {self.player.queue.mode.name}\n"
                           f"• Quality: 384kbps Ultra HD\n"
                           f"• Auto-play: Enabled\n"
                           f"• Queue Size: {len(self.player.queue)} tracks",
                color=0x1DB954
            ), ephemeral=True
        )

class AdvancedMusicControlView(View):
    def __init__(self, player, ctx):
        super().__init__(timeout=180)
        self.player = player
        self.ctx = ctx
        self.emoji = EmojiConfig()
        self.setup_buttons()

    def setup_buttons(self):
        # Row 1: Main playback controls - 5 buttons
        self.add_item(Button(emoji="⏮️", style=discord.ButtonStyle.secondary, custom_id="previous", row=0))
        self.add_item(Button(emoji="⏪", style=discord.ButtonStyle.secondary, custom_id="rewind", row=0))
        self.add_item(Button(emoji="⏸️", style=discord.ButtonStyle.secondary, custom_id="pause_resume", row=0))
        self.add_item(Button(emoji="⏩", style=discord.ButtonStyle.secondary, custom_id="forward", row=0))
        self.add_item(Button(emoji="⏭️", style=discord.ButtonStyle.secondary, custom_id="skip", row=0))

        # Row 2: Volume and control buttons - 5 buttons
        self.add_item(Button(emoji="🔉", style=discord.ButtonStyle.primary, custom_id="vol_down", row=1))
        self.add_item(Button(emoji="🔁", style=discord.ButtonStyle.success, custom_id="loop", row=1))
        self.add_item(Button(emoji="⏹️", style=discord.ButtonStyle.danger, custom_id="stop", row=1))
        self.add_item(Button(emoji="🔀", style=discord.ButtonStyle.success, custom_id="shuffle", row=1))
        self.add_item(Button(emoji="🔊", style=discord.ButtonStyle.primary, custom_id="vol_up", row=1))

        # Row 3: Additional controls - 5 buttons
        self.add_item(Button(emoji="🎛️", style=discord.ButtonStyle.secondary, custom_id="filter_menu", row=2))
        self.add_item(Button(emoji="📜", style=discord.ButtonStyle.secondary, custom_id="show_queue", row=2))
        self.add_item(Button(emoji="🎚️", style=discord.ButtonStyle.secondary, custom_id="equalizer", row=2))
        self.add_item(Button(emoji="🗑️", style=discord.ButtonStyle.danger, custom_id="clear_queue", row=2))
        self.add_item(Button(emoji="💾", style=discord.ButtonStyle.success, custom_id="save_playlist", row=2))

        # Attach callbacks
        for item in self.children:
            if isinstance(item, Button):
                item.callback = self.button_callback

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not self.ctx.voice_client:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"{self.emoji.ERROR} Player Not Active",
                    description="I'm not currently in a voice channel.",
                    color=0xFF0000
                ), ephemeral=True
            )
            return False
        if interaction.user in self.ctx.voice_client.channel.members:
            return True
        await interaction.response.send_message(
            embed=discord.Embed(
                title=f"{self.emoji.ERROR} Permission Denied",
                description="Only members in the same voice channel can control the player.",
                color=0xFF0000
            ), ephemeral=True
        )
        return False

    async def button_callback(self, interaction: discord.Interaction):
        button_id = interaction.data["custom_id"]

        if button_id == "pause_resume":
            await self.pause_resume(interaction)
        elif button_id == "skip":
            await self.skip(interaction)
        elif button_id == "previous":
            await self.previous(interaction)
        elif button_id == "rewind":
            await self.rewind(interaction)
        elif button_id == "forward":
            await self.forward(interaction)
        elif button_id == "loop":
            await self.loop(interaction)
        elif button_id == "shuffle":
            await self.shuffle(interaction)
        elif button_id == "vol_down":
            await self.volume_down(interaction)
        elif button_id == "vol_up":
            await self.volume_up(interaction)
        elif button_id == "filter_menu":
            await self.filter_menu(interaction)
        elif button_id == "show_queue":
            await self.show_queue(interaction)
        elif button_id == "clear_queue":
            await self.clear_queue(interaction)
        elif button_id == "equalizer":
            await self.equalizer_menu(interaction)
        elif button_id == "save_playlist":
            await self.save_playlist(interaction)
        elif button_id == "stop":
            await self.stop(interaction)

    async def pause_resume(self, interaction: discord.Interaction):
        if not self.player.playing and not self.player.paused:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} No Music Playing",
                description="There's no music currently playing!",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if self.player.paused:
            await self.player.pause(False)
            embed = discord.Embed(
                title=f"{self.emoji.SUCCESS} Playback Resumed",
                description=f"**{self.player.current.title}** has been resumed!",
                color=0x1DB954
            )
        else:
            await self.player.pause(True)
            embed = discord.Embed(
                title=f"{self.emoji.PAUSE} Playback Paused",
                description=f"**{self.player.current.title}** has been paused!",
                color=0xFFA500
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def skip(self, interaction: discord.Interaction):
        if not self.player.playing:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} No Music Playing",
                description="There's no music currently playing!",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await self.player.stop()
        embed = discord.Embed(
            title=f"{self.emoji.SKIP} Track Skipped",
            description=f"Skipped by **{interaction.user.display_name}**!",
            color=0x1DB954
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def previous(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        if guild_id in track_histories and track_histories[guild_id]:
            previous_track = track_histories[guild_id].pop()
            await self.player.play(previous_track)
            embed = discord.Embed(
                title=f"{self.emoji.PREVIOUS} Playing Previous Track",
                description=f"**{previous_track.title}**",
                color=0x1DB954
            )
        else:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} No Previous Track",
                description="There's no previous track in history!",
                color=0xFF0000
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def rewind(self, interaction: discord.Interaction):
        if not self.player.playing:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} No Music Playing",
                description="There's no music currently playing!",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        new_position = max(0, self.player.position - 30000)  # Rewind 30 seconds
        await self.player.seek(new_position)
        embed = discord.Embed(
            title="⏪ Rewinded",
            description=f"Rewinded 30 seconds in **{self.player.current.title}**!",
            color=0x1DB954
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def forward(self, interaction: discord.Interaction):
        if not self.player.playing:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} No Music Playing",
                description="There's no music currently playing!",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        new_position = min(self.player.current.length, self.player.position + 30000)  # Forward 30 seconds
        await self.player.seek(new_position)
        embed = discord.Embed(
            title="⏩ Forwarded",
            description=f"Forwarded 30 seconds in **{self.player.current.title}**!",
            color=0x1DB954
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def loop(self, interaction: discord.Interaction):
        self.player.queue.mode = wavelink.QueueMode.loop_all if self.player.queue.mode != wavelink.QueueMode.loop_all else wavelink.QueueMode.normal
        mode = "enabled" if self.player.queue.mode == wavelink.QueueMode.loop else "disabled"
        embed = discord.Embed(
            title=f"{self.emoji.REPEAT} Loop {mode.title()}",
            description=f"Loop mode has been **{mode}**!",
            color=0x1DB954 if mode == "enabled" else 0xFFA500
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def shuffle(self, interaction: discord.Interaction):
        if self.player.queue and not self.player.queue.is_empty:
            queued_tracks = list(self.player.queue)
            random.shuffle(queued_tracks)
            self.player.queue.clear()
            await self.player.queue.put_wait(queued_tracks)
            embed = discord.Embed(
                title=f"{self.emoji.SHUFFLE} Queue Shuffled",
                description=f"Queue has been shuffled!",
                color=0x1DB954
            )
        else:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Queue Empty",
                description="The queue is currently empty!",
                color=0xFF0000
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def volume_down(self, interaction: discord.Interaction):
        current_volume = self.player.volume
        new_volume = max(0, current_volume - 20)
        await self.player.set_volume(new_volume)
        embed = discord.Embed(
            title=f"{self.emoji.VOLUME_DOWN} Volume Decreased",
            description=f"Volume: `{current_volume}%` → `{new_volume}%`",
            color=0x1DB954
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def volume_up(self, interaction: discord.Interaction):
        current_volume = self.player.volume
        new_volume = min(200, current_volume + 20)
        await self.player.set_volume(new_volume)
        embed = discord.Embed(
            title=f"{self.emoji.VOLUME_UP} Volume Increased",
            description=f"Volume: `{current_volume}%` → `{new_volume}%`",
            color=0x1DB954
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def filter_menu(self, interaction: discord.Interaction):
        filter_view = FilterSelectView(self.player, self.ctx)
        embed = discord.Embed(
            title=f"{self.emoji.FILTER} Audio Filters",
            description="Select an audio filter to apply:",
            color=0x1DB954
        )
        await interaction.response.send_message(embed=embed, view=filter_view, ephemeral=True)

    async def equalizer_menu(self, interaction: discord.Interaction):
        eq_view = EqualizerView(self.player, self.ctx)
        embed = discord.Embed(
            title="🎚️ Equalizer Presets",
            description="Select an equalizer preset:",
            color=0x1DB954
        )
        await interaction.response.send_message(embed=embed, view=eq_view, ephemeral=True)

    async def show_queue(self, interaction: discord.Interaction):
        if not self.player.queue or self.player.queue.is_empty:
            embed = discord.Embed(
                title=f"{self.emoji.QUEUE} Queue Empty",
                description="The queue is currently empty!",
                color=0xFFA500
            )
        else:
            tracks = list(self.player.queue)[:10]
            queue_text = "\n".join([f"`{i+1}.` **{track.title[:40]}**" for i, track in enumerate(tracks)])
            embed = discord.Embed(
                title=f"{self.emoji.QUEUE} Current Queue",
                description=queue_text,
                color=0x1DB954
            )
            if len(self.player.queue) > 10:
                embed.set_footer(text=f"And {len(self.player.queue) - 10} more tracks...")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def clear_queue(self, interaction: discord.Interaction):
        if self.player.queue.is_empty:
            embed = discord.Embed(
                title=f"{self.emoji.WARNING} Queue Already Empty",
                description="The queue is already empty!",
                color=0xFFA500
            )
        else:
            queue_count = len(self.player.queue)
            self.player.queue.clear()
            embed = discord.Embed(
                title=f"{self.emoji.CLEAR} Queue Cleared",
                description=f"Cleared `{queue_count}` tracks!",
                color=0x1DB954
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def save_playlist(self, interaction: discord.Interaction):
        if self.player.queue.is_empty:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Queue Empty",
                description="There are no tracks in the queue to save!",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        view = PlaylistSaveView(self.player.queue, interaction.user.id)
        embed = discord.Embed(
            title="💾 Save Playlist",
            description="Save the current queue as a playlist:",
            color=0x1DB954
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def stop(self, interaction: discord.Interaction):
        if self.player:
            # Clear active player message
            guild_id = interaction.guild.id
            if guild_id in active_player_messages:
                try:
                    await active_player_messages[guild_id].delete()
                    del active_player_messages[guild_id]
                except:
                    pass

            await self.player.disconnect()
            embed = discord.Embed(
                title=f"{self.emoji.STOP} Playback Stopped",
                description="Music playback has been stopped!",
                color=0x1DB954
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Not Connected",
                description="I'm not connected to any voice channel!",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

class FilterSelectView(View):
    def __init__(self, player, ctx):
        super().__init__(timeout=60)
        self.player = player
        self.ctx = ctx
        self.emoji = EmojiConfig()

    @discord.ui.select(
        placeholder="🎛️ Select Audio Filter...",
        options=[
            discord.SelectOption(label="Nightcore", description="Increase pitch and speed", emoji="🎵"),
            discord.SelectOption(label="Bass Boost", description="Enhance bass frequencies", emoji="🔊"),
            discord.SelectOption(label="Vaporwave", description="Slow down and pitch down", emoji="🌴"),
            discord.SelectOption(label="Karaoke", description="Remove vocal frequencies", emoji="🎤"),
            discord.SelectOption(label="Tremolo", description="Amplitude modulation effect", emoji="🎛️"),
            discord.SelectOption(label="Vibrato", description="Pitch modulation effect", emoji="🎶"),
            discord.SelectOption(label="Rotation", description="3D rotation effect", emoji="🔄"),
            discord.SelectOption(label="Distortion", description="Add distortion effect", emoji="🎸"),
            discord.SelectOption(label="Clear Filters", description="Remove all filters", emoji="🧹"),
        ]
    )
    async def select_filter(self, interaction: discord.Interaction, select: Select):
        filter_name = select.values[0]

        filters = wavelink.Filters()

        if filter_name == "Nightcore":
            filters.timescale.set(pitch=1.2, speed=1.2, rate=1)
            description = "Applied Nightcore filter - increased pitch and speed!"
        elif filter_name == "Bass Boost":
            filters.equalizer.set(bands=[{"band": 0, "gain": 0.8}, {"band": 1, "gain": 0.6}, {"band": 2, "gain": 0.4}])
            description = "Applied Bass Boost - enhanced low frequencies!"
        elif filter_name == "Vaporwave":
            filters.timescale.set(rate=0.8, pitch=0.9)
            description = "Applied Vaporwave filter - slowed down and pitched down!"
        elif filter_name == "Karaoke":
            filters.karaoke.set(level=1.0, mono_level=1.0, filter_band=220.0, filter_width=100.0)
            description = "Applied Karaoke filter - vocal removal enabled!"
        elif filter_name == "Tremolo":
            filters.tremolo.set(depth=0.5, frequency=10.0)
            description = "Applied Tremolo effect - amplitude modulation!"
        elif filter_name == "Vibrato":
            filters.vibrato.set(depth=0.5, frequency=5.0)
            description = "Applied Vibrato effect - pitch modulation!"
        elif filter_name == "Rotation":
            filters.rotation.set(rotation_hz=0.2)
            description = "Applied Rotation effect - 3D audio rotation!"
        elif filter_name == "Distortion":
            filters.distortion.set(sin_offset=0.0, sin_scale=1.0, cos_offset=0.0, cos_scale=1.0, tan_offset=0.0, tan_scale=1.0, offset=0.0, scale=1.0)
            description = "Applied Distortion effect - gritty sound!"
        elif filter_name == "Clear Filters":
            filters = wavelink.Filters()
            description = "All audio filters have been cleared!"

        await self.player.set_filters(filters)

        embed = discord.Embed(
            title=f"{self.emoji.FILTER} Filter Applied",
            description=description,
            color=0x1DB954
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


# Playlist data storage
user_playlists = {}

class EqualizerView(View):
    def __init__(self, player, ctx):
        super().__init__(timeout=60)
        self.player = player
        self.ctx = ctx
        self.emoji = EmojiConfig()

    @discord.ui.select(
        placeholder="🎚️ Select Equalizer Preset...",
        options=[
            discord.SelectOption(label="Flat", description="No changes to audio", emoji="📊"),
            discord.SelectOption(label="Rock", description="Enhanced for rock music", emoji="🎸"),
            discord.SelectOption(label="Pop", description="Optimized for pop music", emoji="🎤"),
            discord.SelectOption(label="Classical", description="Classical music preset", emoji="🎻"),
            discord.SelectOption(label="Electronic", description="Electronic/EDM preset", emoji="🎹"),
            discord.SelectOption(label="Hip-Hop", description="Hip-hop and rap preset", emoji="🎧"),
            discord.SelectOption(label="Jazz", description="Jazz music preset", emoji="🎺"),
            discord.SelectOption(label="Metal", description="Heavy metal preset", emoji="⚡"),
        ]
    )
    async def select_eq(self, interaction: discord.Interaction, select: Select):
        preset = select.values[0]
        filters = wavelink.Filters()

        if preset == "Rock":
            filters.equalizer.set(bands=[
                {"band": 0, "gain": 0.3}, {"band": 1, "gain": 0.2}, {"band": 2, "gain": 0.1},
                {"band": 3, "gain": -0.1}, {"band": 4, "gain": 0.2}, {"band": 5, "gain": 0.3}
            ])
        elif preset == "Pop":
            filters.equalizer.set(bands=[
                {"band": 0, "gain": -0.1}, {"band": 1, "gain": 0.2}, {"band": 2, "gain": 0.3},
                {"band": 3, "gain": 0.2}, {"band": 4, "gain": 0.1}, {"band": 5, "gain": -0.1}
            ])
        elif preset == "Classical":
            filters.equalizer.set(bands=[
                {"band": 0, "gain": 0.2}, {"band": 1, "gain": 0.1}, {"band": 2, "gain": -0.1},
                {"band": 3, "gain": -0.1}, {"band": 4, "gain": 0.1}, {"band": 5, "gain": 0.2}
            ])
        elif preset == "Electronic":
            filters.equalizer.set(bands=[
                {"band": 0, "gain": 0.4}, {"band": 1, "gain": 0.3}, {"band": 2, "gain": 0.1},
                {"band": 3, "gain": 0.2}, {"band": 4, "gain": 0.3}, {"band": 5, "gain": 0.4}
            ])
        elif preset == "Hip-Hop":
            filters.equalizer.set(bands=[
                {"band": 0, "gain": 0.5}, {"band": 1, "gain": 0.3}, {"band": 2, "gain": 0.0},
                {"band": 3, "gain": 0.1}, {"band": 4, "gain": 0.2}, {"band": 5, "gain": 0.3}
            ])
        elif preset == "Jazz":
            filters.equalizer.set(bands=[
                {"band": 0, "gain": 0.1}, {"band": 1, "gain": 0.2}, {"band": 2, "gain": 0.1},
                {"band": 3, "gain": 0.2}, {"band": 4, "gain": 0.1}, {"band": 5, "gain": 0.2}
            ])
        elif preset == "Metal":
            filters.equalizer.set(bands=[
                {"band": 0, "gain": 0.4}, {"band": 1, "gain": 0.3}, {"band": 2, "gain": 0.2},
                {"band": 3, "gain": 0.1}, {"band": 4, "gain": 0.3}, {"band": 5, "gain": 0.4}
            ])

        await self.player.set_filters(filters)
        embed = discord.Embed(
            title="🎚️ Equalizer Applied",
            description=f"Applied **{preset}** equalizer preset!",
            color=0x1DB954
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


class PlaylistAddView(View):
    def __init__(self, track, user_id):
        super().__init__(timeout=60)
        self.track = track
        self.user_id = user_id
        self.emoji = EmojiConfig()

    @discord.ui.button(label="Create New Playlist", style=discord.ButtonStyle.success, emoji="➕")
    async def create_new(self, interaction: discord.Interaction, button: Button):
        modal = PlaylistNameModal(self.track, self.user_id, is_new=True)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Add to Existing", style=discord.ButtonStyle.primary, emoji="📂")
    async def add_existing(self, interaction: discord.Interaction, button: Button):
        if self.user_id not in user_playlists or not user_playlists[self.user_id]:
            embed = discord.Embed(
                title="❌ No Playlists",
                description="You don't have any playlists yet! Create one first.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        view = SelectPlaylistView(self.track, self.user_id)
        embed = discord.Embed(
            title="📂 Select Playlist",
            description="Choose a playlist to add this track to:",
            color=0x1DB954
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class PlaylistNameModal(discord.ui.Modal, title="Playlist Name"):
    name = discord.ui.TextInput(
        label="Enter Playlist Name",
        placeholder="My Awesome Playlist",
        required=True,
        max_length=50
    )

    def __init__(self, track, user_id, is_new=True):
        super().__init__()
        self.track = track
        self.user_id = user_id
        self.is_new = is_new

    async def on_submit(self, interaction: discord.Interaction):
        playlist_name = self.name.value

        if self.user_id not in user_playlists:
            user_playlists[self.user_id] = {}

        if playlist_name not in user_playlists[self.user_id]:
            user_playlists[self.user_id][playlist_name] = []

        user_playlists[self.user_id][playlist_name].append({
            'title': self.track.title,
            'uri': self.track.uri,
            'author': self.track.author
        })

        embed = discord.Embed(
            title="✅ Track Added",
            description=f"Added **{self.track.title}** to playlist **{playlist_name}**!",
            color=0x1DB954
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


class SelectPlaylistView(View):
    def __init__(self, track, user_id):
        super().__init__(timeout=60)
        self.track = track
        self.user_id = user_id
        self.emoji = EmojiConfig()

        playlists = user_playlists.get(user_id, {})
        options = [
            discord.SelectOption(label=name, description=f"{len(tracks)} tracks", emoji="📂")
            for name, tracks in list(playlists.items())[:25]
        ]

        select = Select(placeholder="Select a playlist...", options=options)
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        playlist_name = interaction.data["values"][0]

        user_playlists[self.user_id][playlist_name].append({
            'title': self.track.title,
            'uri': self.track.uri,
            'author': self.track.author
        })

        embed = discord.Embed(
            title="✅ Track Added",
            description=f"Added **{self.track.title}** to **{playlist_name}**!",
            color=0x1DB954
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


class QueueRemoveView(View):
    def __init__(self, player):
        super().__init__(timeout=60)
        self.player = player
        self.emoji = EmojiConfig()

        queue_list = list(player.queue)[:25]
        options = [
            discord.SelectOption(
                label=f"{i+1}. {track.title[:50]}",
                description=track.author[:50],
                value=str(i)
            )
            for i, track in enumerate(queue_list)
        ]

        select = Select(placeholder="Select track to remove...", options=options)
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        index = int(interaction.data["values"][0])
        queue_list = list(self.player.queue)

        if index < len(queue_list):
            removed_track = queue_list[index]
            del queue_list[index]
            self.player.queue.clear()
            for track in queue_list:
                self.player.queue.put(track)

            embed = discord.Embed(
                title="✅ Track Removed",
                description=f"Removed **{removed_track.title}** from queue!",
                color=0x1DB954
            )
        else:
            embed = discord.Embed(
                title="❌ Error",
                description="Could not remove track!",
                color=0xFF0000
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)


class PlaylistManagerView(View):
    def __init__(self, user_id, ctx):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.ctx = ctx
        self.emoji = EmojiConfig()

    @discord.ui.button(label="View Playlists", style=discord.ButtonStyle.primary, emoji="📂")
    async def view_playlists(self, interaction: discord.Interaction, button: Button):
        playlists = user_playlists.get(self.user_id, {})

        if not playlists:
            embed = discord.Embed(
                title="📂 Your Playlists",
                description="You don't have any playlists yet!",
                color=0xFFA500
            )
        else:
            embed = discord.Embed(
                title="📂 Your Playlists",
                description="Your saved playlists:",
                color=0x1DB954
            )
            for name, tracks in list(playlists.items())[:10]:
                embed.add_field(
                    name=f"📁 {name}",
                    value=f"`{len(tracks)}` tracks",
                    inline=True
                )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Delete Playlist", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def delete_playlist(self, interaction: discord.Interaction, button: Button):
        playlists = user_playlists.get(self.user_id, {})

        if not playlists:
            embed = discord.Embed(
                title="❌ No Playlists",
                description="You don't have any playlists to delete!",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        view = DeletePlaylistView(self.user_id)
        embed = discord.Embed(
            title="🗑️ Delete Playlist",
            description="Select a playlist to delete:",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class DeletePlaylistView(View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.emoji = EmojiConfig()

        playlists = user_playlists.get(user_id, {})
        options = [
            discord.SelectOption(label=name, description=f"{len(tracks)} tracks", emoji="📂")
            for name, tracks in list(playlists.items())[:25]
        ]

        select = Select(placeholder="Select playlist to delete...", options=options)
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        playlist_name = interaction.data["values"][0]

        if self.user_id in user_playlists and playlist_name in user_playlists[self.user_id]:
            del user_playlists[self.user_id][playlist_name]
            embed = discord.Embed(
                title="✅ Playlist Deleted",
                description=f"Deleted playlist **{playlist_name}**!",
                color=0x1DB954
            )
        else:
            embed = discord.Embed(
                title="❌ Error",
                description="Could not delete playlist!",
                color=0xFF0000
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)


class PlaylistSaveView(View):
    def __init__(self, queue, user_id):
        super().__init__(timeout=60)
        self.queue = queue
        self.user_id = user_id
        self.emoji = EmojiConfig()

    @discord.ui.button(label="Save Queue as Playlist", style=discord.ButtonStyle.success, emoji="💾")
    async def save_queue(self, interaction: discord.Interaction, button: Button):
        modal = SaveQueueModal(self.queue, self.user_id)
        await interaction.response.send_modal(modal)


class SaveQueueModal(discord.ui.Modal, title="Save Queue as Playlist"):
    name = discord.ui.TextInput(
        label="Playlist Name",
        placeholder="My Queue Playlist",
        required=True,
        max_length=50
    )

    def __init__(self, queue, user_id):
        super().__init__()
        self.queue = queue
        self.user_id = user_id

    async def on_submit(self, interaction: discord.Interaction):
        playlist_name = self.name.value

        if self.user_id not in user_playlists:
            user_playlists[self.user_id] = {}

        user_playlists[self.user_id][playlist_name] = [
            {'title': track.title, 'uri': track.uri, 'author': track.author}
            for track in list(self.queue)
        ]

        embed = discord.Embed(
            title="✅ Playlist Saved",
            description=f"Saved **{len(list(self.queue))}** tracks to **{playlist_name}**!",
            color=0x1DB954
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


class PlaylistLoadView(View):
    def __init__(self, user_id, player):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.player = player
        self.emoji = EmojiConfig()

        playlists = user_playlists.get(user_id, {})

        if not playlists:
            return

        options = [
            discord.SelectOption(label=name, description=f"{len(tracks)} tracks", emoji="📂")
            for name, tracks in list(playlists.items())[:25]
        ]

        select = Select(placeholder="Select playlist to load...", options=options)
        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        playlist_name = interaction.data["values"][0]
        tracks_data = user_playlists[self.user_id][playlist_name]

        loaded_count = 0
        for track_data in tracks_data:
            try:
                results = await wavelink.Playable.search(track_data['uri'])
                if results:
                    await self.player.queue.put_wait(results[0] if isinstance(results, list) else results)
                    loaded_count += 1
            except:
                continue

        embed = discord.Embed(
            title="✅ Playlist Loaded",
            description=f"Loaded **{loaded_count}** tracks from **{playlist_name}**!",
            color=0x1DB954
        )

        if not self.player.playing and not self.player.queue.is_empty:
            next_track = await self.player.queue.get_wait()
            await self.player.play(next_track)
            await self.player.ctx.cog.display_player_embed(self.player, next_track, self.player.ctx)

        await interaction.response.send_message(embed=embed, ephemeral=True)


class PlatformSelectView(View):
    def __init__(self, ctx, query):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.query = query
        self.emoji = EmojiConfig()

        platforms = [
            (f"{self.emoji.YOUTUBE} YouTube", "ytsearch", discord.ButtonStyle.danger),
            (f"{self.emoji.SOUNDCLOUD} SoundCloud", "scsearch", discord.ButtonStyle.primary),
        ]

        for name, source, style in platforms:
            button = Button(label=name, style=style)
            button.callback = self.create_callback(source, name)
            self.add_item(button)

    def create_callback(self, source, platform_name):
        async def callback(interaction: discord.Interaction):
            if interaction.user != self.ctx.author:
                embed = discord.Embed(
                    title=f"{self.emoji.ERROR} Permission Denied",
                    description="Only the command author can select a platform.",
                    color=0xFF0000
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            embed = discord.Embed(
                title=f"{self.emoji.SEARCH} Searching...",
                description=f"Searching for `{self.query}` on {platform_name}...",
                color=0x1DB954
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await self.perform_search(source, platform_name)
            await interaction.message.delete()
        return callback

    async def perform_search(self, source, platform_name):
        results = await wavelink.Playable.search(self.query, source=source)
        if not results:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} No Results Found",
                description=f"No results found for `{self.query}` on {platform_name}.",
                color=0xFF0000
            )
            return await self.ctx.send(embed=embed)

        top_results = results[:5]
        embed = discord.Embed(
            title=f"{self.emoji.SEARCH} Search Results - {platform_name}",
            description=f"Top 5 results for `{self.query}`:",
            color=0x1DB954
        )

        for i, track in enumerate(top_results, 1):
            duration = f"{track.length // 1000 // 60}:{track.length // 1000 % 60:02d}"
            embed.add_field(
                name=f"{i}. {track.title}",
                value=f"**Artist:** {track.author}\n**Duration:** {duration} | [Link]({track.uri})",
                inline=False
            )

        await self.ctx.send(embed=embed, view=SearchResultView(self.ctx, top_results))

class SearchResultView(View):
    def __init__(self, ctx, results):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.results = results
        self.emoji = EmojiConfig()

        for i in range(min(5, len(results))):
            button = Button(label=str(i + 1), style=discord.ButtonStyle.primary, emoji=f"{i+1}️⃣")
            button.callback = self.create_callback(i)
            self.add_item(button)

    def create_callback(self, index):
        async def callback(interaction: discord.Interaction):
            if interaction.user != self.ctx.author:
                embed = discord.Embed(
                    title=f"{self.emoji.ERROR} Permission Denied",
                    description="Only the command author can select a track.",
                    color=0xFF0000
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            track = self.results[index]
            vc = self.ctx.voice_client
            if not vc:
                if not self.ctx.author.voice:
                    embed = discord.Embed(
                        title=f"{self.emoji.ERROR} Voice Channel Required",
                        description="You need to be in a voice channel to play music.",
                        color=0xFF0000
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                vc = await self.ctx.author.voice.channel.connect(cls=wavelink.Player)

            vc.ctx = self.ctx

            if not vc.playing:
                await vc.play(track)
                embed = discord.Embed(
                    title=f"{self.emoji.MUSICAL_NOTE} Now Playing",
                    description=f"**{track.title}** by **{track.author}**",
                    color=0x1DB954
                )
                await interaction.response.send_message(embed=embed)
                await self.ctx.cog.display_player_embed(vc, track, self.ctx)
            else:
                await vc.queue.put_wait(track)
                embed = discord.Embed(
                    title=f"{self.emoji.ADD} Added to Queue",
                    description=f"**{track.title}** by **{track.author}**",
                    color=0x1DB954
                )
                embed.set_footer(text=f"Position in queue: {len(vc.queue)}")
                await interaction.response.send_message(embed=embed)
        return callback

# REMOVED TOP.GG VOTE SYSTEM FUNCTIONS

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.inactivity_timeout = 120
        self.player_inactivity = {}
        self.emoji = EmojiConfig()
        self.responses = ResponseMessages()

    async def log_track_play(self, ctx, track):
        """Log music play to database"""
        try:
            await self.client.music_db.register_server(ctx.guild.id, ctx.guild.name)
            if ctx.author.voice and ctx.author.voice.channel:
                await self.client.music_db.register_voice_channel(
                    ctx.author.voice.channel.id,
                    ctx.guild.id,
                    ctx.author.voice.channel.name
                )

                source = "youtube"
                if "spotify" in track.uri.lower():
                    source = "spotify"
                elif "soundcloud" in track.uri.lower():
                    source = "soundcloud"

                await self.client.music_db.log_music_play(
                    server_id=ctx.guild.id,
                    channel_id=ctx.author.voice.channel.id,
                    user_id=ctx.author.id,
                    user_name=str(ctx.author),
                    track_title=track.title,
                    track_author=track.author,
                    track_uri=track.uri,
                    track_duration=track.length // 1000,
                    track_source=source
                )
        except Exception as e:
            print(f"❌ Database logging error: {e}")

    async def log_search(self, ctx, query, results_count):
        """Log music search to database"""
        try:
            await self.client.music_db.register_server(ctx.guild.id, ctx.guild.name)
            await self.client.music_db.log_search(
                server_id=ctx.guild.id,
                user_id=ctx.author.id,
                user_name=str(ctx.author),
                search_query=query,
                results_count=results_count
            )
        except Exception as e:
            print(f"❌ Search logging error: {e}")

    async def save_session(self, player, ctx):
        """Save current playback session"""
        try:
            if not ctx.author.voice or not ctx.author.voice.channel:
                return

            current_track = None
            if player.current:
                current_track = {
                    'title': player.current.title,
                    'author': player.current.author,
                    'uri': player.current.uri,
                    'length': player.current.length
                }

            queue_data = []
            for track in list(player.queue)[:50]:
                queue_data.append({
                    'title': track.title,
                    'author': track.author,
                    'uri': track.uri,
                    'length': track.length
                })

            await self.client.music_db.save_playback_session(
                server_id=ctx.guild.id,
                channel_id=ctx.author.voice.channel.id,
                current_track=current_track,
                queue_data=queue_data,
                position=player.position,
                volume=player.volume,
                is_paused=player.paused,
                loop_mode='loop' if player.queue.mode == wavelink.QueueMode.loop else 'normal',
                auto_resume=True
            )
        except Exception as e:
            print(f"❌ Session save error: {e}")

    async def cog_load(self):
        """Called when the cog is loaded"""
        await self.connect_nodes()
        asyncio.create_task(self.monitor_inactivity())

    async def connect_nodes(self) -> None:
        """Connect to Lavalink nodes with high quality settings"""
        try:
            # Try to load from config first, then fall back to environment variables
            lavalink_uri = None
            lavalink_password = None

            try:
                with open('bot_config.json', 'r') as f:
                    config = json.load(f)
                    lavalink_uri = config.get('lavalink_uri') or os.environ.get("LAVALINK_URI")
                    lavalink_password = config.get('lavalink_password') or os.environ.get("LAVALINK_PASSWORD")
            except FileNotFoundError:
                lavalink_uri = os.environ.get("LAVALINK_URI")
                lavalink_password = os.environ.get("LAVALINK_PASSWORD")

            if not lavalink_uri or not lavalink_password:
                print("❌ Lavalink is not configured. Set LAVALINK_URI and LAVALINK_PASSWORD in bot_config.json or environment.")
                return
            nodes = [wavelink.Node(uri=lavalink_uri, password=lavalink_password)]
            await wavelink.Pool.connect(nodes=nodes, client=self.client, cache_capacity=None)
            print("🎵 Successfully connected to Lavalink node with ULTRA HD (384kbps) settings")
        except Exception as e:
            print(f"❌ Failed to connect to Lavalink: {e}")

    async def monitor_inactivity(self):
        """Monitor voice channel inactivity"""
        while True:
            await asyncio.sleep(60)
            for guild in self.client.guilds:
                await self.check_inactivity(guild.id)

    async def check_inactivity(self, guild_id):
        """Check for inactivity in a guild"""
        guild = self.client.get_guild(guild_id)
        if not guild:
            return

        player = None
        for vc in self.client.voice_clients:
            if vc.guild.id == guild.id:
                player = vc
                break

        if player and player.playing and len(player.channel.members) == 1:
            await self.inactivity_timer(guild)

    async def inactivity_timer(self, guild):
        """Handle inactivity timeout"""
        await asyncio.sleep(self.inactivity_timeout)

        player = None
        for vc in self.client.voice_clients:
            if vc.guild.id == guild.id:
                player = vc
                break

        if player and len(player.channel.members) == 1:
            await player.disconnect(force=True)
            try:
                embed = discord.Embed(
                    title=f"{self.emoji.WARNING} Inactivity Timeout",
                    description="I've been disconnected due to inactivity (being alone in the voice channel for more than 2 minutes).",
                    color=0xFFA500
                )
                embed.add_field(name="Thank You", value="Thanks for Choosing Me!", inline=False)

                support = Button(
                    label='Support Server',
                    style=discord.ButtonStyle.link,
                    url='https://discord.gg/DXMHHk7rAt',
                    emoji="🆘"
                )
                invite = Button(
                    label='Invite Me',
                    style=discord.ButtonStyle.link,
                    url='https://discord.com/oauth2/authorize?client_id=1422355258562318358&permissions=8&integration_type=0&scope=applications.commands+bot',
                    emoji="🤖"
                )
                view = View()
                view.add_item(support)
                view.add_item(invite)

                if hasattr(player, 'ctx') and player.ctx:
                    await player.ctx.channel.send(embed=embed, view=view)
            except Exception as e:
                print(f"❌ Error sending inactivity message: {e}")

    async def auto_delete_message(self, message, delay):
        """Auto-deletes a message after a specified delay."""
        await asyncio.sleep(delay)
        try:
            await message.delete()
        except discord.NotFound:
            pass  # Message already deleted
        except Exception as e:
            print(f"Error deleting message: {e}")

    async def display_player_embed(self, player, track, ctx, autoplay=False):
        """Display the player embed with track information and quality indicators"""
        try:
            # Skip control panel if in autoplay-only mode
            if hasattr(player, '_autoplay_only') and player._autoplay_only:
                # Simple notification without control panel
                simple_embed = discord.Embed(
                    title=f"{self.emoji.MUSICAL_NOTES} Now Playing - 24/7 Autoplay",
                    description=f"**{track.title}**\nby **{track.author}**",
                    color=0x1DB954
                )
                if track.artwork:
                    simple_embed.set_thumbnail(url=track.artwork)
                simple_embed.set_footer(text="Autoplay Mode - Music plays continuously without interruption")
                msg = await ctx.send(embed=simple_embed)
                # Auto-delete after 10 seconds
                await asyncio.sleep(10)
                try:
                    await msg.delete()
                except:
                    pass
                return

            # Delete previous player message if exists
            guild_id = ctx.guild.id
            if guild_id in active_player_messages:
                try:
                    await active_player_messages[guild_id].delete()
                except:
                    pass

            # Create enhanced embed
            sec = track.length // 1000
            duration = f"0{sec // 60}:{sec % 60:02d}" if sec < 600 else f"{sec // 60}:{sec % 60:02d}"

            # Determine source emoji
            if "spotify" in track.uri.lower():
                source_emoji = self.emoji.SPOTIFY
                source_name = "Spotify"
            elif "youtube" in track.uri.lower():
                source_emoji = self.emoji.YOUTUBE
                source_name = "YouTube"
            elif "soundcloud" in track.uri.lower():
                source_emoji = self.emoji.SOUNDCLOUD
                source_name = "SoundCloud"
            else:
                source_emoji = self.emoji.MUSICAL_NOTE
                source_name = "Unknown"

            embed = discord.Embed(
                title=f"{self.emoji.MUSICAL_NOTES} Now Playing - Ultra HD 384kbps",
                color=0x1DB954
            )

            embed.add_field(
                name=f"{self.emoji.MUSICAL_NOTE} Track",
                value=f"**{track.title}**",
                inline=False
            )
            embed.add_field(
                name=f"{self.emoji.MICROPHONE} Artist",
                value=f"**{track.author}**",
                inline=True
            )
            embed.add_field(
                name=f"{self.emoji.CLOCK} Duration",
                value=f"**{duration}**",
                inline=True
            )
            embed.add_field(
                name=f"{self.emoji.QUALITY} Quality",
                value=f"**384kbps Ultra HD**",
                inline=True
            )
            embed.add_field(
                name=f"{self.emoji.RADIO} Source",
                value=f"{source_emoji} **{source_name}**",
                inline=True
            )
            embed.add_field(
                name=f"{self.emoji.VOLUME_HIGH} Volume",
                value=f"**{player.volume}%**",
                inline=True
            )

            if track.artwork:
                embed.set_image(url=track.artwork)

            requester_text = f"{ctx.author.display_name} ({'Autoplay' if autoplay else 'Requested'})"
            embed.set_footer(
                text=f"Requested by {requester_text} • High Quality Audio Streaming",
                icon_url=ctx.author.display_avatar.url
            )

            # Send embed with ultra advanced controls (25+ buttons) and store the message
            message = await ctx.send(embed=embed, view=UltraAdvancedMusicControlView(player, ctx))
            active_player_messages[guild_id] = message

            # Log track play to database
            await self.log_track_play(ctx, track)

            # Save playback session
            await self.save_session(player, ctx)

        except Exception as e:
            print(f"❌ Error displaying player embed: {e}")
            # Fallback to basic embed
            await self.display_fallback_embed(player, track, ctx, autoplay)

    async def display_fallback_embed(self, player, track, ctx, autoplay=False):
        """Fallback embed without advanced features"""
        sec = track.length // 1000
        duration = f"0{sec // 60}:{sec % 60:02d}" if sec < 600 else f"{sec // 60}:{sec % 60:02d}"

        embed = discord.Embed(
            title=f"{self.emoji.MUSICAL_NOTES} Now Playing",
            description=f"**{track.title}** by **{track.author}**",
            color=0x1DB954
        )
        embed.add_field(name="Duration", value=duration, inline=True)
        embed.add_field(name="Source", value="YouTube", inline=True)

        if track.artwork:
            embed.set_image(url=track.artwork)

        requester_text = "Autoplay" if autoplay else ctx.author.display_name
        embed.set_footer(text=f"Requested by {requester_text}")

        message = await ctx.send(embed=embed, view=UltraAdvancedMusicControlView(player, ctx))
        active_player_messages[ctx.guild.id] = message

    async def on_track_end(self, payload: wavelink.TrackEndEventPayload):
        """Handle track end events"""
        player = payload.player

        if not player:
            return

        # Clear active player message when track ends (only if not autoplay-only mode)
        if hasattr(player, 'ctx') and player.ctx:
            guild_id = player.ctx.guild.id
            if not (hasattr(player, '_autoplay_only') and player._autoplay_only):
                if guild_id in active_player_messages:
                    try:
                        await active_player_messages[guild_id].delete()
                        del active_player_messages[guild_id]
                    except:
                        pass

        # If in autoplay-only mode, automatically add more random songs
        if hasattr(player, '_autoplay_only') and player._autoplay_only:
            # Auto-add random songs when queue is low
            if len(player.queue) < 5:
                autoplay_queries = [
                    "lofi hip hop radio", "lofi study music", "chill lofi beats", "lofi relaxing music",
                    "latest hindi songs", "bollywood romantic songs", "hindi lofi songs",
                    "sad songs english", "heartbreak songs", "emotional songs english",
                    "top english songs", "pop hits", "indie music", "acoustic songs",
                    "arabic songs", "arabic music", "arabic lofi", "arabic romantic songs"
                ]

                # Add 10 more random songs
                for _ in range(10):
                    random_query = random.choice(autoplay_queries)
                    try:
                        tracks = await wavelink.Playable.search(random_query)
                        if tracks:
                            track = tracks[0] if not isinstance(tracks, wavelink.Playlist) else tracks.tracks[0]
                            await player.queue.put_wait(track)
                    except:
                        continue

        if player.queue and not player.queue.is_empty:
            next_track = await player.queue.get_wait()
            await player.play(next_track)
            if hasattr(player, 'ctx') and player.ctx:
                await self.display_player_embed(player, next_track, player.ctx)
        elif player.autoplay == wavelink.AutoPlayMode.enabled:
            await asyncio.sleep(2)
            if player.current and hasattr(player, 'ctx') and player.ctx:
                await self.display_player_embed(player, player.current, player.ctx, autoplay=True)
        else:
            await player.disconnect()
            if hasattr(player, 'ctx') and player.ctx:
                embed = discord.Embed(
                    title=f"{self.emoji.STOP} Queue Ended",
                    description="All tracks have been played. I've left the voice channel.",
                    color=0x1DB954
                )

                support = Button(
                    label='Support Server',
                    style=discord.ButtonStyle.link,
                    url='https://discord.gg/DXMHHk7rAt',
                    emoji="🆘"
                )
                invite = Button(
                    label='Invite Me',
                    style=discord.ButtonStyle.link,
                    url='https://discord.com/oauth2/authorize?client_id=1422355258562318358&permissions=8&integration_type=0&scope=applications.commands+bot',
                    emoji="🤖"
                )

                view = View()
                view.add_item(support)
                view.add_item(invite)

                await player.ctx.channel.send(embed=embed, view=view)

    async def play_source(self, ctx, query):
        """Play music from a query with high quality audio"""
        # REMOVED VOTE REQUIREMENT CHECK

        if not ctx.author.voice:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Voice Channel Required",
                description="You need to be in a voice channel to play music!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        vc = ctx.voice_client
        if not vc:
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
            await vc.set_volume(100)  # Set high quality default volume

        vc.ctx = ctx

        if vc.playing and ctx.voice_client and ctx.voice_client.channel != ctx.author.voice.channel:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Wrong Voice Channel",
                description=f"You must be in {ctx.voice_client.channel.mention} to control the music!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        vc.autoplay = wavelink.AutoPlayMode.disabled

        # Check for Spotify links
        if re.match(SPOTIFY_TRACK_REGEX, query):
            await self.handle_spotify_link(ctx, vc, query, "track")
            return
        elif re.match(SPOTIFY_PLAYLIST_REGEX, query):
            await self.handle_spotify_link(ctx, vc, query, "playlist")
            return
        elif re.match(SPOTIFY_ALBUM_REGEX, query):
            await self.handle_spotify_link(ctx, vc, query, "album")
            return

        # Regular search
        embed = discord.Embed(
            title=f"{self.emoji.SEARCH} Searching High Quality Audio...",
            description=f"Searching for `{query}`...",
            color=0x1DB954
        )
        search_msg = await ctx.send(embed=embed)

        tracks = await wavelink.Playable.search(query)

        # Log search to database
        results_count = len(tracks.tracks) if isinstance(tracks, wavelink.Playlist) else (1 if tracks else 0)
        await self.log_search(ctx, query, results_count)

        if not tracks:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} No Results Found",
                description=f"No results found for `{query}`.",
                color=0xFF0000
            )
            await search_msg.edit(embed=embed)
            return

        if isinstance(tracks, wavelink.Playlist):
            await vc.queue.put_wait(tracks.tracks)

            # Calculate total duration
            total_duration_sec = sum(t.length // 1000 for t in tracks.tracks)
            total_duration = f"{total_duration_sec // 60}:{total_duration_sec % 60:02d}"

            embed = discord.Embed(
                title=f"{self.emoji.ADD} Playlist Added to Queue",
                description=f"**{tracks.name}**",
                color=0x1DB954
            )
            embed.add_field(name=f"{self.emoji.MUSICAL_NOTES} Tracks", value=f"{len(tracks.tracks)} songs", inline=True)
            embed.add_field(name=f"{self.emoji.CLOCK} Total Duration", value=total_duration, inline=True)
            embed.add_field(name=f"{self.emoji.QUALITY} Quality", value="384kbps Ultra HD", inline=True)

            embed.set_footer(
                text=f"Requested by {ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url
            )

            await search_msg.edit(embed=embed)
            # Auto-delete after 5 seconds
            asyncio.create_task(self.auto_delete_message(search_msg, 5))

            if not vc.playing and not vc.queue.is_empty:
                next_track = await vc.queue.get_wait()
                await vc.play(next_track)
                await self.display_player_embed(vc, next_track, ctx)
        else:
            track = tracks[0]
            await vc.queue.put_wait(track)

            # Create enhanced track added embed
            duration = f"{track.length // 1000 // 60}:{track.length // 1000 % 60:02d}"
            embed = discord.Embed(
                title=f"{self.emoji.ADD} Track Added to Queue",
                description=f"**{track.title}**",
                color=0x1DB954
            )
            embed.add_field(name=f"{self.emoji.MICROPHONE} Artist", value=track.author, inline=True)
            embed.add_field(name=f"{self.emoji.CLOCK} Duration", value=duration, inline=True)
            embed.add_field(name=f"{self.emoji.QUALITY} Quality", value="384kbps Ultra HD", inline=True)

            if track.artwork:
                embed.set_thumbnail(url=track.artwork)

            embed.set_footer(
                text=f"Requested by {ctx.author.display_name}",
                icon_url=ctx.author.display_avatar.url
            )

            await search_msg.edit(embed=embed)
            # Auto-delete after 5 seconds
            asyncio.create_task(self.auto_delete_message(search_msg, 5))

            if not vc.playing and not vc.queue.is_empty:
                next_track = await vc.queue.get_wait()
                await vc.play(next_track)
                await self.display_player_embed(vc, next_track, ctx)

    async def handle_spotify_link(self, ctx, vc, link, type_):
        """Handle Spotify links"""
        try:
            if type_ == "track":
                track_id = re.search(SPOTIFY_TRACK_REGEX, link).group(1)
                track_info = await spotify_api.get_track(track_id)

                title = track_info['name']
                author = ', '.join(artist['name'] for artist in track_info['artists'])

                search_query = f"{title} by {author}"
                search_results = await wavelink.Playable.search(search_query)

                if not search_results:
                    embed = discord.Embed(
                        title=f"{self.emoji.ERROR} Track Not Available",
                        description="This Spotify track is not available on YouTube.",
                        color=0xFF0000
                    )
                    await ctx.send(embed=embed)
                    return

                track = search_results[0]
                await vc.queue.put_wait(track)

                # Create enhanced Spotify track added embed
                duration = f"{track.length // 1000 // 60}:{track.length // 1000 % 60:02d}"
                embed = discord.Embed(
                    title=f"{self.emoji.SPOTIFY} Spotify Track Added",
                    description=f"**{track.title}**",
                    color=0x1DB954
                )
                embed.add_field(name=f"{self.emoji.MICROPHONE} Artist", value=track.author, inline=True)
                embed.add_field(name=f"{self.emoji.CLOCK} Duration", value=duration, inline=True)
                embed.add_field(name=f"{self.emoji.QUALITY} Quality", value="384kbps Ultra HD", inline=True)

                if track.artwork:
                    embed.set_thumbnail(url=track.artwork)

                embed.set_footer(
                    text=f"Requested by {ctx.author.display_name}",
                    icon_url=ctx.author.display_avatar.url
                )

                msg = await ctx.send(embed=embed)
                # Auto-delete after 5 seconds
                asyncio.create_task(self.auto_delete_message(msg, 5))

                if not vc.playing:
                    await vc.play(track)
                    await self.display_player_embed(vc, track, ctx)

            elif type_ == "playlist":
                embed = discord.Embed(
                    title=f"{self.emoji.LOADING} Processing Playlist",
                    description="Adding tracks from Spotify playlist... This may take a while...",
                    color=0x1DB954
                )
                process_msg = await ctx.send(embed=embed)

                playlist_id = re.search(SPOTIFY_PLAYLIST_REGEX, link).group(1)
                playlist_info = await spotify_api.get(f"playlists/{playlist_id}")
                tracks = playlist_info.get("tracks", {}).get("items", [])
                playlist_length = len(tracks)

                if not tracks:
                    embed = discord.Embed(
                        title=f"{self.emoji.ERROR} Empty Playlist",
                        description="No tracks found in the Spotify playlist.",
                        color=0xFF0000
                    )
                    await process_msg.edit(embed=embed)
                    return

                c = 0
                for track_item in tracks:
                    title = track_item['track']['name']
                    author = ', '.join(artist['name'] for artist in track_item['track']['artists'])
                    search_query = f"{title} {author}"

                    track_results = await wavelink.Playable.search(search_query)
                    if track_results:
                        await vc.queue.put_wait(track_results[0])
                        c += 1

                embed = discord.Embed(
                    title=f"{self.emoji.ADD} Spotify Playlist Added",
                    description=f"**{c}** out of **{playlist_length}** tracks from **{playlist_info['name']}** have been added to the queue!",
                    color=0x1DB954
                )
                await process_msg.edit(embed=embed)
                # Auto-delete after 5 seconds
                asyncio.create_task(self.auto_delete_message(process_msg, 5))

                if not vc.playing:
                    next_track = await vc.queue.get_wait()
                    await vc.play(next_track)
                    await self.display_player_embed(vc, next_track, ctx)

            elif type_ == "album":
                embed = discord.Embed(
                    title=f"{self.emoji.LOADING} Processing Album",
                    description="Adding tracks from Spotify album... Please wait...",
                    color=0x1DB954
                )
                await ctx.send(embed=embed)

                album_id = re.search(SPOTIFY_ALBUM_REGEX, link).group(1)
                album_info = await spotify_api.get(f"albums/{album_id}")
                tracks = album_info.get("tracks", {}).get("items", [])

                if not tracks:
                    embed = discord.Embed(
                        title=f"{self.emoji.ERROR} Empty Album",
                        description="No tracks found in the Spotify album.",
                        color=0xFF0000
                    )
                    await ctx.send(embed=embed)
                    return

                for track_item in tracks:
                    title = track_item['name']
                    author = ', '.join(artist['name'] for artist in track_item['artists'])
                    search_query = f"{title} {author}"

                    track_results = await wavelink.Playable.search(search_query)
                    if track_results:
                        await vc.queue.put_wait(track_results[0])

                embed = discord.Embed(
                    title=f"{self.emoji.ADD} Spotify Album Added",
                    description=f"All tracks from **{album_info['name']}** have been added to the queue!",
                    color=0x1DB954
                )
                await ctx.send(embed=embed)
                if not vc.playing:
                    next_track = await vc.queue.get_wait()
                    await vc.play(next_track)
                    await self.display_player_embed(vc, next_track, ctx)

        except Exception as e:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Spotify Error",
                description=f"An error occurred while processing the Spotify link: {str(e)}",
                color=0xFF0000
            )
            await ctx.send(embed=embed)

    def create_progress_bar(self, completed, total, length=15):
        """Create a visual progress bar"""
        if total == 0:
            return "▬" * length

        percentage = completed / total
        filled_length = int(length * percentage)
        bar = '█' * filled_length + '▬' * (length - filled_length)
        return bar

    # Music commands with enhanced responses
    @commands.hybrid_command(name="play", aliases=['p'], usage="play <query>", help="Plays a song or playlist with high quality audio.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def play(self, ctx: commands.Context, *, query: str):
        """Play music from YouTube, Spotify, or search query with high quality audio"""
        await self.play_source(ctx, query)

    @commands.hybrid_command(name="search", usage="search <query>", help="Searches music from multiple platforms.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def search2(self, ctx: commands.Context, *, query: str):
        """Search for music across different platforms"""
        if not ctx.author.voice:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Voice Channel Required",
                description="You need to be in a voice channel to search for music!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"{self.emoji.SEARCH} Select Search Platform",
            description=f"Choose where to search for: **{query}**",
            color=0x1DB954
        )
        embed.add_field(
            name=f"{self.emoji.YOUTUBE} YouTube",
            value="Search on YouTube Music",
            inline=True
        )
        embed.add_field(
            name=f"{self.emoji.SOUNDCLOUD} SoundCloud",
            value="Search on SoundCloud",
            inline=True
        )
        await ctx.send(embed=embed, view=PlatformSelectView(ctx, query))

    @commands.hybrid_command(name="nowplaying", aliases=["np"], usage="nowplaying", help="Shows the info about current playing song.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def nowplaying(self, ctx: commands.Context):
        """Display currently playing track with progress bar"""
        vc = ctx.voice_client
        if not vc or not vc.playing:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} No Music Playing",
                description="There's no music currently playing!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if not ctx.author.voice or ctx.author.voice.channel.id != vc.channel.id:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Wrong Voice Channel",
                description="You need to be in the same voice channel as me!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        track = vc.current
        position = vc.position / 1000
        length = track.length / 1000

        progress_bar = self.create_progress_bar(position, length)
        position_str = f"{int(position // 60)}:{int(position % 60):02d}"
        length_str = f"{int(length // 60)}:{int(length % 60):02d}"

        # Determine source
        if "spotify" in track.uri:
            source_emoji = self.emoji.SPOTIFY
            source_name = "Spotify"
        elif "youtube" in track.uri:
            source_emoji = self.emoji.YOUTUBE
            source_name = "YouTube"
        elif "soundcloud" in track.uri:
            source_emoji = self.emoji.SOUNDCLOUD
            source_name = "SoundCloud"
        else:
            source_emoji = self.emoji.MUSICAL_NOTE
            source_name = "Unknown"

        embed = discord.Embed(
            title=f"{self.emoji.MUSICAL_NOTES} Now Playing - High Quality",
            color=0x1DB954
        )
        embed.add_field(
            name=f"{self.emoji.MUSICAL_NOTE} Track",
            value=f"[{track.title}]({track.uri})",
            inline=False
        )
        embed.add_field(
            name=f"{self.emoji.MICROPHONE} Artist",
            value=track.author,
            inline=True
        )
        embed.add_field(
            name=f"{self.emoji.QUALITY} Quality",
            value="320kbps",
            inline=True
        )
        embed.add_field(
            name=f"{self.emoji.CLOCK} Progress",
            value=f"`{position_str}` {progress_bar} `{length_str}`",
            inline=False
        )
        embed.add_field(
            name=f"{self.emoji.QUEUE} Queue",
            value=f"`{len(vc.queue)}` tracks waiting",
            inline=True
        )
        embed.add_field(
            name=f"{self.emoji.RADIO} Source",
            value=f"{source_emoji} {source_name}",
            inline=True
        )

        if track.artwork:
            embed.set_image(url=track.artwork)

        embed.set_footer(
            text=f"Requested by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="join", usage="join", help="Joins your voice channel.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def join(self, ctx: commands.Context):
        """Join the voice channel"""
        if not ctx.author.voice:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Voice Channel Required",
                description="You need to be in a voice channel for me to join!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if ctx.voice_client:
            if ctx.voice_client.channel == ctx.author.voice.channel:
                embed = discord.Embed(
                    title=f"{self.emoji.WARNING} Already Connected",
                    description=f"I'm already in {ctx.voice_client.channel.mention}!",
                    color=0xFFA500
                )
                await ctx.send(embed=embed)
                return
            else:
                # Move to the new channel
                await ctx.voice_client.move_to(ctx.author.voice.channel)
                embed = discord.Embed(
                    title=f"{self.emoji.SUCCESS} Moved",
                    description=f"Moved to {ctx.author.voice.channel.mention}!",
                    color=0x1DB954
                )
                await ctx.send(embed=embed)
                return

        channel = ctx.author.voice.channel
        try:
            # Check if Lavalink is connected
            if not wavelink.Pool.nodes:
                embed = discord.Embed(
                    title=f"{self.emoji.ERROR} Lavalink Not Connected",
                    description="Music server is not ready. Please wait a moment and try again.",
                    color=0xFF0000
                )
                await ctx.send(embed=embed)
                return

            vc = await channel.connect(cls=wavelink.Player)
            vc.ctx = ctx
            await vc.set_volume(100)
            vc.autoplay = wavelink.AutoPlayMode.disabled

            embed = discord.Embed(
                title=f"{self.emoji.SUCCESS} Connected",
                description=f"✅ Successfully joined {channel.mention}!\n\n"
                           "🎵 Use `/play` or `/play` to start playing music\n"
                           "🔄 Use `/autoplay` or `/autoplay` for 24/7 mode",
                color=0x1DB954
            )
            embed.set_footer(text=f"Joined by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)

        except Exception as e:
            print(f"Error joining voice channel: {e}")
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Connection Failed",
                description=f"Failed to join voice channel. Make sure I have proper permissions.\nError: {str(e)}",
                color=0xFF0000
            )
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="disconnect", aliases=["dc", "leave"], usage="disconnect", help="Disconnects from voice channel.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def disconnect(self, ctx: commands.Context):
        """Disconnect from voice channel"""
        vc = ctx.voice_client
        if not vc:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Not Connected",
                description="I'm not connected to any voice channel!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.voice and ctx.author.voice.channel != vc.channel:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Wrong Voice Channel",
                description="You need to be in the same voice channel as me!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        await vc.disconnect()
        embed = discord.Embed(
            title=f"{self.emoji.SUCCESS} Disconnected",
            description="Successfully disconnected from the voice channel!",
            color=0x1DB954
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="pause", usage="pause", help="Pauses the current track.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pause(self, ctx: commands.Context):
        """Pause the music"""
        vc = ctx.voice_client
        if not vc or not vc.playing:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} No Music Playing",
                description="There's no music currently playing!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.voice and ctx.author.voice.channel != vc.channel:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Wrong Voice Channel",
                description="You need to be in the same voice channel as me!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        await vc.pause(True)

        # Enhanced pause embed
        position = vc.position / 1000
        duration = vc.current.length / 1000
        position_str = f"{int(position // 60)}:{int(position % 60):02d}"
        duration_str = f"{int(duration // 60)}:{int(duration % 60):02d}"

        embed = discord.Embed(
            title=f"{self.emoji.PAUSE} Playback Paused",
            description=f"**{vc.current.title}**",
            color=0xFFA500
        )
        embed.add_field(name=f"{self.emoji.MICROPHONE} Artist", value=vc.current.author, inline=True)
        embed.add_field(name=f"{self.emoji.CLOCK} Paused At", value=f"{position_str} / {duration_str}", inline=True)
        embed.add_field(name=f"{self.emoji.QUEUE} Queue", value=f"{len(vc.queue)} tracks", inline=True)

        if vc.current.artwork:
            embed.set_thumbnail(url=vc.current.artwork)

        embed.set_footer(
            text=f"Paused by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )

        msg = await ctx.send(embed=embed)

        # Auto-delete after 1 second
        await asyncio.sleep(1)
        try:
            await msg.delete()
        except:
            pass

    @commands.hybrid_command(name="resume", usage="resume", help="Resumes the paused track.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def resume(self, ctx: commands.Context):
        """Resume the music"""
        vc = ctx.voice_client
        if not vc:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Not Connected",
                description="I'm not connected to any voice channel!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if not vc.paused:
            embed = discord.Embed(
                title=f"{self.emoji.WARNING} Already Playing",
                description="The music is already playing!",
                color=0xFFA500
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.voice and ctx.author.voice.channel != vc.channel:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Wrong Voice Channel",
                description="You need to be in the same voice channel as me!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        await vc.pause(False)

        # Enhanced resume embed
        position = vc.position / 1000
        duration = vc.current.length / 1000
        position_str = f"{int(position // 60)}:{int(position % 60):02d}"
        duration_str = f"{int(duration // 60)}:{int(duration % 60):02d}"

        embed = discord.Embed(
            title=f"{self.emoji.PLAY} Playback Resumed",
            description=f"**{vc.current.title}**",
            color=0x1DB954
        )
        embed.add_field(name=f"{self.emoji.MICROPHONE} Artist", value=vc.current.author, inline=True)
        embed.add_field(name=f"{self.emoji.CLOCK} Resume At", value=f"{position_str} / {duration_str}", inline=True)
        embed.add_field(name=f"{self.emoji.QUEUE} Queue", value=f"{len(vc.queue)} tracks", inline=True)

        if vc.current.artwork:
            embed.set_thumbnail(url=vc.current.artwork)

        embed.set_footer(
            text=f"Resumed by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )

        msg = await ctx.send(embed=embed)

        # Auto-delete after 1 second
        await asyncio.sleep(1)
        try:
            await msg.delete()
        except:
            pass

    @commands.hybrid_command(name="skip", usage="skip", help="Skips the current track.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def skip(self, ctx: commands.Context):
        """Skip the current track"""
        vc = ctx.voice_client
        if not vc or not vc.playing:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} No Music Playing",
                description="There's no music currently playing!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.voice and ctx.author.voice.channel != vc.channel:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Wrong Voice Channel",
                description="You need to be in the same voice channel as me!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        current_track_title = vc.current.title
        current_track_author = vc.current.author
        current_track_artwork = vc.current.artwork if hasattr(vc.current, 'artwork') else None

        await vc.stop()

        # Enhanced skip embed
        embed = discord.Embed(
            title=f"{self.emoji.SKIP} Track Skipped",
            description=f"**{current_track_title}**",
            color=0x1DB954
        )
        embed.add_field(name=f"{self.emoji.MICROPHONE} Artist", value=current_track_author, inline=True)

        if not vc.queue.is_empty:
            next_track = list(vc.queue)[0] if len(vc.queue) > 0 else None
            if next_track:
                embed.add_field(name=f"{self.emoji.MUSICAL_NOTE} Next", value=next_track.title[:30] + "..." if len(next_track.title) > 30 else next_track.title, inline=True)

        embed.add_field(name=f"{self.emoji.QUEUE} Remaining", value=f"{len(vc.queue)} tracks", inline=True)

        if current_track_artwork:
            embed.set_thumbnail(url=current_track_artwork)

        embed.set_footer(
            text=f"Skipped by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )

        msg = await ctx.send(embed=embed)

        # Auto-delete after 1 second
        await asyncio.sleep(1)
        try:
            await msg.delete()
        except:
            pass

    @commands.hybrid_command(name="stop", usage="stop", help="Stops playback and clears the queue.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def stop(self, ctx: commands.Context):
        """Stop playback and clear queue"""
        vc = ctx.voice_client
        if not vc:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Not Connected",
                description="I'm not connected to any voice channel!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.voice and ctx.author.voice.channel != vc.channel:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Wrong Voice Channel",
                description="You need to be in the same voice channel as me!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        # Clear active player message
        guild_id = ctx.guild.id
        if guild_id in active_player_messages:
            try:
                await active_player_messages[guild_id].delete()
                del active_player_messages[guild_id]
            except:
                pass

        vc.queue.clear()
        await vc.disconnect()
        embed = discord.Embed(
            title=f"{self.emoji.STOP} Playback Stopped",
            description="Music playback has been stopped and queue cleared!",
            color=0x1DB954
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="volume", aliases=["vol"], usage="volume <1-150>", help="Sets the player volume.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def volume(self, ctx: commands.Context, volume: int):
        """Set the player volume"""
        vc = ctx.voice_client
        if not vc:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Not Connected",
                description="I'm not connected to any voice channel!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.voice and ctx.author.voice.channel != vc.channel:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Wrong Voice Channel",
                description="You need to be in the same voice channel as me!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if not 1 <= volume <= 200:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Invalid Volume",
                description="Volume must be between 1 and 200!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        old_volume = vc.volume
        await vc.set_volume(volume)

        # Enhanced volume embed
        volume_emoji = self.emoji.VOLUME_MUTE if volume == 0 else self.emoji.VOLUME_LOW if volume < 50 else self.emoji.VOLUME_HIGH

        embed = discord.Embed(
            title=f"{volume_emoji} Volume Adjusted",
            description=f"Volume changed from `{old_volume}%` to `{volume}%`",
            color=0x1DB954
        )

        if vc.playing:
            embed.add_field(name=f"{self.emoji.MUSICAL_NOTE} Now Playing", value=vc.current.title[:40] + "..." if len(vc.current.title) > 40 else vc.current.title, inline=False)

        embed.set_footer(
            text=f"Adjusted by {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )

        msg = await ctx.send(embed=embed)

        # Auto-delete after 1 second
        await asyncio.sleep(1)
        try:
            await msg.delete()
        except:
            pass

    @commands.hybrid_command(name="queue", aliases=["q"], usage="queue", help="Shows the current queue.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def queue(self, ctx: commands.Context):
        """Show the current queue"""
        vc = ctx.voice_client
        if not vc:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Not Connected",
                description="I'm not connected to any voice channel!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if vc.queue.is_empty:
            embed = discord.Embed(
                title=f"{self.emoji.QUEUE} Queue Empty",
                description="The queue is currently empty!",
                color=0xFFA500
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"{self.emoji.QUEUE} Current Queue",
            description=f"Showing up to 10 tracks in queue",
            color=0x1DB954
        )

        queue_list = list(vc.queue)[:10]
        for i, track in enumerate(queue_list, start=1):
            duration = f"{track.length // 1000 // 60}:{track.length // 1000 % 60:02d}"
            embed.add_field(
                name=f"{i}. {track.title}",
                value=f"**Artist:** {track.author} | **Duration:** {duration}",
                inline=False
            )

        if len(vc.queue) > 10:
            embed.set_footer(text=f"And {len(vc.queue) - 10} more tracks in queue...")

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="clearqueue", aliases=["cq"], usage="clearqueue", help="Clears the entire queue.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def clearqueue(self, ctx: commands.Context):
        """Clear the queue"""
        vc = ctx.voice_client
        if not vc:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Not Connected",
                description="I'm not connected to any voice channel!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.voice and ctx.author.voice.channel != vc.channel:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Wrong Voice Channel",
                description="You need to be in the same voice channel as me!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if vc.queue.is_empty:
            embed = discord.Embed(
                title=f"{self.emoji.WARNING} Queue Already Empty",
                description="The queue is already empty!",
                color=0xFFA500
            )
            await ctx.send(embed=embed)
            return

        queue_count = len(vc.queue)
        vc.queue.clear()
        embed = discord.Embed(
            title=f"{self.emoji.CLEAR} Queue Cleared",
            description=f"Cleared `{queue_count}` tracks from the queue!",
            color=0x1DB954
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="shuffle", usage="shuffle", help="Shuffles the queue.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def shuffle(self, ctx: commands.Context):
        """Shuffle the queue"""
        vc = ctx.voice_client
        if not vc:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Not Connected",
                description="I'm not connected to any voice channel!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.voice and ctx.author.voice.channel != vc.channel:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Wrong Voice Channel",
                description="You need to be in the same voice channel as me!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if vc.queue.is_empty:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Queue Empty",
                description="The queue is empty, nothing to shuffle!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        random.shuffle(vc.queue)
        embed = discord.Embed(
            title=f"{self.emoji.SHUFFLE} Queue Shuffled",
            description=f"Shuffled `{len(vc.queue)}` tracks in the queue!",
            color=0x1DB954
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="loop", usage="loop", help="Toggles loop mode.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def loop(self, ctx: commands.Context):
        """Toggle loop mode"""
        vc = ctx.voice_client
        if not vc or not vc.playing:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} No Music Playing",
                description="There's no music currently playing!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.voice and ctx.author.voice.channel != vc.channel:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Wrong Voice Channel",
                description="You need to be in the same voice channel as me!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        vc.queue.mode = wavelink.QueueMode.loop if vc.queue.mode != wavelink.QueueMode.loop else wavelink.QueueMode.normal
        mode = "enabled" if vc.queue.mode == wavelink.QueueMode.loop else "disabled"
        embed = discord.Embed(
            title=f"{self.emoji.REPEAT} Loop {mode.title()}",
            description=f"Loop mode has been **{mode}**!",
            color=0x1DB954 if mode == "enabled" else 0xFFA500
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="autoplay", usage="autoplay", help="Start 24/7 autoplay with unlimited random songs")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def autoplay(self, ctx: commands.Context):
        """Start 24/7 autoplay with unlimited random songs - no control panel, just music"""
        if not ctx.author.voice:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Voice Channel Required",
                description="You need to be in a voice channel to use autoplay!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        vc = ctx.voice_client
        if not vc:
            try:
                vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
                await vc.set_volume(100)
            except Exception as e:
                embed = discord.Embed(
                    title=f"{self.emoji.ERROR} Connection Failed",
                    description=f"Failed to join voice channel: {str(e)}",
                    color=0xFF0000
                )
                await ctx.send(embed=embed)
                return

        vc.ctx = ctx
        vc.autoplay = wavelink.AutoPlayMode.enabled

        # Mark this player as autoplay-only (no control panel)
        vc._autoplay_only = True

        # Define song categories for 24/7 random playback
        autoplay_queries = [
            # Lofi music
            "lofi hip hop radio", "lofi study music", "chill lofi beats", "lofi relaxing music",
            "lofi sleep music", "lofi jazz", "lofi piano", "lofi rain", "lofi cafe",

            # Hindi songs
            "latest hindi songs", "bollywood romantic songs", "hindi lofi songs",
            "arijit singh songs", "hindi sad songs", "shreya ghoshal songs",
            "atif aslam hindi songs", "latest bollywood songs", "jubin nautiyal songs",

            # English sad songs
            "sad songs english", "heartbreak songs", "emotional songs english",
            "depressing songs", "cry songs", "breakup songs english",
            "sad love songs", "lonely songs", "melancholic songs",

            # English popular
            "top english songs", "pop hits", "indie music", "alternative rock",
            "acoustic songs", "chill english songs", "soft pop songs",

            # Arabian/Arabic music
            "arabic songs", "arabic music", "arabic lofi", "arabic romantic songs",
            "arabic sad songs", "mohamed hamaki", "tamer hosny songs",
            "nancy ajram songs", "fairuz arabic songs", "amr diab songs"
        ]

        # Add initial songs to queue
        embed = discord.Embed(
            title=f"{self.emoji.LOADING} Starting 24/7 Autoplay",
            description="🎵 Loading unlimited random songs...\n\n"
                       "**Genres included:**\n"
                       "• 🎧 Lofi & Chill Beats\n"
                       "• 🇮🇳 Hindi & Bollywood\n"
                       "• 😢 Sad & Emotional\n"
                       "• 🎤 English Pop & Indie\n"
                       "• 🕌 Arabian/Arabic Music",
            color=0x1DB954
        )

        # Handle both slash commands and text commands properly
        if ctx.interaction and not ctx.interaction.response.is_done():
            await ctx.interaction.response.defer()
            status_msg = await ctx.interaction.followup.send(embed=embed, wait=True)
        else:
            status_msg = await ctx.send(embed=embed)

        added_count = 0
        for _ in range(20):  # Add 20 random songs to start
            random_query = random.choice(autoplay_queries)
            try:
                tracks = await wavelink.Playable.search(random_query)
                if tracks:
                    track = tracks[0] if not isinstance(tracks, wavelink.Playlist) else tracks.tracks[0]
                    await vc.queue.put_wait(track)
                    added_count += 1
            except:
                continue

        embed = discord.Embed(
            title=f"{self.emoji.SUCCESS} 24/7 Autoplay Started!",
            description=f"✅ **Unlimited music playback activated!**\n\n"
                       f"🎵 **{added_count}** songs loaded initially\n"
                       "🔄 **Auto-queue enabled** - Songs will keep adding automatically\n"
                       "🎶 **Quality:** 384kbps Ultra HD\n"
                       "🎧 **Genres:** Lofi, Hindi, Sad, English, Arabian\n"
                       "♾️ **Mode:** Continuous 24/7 playback\n\n"
                       f"**Stop with:** `/stop` or `/stop`",
            color=0x1DB954
        )
        embed.set_footer(text=f"Started by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        await status_msg.edit(embed=embed)

        # Auto-delete status message after 5 seconds
        await asyncio.sleep(5)
        try:
            await status_msg.delete()
        except:
            pass

        if not vc.playing:
            next_track = await vc.queue.get_wait()
            await vc.play(next_track)
            # Send simple notification without control panel
            simple_embed = discord.Embed(
                title=f"{self.emoji.MUSICAL_NOTES} Now Playing - 24/7 Autoplay",
                description=f"**{next_track.title}**\nby **{next_track.author}**",
                color=0x1DB954
            )
            if next_track.artwork:
                simple_embed.set_thumbnail(url=next_track.artwork)
            simple_embed.set_footer(text="Autoplay Mode - No controls needed, music plays continuously")
            msg = await ctx.send(embed=simple_embed)
            # Auto-delete after 10 seconds
            await asyncio.sleep(10)
            try:
                await msg.delete()
            except:
                pass

    @commands.hybrid_command(name="seek", usage="seek <seconds>", help="Seeks to a position in the track.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def seek(self, ctx: commands.Context, seconds: int):
        """Seek to a position in the track"""
        vc = ctx.voice_client
        if not vc or not vc.playing:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} No Music Playing",
                description="There's no music currently playing!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.voice and ctx.author.voice.channel != vc.channel:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Wrong Voice Channel",
                description="You need to be in the same voice channel as me!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if seconds < 0 or seconds * 1000 > vc.current.length:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Invalid Position",
                description=f"Position must be between 0 and {vc.current.length // 1000} seconds!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        await vc.seek(seconds * 1000)
        embed = discord.Embed(
            title=f"{self.emoji.CLOCK} Seeked",
            description=f"Seeked to `{seconds // 60}:{seconds % 60:02d}` in **{vc.current.title}**!",
            color=0x1DB954
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="replay", usage="replay", help="Replays the current track.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def replay(self, ctx: commands.Context):
        """Replay the current track"""
        vc = ctx.voice_client
        if not vc or not vc.playing:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} No Music Playing",
                description="There's no music currently playing!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.voice and ctx.author.voice.channel != vc.channel:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Wrong Voice Channel",
                description="You need to be in the same voice channel as me!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        await vc.seek(0)
        embed = discord.Embed(
            title=f"{self.emoji.REPEAT} Replaying",
            description=f"Replaying **{vc.current.title}**!",
            color=0x1DB954
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="playlist", usage="playlist <action>", help="Manage your music playlists")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def playlist(self, ctx: commands.Context):
        """Playlist management system"""
        embed = discord.Embed(
            title="📂 Playlist Management",
            description="Manage your personal music playlists!",
            color=0x1DB954
        )
        embed.add_field(
            name="Available Commands",
            value=(
                "• `/playlist create <name>` - Create a new playlist\n"
                "• `/playlist list` - View your playlists\n"
                "• `/playlist add <playlist>` - Add current track to playlist\n"
                "• `/playlist play <playlist>` - Play a playlist\n"
                "• `/playlist delete <playlist>` - Delete a playlist\n"
                "• `/playlist view <playlist>` - View playlist tracks"
            ),
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="createplaylist", usage="createplaylist <name>", help="Create a new playlist")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def createplaylist(self, ctx: commands.Context, *, name: str):
        """Create a new playlist"""
        user_id = ctx.author.id

        if user_id not in user_playlists:
            user_playlists[user_id] = {}

        if name in user_playlists[user_id]:
            embed = discord.Embed(
                title="❌ Playlist Exists",
                description=f"You already have a playlist named **{name}**!",
                color=0xFF0000
            )
        else:
            user_playlists[user_id][name] = []
            embed = discord.Embed(
                title="✅ Playlist Created",
                description=f"Created playlist **{name}**!",
                color=0x1DB954
            )

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="playlists", usage="playlists", help="View your playlists")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def playlists(self, ctx: commands.Context):
        """View all your playlists"""
        user_id = ctx.author.id
        playlists = user_playlists.get(user_id, {})

        if not playlists:
            embed = discord.Embed(
                title="📂 Your Playlists",
                description="You don't have any playlists yet!\nUse `/createplaylist <name>` to create one.",
                color=0xFFA500
            )
        else:
            embed = discord.Embed(
                title="📂 Your Playlists",
                description=f"You have {len(playlists)} playlist(s):",
                color=0x1DB954
            )
            for name, tracks in list(playlists.items())[:10]:
                embed.add_field(
                    name=f"📁 {name}",
                    value=f"`{len(tracks)}` tracks",
                    inline=True
                )

            if len(playlists) > 10:
                embed.set_footer(text=f"And {len(playlists) - 10} more playlists...")

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="playplaylist", usage="playplaylist <name>", help="Play a saved playlist")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def playplaylist(self, ctx: commands.Context, *, name: str):
        """Play a saved playlist"""
        if not ctx.author.voice:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Voice Channel Required",
                description="You need to be in a voice channel!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        user_id = ctx.author.id
        playlists = user_playlists.get(user_id, {})

        if name not in playlists:
            embed = discord.Embed(
                title="❌ Playlist Not Found",
                description=f"You don't have a playlist named **{name}**!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        vc = ctx.voice_client
        if not vc:
            vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)
            await vc.set_volume(100)

        vc.ctx = ctx

        embed = discord.Embed(
            title=f"{self.emoji.LOADING} Loading Playlist",
            description=f"Loading **{name}**...",
            color=0x1DB954
        )
        msg = await ctx.send(embed=embed)

        tracks_data = playlists[name]
        loaded_count = 0

        for track_data in tracks_data:
            try:
                results = await wavelink.Playable.search(track_data['uri'])
                if results:
                    await vc.queue.put_wait(results[0] if isinstance(results, list) else results)
                    loaded_count += 1
            except:
                continue

        embed = discord.Embed(
            title="✅ Playlist Loaded",
            description=f"Loaded **{loaded_count}** tracks from **{name}**!",
            color=0x1DB954
        )
        await msg.edit(embed=embed)

        if not vc.playing:
            next_track = await vc.queue.get_wait()
            await vc.play(next_track)
            await self.display_player_embed(vc, next_track, ctx)

    @commands.hybrid_command(name="deleteplaylist", usage="deleteplaylist <name>", help="Delete a playlist")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def deleteplaylist(self, ctx: commands.Context, *, name: str):
        """Delete a playlist"""
        user_id = ctx.author.id
        playlists = user_playlists.get(user_id, {})

        if name not in playlists:
            embed = discord.Embed(
                title="❌ Playlist Not Found",
                description=f"You don't have a playlist named **{name}**!",
                color=0xFF0000
            )
        else:
            del user_playlists[user_id][name]
            embed = discord.Embed(
                title="✅ Playlist Deleted",
                description=f"Deleted playlist **{name}**!",
                color=0x1DB954
            )

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="viewplaylist", usage="viewplaylist <name>", help="View tracks in a playlist")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def viewplaylist(self, ctx: commands.Context, *, name: str):
        """View tracks in a playlist"""
        user_id = ctx.author.id
        playlists = user_playlists.get(user_id, {})

        if name not in playlists:
            embed = discord.Embed(
                title="❌ Playlist Not Found",
                description=f"You don't have a playlist named **{name}**!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        tracks = playlists[name]

        if not tracks:
            embed = discord.Embed(
                title=f"📁 {name}",
                description="This playlist is empty!",
                color=0xFFA500
            )
        else:
            embed = discord.Embed(
                title=f"📁 {name}",
                description=f"{len(tracks)} tracks in this playlist:",
                color=0x1DB954
            )

            for i, track in enumerate(tracks[:10], 1):
                embed.add_field(
                    name=f"{i}. {track['title'][:40]}",
                    value=f"by {track['author'][:30]}",
                    inline=False
                )

            if len(tracks) > 10:
                embed.set_footer(text=f"And {len(tracks) - 10} more tracks...")

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="stats", aliases=["statistics"], usage="stats", help="View comprehensive server music statistics")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def stats(self, ctx: commands.Context):
        """Display comprehensive server music statistics"""
        try:
            stats = await self.client.music_db.get_server_stats(ctx.guild.id)

            embed = discord.Embed(
                title=f"📊 {ctx.guild.name} - Music Statistics",
                description="Comprehensive music analytics for this server",
                color=0x1DB954
            )
            embed.add_field(
                name=f"{self.emoji.MUSICAL_NOTES} Total Plays",
                value=f"**{stats['total_plays']:,}** tracks played",
                inline=True
            )
            embed.add_field(
                name=f"{self.emoji.SEARCH} Total Searches",
                value=f"**{stats['total_searches']:,}** searches",
                inline=True
            )
            embed.add_field(
                name="📈 This Week",
                value=f"**{stats['plays_this_week']:,}** plays",
                inline=True
            )
            embed.add_field(
                name=f"{self.emoji.HEADPHONES} Unique Listeners",
                value=f"**{stats['unique_listeners']}** users",
                inline=True
            )
            embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
            embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

            await ctx.send(embed=embed)
        except Exception as e:
            print(f"Stats error: {e}")
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Error",
                description="No statistics available yet. Play some music first!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="toptracks", aliases=["top"], usage="toptracks [limit]", help="View most played tracks")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def toptracks(self, ctx: commands.Context, limit: int = 10):
        """Display server's most played tracks"""
        try:
            if limit > 25:
                limit = 25

            top_tracks = await self.client.music_db.get_top_tracks(ctx.guild.id, limit)

            if not top_tracks:
                embed = discord.Embed(
                    title=f"{self.emoji.ERROR} No Data",
                    description="No tracks have been played yet!",
                    color=0xFF0000
                )
                await ctx.send(embed=embed)
                return

            embed = discord.Embed(
                title=f"🏆 Top {len(top_tracks)} Most Played Tracks",
                description=f"Most popular tracks in **{ctx.guild.name}**",
                color=0x1DB954
            )

            for i, track in enumerate(top_tracks, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                embed.add_field(
                    name=f"{medal} {track['title'][:40]}",
                    value=f"by **{track['author'][:30]}** • {track['play_count']} plays",
                    inline=False
                )

            embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            print(f"Top tracks error: {e}")
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Error",
                description="Could not fetch top tracks!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="history", aliases=["myhistory"], usage="history", help="View your listening history")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def history(self, ctx: commands.Context):
        """Display user's listening history"""
        try:
            history = await self.client.music_db.get_user_listening_history(ctx.guild.id, ctx.author.id, 10)

            if not history:
                embed = discord.Embed(
                    title=f"{self.emoji.ERROR} No History",
                    description="You haven't listened to any music yet!",
                    color=0xFF0000
                )
                await ctx.send(embed=embed)
                return

            embed = discord.Embed(
                title=f"{self.emoji.HISTORY} Your Listening History",
                description=f"Recently played tracks by **{ctx.author.display_name}**",
                color=0x1DB954
            )

            for i, track in enumerate(history, 1):
                duration = f"{track['duration'] // 60}:{track['duration'] % 60:02d}"
                embed.add_field(
                    name=f"{i}. {track['title'][:40]}",
                    value=f"by **{track['author'][:30]}** • {duration}",
                    inline=False
                )

            embed.set_footer(text=f"Last 10 tracks played", icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
        except Exception as e:
            print(f"History error: {e}")
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Error",
                description="Could not fetch listening history!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="mystats", aliases=["userstats"], usage="mystats", help="View your personal listening statistics")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def mystats(self, ctx: commands.Context):
        """Display user's personal listening statistics"""
        try:
            user_stats = await self.client.music_db.get_user_stats(ctx.guild.id, ctx.author.id)

            if not user_stats:
                embed = discord.Embed(
                    title=f"{self.emoji.ERROR} No Data",
                    description="You haven't listened to any music yet!",
                    color=0xFF0000
                )
                await ctx.send(embed=embed)
                return

            total_hours = user_stats['total_duration'] // 3600
            total_minutes = (user_stats['total_duration'] % 3600) // 60

            embed = discord.Embed(
                title=f"{self.emoji.DASHBOARD} {ctx.author.display_name}'s Stats",
                description="Your personal listening statistics",
                color=0x1DB954
            )
            embed.add_field(
                name=f"{self.emoji.MUSICAL_NOTES} Total Listens",
                value=f"**{user_stats['total_listens']:,}** tracks",
                inline=True
            )
            embed.add_field(
                name=f"{self.emoji.CLOCK} Listening Time",
                value=f"**{total_hours}h {total_minutes}m**",
                inline=True
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            embed.set_footer(text=f"Member since server creation • Music lover")

            await ctx.send(embed=embed)
        except Exception as e:
            print(f"User stats error: {e}")
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Error",
                description="Could not fetch your statistics!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="recentsearches", aliases=["searches"], usage="recentsearches", help="View recent music searches")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def recentsearches(self, ctx: commands.Context):
        """Display recent music searches in the server"""
        try:
            searches = await self.client.music_db.get_recent_searches(ctx.guild.id, 10)

            if not searches:
                embed = discord.Embed(
                    title=f"{self.emoji.ERROR} No Searches",
                    description="No searches have been made yet!",
                    color=0xFF0000
                )
                await ctx.send(embed=embed)
                return

            embed = discord.Embed(
                title=f"{self.emoji.SEARCH} Recent Music Searches",
                description=f"Latest searches in **{ctx.guild.name}**",
                color=0x1DB954
            )

            for i, search in enumerate(searches, 1):
                results_text = f"{search['results']} results" if search['results'] > 0 else "No results"
                embed.add_field(
                    name=f"{i}. {search['query'][:40]}",
                    value=f"by **{search['user_name']}** • {results_text}",
                    inline=False
                )

            embed.set_footer(text=f"Last 10 searches", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
            await ctx.send(embed=embed)
        except Exception as e:
            print(f"Recent searches error: {e}")
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Error",
                description="Could not fetch recent searches!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="previous", aliases=["prev"], usage="previous", help="Play the previous track")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def previous(self, ctx: commands.Context):
        """Play the previous track"""
        vc = ctx.voice_client
        if not vc:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Not Connected",
                description="I'm not connected to any voice channel!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.voice and ctx.author.voice.channel != vc.channel:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Wrong Voice Channel",
                description="You need to be in the same voice channel as me!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        guild_id = ctx.guild.id
        if guild_id in track_histories and track_histories[guild_id]:
            previous_track = track_histories[guild_id].pop()
            await vc.play(previous_track)
            embed = discord.Embed(
                title=f"{self.emoji.PREVIOUS} Playing Previous Track",
                description=f"**{previous_track.title}**",
                color=0x1DB954
            )
            await ctx.send(embed=embed)
            await self.display_player_embed(vc, previous_track, ctx)
        else:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} No Previous Track",
                description="There's no previous track in history!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)

    # REMOVED VOTE-RELATED COMMANDS

# Filter Cog with enhanced responses
class FilterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_filters = {}
        self.emoji = EmojiConfig()

    async def apply_filter(self, ctx: commands.Context, filter_name: str):
        player = ctx.voice_client
        if not player or not player.playing:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} No Music Playing",
                description="There's no music currently playing!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.voice is None or ctx.author.voice.channel != player.channel:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Wrong Voice Channel",
                description="You need to be in the same voice channel as me!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        filters = wavelink.Filters()

        if filter_name == "nightcore":
            filters.timescale.set(pitch=1.2, speed=1.2, rate=1)
            description = "🎵 Applied **Nightcore** filter - increased pitch and speed for that energetic feel!"
        elif filter_name == "bassboost":
            filters.equalizer.set(bands=[{"band": 0, "gain": 0.8}, {"band": 1, "gain": 0.6}, {"band": 2, "gain": 0.4}])
            description = "🔊 Applied **Bass Boost** - enhanced low frequencies for powerful bass!"
        elif filter_name == "vaporwave":
            filters.timescale.set(rate=0.8, pitch=0.9)
            description = "🌴 Applied **Vaporwave** filter - slowed down and pitched down for that nostalgic vibe!"
        elif filter_name == "karaoke":
            filters.karaoke.set(level=1.0, mono_level=1.0, filter_band=220.0, filter_width=100.0)
            description = "🎤 Applied **Karaoke** filter - vocal removal enabled, sing along!"
        elif filter_name == "tremolo":
            filters.tremolo.set(depth=0.5, frequency=10.0)
            description = "🎛️ Applied **Tremolo** effect - amplitude modulation for rhythmic variation!"
        elif filter_name == "vibrato":
            filters.vibrato.set(depth=0.5, frequency=5.0)
            description = "🎶 Applied **Vibrato** effect - pitch modulation for expressive sound!"
        elif filter_name == "rotation":
            filters.rotation.set(rotation_hz=0.2)
            description = "🔄 Applied **Rotation** effect - 3D audio rotation for immersive experience!"
        elif filter_name == "distortion":
            filters.distortion.set(sin_offset=0.0, sin_scale=1.0, cos_offset=0.0, cos_scale=1.0, tan_offset=0.0, tan_scale=1.0, offset=0.0, scale=1.0)
            description = "🎸 Applied **Distortion** effect - gritty sound for rock and metal!"
        elif filter_name == "clear":
            filters = wavelink.Filters()
            description = "🧹 **All filters cleared** - back to original sound!"

        await player.set_filters(filters)
        self.active_filters[ctx.guild.id] = filter_name if filter_name != "clear" else None

        embed = discord.Embed(
            title=f"{self.emoji.FILTER} Filter Applied",
            description=description,
            color=0x1DB954
        )
        await ctx.send(embed=embed)

    @commands.hybrid_group(invoke_without_command=True)
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def filter(self, ctx: commands.Context):
        """Audio filter system"""
        embed = discord.Embed(
            title=f"{self.emoji.FILTER} Audio Filters",
            description="Enhance your music experience with various audio effects!",
            color=0x1DB954
        )
        embed.add_field(
            name="Available Commands",
            value="• `filter enable` - Enable audio filters\n• `filter disable` - Disable all filters",
            inline=False
        )
        embed.add_field(
            name="Current Filter",
            value=f"`{self.active_filters.get(ctx.guild.id, 'None')}`",
            inline=True
        )
        await ctx.send(embed=embed)

    @filter.command(help="Enable audio filters.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def enable(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or not player.playing:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} No Music Playing",
                description="I'm not playing any music right now!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.voice is None or ctx.author.voice.channel != player.channel:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Wrong Voice Channel",
                description="You need to be in the same voice channel as me!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        current_filter = self.active_filters.get(ctx.guild.id, "None")
        embed = discord.Embed(
            title=f"{self.emoji.FILTER} Enable Audio Filter",
            description="Choose an audio filter to apply to the current track:",
            color=0x1DB954
        )
        embed.add_field(name="Current Filter", value=f"`{current_filter}`", inline=False)
        embed.add_field(
            name="Available Filters",
            value="• **Nightcore** - Faster, higher pitch\n• **Bass Boost** - Enhanced bass\n• **Vaporwave** - Slower, dreamy\n• **Karaoke** - Vocal removal\n• **Tremolo** - Volume modulation\n• **Vibrato** - Pitch modulation\n• **Rotation** - 3D audio effect\n• **Distortion** - Gritty sound",
            inline=False
        )

        await ctx.send(embed=embed, view=FilterSelectView(player, ctx))

    @filter.command(help="Disable all audio filters.")
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def disable(self, ctx: commands.Context):
        player = ctx.voice_client
        if not player or not player.playing:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} No Music Playing",
                description="I'm not playing any music right now!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        if ctx.author.voice is None or ctx.author.voice.channel != player.channel:
            embed = discord.Embed(
                title=f"{self.emoji.ERROR} Wrong Voice Channel",
                description="You need to be in the same voice channel as me!",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        filters = wavelink.Filters()
        await player.set_filters(filters)
        self.active_filters.pop(ctx.guild.id, None)

        embed = discord.Embed(
            title=f"{self.emoji.SUCCESS} Filters Disabled",
            description="All audio filters have been removed!",
            color=0x1DB954
        )
        await ctx.send(embed=embed)

# Help Command System
class HelpView(View):
    def __init__(self, ctx):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.current_page = 0
        self.pages = self.create_help_pages()
        self.emoji = EmojiConfig()

    def create_help_pages(self):
        pages = []

        # Page 1: Basic Commands
        embed1 = discord.Embed(
            title="🎵 DrakLeafX Music Bot - Help Menu",
            description="**Complete Music System with High Quality Audio**\n\n**Command Mode:** Slash commands only (`/`) `/`",
            color=0x1DB954
        )
        embed1.add_field(
            name="🎶 Basic Music Commands",
            value=(
                "`/play <query>` - Play music from YouTube/Spotify\n"
                "`/search <query>` - Search music across platforms\n"
                "`/nowplaying` - Show current track info\n"
                "`/queue` - Show current queue\n"
                "`/skip` - Skip current track\n"
                "`/pause` - Pause playback\n"
                "`/resume` - Resume playback\n"
                "`/stop` - Stop playback and clear queue\n"
                "`/volume <1-150>` - Adjust volume"
            ),
            inline=False
        )
        embed1.set_footer(text="Page 1/4 - Use buttons below to navigate")
        pages.append(embed1)

        # Page 2: Advanced Controls
        embed2 = discord.Embed(
            title="🎛️ Advanced Music Controls",
            description="**Enhanced Music Management Features**",
            color=0x1DB954
        )
        embed2.add_field(
            name="🔧 Player Controls",
            value=(
                "`/loop` - Toggle loop mode\n"
                "`/shuffle` - Shuffle queue\n"
                "`/seek <seconds>` - Seek to position\n"
                "`/replay` - Replay current track\n"
                "`/previous` - Play previous track\n"
                "`/autoplay` - Toggle autoplay\n"
                "`/clearqueue` - Clear entire queue\n"
                "`/join` - Join voice channel\n"
                "`/disconnect` - Leave voice channel"
            ),
            inline=False
        )
        embed2.set_footer(text="Page 2/4 - Use buttons below to navigate")
        pages.append(embed2)

        # Page 3: Playlist & Filters
        embed3 = discord.Embed(
            title="📂 Playlists & Audio Effects",
            description="**Personal Playlists and Audio Enhancement**",
            color=0x1DB954
        )
        embed3.add_field(
            name="📂 Playlist Commands",
            value=(
                "`/playlist` - Playlist management\n"
                "`/createplaylist <name>` - Create playlist\n"
                "`/playlists` - View your playlists\n"
                "`/playplaylist <name>` - Play saved playlist\n"
                "`/deleteplaylist <name>` - Delete playlist\n"
                "`/viewplaylist <name>` - View playlist tracks"
            ),
            inline=False
        )
        embed3.add_field(
            name="🎛️ Audio Filters",
            value=(
                "`/filter enable` - Enable audio filters\n"
                "`/filter disable` - Disable all filters\n"
                "**Filters Available:** Nightcore, Bass Boost, Vaporwave, Karaoke, Tremolo, Vibrato, Rotation, Distortion"
            ),
            inline=False
        )
        embed3.set_footer(text="Page 3/4 - Use buttons below to navigate")
        pages.append(embed3)

        # Page 4: Features & Support
        embed4 = discord.Embed(
            title="🌟 Features & Support",
            description="**Advanced Features and Bot Information**",
            color=0x1DB954
        )
        embed4.add_field(
            name="🚀 Premium Features",
            value=(
                "• **High Quality Audio** - 320kbps streaming\n"
                "• **Multi-Platform Support** - YouTube, Spotify, SoundCloud\n"
                "• **Advanced Controls** - Beautiful interactive player\n"
                "• **Audio Filters** - Professional sound effects\n"
                "• **Playlist System** - Personal music collections\n"
                "• **Equalizer Presets** - Optimized audio profiles\n"
                "• **Spotify Integration** - Direct link support\n"
                "• **Auto-Cleanup** - Smart message management"
            ),
            inline=False
        )
        embed4.add_field(
            name="🔗 Support & Links",
            value=(
                "[Support Server](https://discord.gg/DXMHHk7rAt) | "
                "[Invite Bot](https://discord.com/oauth2/authorize?client_id=1422355258562318358&permissions=8&integration_type=0&scope=applications.commands+bot)"
            ),
            inline=False
        )
        embed4.set_footer(text="Page 4/4 - Thanks for using Me!")
        pages.append(embed4)

        return pages

    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary)
    async def first_page(self, interaction: discord.Interaction, button: Button):
        self.current_page = 0
        await interaction.response.edit_message(embed=self.pages[self.current_page])

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction: discord.Interaction, button: Button):
        self.current_page = max(0, self.current_page - 1)
        await interaction.response.edit_message(embed=self.pages[self.current_page])

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: Button):
        self.current_page = min(len(self.pages) - 1, self.current_page + 1)
        await interaction.response.edit_message(embed=self.pages[self.current_page])

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)
    async def last_page(self, interaction: discord.Interaction, button: Button):
        self.current_page = len(self.pages) - 1
        await interaction.response.edit_message(embed=self.pages[self.current_page])

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", usage="help", help="Shows all available commands with details.")
    async def help_command(self, ctx: commands.Context):
        """Show comprehensive help menu"""
        view = HelpView(ctx)
        await ctx.send(embed=view.pages[0], view=view)

class _music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = EmojiConfig()

    """Music commands"""

    def help_custom(self):
        emoji = self.emoji.MUSICAL_NOTES
        label = "Music Commands"
        description = "Complete music system with advanced controls and high quality audio"
        return emoji, label, description

    @commands.group()
    async def __Music__(self, ctx: commands.Context):
        """`play` , `search` , `loop` , `autoplay` , `nowplaying` , `shuffle` , `stop` , `skip` , `previous` , `seek` , `join` , `disconnect` , `replay` , `queue` , `clearqueue` , `pause` , `resume` , `volume` , `filter` , `filter enable` , `filter disable` , `playlist` , `createplaylist` , `playlists` , `playplaylist` , `deleteplaylist` , `viewplaylist`"""

# Bot setup
intents = discord.Intents.all()

def load_bot_token():
    """Load Discord bot token from config or environment"""
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
            token = config.get('discord_token') or os.environ.get('DISCORD_TOKEN')
            if token and token.strip():
                return token
    except FileNotFoundError:
        pass
    return os.environ.get('DISCORD_TOKEN')

class MusicBot(commands.Bot):
    def __init__(self):
        # Updated prefixes - removed "!" and added "/"
        # Empty prefix list disables ALL text-prefix commands. Hybrid commands remain available as slash commands.
        super().__init__(command_prefix=[], intents=intents, help_command=None)
        self.session = None
        self.music_db = MusicDatabase()

    async def setup_hook(self):
        """Called when bot is starting"""
        self.session = aiohttp.ClientSession()
        await self.music_db.connect()
        self.update_presence.start()
        self.auto_resume_sessions.start()

        print("🤖 Bot is starting in slash-command-only mode (/) ")

        # Load cogs
        await self.add_cog(Music(self))
        await self.add_cog(FilterCog(self))
        await self.add_cog(HelpCog(self))
        await self.add_cog(_music(self))
        print("✅ All cogs loaded successfully!")

        # Sync application commands
        try:
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} slash command(s)")
        except Exception as e:
            print(f"❌ Failed to sync commands: {e}")

    async def close(self):
        """Called when bot is closing"""
        if self.session:
            await self.session.close()
        if self.music_db:
            await self.music_db.close()
        await super().close()

    @tasks.loop(minutes=5)
    async def update_presence(self):
        """Update bot presence with server stats"""
        try:
            total_members = sum(guild.member_count for guild in self.guilds)

            # Rich Presence with streaming activity
            activity = discord.Activity(
                type=discord.ActivityType.streaming,
                name=f"{len(self.guilds)} Servers | {total_members} Members | High Quality Audio",
                details="Ultra HD Music Player - 384kbps",
                state="Powered by RAJ | Slash Commands Only",
                url="https://twitch.tv/discord"
            )

            await self.change_presence(
                activity=activity,
                status=discord.Status.online
            )
        except Exception as e:
            print(f"❌ Error updating presence: {e}")

    @update_presence.before_loop
    async def before_update_presence(self):
        """Wait until the bot is ready before starting the loop"""
        await self.wait_until_ready()

    @tasks.loop(minutes=1)
    async def auto_resume_sessions(self):
        """Auto-resume playback sessions that were interrupted"""
        try:
            sessions = await self.music_db.get_all_active_sessions()
            for session in sessions:
                if not session['auto_resume']:
                    continue

                guild = self.get_guild(session['server_id'])
                if not guild:
                    continue

                channel = guild.get_channel(session['channel_id'])
                if not channel:
                    continue

                voice_client = guild.voice_client
                if voice_client and voice_client.playing:
                    continue

                if not voice_client or not voice_client.channel:
                    continue

                player = cast(wavelink.Player, voice_client)

                if session['current_track'] and not player.playing:
                    print(f"🔄 Auto-resuming session in {guild.name} - {channel.name}")

        except Exception as e:
            print(f"❌ Auto-resume error: {e}")

    @auto_resume_sessions.before_loop
    async def before_auto_resume(self):
        """Wait until bot is ready"""
        await self.wait_until_ready()

bot = MusicBot()

@bot.event
async def on_ready():
    print(f'🎵 {bot.user.name} is now online!')
    print(f'📊 Connected to {len(bot.guilds)} servers')
    print(f'🎶 High Quality Music System initialized!')
    print(f'💎 Audio Quality: 384kbps Ultra HD')
    print('🔧 Command Mode: Slash commands only (/)')

    # Check YouTube API status
    if youtube_api.has_api_key():
        print(f'🔑 YouTube API: Enabled')
    else:
        print(f'🔑 YouTube API: Disabled')

# Run the bot
async def main():
    async with bot:
        token = load_bot_token()
        if not token:
            print("❌ ERROR: DISCORD_TOKEN not set in environment variables")
            print("   Please set the DISCORD_TOKEN environment variable and restart the bot")
            return
        await bot.start(token)

# Run the bot
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())