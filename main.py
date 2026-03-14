import discord
from discord.ext import commands
from discord.ui import Button, View, Select
from dotenv import load_dotenv
import os
from datetime import datetime

# Загружаем переменные окружения
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    print("Ошибка: Токен не найден в файле .env!")
    exit()

# ================= КОНФИГУРАЦИЯ ID =================
OWNER_ID = 314805583788244993
LOG_CHANNEL_ID = 1482287259280605225
TICKET_CATEGORY_ID = 1482347523254517822  # Категория для тикетов

ADMIN_ROLE_IDS = [
    1482021644703760607, 1482021651867631746, 1482021652488524058,
    1482021653109018734, 1482021654082093076, 1482021656636428411,
    1482021656649269310
]

COSMETIC_ROLES = {
    "knife": 1482026329368170706,
    "science": 1482026329435148421,
    "ghost": 1482026850564968488,
    "radio": 1482026851479195689,
    "moon": 1482026853085610117
}

# ===================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ================= ПРОВЕРКА ПРАВ =================
def is_admin_or_owner():
    async def predicate(ctx):
        if ctx.author.id == OWNER_ID:
            return True
        if hasattr(ctx.author, 'roles'):
            user_role_ids = [role.id for role in ctx.author.roles]
            if any(role_id in user_role_ids for role_id in ADMIN_ROLE_IDS):
                return True
        return False
    return commands.check(predicate)

# ================= ЛОГИРОВАНИЕ =================
async def send_log(guild, title, description, color, fields=None, thumbnail=None, footer=None):
    """Отправляет лог в канал логов"""
    try:
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if not log_channel:
            log_channel = await bot.fetch_channel(LOG_CHANNEL_ID)
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.utcnow()
        )
        
        if fields:
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
        
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        
        if footer:
            embed.set_footer(text=footer)
        else:
            embed.set_footer(text=f"🏥 Безумие - Реанимация | ID: {guild.id}")
        
        await log_channel.send(embed=embed)
    except Exception as e:
        print(f"Ошибка отправки лога: {e}")

# ================= ТИКЕТЫ - КНОПКИ И SELECT =================
class TicketCategorySelect(Select):
    """Выбор категории тикета"""
    def __init__(self):
        options = [
            discord.SelectOption(label="👥 Заявка в персонал", value="staff", emoji="👥", description="Подать заявку на роль модератора/админа"),
            discord.SelectOption(label="🎖 Особый статус", value="special", emoji="🎖", description="Получить уникальную роль за достижения"),
            discord.SelectOption(label="💻 Разработчиком", value="dev", emoji="💻", description="Подать заявку в команду разработчиков"),
        ]
        super().__init__(placeholder="Выберите категорию тикета...", options=options, custom_id="ticket_category")

    async def callback(self, interaction: discord.Interaction):
        category_id = TICKET_CATEGORY_ID
        category = interaction.guild.get_channel(category_id)
        
        if not category:
            await interaction.response.send_message("❌ Категория для тикетов не найдена!", ephemeral=True)
            return
        
        # Проверка на существующий тикет
        for channel in interaction.guild.text_channels:
            if channel.category_id == category_id and interaction.user.name in channel.name:
                await interaction.response.send_message(f"❌ У вас уже есть открытый тикет: {channel.mention}", ephemeral=True)
                return
        
        # Создаём канал
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        
        # Добавляем права для админов
        for role_id in ADMIN_ROLE_IDS:
            role = interaction.guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        category_name = {
            "staff": "Заявка в персонал",
            "special": "Особый статус",
            "dev": "Разработчиком"
        }
        
        channel_name = f"тикет-{interaction.user.name}-{self.values[0]}"
        
        try:
            ticket_channel = await interaction.guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites,
                topic=f"Тикет от {interaction.user.mention} | Категория: {category_name[self.values[0]]}"
            )
            
            # Отправляем сообщение в тикет
            embed = discord.Embed(
                title="🎫 Тикет создан",
                description=f"Здравствуйте, {interaction.user.mention}!\n\n"
                            f"Ваш тикет был создан в категории **{category_name[self.values[0]]}**.\n"
                            f"Ожидайте ответа от администрации.",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="📌 Информация", value=(
                f"**Создатель:** {interaction.user.mention}\n"
                f"**Категория:** {category_name[self.values[0]]}\n"
                f"**Время создания:** <t:{int(datetime.utcnow().timestamp())}:F>"
            ), inline=False)
            
            await ticket_channel.send(embed=embed, view=TicketControlView())
            
            # Скрываем меню выбора
            await interaction.response.send_message(
                f"✅ Тикет создан: {ticket_channel.mention}",
                ephemeral=True
            )
            
            # Лог
            await send_log(
                guild=interaction.guild,
                title="🎫 Тикет создан",
                description=f"{interaction.user.mention} создал тикет в категории {category_name[self.values[0]]}",
                color=discord.Color.green(),
                thumbnail=interaction.user.display_avatar.url,
                fields=[
                    ("Пользователь", f"{interaction.user.mention}\n`{interaction.user.id}`", True),
                    ("Категория", category_name[self.values[0]], True),
                    ("Канал", ticket_channel.mention, False)
                ]
            )
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Ошибка создания тикета: {e}", ephemeral=True)

class TicketControlView(View):
    """Кнопки управления тикетом"""
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="🔒 Закрыть тикет", style=discord.ButtonStyle.red, custom_id="ticket_close"))
        self.add_item(Button(label="🗑️ Удалить тикет", style=discord.ButtonStyle.danger, custom_id="ticket_delete"))

class TicketCreateView(View):
    """Кнопка создания тикета"""
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="🎫 Создать тикет", style=discord.ButtonStyle.blurple, custom_id="ticket_create"))

class TicketCategoryView(View):
    """Меню выбора категории"""
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketCategorySelect())

# ================= РОЛИ - КНОПКИ =================
class RoleSelectView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RoleButton(label="Агрессия", role_id=COSMETIC_ROLES["knife"], emoji="🔪", style=discord.ButtonStyle.danger))
        self.add_item(RoleButton(label="Наука", role_id=COSMETIC_ROLES["science"], emoji="🧪", style=discord.ButtonStyle.blurple))
        self.add_item(RoleButton(label="Призрак", role_id=COSMETIC_ROLES["ghost"], emoji="👻", style=discord.ButtonStyle.gray))
        self.add_item(RoleButton(label="Мутант", role_id=COSMETIC_ROLES["radio"], emoji="☢️", style=discord.ButtonStyle.green))
        self.add_item(RoleButton(label="Инкогнито", role_id=COSMETIC_ROLES["moon"], emoji="🌑", style=discord.ButtonStyle.gray))

class RoleButton(Button):
    def __init__(self, label, role_id, emoji, style):
        super().__init__(label=label, emoji=emoji, style=style, custom_id=f"role_{role_id}")
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        role = guild.get_role(self.role_id)

        if not role:
            await interaction.response.send_message("❌ Ошибка: Роль не найдена.", ephemeral=True)
            return

        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"✅ Роль **{role.name}** удалена.", ephemeral=True)
            await send_log(
                guild=guild,
                title="🔓 Роль удалена (Самовыдача)",
                description=f"{user.mention} удалил роль **{role.name}**",
                color=discord.Color.orange(),
                thumbnail=user.display_avatar.url,
                fields=[
                    ("Пользователь", f"{user.mention}\n`{user.id}`", True),
                    ("Роль", f"{role.mention}\n`{role.id}`", True),
                    ("Действие", "❌ Удаление", True)
                ]
            )
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"✅ Роль **{role.name}** выдана.", ephemeral=True)
            await send_log(
                guild=guild,
                title="🔐 Роль выдана (Самовыдача)",
                description=f"{user.mention} получил роль **{role.name}**",
                color=discord.Color.green(),
                thumbnail=user.display_avatar.url,
                fields=[
                    ("Пользователь", f"{user.mention}\n`{user.id}`", True),
                    ("Роль", f"{role.mention}\n`{role.id}`", True),
                    ("Действие", "✅ Выдача", True)
                ]
            )

# ================= СОБЫТИЯ =================

@bot.event
async def on_ready():
    bot.add_view(TicketCreateView())
    bot.add_view(TicketCategoryView())
    bot.add_view(TicketControlView())
    bot.add_view(RoleSelectView())
    status = discord.Status.dnd
    activity = discord.Activity(name="За сервером Безумия", type=discord.ActivityType.watching)
    await bot.change_presence(status=status, activity=activity)
    print(f'Бот {bot.user.name} запущен!')
    print(f'Канал логов: {LOG_CHANNEL_ID}')
    print(f'Категория тикетов: {TICKET_CATEGORY_ID}')
    
    try:
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if not log_channel:
            log_channel = await bot.fetch_channel(LOG_CHANNEL_ID)
        embed = discord.Embed(
            title="🟢 Бот запущен",
            description="Система логирования и тикетов активна",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Бот", value=f"{bot.user.mention}\n`{bot.user.id}`", inline=False)
        embed.add_field(name="Серверов", value=str(len(bot.guilds)), inline=True)
        embed.add_field(name="Пользователей", value=str(sum(len(guild.members) for guild in bot.guilds)), inline=True)
        await log_channel.send(embed=embed)
    except Exception as e:
        print(f"Не удалось отправить лог запуска: {e}")

@bot.event
async def on_member_join(member):
    """Лог вступления"""
    await send_log(
        guild=member.guild,
        title="📥 Участник вступил",
        description=f"{member.mention} присоединился к серверу",
        color=discord.Color.green(),
        thumbnail=member.display_avatar.url,
        fields=[
            ("Пользователь", f"{member.mention}\n`{member.id}`", True),
            ("Аккаунт создан", f"<t:{int(member.created_at.timestamp())}:R>", True),
            ("Всего участников", str(len(member.guild.members)), True)
        ]
    )

@bot.event
async def on_member_remove(member):
    """Логирование выхода участника"""
    await send_log(
        guild=member.guild,
        title="📤 Участник покинул сервер",
        description=f"{member.mention} покинул сервер",
        color=discord.Color.red(),
        thumbnail=member.display_avatar.url,
        fields=[
            ("Пользователь", f"{member.name}\n`{member.id}`", True),
            ("Был на сервере", f"<t:{int(member.joined_at.timestamp())}:R>" if member.joined_at else "Неизвестно", True),
            ("Всего участников", str(len(member.guild.members)), True)
        ]
    )

@bot.event
async def on_member_update(before, after):
    """Логирование изменений участника (роли, никнейм)"""
    guild = after.guild
    
    if before.nick != after.nick:
        old_nick = before.nick if before.nick else before.name
        new_nick = after.nick if after.nick else after.name
        await send_log(
            guild=guild,
            title="✏️ Никнейм изменён",
            description=f"{after.mention} изменил никнейм",
            color=discord.Color.blue(),
            thumbnail=after.display_avatar.url,
            fields=[
                ("Пользователь", f"{after.mention}\n`{after.id}`", True),
                ("Было", old_nick, True),
                ("Стало", new_nick, True)
            ]
        )
    
    before_roles = set(before.roles)
    after_roles = set(after.roles)
    
    added_roles = after_roles - before_roles
    removed_roles = before_roles - after_roles
    
    added_roles = {r for r in added_roles if r.id != guild.id}
    removed_roles = {r for r in removed_roles if r.id != guild.id}
    
    if added_roles:
        roles_list = ", ".join([r.mention for r in added_roles])
        await send_log(
            guild=guild,
            title="🔐 Роль выдана",
            description=f"{after.mention} получил роль(и): {roles_list}",
            color=discord.Color.green(),
            thumbnail=after.display_avatar.url,
            fields=[
                ("Пользователь", f"{after.mention}\n`{after.id}`", True),
                ("Роль(и)", roles_list, False)
            ]
        )
    
    if removed_roles:
        roles_list = ", ".join([r.mention for r in removed_roles])
        await send_log(
            guild=guild,
            title="🔓 Роль удалена",
            description=f"{after.mention} потерял роль(и): {roles_list}",
            color=discord.Color.orange(),
            thumbnail=after.display_avatar.url,
            fields=[
                ("Пользователь", f"{after.mention}\n`{after.id}`", True),
                ("Роль(и)", roles_list, False)
            ]
        )

@bot.event
async def on_message(message):
    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    if before.author.bot:
        return
    if before.content == after.content:
        return
    
    await send_log(
        guild=after.guild,
        title="✏️ Сообщение отредактировано",
        description=f"{after.author.mention} отредактировал сообщение в {after.channel.mention}",
        color=discord.Color.blue(),
        thumbnail=after.author.display_avatar.url,
        fields=[
            ("Автор", f"{after.author.mention}\n`{after.author.id}`", True),
            ("Канал", after.channel.mention, True),
            ("Было", f"```{before.content[:1000]}```" if before.content else "*(пусто)*", False),
            ("Стало", f"```{after.content[:1000]}```" if after.content else "*(пусто)*", False)
        ]
    )

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    
    await send_log(
        guild=message.guild,
        title="🗑️ Сообщение удалено",
        description=f"Сообщение от {message.author.mention} удалено в {message.channel.mention}",
        color=discord.Color.red(),
        thumbnail=message.author.display_avatar.url if message.author else None,
        fields=[
            ("Автор", f"{message.author.mention}\n`{message.author.id}`" if message.author else "Неизвестно", True),
            ("Канал", message.channel.mention, True),
            ("Содержимое", f"```{message.content[:1000]}```" if message.content else "*(нет текста/вложение)*", False)
        ]
    )

@bot.event
async def on_member_ban(guild, user):
    await send_log(
        guild=guild,
        title="🔨 Пользователь забанен",
        description=f"{user.mention} был забанен",
        color=discord.Color.dark_red(),
        thumbnail=user.display_avatar.url if hasattr(user, 'display_avatar') else None,
        fields=[
            ("Пользователь", f"{user.mention}\n`{user.id}`", True),
            ("Действие", "⛔ Бан", True)
        ]
    )

@bot.event
async def on_member_unban(guild, user):
    await send_log(
        guild=guild,
        title="✅ Пользователь разбанен",
        description=f"{user.mention} был разбанен",
        color=discord.Color.green(),
        thumbnail=user.display_avatar.url if hasattr(user, 'display_avatar') else None,
        fields=[
            ("Пользователь", f"{user.mention}\n`{user.id}`", True),
            ("Действие", "✅ Разбан", True)
        ]
    )

@bot.event
async def on_voice_state_update(member, before, after):
    guild = member.guild
    
    if before.channel is None and after.channel is not None:
        await send_log(
            guild=guild,
            title="🔊 Подключился к голосовому",
            description=f"{member.mention} подключился к {after.channel.mention}",
            color=discord.Color.blue(),
            thumbnail=member.display_avatar.url,
            fields=[
                ("Пользователь", f"{member.mention}\n`{member.id}`", True),
                ("Канал", after.channel.mention, True)
            ]
        )
    
    if before.channel is not None and after.channel is None:
        await send_log(
            guild=guild,
            title="🔇 Отключился от голосового",
            description=f"{member.mention} отключился от {before.channel.mention}",
            color=discord.Color.greyple(),
            thumbnail=member.display_avatar.url,
            fields=[
                ("Пользователь", f"{member.mention}\n`{member.id}`", True),
                ("Канал", before.channel.mention, True)
            ]
        )
    
    if before.channel is not None and after.channel is not None and before.channel != after.channel:
        await send_log(
            guild=guild,
            title="🔄 Перешёл в другой голосовой",
            description=f"{member.mention} перешёл из {before.channel.mention} в {after.channel.mention}",
            color=discord.Color.blue(),
            thumbnail=member.display_avatar.url,
            fields=[
                ("Пользователь", f"{member.mention}\n`{member.id}`", True),
                ("Было", before.channel.mention, True),
                ("Стало", after.channel.mention, True)
            ]
        )

# ================= КОМАНДА ROLES =================

@bot.command(name='roles')
async def roles_command(ctx):
    try:
        await ctx.message.delete()
    except discord.errors.Forbidden:
        pass

    embed = discord.Embed(
        title="🏥 Роли сервера Безумие - Реанимация",
        description="Нажмите на кнопки ниже, чтобы получить косметические роли.",
        color=discord.Color.red()
    )

    embed.add_field(name="👑 АДМИНИСТРАЦИЯ", value=(
        f"<@&1482021644703760607> — Владелец, финальное слово)\n"
        f"<@&1482021651867631746> — Координация отделов\n"
        f"<@&1482021652488524058> — Контроль модерации"
    ), inline=False)

    embed.add_field(name="🛡 ПЕРСОНАЛ КЛИНИКИ", value=(
        f"<@&1482021653109018734> — Модератор чатов (Правила, предупреждения)\n"
        f"<@&1482021654082093076> — Помощник модератора (Встреча новичков)\n"
        f"<@&1482021656636428411> — Выдача ролей и верификация\n"
        f"<@&1482021656649269310> — Тех. поддержка (Баги, аккаунты)"
    ), inline=False)

    embed.add_field(name="🧪 РАЗРАБОТЧИКИ", value=(
        f"<@&1482021658708541570> — Ведущий разработчик\n"
        f"<@&1482021658796752986> — Программист (Скрипты, фиксы)\n"
        f"<@&1482021659878883358> — Визуал (Интерфейс, иконки)"
    ), inline=False)

    embed.add_field(name="🎖 ОСОБЫЕ СТАТУСЫ", value=(
        f"<@&1482026327216492684> — Топ-игрок сервера\n"
        f"<@&1482021673266839583> — Тестировщик сборок\n"
        f"<@&1482021674378334319> — Представитель проекта\n"
        f"<@&1482026325693825025> — Спонсор проекта\n"
        f"<@&1482026326746599575> — Фан-арт/Гайд/Мем\n"
        f"<@&1482021672604405935> — Ветеран (Играл в оригинал)"
    ), inline=False)

    embed.add_field(name="🎭 КОСМЕТИЧЕСКИЕ", value=(
        f"<@&1482026329368170706> — Для любителей агрессивного стиля\n"
        f"<@&1482026329435148421> — Для фанатов лора и науки\n"
        f"<@&1482026850564968488> — Нейтральный, таинственный\n"
        f"<@&1482026851479195689> — Кислотно-зелёный, стиль «мутант»\n"
        f"<@&1482026853085610117> — Тёмный, для инкогнито"
    ), inline=False)

    embed.set_footer(text="Безумие - Реанимация | Система ролей")
    await ctx.send(embed=embed, view=RoleSelectView())

# ================= КОМАНДА TICKETS =================

@bot.command(name='tickets')
@is_admin_or_owner()
async def tickets_command(ctx):
    """Отправляет панель создания тикетов"""
    try:
        await ctx.message.delete()
    except:
        pass

    embed = discord.Embed(
        title="🎫 Система тикетов | Техподдержка",
        description="Нажмите на кнопку ниже, чтобы создать тикет для связи с администрацией.\n\n"
                    "**Доступные категории:**\n"
                    "👥 **Заявка в персонал** — Подать заявку на роль модератора/админа\n"
                    "🎖 **Особый статус** — Получить уникальную роль за достижения\n"
                    "💻 **Разработчиком** — Подать заявку в команду разработчиков\n\n"
                    "⚠️ **Правила:**\n"
                    "• Не создавайте более 1 тикета одновременно\n"
                    "• Ожидайте ответа администрации\n"
                    "• Не злоупотребляйте системой тикетов",
        color=discord.Color.blue(),
        timestamp=datetime.utcnow()
    )
    
    embed.set_footer(text="🏥 Безумие - Реанимация | Служба поддержки")
    
    await ctx.send(embed=embed, view=TicketCreateView())
    
    await send_log(
        guild=ctx.guild,
        title="🎫 Панель тикетов создана",
        description=f"{ctx.author.mention} создал панель тикетов",
        color=discord.Color.blue(),
        fields=[
            ("Администратор", f"{ctx.author.mention}\n`{ctx.author.id}`", True),
            ("Канал", ctx.channel.mention, True)
        ]
    )

# ================= КОМАНДА SAY =================

@bot.command(name='say')
@is_admin_or_owner()
async def say_command(ctx, *, message: str = None):
    if not message:
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.send("❌ **Укажите текст сообщения!**\nПример: `!say Привет всем!`", delete_after=10)
        return

    try:
        await ctx.message.delete()
    except discord.errors.Forbidden:
        pass
    
    await ctx.send(message)
    
    await send_log(
        guild=ctx.guild,
        title="📢 Команда !say использована",
        description=f"{ctx.author.mention} использовал команду !say",
        color=discord.Color.blue(),
        fields=[
            ("Администратор", f"{ctx.author.mention}\n`{ctx.author.id}`", True),
            ("Канал", ctx.channel.mention, True),
            ("Сообщение", message[:1000], False)
        ]
    )

@say_command.error
async def say_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.send("🔒 **Нет прав!** Эта команда доступна только Администрации.", delete_after=5)
    else:
        print(f"Ошибка в команде say: {error}")

# ================= ОБРАБОТКА КНОПОК ТИКЕТОВ =================

@bot.event
async def on_interaction(interaction: discord.Interaction):
    """Обработка кнопок тикетов"""
    if interaction.type == discord.InteractionType.component:
        
        # Создание тикета
        if interaction.data['custom_id'] == 'ticket_create':
            await interaction.response.send_message(
                "📋 Выберите категорию тикета:",
                view=TicketCategoryView(),
                ephemeral=True
            )
        
        # Закрытие тикета
        elif interaction.data['custom_id'] == 'ticket_close':
            channel = interaction.channel
            
            # Проверка что это тикет
            if not channel.name.startswith('тикет-'):
                await interaction.response.send_message("❌ Это не тикет!", ephemeral=True)
                return
            
            # Закрываем канал (ограничиваем доступ)
            overwrites = channel.overwrites
            overwrites[interaction.guild.default_role] = discord.PermissionOverwrite(read_messages=False)
            overwrites[interaction.user] = discord.PermissionOverwrite(read_messages=True, send_messages=False)
            await channel.edit(overwrites=overwrites)
            
            embed = discord.Embed(
                title="🔒 Тикет закрыт",
                description="Тикет был закрыт. Если у вас есть ещё вопросы, создайте новый тикет.",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow()
            )
            await channel.send(embed=embed)
            
            await interaction.response.send_message("✅ Тикет закрыт!", ephemeral=True)
            
            await send_log(
                guild=interaction.guild,
                title="🔒 Тикет закрыт",
                description=f"{interaction.user.mention} закрыл тикет {channel.mention}",
                color=discord.Color.orange(),
                fields=[
                    ("Пользователь", f"{interaction.user.mention}\n`{interaction.user.id}`", True),
                    ("Канал", channel.mention, False)
                ]
            )
        
        # Удаление тикета
        elif interaction.data['custom_id'] == 'ticket_delete':
            channel = interaction.channel
            
            if not channel.name.startswith('тикет-'):
                await interaction.response.send_message("❌ Это не тикет!", ephemeral=True)
                return
            
            await interaction.response.send_message("⚠️ Тикет будет удалён через 5 секунд...", ephemeral=True)
            
            await send_log(
                guild=interaction.guild,
                title="🗑️ Тикет удалён",
                description=f"{interaction.user.mention} удалил тикет {channel.mention}",
                color=discord.Color.red(),
                fields=[
                    ("Пользователь", f"{interaction.user.mention}\n`{interaction.user.id}`", True),
                    ("Канал", channel.mention, False)
                ]
            )
            
            await asyncio.sleep(5)
            await channel.delete()

# ===================================================

bot.run(TOKEN)
