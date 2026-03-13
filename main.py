import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем токен
TOKEN = os.getenv('DISCORD_TOKEN')

# Проверка на наличие токена
if not TOKEN:
    print("Ошибка: Токен не найден в файле .env!")
    exit()

# Настройки интентов (разрешений)
intents = discord.Intents.default()
intents.message_content = True

# Создаем клиента
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    # Устанавливаем статус "Не беспокоить" (DND)
    status = discord.Status.dnd
    
    # Устанавливаем активность "Смотрит за сервером Безумия"
    activity = discord.Activity(
        name="За сервером Безумия", 
        type=discord.ActivityType.watching
    )
    
    await bot.change_presence(status=status, activity=activity)
    
    print(f'Бот {bot.user.name} успешно запущен!')
    print('--------------------------------')

# Запуск бота
bot.run(TOKEN)
