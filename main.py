import os
import discord
from discord.ext import commands
import asyncio
from dotenv import load_dotenv

# ============================================
# 🔐 ЗАГРУЗКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ
# ============================================

load_dotenv()  # Загрузка переменных из .env файла

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Проверка токена перед запуском
if not DISCORD_TOKEN:
    print("❌ ОШИБКА: DISCORD_TOKEN не найден в .env файле!")
    print("   Проверьте файл .env и убедитесь, что токен указан правильно.")
    exit(1)

# ============================================
# 🛡️ КОНФИГУРАЦИЯ ПРАВ ДОСТУПА
# ============================================

# ID владельца бота
OWNER_ID = 314805583788244993

# ID админ-ролей (любой с такой ролью получает доступ к командам)
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
intents.members = True          # Доступ к списку участников (обязательно для !addrole)
intents.message_content = True  # Доступ к тексту сообщений (обязательно для команд)

bot = commands.Bot(command_prefix='!', intents=intents)

# ============================================
# 🛡️ ПРОВЕРКА ПРАВ ДОСТУПА
# ============================================

async def is_authorized(ctx):
    """Проверяет, есть ли у пользователя права на использование команд"""
    # Проверка на владельца
    if ctx.author.id == OWNER_ID:
        return True
    
    # Проверка на наличие админ-роли
    if hasattr(ctx, 'guild') and ctx.guild:
        for role_id in ADMIN_ROLE_IDS:
            role = ctx.guild.get_role(role_id)
            if role and role in ctx.author.roles:
                return True
    
    return False

# ============================================
# 🤖 СОБЫТИЯ БОТА
# ============================================

@bot.event
async def on_ready():
    """Событие при запуске бота"""
    
    # 🟣 Установка статуса "Не беспокоить" и активности
    await bot.change_presence(
        status=discord.Status.dnd,  # Status.dnd = Do Not Disturb (Не беспокоить)
        activity=discord.Activity(
            type=discord.ActivityType.watching,  # Тип активности: Смотрит
            name="за Модерирует сервер"          # Текст активности
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
    print('   !help - Показать справку')
    print('   !ping - Проверка задержки')
    print('   !info - Информация о боте')
    print('----------------------------------')

@bot.event
async def on_command_error(ctx, error):
    """Обработка ошибок команд"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ **Ошибка:** Команда не найдена. Используйте `!help`")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ **Ошибка:** Укажите все необходимые аргументы.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ **Подождите:** Команда на перезарядке. Попробуйте через {error.retry_after:.1f} сек.")
    else:
        await ctx.send(f"❌ **Произошла ошибка:** {error}")

# ============================================
# ⚔️ КОМАНДЫ БОТА
# ============================================

@bot.command(name='addrole')
@commands.cooldown(1, 60, commands.BucketType.default)  # Лимит: 1 раз в 60 секунд
async def add_role_to_all(ctx, role_id: int):
    """
    Выдает указанную роль всем участникам сервера.
    Доступно только владельцу и обладателям админ-ролей.
    """
    
    # 1. Проверка прав доступа
    if not await is_authorized(ctx):
        await ctx.send("🚫 **Ошибка доступа:** У вас нет прав для использования этой команды.")
        return

    # 2. Поиск роли
    try:
        role = ctx.guild.get_role(role_id)
        if role is None:
            await ctx.send("❌ **Ошибка:** Роль с таким ID не найдена на этом сервере.")
            return
        
        # Проверка иерархии (бот не может выдать роль выше себя)
        if role.position >= ctx.guild.me.top_role.position:
            await ctx.send("❌ **Ошибка:** Эта роль находится выше моей высшей роли. Поднимите меня в списке ролей.")
            return

    except Exception as e:
        await ctx.send(f"❌ **Ошибка при поиске роли:** {e}")
        return

    # 3. Процесс выдачи
    msg = await ctx.send(f"⚙️ **Запуск процесса...**\nНачинаю выдачу роли **{role.name}** всем участникам.")
    
    success_count = 0
    fail_count = 0
    skipped_count = 0
    total_members = len(ctx.guild.members)

    await ctx.send(f"ℹ️ Всего участников: {total_members}. Это может занять время...")

    for member in ctx.guild.members:
        try:
            # Пропускаем ботов
            if member.bot:
                skipped_count += 1
                continue
            
            # Пропускаем тех, у кого роль уже есть
            if role in member.roles:
                skipped_count += 1
                continue
            
            await member.add_roles(role, reason=f"Массовая выдача по команде {ctx.author.name}")
            success_count += 1
            
            # Небольшая задержка, чтобы не упереться в лимиты API (Rate Limits)
            await asyncio.sleep(0.1) 
            
        except discord.Forbidden:
            fail_count += 1
        except Exception:
            fail_count += 1

    # 4. Отчет
    await msg.edit(content=(
        f"✅ **Готово!**\n"
        f"🎭 Роль: **{role.name}**\n"
        f"👥 Всего участников: {total_members}\n"
        f"🟢 Успешно выдано: {success_count}\n"
        f"⚪ Пропущено (уже есть/боты): {skipped_count}\n"
        f"🔴 Ошибки: {fail_count}"
    ))

@bot.command(name='help')
async def help_command(ctx):
    """Показывает справку по командам"""
    
    if not await is_authorized(ctx):
        await ctx.send("🚫 **Ошибка доступа:** У вас нет прав для просмотра этой справки.")
        return
    
    embed = discord.Embed(
        title="📜 Справка по командам",
        description="Список доступных команд для администрации",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="!addrole <ID_роли>",
        value="Выдает указанную роль всем участникам сервера.\n*Кулдаун: 60 секунд*",
        inline=False
    )
    embed.add_field(
        name="!help",
        value="Показать эту справку",
        inline=False
    )
    embed.add_field(
        name="!ping",
        value="Проверка задержки бота",
        inline=False
    )
    embed.add_field(
        name="!info",
        value="Информация о боте и статусе",
        inline=False
    )
    embed.set_footer(text=f"Запрос от {ctx.author.name}")
    
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping_command(ctx):
    """Проверка работоспособности бота"""
    await ctx.send(f"🏓 Понг! Задержка: {round(bot.latency * 1000)}ms")

@bot.command(name='info')
async def info_command(ctx):
    """Показывает информацию о боте и правах"""
    
    embed = discord.Embed(
        title="ℹ️ Информация о боте",
        description="Статус и конфигурация",
        color=discord.Color.red()  # Красный цвет под статус DND
    )
    embed.add_field(
        name="🤖 Бот",
        value=f"{bot.user.name}",
        inline=True
    )
    embed.add_field(
        name="🛡️ Владелец",
        value=f"ID: `{OWNER_ID}`",
        inline=True
    )
    embed.add_field(
        name="🔑 Админ-ролей",
        value=f"{len(ADMIN_ROLE_IDS)}",
        inline=True
    )
    embed.add_field(
        name="🟣 Статус",
        value="Не беспокоить (DND)",
        inline=True
    )
    embed.add_field(
        name="👁️ Активность",
        value="Смотрит за Модерирует сервер",
        inline=True
    )
    embed.add_field(
        name="🔗 Серверов",
        value=f"{len(bot.guilds)}",
        inline=True
    )
    embed.set_footer(text=f"Запрос от {ctx.author.name}")
    
    await ctx.send(embed=embed)

# ============================================
# 🚀 ЗАПУСК БОТА
# ============================================

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
