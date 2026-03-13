import os
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Modal, TextInput
import asyncio
from dotenv import load_dotenv

# ============================================
# 🔐 ЗАГРУЗКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ
# ============================================

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

if not DISCORD_TOKEN:
    print("❌ ОШИБКА: DISCORD_TOKEN не найден в .env файле!")
    exit(1)

# ============================================
# 🛡️ КОНФИГУРАЦИЯ ПРАВ ДОСТУПА
# ============================================

OWNER_ID = 314805583788244993

ADMIN_ROLE_IDS = [
    1482021644703760607,
    1482021651867631746,
    1482021652488524058,
    1482021653109018734,
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
# 🛡️ ПРОВЕРКА ПРАВ ДОСТУПА
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
# 🧹 ФУНКЦИЯ ОЧИСТКИ
# ============================================

async def delete_user_message(ctx):
    try:
        if not isinstance(ctx, discord.Interaction):
            await ctx.message.delete()
    except:
        pass

# ============================================
# 🎨 МОДАЛЬНОЕ ОКНО ДЛЯ СОЗДАНИЯ ЭМБЕДА
# ============================================

class EmbedCreatorModal(Modal, title='🎨 Создание эмбеда'):
    def __init__(self, channel: discord.TextChannel):
        super().__init__()
        self.channel = channel
        
        self.title_input = TextInput(
            label='Заголовок',
            placeholder='Введите заголовок эмбеда',
            max_length=256,
            required=True
        )
        self.add_item(self.title_input)
        
        self.description_input = TextInput(
            label='Описание',
            placeholder='Введите описание эмбеда',
            max_length=4096,
            required=False,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.description_input)
        
        self.color_input = TextInput(
            label='Цвет (HEX без #)',
            placeholder='Пример: FF0000',
            max_length=6,
            required=False,
            default='FF0000'
        )
        self.add_item(self.color_input)
        
        self.author_input = TextInput(
            label='Имя автора',
            placeholder='Кто создал эмбед',
            max_length=256,
            required=False
        )
        self.add_item(self.author_input)
        
        self.author_icon_input = TextInput(
            label='Иконка автора (URL)',
            placeholder='https://example.com/avatar.png',
            max_length=512,
            required=False
        )
        self.add_item(self.author_icon_input)
        
        self.image_input = TextInput(
            label='Баннер (URL)',
            placeholder='https://example.com/banner.png',
            max_length=512,
            required=False
        )
        self.add_item(self.image_input)
        
        self.thumbnail_input = TextInput(
            label='Миниатюра (URL)',
            placeholder='https://example.com/thumb.png',
            max_length=512,
            required=False
        )
        self.add_item(self.thumbnail_input)
        
        self.footer_input = TextInput(
            label='Текст подвала',
            placeholder='Текст внизу эмбеда',
            max_length=2048,
            required=False
        )
        self.add_item(self.footer_input)
        
        self.footer_icon_input = TextInput(
            label='Иконка подвала (URL)',
            placeholder='https://example.com/footer.png',
            max_length=512,
            required=False
        )
        self.add_item(self.footer_icon_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            embed = discord.Embed(
                title=self.title_input.value,
                description=self.description_input.value if self.description_input.value else None,
                color=int(self.color_input.value, 16) if self.color_input.value else discord.Color.red()
            )
            
            if self.author_input.value:
                embed.set_author(
                    name=self.author_input.value,
                    icon_url=self.author_icon_input.value if self.author_icon_input.value else None
                )
            
            if self.image_input.value:
                embed.set_image(url=self.image_input.value)
            
            if self.thumbnail_input.value:
                embed.set_thumbnail(url=self.thumbnail_input.value)
            
            if self.footer_input.value:
                embed.set_footer(
                    text=self.footer_input.value,
                    icon_url=self.footer_icon_input.value if self.footer_icon_input.value else None
                )
            
            await self.channel.send(embed=embed)
            
            await interaction.followup.send(
                f"✅ **Эмбед успешно создан!**\n"
                f"📬 Канал: {self.channel.mention}\n"
                f"📝 Заголовок: **{self.title_input.value}**",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.followup.send(
                f"❌ **Ошибка при создании эмбеда:**\n`{e}`\n\n"
                f"Проверьте корректность URL изображений и HEX цвета.",
                ephemeral=True
            )
    
    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message(
            f"❌ **Произошла ошибка:** {error}",
            ephemeral=True
        )

# ============================================
# 🤖 СОБЫТИЯ БОТА
# ============================================

@bot.event
async def on_ready():
    # 🔄 ПРИНУДИТЕЛЬНАЯ СИНХРОНИЗАЦИЯ КОМАНД
    try:
        synced = await bot.tree.sync()
        print(f"✅ Синхронизировано {len(synced)} slash-команд")
        for cmd in synced:
            print(f"   └─ /{cmd.name}")
    except Exception as e:
        print(f"❌ Ошибка синхронизации: {e}")
    
    # 🟣 Установка статуса
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="за Модерирует сервер"
        )
    )
    
    print('✅ Бот успешно запущен!')
    print(f'🤖 Пользователь: {bot.user} (ID: {bot.user.id})')
    print(f'🛡️ Владелец: {OWNER_ID}')
    print(f'🔑 Админ-ролей: {len(ADMIN_ROLE_IDS)}')
    print(f'🔗 Серверов: {len(bot.guilds)}')
    print('----------------------------------')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ **Ошибка:** Команда не найдена.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ **Ошибка:** Укажите все необходимые аргументы.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ **Подождите:** Команда на перезарядке. Попробуйте через {error.retry_after:.1f} сек.")
    else:
        await ctx.send(f"❌ **Произошла ошибка:** {error}")

# ============================================
# ⚔️ TEXT КОМАНДЫ (PREFIX !)
# ============================================

@bot.command(name='addrole')
@commands.cooldown(1, 60, commands.BucketType.default)
async def add_role_to_all(ctx, role_id: int):
    await delete_user_message(ctx)
    
    if not await is_authorized(ctx):
        await ctx.send("🚫 **Ошибка доступа:** У вас нет прав для использования этой команды.")
        return

    try:
        role = ctx.guild.get_role(role_id)
        if role is None:
            await ctx.send("❌ **Ошибка:** Роль с таким ID не найдена на этом сервере.")
            return
        
        if role.position >= ctx.guild.me.top_role.position:
            await ctx.send("❌ **Ошибка:** Эта роль находится выше моей высшей роли. Поднимите меня в списке ролей.")
            return

    except Exception as e:
        await ctx.send(f"❌ **Ошибка при поиске роли:** {e}")
        return

    msg = await ctx.send(f"⚙️ **Запуск процесса...**\nНачинаю выдачу роли **{role.name}** всем участникам.")
    
    success_count = 0
    fail_count = 0
    skipped_count = 0
    total_members = len(ctx.guild.members)

    await ctx.send(f"ℹ️ Всего участников: {total_members}. Это может занять время...")

    for member in ctx.guild.members:
        try:
            if member.bot:
                skipped_count += 1
                continue
            
            if role in member.roles:
                skipped_count += 1
                continue
            
            await member.add_roles(role, reason=f"Массовая выдача по команде {ctx.author.name}")
            success_count += 1
            
            await asyncio.sleep(0.1) 
            
        except discord.Forbidden:
            fail_count += 1
        except Exception:
            fail_count += 1

    await msg.edit(content=(
        f"✅ **Готово!**\n"
        f"🎭 Роль: **{role.name}**\n"
        f"👥 Всего участников: {total_members}\n"
        f"🟢 Успешно выдано: {success_count}\n"
        f"⚪ Пропущено (уже есть/боты): {skipped_count}\n"
        f"🔴 Ошибки: {fail_count}"
    ))

@bot.command(name='ping')
async def ping_command(ctx):
    await delete_user_message(ctx)
    await ctx.send(f"🏓 Понг! Задержка: {round(bot.latency * 1000)}ms")

# ============================================
# 🎨 SLASH КОМАНДЫ (/)
# ============================================

@bot.tree.command(name='create_embed', description='Создать кастомный эмбед через модальное окно')
@app_commands.describe(
    channel='Канал для отправки эмбеда'
)
async def create_embed_command(
    interaction: discord.Interaction,
    channel: discord.TextChannel
):
    """Открывает модальное окно для создания эмбеда"""
    
    if not await is_authorized(interaction):
        await interaction.response.send_message(
            "🚫 **Ошибка доступа:** У вас нет прав для использования этой команды.",
            ephemeral=True
        )
        return
    
    modal = EmbedCreatorModal(channel)
    await interaction.response.send_modal(modal)

# ============================================
# 🚀 ЗАПУСК БОТА
# ============================================

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
