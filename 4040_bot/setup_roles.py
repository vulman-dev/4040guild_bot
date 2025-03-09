import discord
from discord.ext import commands
from discord import ui, Interaction, ButtonStyle

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Для работы с ролями участников
bot = commands.Bot(command_prefix="!", intents=intents)

# ID каналов и ролей
ACCESS_CHANNEL_ID = 1050473475606843502  # Замените на ID канала "Получение доступа"
OFFICER_CHAT_ID = 1101166962085732455    # Замените на ID офицерского чата
SOROKOVNIK_ROLE_ID = 953983545267855360 # Замените на ID роли @Сороковник
OFFICER_ROLE_ID = 953983815032901662    # Замените на ID роли @офицер

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

# Запуск бота
bot.run("")