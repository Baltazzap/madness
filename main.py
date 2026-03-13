import os
import discord
from discord.ext import commands
from discord import app_commands
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

async def is_authorized(ctx):
    if isinstance(ctx, discord.Interaction):
        if ctx.user.id == OWNER_ID:
            return True
        if ctx.guild:
            for role_id in ADMIN_ROLE_IDS:
                role = ctx.guild.get_role(role_id)
                if role and role in ctx.user.roles:
                    return True
        return False
    else:
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
    """Удаляет сообщение пользователя после команды"""
    try:
        if isinstance(ctx, discord.Interaction):
            # Для slash-команд сообщение не удаляется (оно скрыто)
            pass
        else:
            # Для префикс-команд удаляем сообщение
            await ctx.message.delete()
    except discord.Forbidden:
        # У бота нет прав на удаление
        pass
    except Exception:
        # Игнорируем другие ошибки (например, сообщение уже удалено)
        pass

# ============================================
# 🤖 СОБЫТИЯ БОТА
# ============================================

@bot.event
async def on_ready():
    # Синхронизация slash-команд
    try:
        synced = await bot.tree.sync()
        print(f"✅ Синхронизировано {len(synced)} slash-команд")
    except Exception as e:
        print(f"❌ Ошибка синхронизации: {e}")
    
    # 🟣 Установка статуса "Не беспокоить" и активности
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
    print(f'🟣 Статус: Не беспокоить (DND)')
    print(f'👁️ Активность: Смотрит за Модерирует сервер')
    print('----------------------------------')
    print('📜 Команды:')
    print('   !addrole <ID_роли> - Выдать роль всем участникам')
    print('   !ping - Проверка задержки')
    print('   /create_embed - Создать кастомный эмбед')
    print('----------------------------------')
    print('🧹 Автосоздание: Сообщения команд будут удаляться')

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
    # 🧹 Удаляем сообщение пользователя
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
    # 🧹 Удаляем сообщение пользователя
    await delete_user_message(ctx)
    
    await ctx.send(f"🏓 Понг! Задержка: {round(bot.latency * 1000)}ms")

# ============================================
# 🎨 SLASH КОМАНДЫ (/)
# ============================================

@bot.tree.command(name='create_embed', description='Создать кастомный эмбед в выбранный канал')
@app_commands.describe(
    channel='Канал для отправки эмбеда',
    title='Заголовок эмбеда',
    description='Описание эмбеда',
    color='Цвет эмбеда (HEX без #, например: FF0000)',
    author_name='Имя автора',
    author_icon='URL иконки автора (картинка)',
    image='URL изображения (баннер внизу эмбеда)',
    thumbnail='URL миниатюры (справа сверху)',
    footer='Текст в подвале',
    footer_icon='URL иконки для подвала'
)
@app_commands.checks.has_permissions(administrator=True)
async def create_embed(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    title: str,
    description: str = None,
    color: str = 'FF0000',
    author_name: str = None,
    author_icon: str = None,
    image: str = None,
    thumbnail: str = None,
    footer: str = None,
    footer_icon: str = None
):
    """Создание кастомного эмбеда с изображением автора и баннером"""
    
    # Проверка прав (дублирующая на всякий случай)
    if not await is_authorized(interaction):
        await interaction.response.send_message("🚫 **Ошибка доступа:** У вас нет прав для использования этой команды.", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    try:
        # Создание эмбеда
        embed = discord.Embed(
            title=title,
            description=description if description else None,
            color=int(color, 16)
        )
        
        # Автор (с иконкой-аватаркой)
        if author_name:
            embed.set_author(
                name=author_name,
                icon_url=author_icon if author_icon else None
            )
        
        # Изображение (баннер внизу)
        if image:
            embed.set_image(url=image)
        
        # Миниатюра (справа сверху)
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        
        # Подвал (footer)
        if footer:
            embed.set_footer(
                text=footer,
                icon_url=footer_icon if footer_icon else None
            )
        
        # Отправка эмбеда в выбранный канал
        await channel.send(embed=embed)
        
        # Подтверждение
        await interaction.followup.send(
            f"✅ **Эмбед успешно создан!**\n"
            f"📬 Отправлен в канал: {channel.mention}\n"
            f"📝 Заголовок: **{title}**",
            ephemeral=True
        )
        
    except Exception as e:
        await interaction.followup.send(
            f"❌ **Ошибка при создании эмбеда:**\n`{e}`\n\n"
            f"Проверьте корректность URL изображений.",
            ephemeral=True
        )

@create_embed.error
async def create_embed_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(
            "🚫 **Ошибка:** У вас нет прав администратора для использования этой команды.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"❌ **Произошла ошибка:** {error}",
            ephemeral=True
        )

# ============================================
# 🚀 ЗАПУСК БОТА
# ============================================

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
