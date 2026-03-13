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
        
        # Поле 1: Автор
        self.author_input = TextInput(
            label='Имя автора',
            placeholder='Оставьте пустым, если не нужно',
            max_length=256,
            required=False
        )
        self.add_item(self.author_input)
        
        # Поле 2: Иконка автора
        self.author_icon_input = TextInput(
            label='Иконка автора (URL)',
            placeholder='https://example.com/avatar.png',
            max_length=512,
            required=False
        )
        self.add_item(self.author_icon_input)
        
        # Поле 3: Баннер (картинка внизу)
        self.image_input = TextInput(
            label='Баннер (URL)',
            placeholder='https://example.com/banner.png',
            max_length=512,
            required=False
        )
        self.add_item(self.image_input)
        
        # Поле 4: Миниатюра (справа сверху)
        self.thumbnail_input = TextInput(
            label='Миниатюра (URL)',
            placeholder='https://example.com/thumb.png',
            max_length=512,
            required=False
        )
        self.add_item(self.thumbnail_input)
        
        # Поле 5: Подвал
        self.footer_input = TextInput(
            label='Текст подвала',
            placeholder='Текст внизу эмбеда',
            max_length=2048,
            required=False
        )
        self.add_item(self.footer_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Парсинг цвета
            try:
                color_val = self.color.strip()
                color = int(color_val, 16)
            except ValueError:
                color = 0xFF0000

            embed = discord.Embed(
                title=self.title,
                description=self.description if self.description else None,
                color=color
            )
            
            # Автор
            if self.author_input.value:
                embed.set_author(
                    name=self.author_input.value,
                    icon_url=self.author_icon_input.value if self.author_icon_input.value else None
                )
            
            # Баннер
            if self.image_input.value:
                embed.set_image(url=self.image_input.value)
            
            # Миниатюра
            if self.thumbnail_input.value:
                embed.set_thumbnail(url=self.thumbnail_input.value)
            
            # Подвал
            if self.footer_input.value:
                embed.set_footer(text=self.footer_input.value)
            
            # Отправка
            await self.channel.send(embed=embed)
            
            await interaction.followup.send(
                f"✅ **Эмбед создан!**\n📬 Канал: {self.channel.mention}",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.followup.send(
                f"❌ **Ошибка:** `{e}`\nПроверьте URL картинок.",
                ephemeral=True
            )

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.followup.send(f"💥 **Критическая ошибка:** {error}", ephemeral=True)

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
    try:
        await ctx.message.delete()
    except:
        pass
    
    if not await is_authorized(ctx):
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
    total_members = len(ctx.guild.members)

    for member in ctx.guild.members:
        try:
            if member.bot or role in member.roles:
                skipped_count += 1
                continue
            
            await member.add_roles(role, reason=f"Массовая выдача")
            success_count += 1
            await asyncio.sleep(0.1)
        except:
            pass

    await msg.edit(content=(
        f"✅ **Готово!**\n"
        f"🟢 Выдано: {success_count}\n"
        f"⚪ Пропущено: {skipped_count}"
    ))

@bot.command(name='ping')
async def ping_command(ctx):
    try:
        await ctx.message.delete()
    except:
        pass
    await ctx.send(f"🏓 {round(bot.latency * 1000)}ms")

@bot.command(name='sync')
@commands.is_owner()
async def sync_force(ctx):
    await bot.tree.sync()
    await ctx.send("✅ Команды обновлены!")

# ============================================
# 🎨 SLASH КОМАНДЫ
# ============================================
@bot.tree.command(name='create_embed', description='Создать эмбед')
@app_commands.describe(
    channel='Канал для отправки',
    title='Заголовок эмбеда',
    description='Описание эмбеда',
    color='Цвет (HEX без #, например FF0000)'
)
async def create_embed_command(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    title: str,
    description: str = None,
    color: str = 'FF0000'
):
    """Создание эмбеда в два этапа"""
    
    if not await is_authorized(interaction):
        await interaction.response.send_message("🚫 Нет прав.", ephemeral=True)
        return
    
    # Открываем модальное окно с оставшимися полями
    modal = EmbedCreatorModal(channel, title, description, color)
    await interaction.response.send_modal(modal)

# ============================================
# 🚀 ЗАПУСК
# ============================================
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
