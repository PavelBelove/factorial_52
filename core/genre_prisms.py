"""
Genre Prisms configuration.
Defines all available genre modifiers and their prompt injections.
"""

# Genre prism configurations
GENRE_PRISMS = {
    "balanced": {
        "emoji": "⚪",
        "name_ru": "Сбалансированный",
        "name_en": "Balanced",
        "description_ru": "История развивается естественно: немного действия, немного чувств, немного тайны. Мир живёт своей жизнью, не склоняясь ни к одному жанру.",
        "description_en": "The story develops naturally: a bit of action, a bit of feelings, a bit of mystery. The world lives its own life, not leaning towards any particular genre.",
        "examples_ru": "Властелин колец, Гарри Поттер, Ведьмак",
        "examples_en": "The Lord of the Rings, Harry Potter, The Witcher",
        "prompt": "",  # Empty - no genre priority
        "advanced": False
    },
    "action": {
        "emoji": "🔥",
        "name_ru": "Экшен / Боевик",
        "name_en": "Action",
        "description_ru": "Больше столкновений, погонь и противостояний. Решения принимаются на ходу, а цена ошибки высока. Мир проверяет героя силой и скоростью реакции.",
        "description_en": "More confrontations, chases, and conflicts. Decisions are made on the fly, and the price of mistakes is high. The world tests the hero with strength and speed of reaction.",
        "examples_ru": "Mad Max, Attack on Titan, John Wick",
        "examples_en": "Mad Max, Attack on Titan, John Wick",
        "prompt": "User's genre priority is action. Focus on dynamics, conflicts, battles, chases, and sharp turns. Scenes should be tense, decisions urgent, consequences tangible.\nReferences: Mad Max, Attack on Titan, John Wick",
        "advanced": False
    },
    "intrigue": {
        "emoji": "🕸",
        "name_ru": "Интриги",
        "name_en": "Intrigue",
        "description_ru": "Тайные мотивы, скрытые альянсы и двойное дно. Никто не говорит всей правды, а любой союз может оказаться временным.",
        "description_en": "Secret motives, hidden alliances, and double meanings. No one tells the whole truth, and any alliance may be temporary.",
        "examples_ru": "Dune, Игра престолов, Карточный домик",
        "examples_en": "Dune, Game of Thrones, House of Cards",
        "prompt": "User's genre priority is intrigue. Emphasize hidden motives, politics, manipulations, and multi-layered schemes. Information is incomplete, trust is dangerous, consequences of decisions unfold over time. Every character plays their own game.\nReferences: Dune, Game of Thrones, House of Cards",
        "advanced": False
    },
    "mystery": {
        "emoji": "🔍",
        "name_ru": "Тайна / Исследование мира",
        "name_en": "Mystery / World Exploration",
        "description_ru": "Мир хранит секреты. История строится вокруг загадок, древних истин и постепенного раскрытия того, как всё устроено на самом деле.",
        "description_en": "The world holds secrets. The story is built around mysteries, ancient truths, and gradual revelation of how everything really works.",
        "examples_ru": "Made in Abyss, Dark, Lost",
        "examples_en": "Made in Abyss, Dark, Lost",
        "prompt": "User's genre priority is detective mystery and world exploration. Emphasize the unknown, hidden laws of the world, discoveries, and questions without quick answers. Truth is revealed in fragments.\nReferences: Made in Abyss, Dark, Lost",
        "advanced": False
    },
    "drama": {
        "emoji": "🎭",
        "name_ru": "Драма",
        "name_en": "Drama",
        "description_ru": "Выборы, за которые приходится платить. Даже успех имеет горькую цену. Отношения, потери и внутренние конфликты важнее внешней победы.",
        "description_en": "Choices that come with a price. Even success has a bitter cost. Relationships, losses, and internal conflicts matter more than external victory.",
        "examples_ru": "Побег из Шоушенка, Attack on Titan, Forrest Gump",
        "examples_en": "The Shawshank Redemption, Attack on Titan, Forrest Gump",
        "prompt": "User's genre priority is drama. Focus on internal conflicts, difficult choices, losses, and consequences. Even luck carries a price. Characters have past, traumas, and contradictory feelings.\nReferences: The Shawshank Redemption, Attack on Titan, Forrest Gump",
        "advanced": False
    },
    "psychology": {
        "emoji": "🧠",
        "name_ru": "Психология / Отношения",
        "name_en": "Psychology / Relationships",
        "description_ru": "История о людях, а не событиях. Симпатии, ревность, дружба, предательство и сложные эмоциональные узлы двигают сюжет.",
        "description_en": "A story about people, not events. Sympathy, jealousy, friendship, betrayal, and complex emotional knots drive the plot.",
        "examples_ru": "Evangelion, Berserk, The Last of Us",
        "examples_en": "Evangelion, Berserk, The Last of Us",
        "prompt": "User's genre priority is interpersonal relationships. Emphasize emotions, relationship dynamics, unsaid things, and personal motivations influencing actions. Characters have deep history, traumas, motives, obligations, and feelings (not always simple, not always towards the protagonist).\nReferences: Evangelion, Berserk, The Last of Us",
        "advanced": False
    },
    "romance": {
        "emoji": "❤️",
        "name_ru": "Романтика / Гарем",
        "name_en": "Romance / Harem",
        "description_ru": "Чувства выходят на первый план. Влечения, выбор между людьми и эмоциональная близость становятся движущей силой истории.",
        "description_en": "Feelings come to the fore. Attractions, choices between people, and emotional intimacy become the driving force of the story.",
        "examples_ru": "Spice and Wolf, Twilight, Your Name",
        "examples_en": "Spice and Wolf, Twilight, Your Name",
        "prompt": "User's genre priority is romance. Amplify emotional intimacy, tension between characters, sympathies, and relationship choices. Feelings influence decisions and fate.\nReferences: Spice and Wolf, Twilight, Your Name",
        "advanced": False
    },
    "humor": {
        "emoji": "😏",
        "name_ru": "Юмор / Ирония",
        "name_en": "Humor / Irony",
        "description_ru": "Лёгкость, самоирония и неожиданные углы взгляда. Даже серьёзные события могут быть поданы с юмором и абсурдом.",
        "description_en": "Lightness, self-irony, and unexpected angles of view. Even serious events can be presented with humor and absurdity.",
        "examples_ru": "Hitchhiker's Guide to the Galaxy, Discworld, Rick and Morty",
        "examples_en": "Hitchhiker's Guide to the Galaxy, Discworld, Rick and Morty",
        "prompt": "User's genre priority is humor and irony. Add wit, absurdity, ironic comments, and unexpected twists. The world can tease the hero.\nReferences: Hitchhiker's Guide to the Galaxy, Discworld, Rick and Morty",
        "advanced": False
    },
    "horror": {
        "emoji": "👁",
        "name_ru": "Хоррор / Жутики",
        "name_en": "Horror",
        "description_ru": "Тревога, неизвестность и ощущение, что что-то не так. Страх рождается из атмосферы и ожидания, а не только из угроз.",
        "description_en": "Anxiety, uncertainty, and the feeling that something is wrong. Fear is born from atmosphere and anticipation, not just from threats.",
        "examples_ru": "Silent Hill, The Thing, Bloodborne",
        "examples_en": "Silent Hill, The Thing, Bloodborne",
        "prompt": "User's genre priority is horror. Create an oppressive atmosphere, uncertainty, and a sense of threat. Fear comes from anticipation and the unknown, not just from violence.\nReferences: Silent Hill, The Thing, Bloodborne",
        "advanced": False
    },
    "survival": {
        "emoji": "🧱",
        "name_ru": "Выживание",
        "name_en": "Survival",
        "description_ru": "Ресурсы ограничены, ошибки наказываются. История о том, как остаться в живых, когда мир враждебен.",
        "description_en": "Resources are limited, mistakes are punished. A story about staying alive when the world is hostile.",
        "examples_ru": "The Road, Metro 2033, Subnautica",
        "examples_en": "The Road, Metro 2033, Subnautica",
        "prompt": "User's genre priority is survival. Emphasize lack of resources, fatigue, risk, and the necessity of difficult decisions for survival. The world does not forgive mistakes. Only the strongest survive.\nReferences: The Road, Metro 2033, Subnautica",
        "advanced": False
    },
    "philosophy": {
        "emoji": "🧿",
        "name_ru": "Философия / Поиск смысла",
        "name_en": "Philosophy / Search for Meaning",
        "description_ru": "История задаёт вопросы, а не даёт ответы. О смысле, выборе, свободе и цене существования.",
        "description_en": "The story asks questions, not gives answers. About meaning, choice, freedom, and the price of existence.",
        "examples_ru": "Ghost in the Shell, Blade Runner, Siddhartha",
        "examples_en": "Ghost in the Shell, Blade Runner, Siddhartha",
        "prompt": "User's genre priority is philosophy. Embed reflections on meaning, freedom, identity, and choice. Events have existential significance. Characters have their own beliefs and ideals.\nReferences: Ghost in the Shell, Blade Runner, Siddhartha",
        "advanced": False
    },
    "epic": {
        "emoji": "🏛",
        "name_ru": "Эпос / Легенда",
        "name_en": "Epic / Legend",
        "description_ru": "История о великих деяниях, судьбах народов и событиях, которые войдут в легенды.",
        "description_en": "A story about great deeds, the fates of peoples, and events that will become legends.",
        "examples_ru": "Илиада, Silmarillion, Mahabharata",
        "examples_en": "Iliad, Silmarillion, Mahabharata",
        "prompt": "User's genre priority is epic. Present events on a grand scale, with a sense of myth, destiny, and historical significance. The hero is part of something greater.\nReferences: Iliad, Silmarillion, Mahabharata",
        "advanced": False
    },
    "road": {
        "emoji": "🛣",
        "name_ru": "Движение / Road Movie",
        "name_en": "Journey / Road Movie",
        "description_ru": "Путь важнее цели. Города, попутчики и случайные встречи меняют героя сильнее, чем финал.",
        "description_en": "The journey matters more than the destination. Cities, fellow travelers, and chance encounters change the hero more than the finale.",
        "examples_ru": "Interstate 60, Journey, Spirited Away",
        "examples_en": "Interstate 60, Journey, Spirited Away",
        "prompt": "User's genre priority is the road. The plot develops through travel, change of places, and encounters. The journey and transformation of the hero matter, not just the destination.\nReferences: Interstate 60, Journey, Spirited Away",
        "advanced": False
    },
    "levelup": {
        "emoji": "⬆️",
        "name_ru": "Level Up / Восхождение",
        "name_en": "Level Up / Ascension",
        "description_ru": "От слабости к силе. Рост возможностей, статуса и понимания мира ощущается шаг за шагом.",
        "description_en": "From weakness to strength. Growth of abilities, status, and understanding of the world is felt step by step.",
        "examples_ru": "Solo Leveling, Hunter x Hunter, Mushoku Tensei",
        "examples_en": "Solo Leveling, Hunter x Hunter, Mushoku Tensei",
        "prompt": "User's genre priority is ascension. Emphasize the hero's growth, expansion of abilities, and changing attitudes of the world towards them. Progress should be tangible.\nReferences: Solo Leveling, Hunter x Hunter, Mushoku Tensei",
        "advanced": False
    },
    "surreal": {
        "emoji": "⚠️",
        "name_ru": "Шиза / Сюрреализм",
        "name_en": "Surrealism",
        "description_ru": "Реальность ненадёжна. Воспоминания могут лгать, а события — противоречить друг другу.\n⚠️ осторожно, у рассказчика может поехать крыша..",
        "description_en": "Reality is unreliable. Memories can lie, and events can contradict each other.\n⚠️ Careful, the narrator might lose their mind..",
        "examples_ru": "Mr. Robot, Fight Club, Shutter Island, Алиса в стране Чудес",
        "examples_en": "Mr. Robot, Fight Club, Shutter Island, Alice in Wonderland",
        "prompt": "User's genre priority is distorted perception. Allow for an unreliable narrator, contradictory scenes, and questionable reality. Truth may be incomplete or delayed.\nReferences: Mr. Robot, Fight Club, Shutter Island",
        "advanced": True
    },
    "timeloop": {
        "emoji": "⚠️",
        "name_ru": "Временные петли",
        "name_en": "Time Loops",
        "description_ru": "Причина и следствие не всегда на своих местах. Повторы, откаты и изменения прошлого.\n⚠️ Требует вдумчивого участия, не попадите в 'день Сурка'.",
        "description_en": "Cause and effect are not always in their place. Repetitions, rollbacks, and changes to the past.\n⚠️ Requires thoughtful participation, don't get stuck in Groundhog Day.",
        "examples_ru": "Re:Zero, The Butterfly Effect, Dark",
        "examples_en": "Re:Zero, The Butterfly Effect, Dark",
        "prompt": "User's genre priority is temporal distortions. Allow for loops, repeating events, and violations of linear time. The hero's choice affects the structure of the story.\nReferences: Re:Zero, The Butterfly Effect, Dark",
        "advanced": True
    }
}

def get_prism_prompt(prism_id: str) -> str:
    """Get the prompt injection for a given prism."""
    prism = GENRE_PRISMS.get(prism_id, GENRE_PRISMS["balanced"])
    return prism["prompt"]

def get_prism_info(prism_id: str, language: str = "ru") -> dict:
    """Get prism information for display."""
    prism = GENRE_PRISMS.get(prism_id, GENRE_PRISMS["balanced"])
    
    name_key = f"name_{language}"
    desc_key = f"description_{language}"
    examples_key = f"examples_{language}"
    
    return {
        "emoji": prism["emoji"],
        "name": prism.get(name_key, prism["name_en"]),
        "description": prism.get(desc_key, prism["description_en"]),
        "examples": prism.get(examples_key, prism["examples_en"]),
        "advanced": prism["advanced"]
    }

def get_all_prisms(language: str = "ru") -> list:
    """Get list of all prisms for menu display."""
    prisms = []
    for prism_id, prism_data in GENRE_PRISMS.items():
        name_key = f"name_{language}"
        prisms.append({
            "id": prism_id,
            "emoji": prism_data["emoji"],
            "name": prism_data.get(name_key, prism_data["name_en"]),
            "advanced": prism_data["advanced"]
        })
    return prisms

