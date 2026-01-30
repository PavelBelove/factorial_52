"""
English localization for PlexMem RPG Bot.
"""
from typing import Dict
from .base import BaseLocalization


class EnglishLocalization(BaseLocalization):
    """English language implementation."""
    
    def get_language_code(self) -> str:
        return "en"
    
    def get_language_name(self) -> str:
        return "English"
    
    # Language selection
    def get_language_selection_message(self) -> str:
        return "Choose your language:"
    
    def get_available_languages(self) -> Dict[str, str]:
        return {
            "ru": "🇷🇺 Русский",
            "en": "🇬🇧 English"
        }
    
    # Main menu
    def get_main_menu_message(self) -> str:
        return (
            "📖 <b>52! Wor‌ld — The Infinite Book</b>\n\n"
            "Where stories are born that will never repeat.\n"
            "Each shuffle of the deck — a new destiny. Each choice — a new plot twist.\n\n"
            "Choose your action:"
        )
    
    def get_main_menu_buttons(self) -> Dict[str, str]:
        return {
            "continue": "📖 Continue reading",
            "new_game": "✨ New adventure",
            "load": "📚 From library",
            "save": "🔖 Place bookmark",
            "settings": "⚙️ Settings",
            "help": "❓ About the book"
        }
    
    # World selection
    def get_world_selection_message(self) -> str:
        return (
            "🌍 <b>Choose a world</b>\n\n"
            "In which book does your story unfold?\n"
            "Each world is unique and breathes its own atmosphere."
        )
    
    def get_world_start_button(self) -> str:
        return "📖 Begin the story"
    
    # Save/Load
    def get_save_menu_message(self) -> str:
        return "🔖 <b>Place a bookmark</b>\n\nIn which book to place the bookmark?"
    
    def get_load_menu_message(self) -> str:
        return "📚 <b>Library</b>\n\nWhich book to open?"
    
    def get_slot_label(self, slot: int) -> str:
        return f"Book {slot}"
    
    def get_empty_slot_label(self) -> str:
        return "📭 Empty"
    
    def get_no_saves_message(self) -> str:
        return "❌ The library is empty.\nStart a new adventure from the main menu."
    
    # Game messages
    def get_game_started_message(self, slot: int) -> str:
        return f"✅ The story has begun. Bookmark in book {slot}"
    
    def get_game_saved_message(self, slot: int) -> str:
        return f"✅ Bookmark placed in book {slot}"
    
    def get_game_loaded_message(self, slot: int) -> str:
        return f"✅ Book {slot} opened\n\nYou can continue reading!"
    
    def get_creating_world_message(self) -> str:
        return "⏳ The Narrator is preparing your unique story...\nThis may take a moment."
    
    # Error messages
    def get_no_active_game_message(self) -> str:
        return "❌ No open book.\nUse /menu to begin a story or open from the library."
    
    def get_error_message(self) -> str:
        return "❌ An error occurred. Please try again."
    
    def get_save_error_message(self) -> str:
        return "❌ Failed to place bookmark. Please try again."
    
    def get_load_error_message(self) -> str:
        return "❌ Failed to open the book. The bookmark may be corrupted."
    
    # Navigation
    def get_back_button(self) -> str:
        return "◀️ Back"
    
    def get_cancel_button(self) -> str:
        return "❌ Cancel"
    
    # Settings
    def get_settings_menu_message(self) -> str:
        return (
            "⚙️ <b>Settings</b>\n\n"
            "Here you can configure story parameters."
        )
    
    def get_settings_buttons(self) -> Dict[str, str]:
        return {
            "language": "🌐 Language",
            "difficulty": "⚔️ Difficulty",
            "content": "🔞 Content"
        }
    
    def get_difficulty_settings_message(self) -> str:
        return (
            "🎮 <b>Difficulty</b>\n\n"
            "Affects check thresholds:\n"
            "• 😊 Easy — reduced thresholds\n"
            "• ⚔️ Normal — standard balance\n"
            "• 💀 Hard — increased thresholds"
        )
    
    def get_content_filter_settings_message(self) -> str:
        return (
            "🔒 <b>Content filter</b>\n\n"
            "Determines adult content level:\n"
            "• 🛡️ Safe — no adult content\n"
            "• 💕 16+ — light romance\n"
            "• 🔞 18+ — adult content"
        )
    
    # Keyboard labels
    def get_difficulty_label(self, difficulty: str) -> str:
        labels = {
            "easy": "😊 Easy",
            "normal": "⚔️ Normal",
            "hard": "💀 Hard"
        }
        return labels.get(difficulty, difficulty)
    
    def get_content_filter_label(self, filter_type: str) -> str:
        labels = {
            "safe": "🛡️ Safe",
            "romantic": "💕 16+",
            "adult": "🔞 18+"
        }
        return labels.get(filter_type, filter_type)
    
    def get_confirm_button(self) -> str:
        return "✅ Confirm"
    
    def get_back_page_button(self) -> str:
        return "⬅️ Back"
    
    def get_forward_page_button(self) -> str:
        return "Forward ➡️"
    
    def get_adult_content_consent_message(self) -> str:
        return (
            "⚠️ <b>WARNING: Adult content (18+)</b>\n\n"
            "By clicking «Confirm», you confirm that:\n\n"
            "• You are 18 years old or older\n"
            "• Viewing such content is legal in your jurisdiction\n"
            "• You voluntarily and consciously remove restrictions on adult content\n"
            "• You understand that the story may contain explicit sexual scenes\n\n"
            "<b>This choice can be changed in settings at any time.</b>"
        )
    
    # Help
    def get_help_message(self) -> str:
        """Deprecated - use get_help_page instead."""
        return self.get_help_page(1)
    
    def get_help_page(self, page: int = 1) -> str:
        """Get help page by number."""
        if page == 1:
            return self.get_help_about_book()
        elif page == 2:
            return self.get_help_bot_control()
        elif page == 3:
            return self.get_help_character_creation()
        elif page == 4:
            return self.get_help_mechanics()
        return self.get_help_about_book()
    
    def get_help_about_book(self) -> str:
        """Help page 1: About 52! World."""
        return (
            "📖 <b>52! Wor‌ld — The Infinite Book</b>\n\n"
            
            "<b>What is this?</b>\n"
            "A <b>living book</b> written for you and with you. "
            "Artificial Intelligence acts as the Narrator, creating a unique story "
            "that responds to your every decision.\n\n"
            
            "<b>Why \"52!\"?</b>\n"
            "The number of unique shuffles of a 52-card deck (52!) is greater than atoms in the Universe. "
            "Every story in every world is <b>absolutely unique</b>. Your book will never repeat.\n"
            "Cards are a source of <b>randomness and plot twists</b>, keeping the story fresh. "
            "The Narrator doesn't know the outcome in advance — they discover it with you.\n\n"
            
            "<b>Adaptive Memory</b>\n"
            "The system remembers everything: your decisions, dialogues, allies and enemies.\n"
            "Characters don't forget your actions, and past choices affect future chapters. "
            "This story remembers you — even hundreds of pages later.\n\n"
            
            "<i>Page 1 of 4</i>"
        )
    
    def get_help_character_creation(self) -> str:
        """Help page 3: Character creation."""
        return (
            "✨ <b>Creating a hero</b>\n\n"
            
            "<b>Beginning of the story:</b>\n"
            "When creating a character, you draw 5 cards to determine characteristics. "
            "The worst is discarded, the rest affect stats. Distribute them yourself, or let the Narrator decide. "
            "But this is just the foundation — <b>describe your hero!</b>\n\n"
            
            "<b>What you can describe:</b>\n"
            "• <b>Appearance</b> — what does your hero look like?\n"
            "• <b>History</b> — where did they come from? What have they experienced?\n"
            "• <b>Personality</b> — brave? Cautious? Cynical?\n"
            "• <b>Unique traits</b> — features that make them special\n"
            "• <b>Preferences</b> — what do you want to see in the story?\n"
            "• <b>Anything!</b> — Want rainbow unicorns? Now's the time to mention them.\n\n"
            
            "<b>The Narrator will remember everything:</b>\n"
            "Everything you describe becomes part of your book. Characters will react to the hero's appearance, "
            "their past will influence the plot, and preferences will help the Narrator create the perfect story.\n\n"
            
            "<b>Four characteristics:</b>\n"
            "♠ <b>Strength</b> — melee combat, willpower, intimidation\n"
            "♥ <b>Magic</b> — spellcasting, wisdom, communication\n"
            "♦ <b>Stamina</b> — defense, endurance, trading\n"
            "♣ <b>Agility</b> — ranged combat, acrobatics, stealth\n\n"
            
            "<i>Page 3 of 4</i>"
        )
    
    def get_help_mechanics(self) -> str:
        """Help page 4: Game mechanics (based on real code)."""
        return (
            "🎴 <b>Factorial 52! Mechanics</b>\n\n"
            
            "<b>Checks (outside combat):</b>\n"
            "Narrator draws 2 cards. Formula:\n"
            "<code>Result = (card1×10 + bonus1) + (card2×10 + bonus2) + characteristic</code>\n\n"
            
            "<b>Card bonuses:</b>\n"
            "• Suit matches the check: <b>+20</b>\n"
            "• Color matches (no suit match): <b>+10</b>\n"
            "• No matches: <b>0</b>\n\n"
            
            "<b>Example:</b> Acrobatics (♣)\n"
            "Drew 8♥ and K♣\n"
            "• 8♥: 80 + 0 (red) = 80\n"
            "• K♣: 130 + 20 (suit!) = 150\n"
            "• + 60 (agility) = <b>290</b>\n\n"
            
            "<b>Difficulty thresholds:</b>\n"
            "Easy | Medium | Hard | Very Hard\n"
            "Difficulty level set in settings\n\n"
            
            "<b>Special combos (Affect the plot, only outside combat):</b>\n"
            "<b>J</b> - Jack: Introduces an unexpected plot twist\n"
            "<b>Q</b> - Queen: Female character/energy influence\n"
            "<b>K</b> - King: Male character/energy influence\n"
            "🃏🃏 Two aces — divine success\n"
            "🂢🂢 Two twos — catastrophe\n\n"
            
            "<b>Development:</b>\n"
            "For a successful check +1 XP to characteristic. "
            "At 10 XP: +1 to characteristic, +1 to HP and mana.\n\n"
            
            "<i>Page 4 of 4</i>"
        )
    
    def get_help_bot_control(self) -> str:
        """Help page 2: Bot control."""
        return (
            "🎮 <b>Book navigation</b>\n\n"
            
            "<b>Commands:</b>\n"
            "/menu — main menu\n"
            "/stats — hero characteristics\n"
            "/inventory — inventory\n"
            "/undo — cancel last page\n"
            "/retry — rewrite last page\n"
            "/session — story statistics\n"
            "/help — this guide\n\n"
            
            "<b>How to interact:</b>\n"
            "Simply write your actions. "
            "The Narrator will describe the results and story development.\n\n"
            
            "<b>Direct speech with the Narrator:</b>\n"
            "A message [in square brackets] is an address directly to the Narrator, outside the story. "
            "Use for describing preferences, correcting errors, or clarifications.\n\n"
            
            "<b>⚠️ About undos and retries:</b>\n"
            "/undo and /retry — for correcting technical glitches and AI hallucinations, "
            "not for \"rewinding\" failed moments. Failures are part of the story!\n\n"
            
            "<b>Saves:</b>\n"
            "Use bookmarks (up to 5 books simultaneously) "
            "to switch between different stories.\n\n"
            
            "<i>Page 2 of 4</i>"
        )
    
    # Additional game messages
    def get_initial_game_message(self, world_id: str) -> str:
        return (
            f"📖 <b>The book opens...</b>\n\n"
            f"Your story begins.\n\n"
            f"Describe your hero or write the first action!"
        )
    
    def get_continue_game_message(self) -> str:
        return (
            "📖 <b>Continue reading</b>\n\n"
            "What does your hero do?"
        )
    
    def get_game_rules(self) -> str:
        return (
            "📜 <b>Story Rules</b>\n\n"
            
            "<b>1. Freedom of action</b>\n"
            "You can do anything. Write your actions in natural language.\n\n"
            
            "<b>2. Consequences</b>\n"
            "Every action has consequences. Think strategically!\n\n"
            
            "<b>3. Memory system</b>\n"
            "AI remembers everything: characters, events, your decisions and their consequences.\n\n"
            
            "<b>4. Character</b>\n"
            "Your character has characteristics, inventory, and history.\n"
            "Use /stats and /inventory commands to view.\n\n"
            
            "<b>5. Saves</b>\n"
            "The story auto-saves. You can have up to 5 different stories simultaneously.\n\n"
            
            "<b>6. Undo actions</b>\n"
            "Use /undo to cancel the last turn and /retry to repeat with a different result.\n\n"
            
            "<b>Enjoy the story! 📖</b>"
        )


