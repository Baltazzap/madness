import os
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Modal, TextInput, Button, View
import asyncio
from dotenv import load_dotenv

# ============================================
# 🔐 ЗАГРУЗКА ПЕРЕМЕННЫХ
# ============================================
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

if not DISCORD_TOKEN:
    print("❌ ОШИБКА: DISCORD_TOKEN не найден в .env!")
    exit(1)

# ============================================
# 🛡️ КОНФИГУРАЦИЯ ID
# ============================================
OWNER_ID = 314805583788244993
CHANNEL_TICKETS_ID = 1482042344638251129
CHANNEL_ROLES_ID = 1482040280705142805
ROLE_PATIENT_ID = 1482026327841181727

# ============================================
# 🎭 ВСЕ РОЛИ СЕРВЕРА (БЕЗ ИКОНОК)
# ============================================

ADMIN_ROLES = [
    {"id": 1482021644703760607, "name": "Глав Врач", "desc": "Владелец сервера, финальное слово во всех решениях."},
    {"id": 1482021651867631746, "name": "Зам. Глав врача", "desc": "Заместитель, координирует работу всех отделов."},
    {"id": 1482021652488524058, "name": "Старший Ординатор", "desc": "Контроль модерации и тех. поддержки, решение конфликтов."},
]

STAFF_ROLES = [
    {"id": 1482021653109018734, "name": "Врач", "desc": "Модератор чатов: следит за правилами, выдаёт предупреждения."},
    {"id": 1482021654082093076, "name": "Санитар", "desc": "Помощник модератора, встречает новичков, отвечает на простые вопросы."},
    {"id": 1482021656636428411, "name": "Регистратор", "desc": "Выдаёт роли, помогает с верификацией и доступом к каналам."},
    {"id": 1482021656649269310, "name": "Техник", "desc": "Техническая поддержка: помощь с запуском, баги, аккаунты."},
]

DEV_ROLES = [
    {"id": 1482021658708541570, "name": "Архитектор", "desc": "Ведущий разработчик, принимает решения по коду и механикам."},
    {"id": 1482021658796752986, "name": "Кодер", "desc": "Программист: скрипты, фиксы, оптимизация."},
    {"id": 1482021659878883358, "name": "Художник", "desc": "Визуал: интерфейс, иконки, промо-материалы."},
]

SPECIAL_ROLES = [
    {"id": 1482026327216492684, "name": "Легенда", "desc": "Топ-игрок сервера, имя известно всем."},
    {"id": 1482021673266839583, "name": "Бета-тестер", "desc": "Участвует в тестировании сборок, ищет баги."},
    {"id": 1482021674378334319, "name": "Партнёр", "desc": "Представитель дружественного проекта/канала."},
    {"id": 1482026325693825025, "name": "Донатор", "desc": "Поддержал проект финансово. Бонусы в игре/чате."},
    {"id": 1482026326746599575, "name": "Креатор", "desc": "Создал популярный фан-арт, гайд или мем."},
    {"id": 1482021672604405935, "name": "Ветеран ВК", "desc": "Играл в оригинал до закрытия. Уважение комьюнити."},
]

COSMETIC_ROLES = [
    {"id": 1482026329368170706, "name": "Маньяк", "desc": "Для любителей агрессивного стиля"},
    {"id": 1482026329435148421, "name": "Безумный учёный", "desc": "Для фанатов лора и науки"},
    {"id": 1482026850564968488, "name": "Призрак", "desc": "Нейтральный, таинственный"},
    {"id": 1482026851479195689, "name": "Радиационный", "desc": "Кислотно-зелёный, стиль «мутант»"},
    {"id": 1482026853085610117, "name": "Тень", "desc": "Тёмный, для инкогнито"},
]

# ============================================
# ⚙️ НАСТРОЙКИ БОТА
# ============================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ============================================
# 🛡️ ПРОВЕРКА ПРАВ
# ============================================
async def is_authorized(interaction: discord.Interaction):
    if interaction.user.id == OWNER_ID:
        return True
    if interaction.guild:
        for role in ADMIN_ROLES + STAFF_ROLES:
            if interaction.guild.get_role(role["id"]) in interaction.user.roles:
                return True
    return False

async def is_authorized_ctx(ctx):
    if ctx.author.id == OWNER_ID:
        return True
    if hasattr(ctx, 'guild') and ctx.guild:
        for role in ADMIN_ROLES + STAFF_ROLES:
            if ctx.guild.get_role(role["id"]) in ctx.author.roles:
                return True
    return False

# ============================================
# 🧹 ФУНКЦИЯ ОЧИСТКИ
# ============================================
async def delete_user_message(ctx):
    try:
        if not isinstance(ctx, discord.Interaction):
            await ctx.message.delete()
    except:
        pass

# ============================================
# 🩹 КНОПКА ПОЛУЧЕНИЯ РОЛИ (ПРАВИЛА)
# ============================================
class PatientRoleButton(Button):
    def __init__(self):
        super().__init__(label='Принять правила', emoji='🩹', style=discord.ButtonStyle.success, custom_id='patient_role')
    
    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        role = guild.get_role(ROLE_PATIENT_ID)
        
        if role is None:
            await interaction.response.send_message("❌ **Ошибка:** Роль «Пациент» не найдена.", ephemeral=True)
            return
        
        if role in interaction.user.roles:
            await interaction.response.send_message("✅ У вас уже есть роль **«Пациент»**!", ephemeral=True)
            return
        
        try:
            await interaction.user.add_roles(role, reason="Принятие правил сервера")
            await interaction.response.send_message(f"✅ **Добро пожаловать в клинику!**\n\nВы получили роль: {role.mention}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ **Ошибка:** {e}", ephemeral=True)

class RulesView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PatientRoleButton())

# ============================================
# 🎭 КНОПКИ ДЛЯ КОСМЕТИЧЕСКИХ РОЛЕЙ
# ============================================
class CosmeticRoleButton(Button):
    def __init__(self, role_data):
        super().__init__(label=role_data['name'], emoji='🎭', style=discord.ButtonStyle.secondary, custom_id=f'cosmetic_{role_data["id"]}')
        self.role_data = role_data
    
    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        role = guild.get_role(self.role_data['id'])
        
        if role is None:
            await interaction.response.send_message(f"❌ **Ошибка:** Роль не найдена.", ephemeral=True)
            return
        
        if role in interaction.user.roles:
            try:
                await interaction.user.remove_roles(role, reason=f"Снятие роли {self.role_data['name']}")
                await interaction.response.send_message(f"❌ **Роль снята:** {role.mention}", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ **Ошибка:** {e}", ephemeral=True)
        else:
            try:
                await interaction.user.add_roles(role, reason=f"Самовыдача роли {self.role_data['name']}")
                await interaction.response.send_message(f"✅ **Роль получена:** {role.mention}", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ **Ошибка:** {e}", ephemeral=True)

class RolesView(View):
    def __init__(self):
        super().__init__(timeout=None)
        for role_data in COSMETIC_ROLES:
            self.add_item(CosmeticRoleButton(role_data))

# ============================================
# 🎨 МОДАЛЬНОЕ ОКНО
# ============================================
class EmbedCreatorModal(Modal, title='🎨 Настройка эмбеда'):
    def __init__(self, channel: discord.TextChannel, title: str, description: str, color: str):
        super().__init__()
        self.channel = channel
        self.title = title
        self.description = description
        self.color = color
        
        self.author_input = TextInput(label='Имя автора', placeholder='Оставьте пустым', max_length=256, required=False)
        self.add_item(self.author_input)
        self.author_icon_input = TextInput(label='Иконка автора (URL)', placeholder='https://...', max_length=512, required=False)
        self.add_item(self.author_icon_input)
        self.image_input = TextInput(label='Баннер (URL)', placeholder='https://...', max_length=512, required=False)
        self.add_item(self.image_input)
        self.thumbnail_input = TextInput(label='Миниатюра (URL)', placeholder='https://...', max_length=512, required=False)
        self.add_item(self.thumbnail_input)
        self.footer_input = TextInput(label='Текст подвала', placeholder='Текст внизу', max_length=2048, required=False)
        self.add_item(self.footer_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            color = int(self.color.strip(), 16) if self.color.strip() else 0xFF0000
            embed = discord.Embed(title=self.title, description=self.description, color=color)
            if self.author_input.value:
                embed.set_author(name=self.author_input.value, icon_url=self.author_icon_input.value or None)
            if self.image_input.value:
                embed.set_image(url=self.image_input.value)
            if self.thumbnail_input.value:
                embed.set_thumbnail(url=self.thumbnail_input.value)
            if self.footer_input.value:
                embed.set_footer(text=self.footer_input.value)
            await self.channel.send(embed=embed)
            await interaction.followup.send(f"✅ **Эмбед создан!**\n📬 Канал: {self.channel.mention}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ **Ошибка:** `{e}`", ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.followup.send(f"💥 **Ошибка:** {error}", ephemeral=True)

# ============================================
# 📜 ФУНКЦИЯ ОТПРАВКИ ПРАВИЛ (ИСПРАВЛЕНО)
# ============================================
async def send_rules_embeds(channel):
    # Одно сообщение с правилами + кнопка
    embed = discord.Embed(
        title="📜 ПРАВИЛА СЕРВЕРА «БЕЗУМИЕ: РЕАНИМАЦИЯ»",
        description="*«В этой клинике свои законы. Нарушишь — станешь частью эксперимента.»*",
        color=0x8B0000
    )
    
    embed.add_field(
        name="⚠️ ОСНОВНЫЕ ПРИНЦИПЫ",
        value="**Правило №0:** Уважай других участников\n**Правило №1:** Здравый смысл превыше всего\n**Правило №2:** Незнание правил не освобождает от ответственности",
        inline=False
    )
    
    embed.add_field(
        name="🗣️ ОБЩЕНИЕ",
        value="✅ Русский/английский язык\n✅ Конструктивная критика\n❌ Оскорбления, спам, реклама\n❌ Контент 18+, спойлеры",
        inline=True
    )
    
    embed.add_field(
        name="⚔️ ИГРА",
        value="✅ Кооперация, тактики\n❌ Читы, мультиаккаунты\n❌ Продажа за реальные деньги",
        inline=True
    )
    
    embed.add_field(
        name="🔐 БЕЗОПАСНОСТЬ",
        value="**Никогда не передавайте:**\n• Пароль от аккаунта\n• Личные данные\n• Коды 2FA\n\n⚠️ Администрация НЕ запросит пароль!",
        inline=False
    )
    
    embed.add_field(
        name="⚖️ НАКАЗАНИЯ",
        value="Оскорбление → ⚠️ → 🔇 → 🔨\nСпам → 🗑️ → 🔇 → 🔨\nЧиты → 🔨 Пермабан",
        inline=True
    )
    
    embed.add_field(
        name="📝 АПЕЛЛЯЦИЯ",
        value=f"Создайте тикет в <#{CHANNEL_TICKETS_ID}>\nУкажите ник и причину\nОжидайте 24-72 часа",
        inline=True
    )
    
    embed.add_field(
        name="🤝 ПРИНЯТИЕ ПРАВИЛ",
        value="Нажмите кнопку **🩹 Принять правила** ниже для получения роли **Пациент** и доступа к серверу.",
        inline=False
    )
    
    embed.set_footer(text="💀 «Безумие» — это не просто игра. Это состояние души.")
    
    view = RulesView()
    await channel.send(embed=embed, view=view)

# ============================================
# 🎭 ФУНКЦИЯ ОТПРАВКИ ВЫБОРА РОЛЕЙ (БЕЗ ИКОНОК)
# ============================================
async def send_roles_embed(channel):
    embed = discord.Embed(
        title="🎭 РОЛИ СЕРВЕРА",
        description="**«Безумие: Реанимация»**\n\nНажмите на кнопку, чтобы получить или снять **косметическую роль**.\n\n*🔒 Остальные роли выдаются администрацией.*",
        color=0x9932CC
    )
    
    # Без иконок, только @role
    admin_mentions = "\n".join([f"<@&{r['id']}> — {r['desc']}" for r in ADMIN_ROLES])
    embed.add_field(name="👑 АДМИНИСТРАЦИЯ", value=admin_mentions, inline=False)
    
    staff_mentions = "\n".join([f"<@&{r['id']}> — {r['desc']}" for r in STAFF_ROLES])
    embed.add_field(name="🛡 ПЕРСОНАЛ КЛИНИКИ", value=staff_mentions, inline=False)
    
    dev_mentions = "\n".join([f"<@&{r['id']}> — {r['desc']}" for r in DEV_ROLES])
    embed.add_field(name="🧪 РАЗРАБОТЧИКИ", value=dev_mentions, inline=False)
    
    special_mentions = "\n".join([f"<@&{r['id']}> — {r['desc']}" for r in SPECIAL_ROLES])
    embed.add_field(name="🎖 ОСОБЫЕ СТАТУСЫ", value=special_mentions, inline=False)
    
    cosmetic_mentions = "\n".join([f"<@&{r['id']}> — {r['desc']}" for r in COSMETIC_ROLES])
    embed.add_field(name="🎭 КОСМЕТИЧЕСКИЕ (Самовыдача)", value=cosmetic_mentions, inline=False)
    
    embed.set_footer(text="🩺 Нажмите кнопку ниже для получения косметической роли")
    
    view = RolesView()
    await channel.send(embed=embed, view=view)

# ============================================
# 🤖 СОБЫТИЯ
# ============================================
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ Синхронизировано {len(synced)} команд")
    except Exception as e:
        print(f"❌ Ошибка синхронизации: {e}")
    
    bot.add_view(RulesView())
    bot.add_view(RolesView())
    
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name="за сервером"))
    print(f'🤖 Бот готов: {bot.user}')
    print(f'🎭 Косметических ролей: {len(COSMETIC_ROLES)}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass  # Игнорируем неизвестные команды
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Подождите {error.retry_after:.1f} сек.", delete_after=5)
    else:
        print(f"Ошибка команды: {error}")

# ============================================
# ⚔️ TEXT КОМАНДЫ
# ============================================
@bot.command(name='addrole')
@commands.cooldown(1, 60, commands.BucketType.default)
async def add_role_to_all(ctx, role_id: int):
    await delete_user_message(ctx)
    if not await is_authorized_ctx(ctx):
        return
    try:
        role = ctx.guild.get_role(role_id)
        if role is None:
            await ctx.send("❌ Роль не найдена.", delete_after=5)
            return
        if role.position >= ctx.guild.me.top_role.position:
            await ctx.send("❌ Роль выше моей.", delete_after=5)
            return
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {e}", delete_after=5)
        return

    msg = await ctx.send(f"⚙️ Выдача роли **{role.name}**...")
    success_count = 0
    skipped_count = 0
    
    for member in ctx.guild.members:
        try:
            if member.bot or role in member.roles:
                skipped_count += 1
                continue
            await member.add_roles(role, reason="Массовая выдача")
            success_count += 1
            await asyncio.sleep(0.1)
        except:
            pass

    await msg.edit(content=f"✅ **Готово!**\n🟢 Выдано: {success_count}\n⚪ Пропущено: {skipped_count}")

@bot.command(name='rules')
async def rules_command(ctx):
    await delete_user_message(ctx)
    if not await is_authorized_ctx(ctx):
        return
    await send_rules_embeds(ctx.channel)

@bot.command(name='roles')
async def roles_command(ctx):
    await delete_user_message(ctx)
    if not await is_authorized_ctx(ctx):
        return
    await send_roles_embed(ctx.channel)

@bot.command(name='ping')
async def ping_command(ctx):
    await delete_user_message(ctx)
    await ctx.send(f"🏓 {round(bot.latency * 1000)}ms", delete_after=10)

@bot.command(name='sync')
@commands.is_owner()
async def sync_force(ctx):
    await delete_user_message(ctx)
    await bot.tree.sync()
    await ctx.send("✅ Команды обновлены!", delete_after=5)

# ============================================
# 🎨 SLASH КОМАНДЫ
# ============================================
@bot.tree.command(name='create_embed', description='Создать эмбед')
@app_commands.describe(channel='Канал', title='Заголовок', description='Описание', color='Цвет (HEX)')
async def create_embed_command(interaction: discord.Interaction, channel: discord.TextChannel, title: str, description: str = None, color: str = 'FF0000'):
    if not await is_authorized(interaction):
        await interaction.response.send_message("🚫 Нет прав.", ephemeral=True)
        return
    modal = EmbedCreatorModal(channel, title, description, color)
    await interaction.response.send_modal(modal)

# ============================================
# 🚀 ЗАПУСК
# ============================================
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
