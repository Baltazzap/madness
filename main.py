import discord
from discord.ext import commands
from discord.ui import Button, View
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
WELCOME_CHANNEL_ID = 1482290408598929439
CHAT_CHANNEL_ID = 1482040574402891986  # ✅ ID основного чата

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

# ================= КНОПКИ =================
class WelcomeButton(View):
    """Кнопка для приветственного сообщения"""
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="📋 Получить роли", style=discord.ButtonStyle.blurple, custom_id="welcome_roles"))
        self.add_item(Button(label="📜 Правила", style=discord.ButtonStyle.gray, custom_id="welcome_rules"))
        self.add_item(Button(label="💬 Чат", style=discord.ButtonStyle.green, custom_id="welcome_chat"))

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
    bot.add_view(WelcomeButton())
    bot.add_view(RoleSelectView())
    status = discord.Status.dnd
    activity = discord.Activity(name="За сервером Безумия", type=discord.ActivityType.watching)
    await bot.change_presence(status=status, activity=activity)
    print(f'Бот {bot.user.name} запущен!')
    print(f'Канал логов: {LOG_CHANNEL_ID}')
    print(f'Канал приветствий: {WELCOME_CHANNEL_ID}')
    print(f'Канал чата: {CHAT_CHANNEL_ID}')
    
    try:
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if not log_channel:
            log_channel = await bot.fetch_channel(LOG_CHANNEL_ID)
        embed = discord.Embed(
            title="🟢 Бот запущен",
            description="Система логирования и приветствий активна",
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
    """Приветствие нового участника"""
    try:
        welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
        if not welcome_channel:
            welcome_channel = await bot.fetch_channel(WELCOME_CHANNEL_ID)
        
        embed = discord.Embed(
            title="🏥 Добро пожаловать в Клинику!",
            description=f"{member.mention}, вы успешно поступили в **Безумие - Реанимация**!\n\n"
                        f"Мы рады видеть вас среди наших пациентов и персонала.\n"
                        f"Не забудьте ознакомиться с правилами и получить роли!",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(name="📊 Информация", value=(
            f"**Пользователь:** {member.name}\n"
            f"**ID:** `{member.id}`\n"
            f"**Аккаунт создан:** <t:{int(member.created_at.timestamp())}:R>\n"
            f"**Всего участников:** {len(member.guild.members)}"
        ), inline=False)
        
        embed.add_field(name="📌 Первые шаги", value=(
            "1️⃣ Прочитайте **правила** сервера\n"
            "2️⃣ Получите **роли** через кнопки ниже\n"
            "3️⃣ Представьтесь в **чате**\n"
            "4️⃣ Наслаждайтесь игрой!"
        ), inline=False)
        
        embed.set_footer(text="🏥 Безумие - Реанимация | Приёмное отделение")
        
        await welcome_channel.send(content=f"🎉 {member.mention}", embed=embed, view=WelcomeButton())
        
    except Exception as e:
        print(f"Ошибка отправки приветствия: {e}")
    
    # Лог вступления (в канал логов)
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

# ================= ОБРАБОТКА КНОПОК ПРИВЕТСТВИЯ =================

@bot.event
async def on_interaction(interaction: discord.Interaction):
    """Обработка кнопок из приветственного сообщения"""
    if interaction.type == discord.InteractionType.component:
        if interaction.data['custom_id'] == 'welcome_roles':
            await interaction.response.send_message(
                "📋 Чтобы получить роли, используйте команду `!roles` в любом чате!",
                ephemeral=True
            )
        elif interaction.data['custom_id'] == 'welcome_rules':
            await interaction.response.send_message(
                "📜 **Правила сервера:**\n"
                "1. Уважайте других участников\n"
                "2. Запрещён спам и флуд\n"
                "3. Запрещены оскорбления\n"
                "4. Слушайтесь администрацию\n"
                "5. Запрещён чит в игре",
                ephemeral=True
            )
        elif interaction.data['custom_id'] == 'welcome_chat':
            await interaction.response.send_message(
                f"💬 Перейдите в канал <#{CHAT_CHANNEL_ID}> для общения!",
                ephemeral=True
            )

# ===================================================

bot.run(TOKEN)
