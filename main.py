import discord
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
import os

# Загружаем переменные окружения
load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

if not TOKEN:
    print("Ошибка: Токен не найден в файле .env!")
    exit()

# ================= КОНФИГУРАЦИЯ ID =================
OWNER_ID = 314805583788244993

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

bot = commands.Bot(command_prefix='!', intents=intents)

# ================= ПРОВЕРКА ПРАВ =================
def is_admin_or_owner():
    """Проверяет, является ли пользователь владельцем или имеет админ-роль"""
    async def predicate(ctx):
        # Проверка на владельца
        if ctx.author.id == OWNER_ID:
            return True
        # Проверка на админ-роли
        if hasattr(ctx.author, 'roles'):
            user_role_ids = [role.id for role in ctx.author.roles]
            if any(role_id in user_role_ids for role_id in ADMIN_ROLE_IDS):
                return True
        return False
    return commands.check(predicate)

# ================= КНОПКИ =================
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
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"✅ Роль **{role.name}** выдана.", ephemeral=True)

# ================= СОБЫТИЯ =================

@bot.event
async def on_ready():
    bot.add_view(RoleSelectView())
    status = discord.Status.dnd
    activity = discord.Activity(name="За сервером Безумия", type=discord.ActivityType.watching)
    await bot.change_presence(status=status, activity=activity)
    print(f'Бот {bot.user.name} запущен!')

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
async def say_command(ctx, *, message: str):
    """
    Бот отправляет сообщение от своего имени.
    Использование: !say Текст сообщения
    """
    # Удаляем сообщение пользователя (чтобы не спамить и скрыть команду)
    try:
        await ctx.message.delete()
    except discord.errors.Forbidden:
        pass
    
    # Отправляем сообщение от имени бота
    await ctx.send(message)

# ===================================================

bot.run(TOKEN)
