import discord
from discord.ext import commands
from discord import ui, Interaction, ButtonStyle, SelectOption
import os
from dotenv import load_dotenv

# Настройка бота
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Для работы с ролями участников
bot = commands.Bot(command_prefix="!", intents=intents)

# ID каналов и ролей
REQUIRED_ROLE_ID = 953983815032901662
RAID_CHAT_ID = 978730386848878652
SOROKOVNIK_ROLE_ID = 953983545267855360
OFFICER_ROLE_ID = 953983815032901662
ACCESS_CHANNEL_ID = 1050473475606843502  # Замените на ID канала "Получение доступа"
OFFICER_CHAT_ID = 1101166962085732455    # Замените на ID офицерского чата

# Структура данных для ролей
ROLE_CLASSES = {
    "ДД": {
        "emoji": {"name": "dd", "id": 1348251767179186217},
        "classes": [
            {"name": "демонолог", "emoji": {"name": "demon", "id": 1348258347584851991}},
            {"name": "разведчик", "emoji": {"name": "ranger", "id": 1348265574547066942}},
            {"name": "паладин", "emoji": {"name": "paladin", "id": 1348265462416543785}},
            {"name": "воин", "emoji": {"name": "warrior", "id": 1348265746622451795}},
            {"name": "жрец", "emoji": {"name": "priest", "id": 1348265492313411584}},
            {"name": "некромант", "emoji": {"name": "necromancy", "id": 1348265431961702444}},
            {"name": "мистик", "emoji": {"name": "psionic", "id": 1348265518133674006}},
            {"name": "инженер", "emoji": {"name": "engineer", "id": 1348265354698293328}},
            {"name": "бард", "emoji": {"name": "bard", "id": 1348265288600260618}},
            {"name": "шаман", "emoji": {"name": "druid", "id": 1348265322372661279}},
            {"name": "волшебник", "emoji": {"name": "wizard", "id": 1348265404627161139}}
        ]
    },
    "Танк": {
        "emoji": {"name": "tank", "id": 1348252020120883232},
        "classes": [
            {"name": "демонолог", "emoji": {"name": "demon", "id": 1348258347584851991}},
            {"name": "разведчик", "emoji": {"name": "ranger", "id": 1348265574547066942}},
            {"name": "паладин", "emoji": {"name": "paladin", "id": 1348265462416543785}},
            {"name": "воин", "emoji": {"name": "warrior", "id": 1348265746622451795}}
        ]
    },
    "Хил": {
        "emoji": {"name": "heal", "id": 1348251988940554301},
        "classes": [
            {"name": "жрец", "emoji": {"name": "priest", "id": 1348265492313411584}},
            {"name": "шаман", "emoji": {"name": "druid", "id": 1348265322372661279}},
            {"name": "некромант", "emoji": {"name": "necromancy", "id": 1348265431961702444}}
        ]
    },
    "Саппорт": {
        "emoji": {"name": "support", "id": 1348252005482762260},
        "classes": [
            {"name": "инженер", "emoji": {"name": "engineer", "id": 1348265354698293328}},
            {"name": "бард", "emoji": {"name": "bard", "id": 1348265288600260618}}
        ]
    }
}

user_data = {}

# Команда для отправки сообщения в канал "Получение доступа"
@bot.command()
@commands.has_role(SOROKOVNIK_ROLE_ID)
async def setup_roles(ctx):
    """Отправляет сообщение с кнопками для получения ролей."""
    view = RoleRequestView()
    await ctx.send("Сообщение для получения ролей отправлено в канал.", delete_after=5)
    
    channel = bot.get_channel(ACCESS_CHANNEL_ID)
    if channel:
        await channel.send(
            "Для получения роли гильдии нажмите на соответствующую кнопку. "
            "Если вам нужна роль гость, нажмите на другую кнопку.",
            view=view
        )
    else:
        await ctx.send("Канал 'Получение доступа' не найден.", delete_after=5)

# Кнопки для выбора роли
class RoleRequestView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Получить роль гильдии", style=ButtonStyle.primary)
    async def request_guild_role(self, interaction: Interaction, button: ui.Button):
        """Обрабатывает запрос на получение роли гильдии."""
        officer_chat = bot.get_channel(OFFICER_CHAT_ID)
        if not officer_chat:
            await interaction.response.send_message(
                "Произошла ошибка: офицерский чат не найден.",
                ephemeral=True
            )
            return
        
        # Отправляем уведомление в офицерский чат
        embed = discord.Embed(
            title="Новая заявка на роль",
            description=f"{interaction.user.mention} запрашивает роль гильдии.",
            color=discord.Color.blue()
        )
        message = await officer_chat.send(
            content=f"<@&{OFFICER_ROLE_ID}> Новая заявка на роль!",
            embed=embed,
            view=OfficerApprovalView(user_id=interaction.user.id)
        )
        
        await interaction.response.send_message(
            "Ваша заявка отправлена. Ожидайте решения офицеров.",
            ephemeral=True
        )

    @ui.button(label="Получить роль гость", style=ButtonStyle.secondary)
    async def request_guest_role(self, interaction: Interaction, button: ui.Button):
        """Обрабатывает запрос на получение роли гость."""
        guild = interaction.guild
        guest_role = discord.utils.get(guild.roles, name="Гость")
        if not guest_role:
            await interaction.response.send_message(
                "Роль 'Гость' не найдена.",
                ephemeral=True
            )
            return
        
        await interaction.user.add_roles(guest_role)
        await interaction.response.send_message(
            "Роль 'Гость' успешно выдана.",
            ephemeral=True
        )

# Кнопки для одобрения или отклонения заявки
class OfficerApprovalView(ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None)
        self.user_id = user_id

    @ui.button(emoji="✅", style=ButtonStyle.success)
    async def approve(self, interaction: Interaction, button: ui.Button):
        """Одобрение заявки."""
        guild = interaction.guild
        user = guild.get_member(self.user_id)
        if not user:
            await interaction.response.send_message(
                "Пользователь не найден.",
                ephemeral=True
            )
            return
        
        sorokovnik_role = discord.utils.get(guild.roles, id=SOROKOVNIK_ROLE_ID)
        if not sorokovnik_role:
            await interaction.response.send_message(
                "Роль '@Сороковник' не найдена.",
                ephemeral=True
            )
            return
        
        await user.add_roles(sorokovnik_role)
        await interaction.response.send_message(
            f"Роль '@Сороковник' успешно выдана {user.mention}.",
            ephemeral=True
        )

    @ui.button(emoji="❌", style=ButtonStyle.danger)
    async def deny(self, interaction: Interaction, button: ui.Button):
        """Отклонение заявки."""
        await interaction.response.send_message(
            "Заявка отклонена.",
            ephemeral=True
        )

# Функционал команды !рчд_список
@bot.command()
@commands.has_role(REQUIRED_ROLE_ID)
async def рчд_список(ctx):
    await ctx.send(
        "Выберите тип рейда:",
        view=RaidSelectionView(),
        ephemeral=True
    )

class RaidSelectionView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="РЧД атака", style=discord.ButtonStyle.primary)
    async def attack(self, interaction: Interaction, button: ui.Button):
        await self.start_raid(interaction, "РЧД атака")

    @ui.button(label="РЧД защита", style=discord.ButtonStyle.primary)
    async def defense(self, interaction: Interaction, button: ui.Button):
        await self.start_raid(interaction, "РЧД защита")

    async def start_raid(self, interaction: Interaction, raid_type: str):
        user_id = interaction.user.id
        user_data[user_id] = {"raid_type": raid_type, "roles": {}}
        
        view = RoleView()
        await interaction.response.send_message(
            f"Вы выбрали **{raid_type}**. Теперь выберите роль:",
            view=view,
            ephemeral=True
        )

class RoleView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for role_name, data in ROLE_CLASSES.items():
            self.add_item(RoleButton(role_name, data['emoji']))

class RoleButton(ui.Button):
    def __init__(self, role_name, emoji_data):
        super().__init__(
            label=role_name,
            style=discord.ButtonStyle.primary,
            emoji=discord.PartialEmoji(
                name=emoji_data["name"],
                id=emoji_data["id"]
            )
        )
        self.role_name = role_name

    async def callback(self, interaction: Interaction):
        user_id = interaction.user.id
        if user_id not in user_data:
            await interaction.response.send_message(
                "Произошла ошибка: данные не найдены. Начните сначала.",
                ephemeral=True
            )
            return
        
        user_data[user_id]["roles"][self.role_name] = {"class": None, "nicks": []}
        
        classes = ROLE_CLASSES[self.role_name]['classes']
        options = [
            SelectOption(
                label=cls['name'],
                value=cls['name'],
                emoji=discord.PartialEmoji(
                    name=cls['emoji']['name'],
                    id=cls['emoji']['id']
                )
            ) for cls in classes
        ]
        
        view = ui.View().add_item(ClassSelect(options, self.role_name))
        await interaction.response.send_message(
            f"Выберите класс для роли **{self.role_name}**:",
            view=view,
            ephemeral=True
        )

class ClassSelect(ui.Select):
    def __init__(self, options, role_name):
        super().__init__(placeholder="Класс", options=options)
        self.role_name = role_name

    async def callback(self, interaction: Interaction):
        user_id = interaction.user.id
        selected_class = self.values[0]
        
        if user_id not in user_data or self.role_name not in user_data[user_id]["roles"]:
            await interaction.response.send_message(
                "Произошла ошибка: роль не найдена. Начните сначала.",
                ephemeral=True
            )
            return
        
        user_data[user_id]["roles"][self.role_name]["class"] = selected_class
        
        modal = NickModal(self.role_name, selected_class)
        await interaction.response.send_modal(modal)

class NickModal(ui.Modal):
    def __init__(self, role, cls):
        super().__init__(title="Введите никнеймы")
        self.role = role
        self.cls = cls
        
        self.nicks = ui.TextInput(
            label="Никнеймы через запятую",
            style=discord.TextStyle.short,
            placeholder="player1, player2, player3",
            required=True
        )
        self.add_item(self.nicks)

    async def on_submit(self, interaction: Interaction):
        user_id = interaction.user.id
        
        if user_id not in user_data or self.role not in user_data[user_id]["roles"]:
            await interaction.response.send_message(
                "Произошла ошибка: данные не найдены. Начните сначала.",
                ephemeral=True
            )
            return
        
        nicks = [n.strip() for n in str(self.nicks).split(",")]
        user_data[user_id]["roles"][self.role]["nicks"].extend(nicks)
        
        await interaction.response.send_message(
            "Добавить еще роль или завершить?",
            view=FinishView(),
            ephemeral=True
        )

class FinishView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Добавить роль", style=discord.ButtonStyle.primary)
    async def add_role(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_message(
            "Выберите роль:",
            view=RoleView(),
            ephemeral=True
        )

    @ui.button(label="Просмотреть текущий список", style=discord.ButtonStyle.secondary)
    async def view_current_list(self, interaction: Interaction, button: ui.Button):
        user_id = interaction.user.id
        
        if user_id not in user_data or not user_data[user_id]["roles"]:
            await interaction.response.send_message("Список пуст!", ephemeral=True)
            return
        
        message = []
        for role_name, data in ROLE_CLASSES.items():
            role_entry = user_data[user_id]["roles"].get(role_name)
            if not role_entry or not role_entry["nicks"]:
                continue
                
            role_emoji = discord.PartialEmoji(
                name=data['emoji']['name'],
                id=data['emoji']['id']
            )
            
            message.append(f"{role_emoji} **{role_name}:**")
            
            for cls_data in data['classes']:
                cls_name = cls_data['name']
                if role_entry["class"] != cls_name:
                    continue
                    
                cls_emoji = discord.PartialEmoji(
                    name=cls_data['emoji']['name'],
                    id=cls_data['emoji']['id']
                )
                nicks = role_entry["nicks"]
                
                message.append(f"  {cls_emoji} {cls_name}: {', '.join(nicks)}")
        
        await interaction.response.send_message("\n".join(message), ephemeral=True)

    @ui.button(label="Удалить/заменить игрока", style=discord.ButtonStyle.danger)
    async def remove_player(self, interaction: Interaction, button: ui.Button):
        modal = RemovePlayerModal()
        await interaction.response.send_modal(modal)

    @ui.button(label="Отправить в чат", style=discord.ButtonStyle.success)
    async def send_to_chat(self, interaction: Interaction, button: ui.Button):
        user_id = interaction.user.id
        
        if user_id not in user_data or not user_data[user_id]["roles"]:
            await interaction.response.send_message("Список пуст!", ephemeral=True)
            return
        
        raid_type = user_data[user_id]["raid_type"]
        message = []

        # Получаем объект роли @Сороковник
        role = interaction.guild.get_role(SOROKOVNIK_ROLE_ID)
        if not role:
            await interaction.response.send_message(
                "Не удалось найти роль @Сороковник.",
                ephemeral=True
            )
            return

        # Формируем сообщение с упоминанием роли
        message.append(f"{role.mention}\n**{raid_type}**\n")
        
        for role_name, data in ROLE_CLASSES.items():
            role_entry = user_data[user_id]["roles"].get(role_name)
            if not role_entry or not role_entry["nicks"]:
                continue
                
            role_emoji = discord.PartialEmoji(
                name=data['emoji']['name'],
                id=data['emoji']['id']
            )
            
            message.append(f"{role_emoji} **{role_name}:**")
            
            for cls_data in data['classes']:
                cls_name = cls_data['name']
                if role_entry["class"] != cls_name:
                    continue
                    
                cls_emoji = discord.PartialEmoji(
                    name=cls_data['emoji']['name'],
                    id=cls_data['emoji']['id']
                )
                nicks = role_entry["nicks"]
                
                message.append(f"  {cls_emoji} {cls_name}: {', '.join(nicks)}")
        
        # Отправляем сообщение в канал
        channel = bot.get_channel(RAID_CHAT_ID)
        if channel:
            await channel.send("\n".join(message))
            await interaction.response.send_message("Список успешно отправлен в чат!", ephemeral=True)
        else:
            await interaction.response.send_message("Не удалось найти указанный канал.", ephemeral=True)

class RemovePlayerModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Удалить/заменить игрока")
        self.role = ui.TextInput(
            label="Роль (например, ДД)",
            style=discord.TextStyle.short,
            required=True
        )
        self.nick = ui.TextInput(
            label="Никнейм для удаления/замены",
            style=discord.TextStyle.short,
            required=True
        )
        self.new_nick = ui.TextInput(
            label="Новый никнейм (если замена)",
            style=discord.TextStyle.short,
            required=False
        )
        self.add_item(self.role)
        self.add_item(self.nick)
        self.add_item(self.new_nick)

    async def on_submit(self, interaction: Interaction):
        user_id = interaction.user.id
        role_name = str(self.role).strip()
        nick_to_remove = str(self.nick).strip()
        new_nick = str(self.new_nick).strip()

        if user_id not in user_data or role_name not in user_data[user_id]["roles"]:
            await interaction.response.send_message(
                "Роль не найдена. Проверьте правильность ввода.",
                ephemeral=True
            )
            return
        
        role_data = user_data[user_id]["roles"][role_name]
        if nick_to_remove in role_data["nicks"]:
            role_data["nicks"].remove(nick_to_remove)
            if new_nick:
                role_data["nicks"].append(new_nick)
            action = "заменен" if new_nick else "удален"
            await interaction.response.send_message(
                f"Игрок `{nick_to_remove}` был успешно {action}.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"Игрок `{nick_to_remove}` не найден в списке.",
                ephemeral=True
            )

load_dotenv()
bot.run(os.getenv("TOKEN"))