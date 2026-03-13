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

# ================= КОНФИГУРАЦИЯ ID (Запомнено на будущее) =================
OWNER_ID = 314805583788244993

ADMIN_ROLE_IDS = [
    1482021644703760607, 1482021651867631746, 1482021652488524058,
    1482021653109018734, 1482021654082093076, 1482021656636428411,
    1482021656649269310
]

# Роли для кнопок (Косметические)
COSMETIC_ROLES = {
    "knife": 1482026329368170706,   # 🔪
    "science": 1482026329435148421, # 🧪
    "ghost": 1482026850564968488,   # 👻
    "radio": 1482026851479195689,   # ☢️
    "moon": 1482026853085610117     # 🌑
}

# ============================================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Необходимо для управления ролями

bot = commands.Bot(command_prefix='!', intents=intents)

# ================= КЛАСС ВИДА (КНОПКИ) =================
class RoleSelectView(View):
    def __init__(self):
        super().__init__(timeout=None)  # timeout=None делает кнопки вечными (persistent)

        # Добавляем кнопки для косметических ролей
        self.add_item(RoleButton(label="🔪 Агрессия", role_id=COSMETIC_ROLES["knife"], emoji="🔪", style=discord.ButtonStyle.danger))
        self.add_item(RoleButton(label="🧪 Наука", role_id=COSMETIC_ROLES["science"], emoji="🧪", style=discord.ButtonStyle.blurple))
        self.add_item(RoleButton(label="👻 Призрак", role_id=COSMETIC_ROLES["ghost"], emoji="👻", style=discord.ButtonStyle.gray))
        self.add_item(RoleButton(label="☢️ Мутант", role_id=COSMETIC_ROLES["radio"], emoji="☢️", style=discord.ButtonStyle.green))
        self.add_item(RoleButton(label="🌑 Инкогнито", role_id=COSMETIC_ROLES["moon"], emoji="🌑", style=discord.ButtonStyle.gray))

class RoleButton(Button):
    def __init__(self, label, role_id, emoji, style):
        super().__init__(label=label, emoji=emoji, style=style, custom_id=f"role_{role_id}")
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        role = guild.get_role(self.role_id)

        if not role:
            await interaction.response.send_message("❌ Ошибка: Роль не найдена на сервере.", ephemeral=True)
            return

        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"✅ Роль {role.name} удалена.", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"✅ Роль {role.name} выдана.", ephemeral=True)

# ================= СОБЫТИЯ БОТА =================

@bot.event
async def on_ready():
    # Регистрируем постоянный вид (чтобы кнопки работали после перезагрузки)
    bot.add_view(RoleSelectView())

    # Установка статуса
    status = discord.Status.dnd
    activity = discord.Activity(name="За сервером Безумия", type=discord.ActivityType.watching)
    await bot.change_presence(status=status, activity=activity)
    
    print(f'Бот {bot.user.name} запущен!')
    print(f'Владелец ID: {OWNER_ID}')
    print(f'Админ ролей загружено: {len(ADMIN_ROLE_IDS)}')

@bot.command(name='roles')
async def roles_command(ctx):
    # Удаляем сообщение с командой
    try:
        await ctx.message.delete()
    except discord.errors.Forbidden:
        pass # Если нет прав на удаление, просто продолжаем

    # Формируем описание эмбеда
    # Заменяем ID на упоминания ролей для красоты, если они существуют, иначе оставляем текст
    def format_role_line(role_id, name, desc):
        return f"<@&{role_id}> - {desc}"

    embed = discord.Embed(
        title="🏥 Роли сервера Безумие - Реанимация",
        description="Выберите косметические роли кнопками ниже.",
        color=discord.Color.red()
    )

    # Текст описания согласно запросу
    roles_text = (
        "**👑 АДМИНИСТРАЦИЯ (Высший совет)**\n"
        f"{format_role_line(1482021644703760607, '', '🩸 Глав Врач (Владелец сервера, финальное слово во всех решениях.)')}\n"
        f"{format_role_line(1482021651867631746, '', '🧬 Зам. Глав врача (Заместитель, координирует работу всех отделов.)')}\n"
        f"{format_role_line(1482021652488524058, '', '⚕️ Старший Ординатор (Контроль модерации и тех. поддержки, решение конфликтов.)')}\n\n"
        
        "**🛡 ПЕРСОНАЛ КЛИНИКИ (Модерация и Стафф)**\n"
        f"{format_role_line(1482021653109018734, '', 'Модератор чатов: следит за правилами, выдаёт предупреждения.)')}\n"
        f"{format_role_line(1482021654082093076, '', 'Помощник модератора, встречает новичков, отвечает на простые вопросы.)')}\n"
        f"{format_role_line(1482021656636428411, '', 'Выдаёт роли, помогает с верификацией и доступом к каналам.)')}\n"
        f"{format_role_line(1482021656649269310, '', 'Техническая поддержка: помощь с запуском, баги, аккаунты.)')}\n\n"

        "**🧪 РАЗРАБОТЧИКИ (Создатели проекта)**\n"
        f"{format_role_line(1482021658708541570, '', 'Ведущий разработчик, принимает решения по коду и механикам.)')}\n"
        f"{format_role_line(1482021658796752986, '', 'Программист: скрипты, фиксы, оптимизация.)')}\n"
        f"{format_role_line(1482021659878883358, '', 'Визуал: интерфейс, иконки, промо-материалы.)')}\n\n"

        "**🎖 ОСОБЫЕ СТАТУСЫ (Уникальные роли)**\n"
        f"{format_role_line(1482026327216492684, '', 'Топ-игрок сервера, имя известно всем.')}\n"
        f"{format_role_line(1482021673266839583, '', 'Участвует в тестировании сборок, ищет баги.')}\n"
        f"{format_role_line(1482021674378334319, '', 'Представитель дружественного проекта/канала.')}\n"
        f"{format_role_line(1482026325693825025, '', 'Поддержал проект финансово. Бонусы в игре/чате.')}\n"
        f"{format_role_line(1482026326746599575, '', 'Создал популярный фан-арт, гайд или мем')}\n"
        f"{format_role_line(1482021672604405935, '', 'Играл в оригинал до закрытия. Уважение комьюнити.')}\n\n"
        
        "**🎭 КОСМЕТИЧЕСКИЕ РОЛИ (Нажми кнопку)**\n"
        f"{format_role_line(1482026329368170706, '', '🔪 Для любителей агрессивного стиля')}\n"
        f"{format_role_line(1482026329435148421, '', '🧪 Для фанатов лора и науки')}\n"
        f"{format_role_line(1482026850564968488, '', '👻 Нейтральный, таинственный')}\n"
        f"{format_role_line(1482026851479195689, '', '☢️ Кислотно-зелёный, стиль «мутант»')}\n"
        f"{format_role_line(1482026853085610117, '', '🌑 Тёмный, для инкогнито')}\n"
    )

    embed.add_field(name="📋 Список должностей", value=roles_text, inline=False)
    embed.set_footer(text="Безумие - Реанимация | Система ролей")

    # Отправляем эмбед с кнопками
    await ctx.send(embed=embed, view=RoleSelectView())

# Запуск
bot.run(TOKEN)
