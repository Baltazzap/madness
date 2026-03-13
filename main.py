import os
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Modal, TextInput
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
# 🛡️ КОНФИГУРАЦИЯ
# ============================================
OWNER_ID = 314805583788244993
ADMIN_ROLE_IDS = [
    1482021644703760607, 1482021651867631746,
    1482021652488524058, 1482021653109018734,
    1482021654082093076
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
        for role_id in ADMIN_ROLE_IDS:
            role = interaction.guild.get_role(role_id)
            if role and role in interaction.user.roles:
                return True
    return False

async def is_authorized_ctx(ctx):
    if ctx.author.id == OWNER_ID:
        return True
    if hasattr(ctx, 'guild') and ctx.guild:
        for role_id in ADMIN_ROLE_IDS:
            role = ctx.guild.get_role(role_id)
            if role and role in ctx.author.roles:
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
# 🎨 МОДАЛЬНОЕ ОКНО (МАКС 5 ПОЛЕЙ)
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
# 📜 ФУНКЦИЯ ОТПРАВКИ ПРАВИЛ
# ============================================
async def send_rules_embeds(channel):
    """Отправляет правила в виде серии эмбедов"""
    
    # Эмбед 1: Заголовок
    embed1 = discord.Embed(
        title="📜 ПРАВИЛА СЕРВЕРА",
        description="**«Безумие: Реанимация»**\n\n*«В этой клинике свои законы. Нарушишь — станешь частью эксперимента.»*",
        color=0x8B0000
    )
    embed1.set_thumbnail(url="https://i.imgur.com/medical-cross.png")  # Замените на свою иконку
    embed1.add_field(name="📅 Обновлено", value="14.03.2026", inline=True)
    embed1.add_field(name="📌 Версия", value="2.1", inline=True)
    embed1.add_field(name="🔞 Возраст", value="16+", inline=True)
    embed1.set_footer(text="Продолжение ниже ⬇️")

    # Эмбед 2: Основные принципы
    embed2 = discord.Embed(
        title="⚠️ РАЗДЕЛ 0: БАЗОВЫЕ ПРИНЦИПЫ",
        color=0x8B0000
    )
    embed2.add_field(
        name="🔹 Правило №0: «Не навреди»",
        value="Уважай других участников. Токсичность, оскорбления и дискриминация караются изоляцией.",
        inline=False
    )
    embed2.add_field(
        name="🔹 Правило №1: «Здравый смысл»",
        value="Даже если чего-то нет в правилах, но это портит атмосферу — администрация применит санкции.",
        inline=False
    )
    embed2.add_field(
        name="🔹 Правило №2: «Незнание не освобождает»",
        value="Вы обязаны ознакомиться с правилами. «Я не читал» не является оправданием.",
        inline=False
    )

    # Эмбед 3: Общение
    embed3 = discord.Embed(
        title="🗣️ РАЗДЕЛ 1: ОБЩЕНИЕ В ЧАТАХ",
        color=0x8B0000
    )
    embed3.add_field(
        name="✅ Разрешено",
        value="• Общение на русском/английском\n• Конструктивная критика\n• Тематические обсуждения\n• Мемы по теме игры",
        inline=True
    )
    embed3.add_field(
        name="❌ Запрещено",
        value="• Оскорбления и унижения\n• Спам, капслок\n• Реклама без согласия\n• Конфликты и троллинг",
        inline=True
    )
    embed3.add_field(
        name="🚫 Контент",
        value="• Порнография 18+\n• Пропаганда наркотиков/суицида\n• Спойлеры без тега\n• Вирусы и фишинг",
        inline=False
    )

    # Эмбед 4: Игровые правила
    embed4 = discord.Embed(
        title="⚔️ РАЗДЕЛ 2: ИГРОВЫЕ ПРАВИЛА",
        color=0x8B0000
    )
    embed4.add_field(
        name="✅ Честная игра",
        value="• Кооперация с игроками\n• Стратегии и тактики\n• Репорты багов",
        inline=True
    )
    embed4.add_field(
        name="❌ Запрещено",
        value="• Читы и эксплойты\n• Мультиаккаунты\n• Продажа за реальные деньги\n• Гриферство",
        inline=True
    )
    embed4.add_field(
        name="🏰 Клановые войны",
        value="• Объявление через тикет\n• Запрет на атаки новичков (<10 ур.)\n• Роспуск за массовые нарушения",
        inline=False
    )

    # Эмбед 5: Безопасность
    embed5 = discord.Embed(
        title="🔐 РАЗДЕЛ 3: БЕЗОПАСНОСТЬ",
        color=0x8B0000
    )
    embed5.add_field(
        name="🛡️ Никогда не передавайте",
        value="• Пароль от аккаунта\n• Личные данные (адрес, телефон)\n• Коды 2FA, данные карт",
        inline=False
    )
    embed5.add_field(
        name="⚠️ Важно",
        value="**Администрация НИКОГДА не запросит ваш пароль!**\n\nФишинг = перманентный бан.",
        inline=False
    )

    # Эмбед 6: Наказания
    embed6 = discord.Embed(
        title="⚖️ РАЗДЕЛ 4: НАКАЗАНИЯ",
        color=0x8B0000
    )
    embed6.add_field(
        name="📋 Система",
        value="**Оскорбление:** ⚠️ → 🔇1ч → 🔇24ч → 🔨7д\n**Спам:** 🗑️ → 🔇30м → 🔇6ч → 🔨3д\n**Реклама:** 🔨1д → 🔨7д → 🔨∞\n**Читы:** 🔨 Пермабан",
        inline=False
    )
    embed6.add_field(
        name="📝 Апелляция",
        value="1. Создайте тикет в #📩・тикет-поддержка\n2. Укажите ник и причину\n3. Приложите доказательства\n4. Ожидайте 24-72 часа",
        inline=False
    )

    # Эмбед 7: Принятие правил
    embed7 = discord.Embed(
        title="🤝 РАЗДЕЛ 5: ПРИНЯТИЕ ПРАВИЛ",
        description="✅ **Чтобы получить доступ:**\n\n1. Прочитайте все правила\n2. Перейдите в <#🎭・роли>\n3. Нажмите реакцию 🩹 под правилами\n4. Получите роль **«Пациент»**\n\n❌ Без роли доступ ограничен.",
        color=0x00FF00
    )
    embed7.set_footer(text="💀 Помните: «Безумие» — это не просто игра. Это состояние души.")

    embeds = [embed1, embed2, embed3, embed4, embed5, embed6, embed7]
    
    for i, embed in enumerate(embeds):
        await channel.send(embed=embed)
        if i < len(embeds) - 1:
            await asyncio.sleep(0.5)  # Небольшая задержка между эмбедами

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
    
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Activity(type=discord.ActivityType.watching, name="за сервером")
    )
    print(f'🤖 Бот готов: {bot.user}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Команда не найдена.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Подождите {error.retry_after:.1f} сек.")
    else:
        await ctx.send(f"❌ Ошибка: {error}")

# ============================================
# ⚔️ TEXT КОМАНДЫ
# ============================================
@bot.command(name='addrole')
@commands.cooldown(1, 60, commands.BucketType.default)
async def add_role_to_all(ctx, role_id: int):
    await delete_user_message(ctx)
    
    if not await is_authorized_ctx(ctx):
        await ctx.send("🚫 Нет прав.")
        return

    try:
        role = ctx.guild.get_role(role_id)
        if role is None:
            await ctx.send("❌ Роль не найдена.")
            return
        if role.position >= ctx.guild.me.top_role.position:
            await ctx.send("❌ Роль выше моей.")
            return
    except Exception as e:
        await ctx.send(f"❌ Ошибка: {e}")
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
    """Отправляет правила сервера в виде эмбедов"""
    await delete_user_message(ctx)
    
    # Проверка прав (только админы могут рассылать правила)
    if not await is_authorized_ctx(ctx):
        await ctx.send("🚫 Нет прав для использования этой команды.", delete_after=5)
        return
    
    await ctx.send("📜 **Отправка правил...**", delete_after=3)
    await send_rules_embeds(ctx.channel)

@bot.command(name='ping')
async def ping_command(ctx):
    await delete_user_message(ctx)
    await ctx.send(f"🏓 {round(bot.latency * 1000)}ms")

@bot.command(name='sync')
@commands.is_owner()
async def sync_force(ctx):
    await bot.tree.sync()
    await ctx.send("✅ Команды обновлены!", delete_after=5)

# ============================================
# 🎨 SLASH КОМАНДЫ
# ============================================
@bot.tree.command(name='create_embed', description='Создать эмбед')
@app_commands.describe(
    channel='Канал для отправки',
    title='Заголовок эмбеда',
    description='Описание эмбеда',
    color='Цвет (HEX без #)'
)
async def create_embed_command(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    title: str,
    description: str = None,
    color: str = 'FF0000'
):
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
