import json
import telebot
from telebot import types
import os
import logs
import time

from service import initialize_telethon, getids
initialize_telethon()

admins = [773159330, 5464285224, 2078087671]
API_TOKEN = '7892869644:AAFTRPKR8fvYthxbQb4G8jm0xXxhUW2UeZw'
bot = telebot.TeleBot(API_TOKEN)

scam_file = 'scam.json'
good_file = 'good.json'

def load_scam():
    with open(scam_file, 'r') as file:
        return json.load(file)
def load_good():
    with open(good_file, 'r') as file:
        return json.load(file)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"👋 Привет! Я бот проверки скамеров\nСейчас в базе {len(load_scam())} скамеров!\n\n✍ Просто отправь ID/Username для проверки\n\n<blockquote>Владелец:\n@RipFather\nАдмин:\n@Bomb4296</blockquote>", parse_mode='HTML')
    
@bot.message_handler(commands=['send'])
def handle_send_command(message):
    if message.from_user.id not in admins:
        bot.reply_to(message, "⛔ У вас нет прав для использования этой команды")
        return

    command_parts = message.text.split(' ', 2)

    if len(command_parts) != 3:
        bot.reply_to(message, "⚠️ Неверный формат команды\n"
            "Используйте: `/send <ID_пользователя> <текст_сообщения>`\n"
            "Пример: `/send 123456789 идиот`",
            parse_mode="Markdown")
        return

    user_id = command_parts[1]
    send_message = command_parts[2].strip()

    try:
        user_id = int(user_id)
    except ValueError:
        bot.reply_to(message, f"⚠️ Неверный ID пользователя: '{user_id}'. ID должен быть числом")
        return

    if not send_message:
        bot.reply_to(message, "⚠️ Текст сообщения не может быть пустым")
        return

    try:
        bot.send_message(chat_id=user_id, text=f"✉ Сообщение от админа @{message.from_user.username}:\n\n{send_message}")
        bot.reply_to(message, f"✅ Сообщение успешно отправлено пользователю `{user_id}`", parse_mode="Markdown")

    except Exception:
        pass

@bot.message_handler(commands=['scam'])
def handle_scam_command(message):
    prompt_msg = bot.reply_to(message,
        "➡️ Пожалуйста, отправьте *следующим сообщением* жалобу на пользователя\n\nНеобходимо указать ID/Username пользователя и дать доказательства в виде скриншотов/видеозаписи", parse_mode="Markdown")

    bot.register_next_step_handler(prompt_msg, process_forward_message)

def process_forward_message(message):
    user = message.from_user
    chat_id = message.chat.id
    message_id_to_forward = message.message_id

    forward_success_count = 0
    for admin_id in admins:
        try:
            intro_text = f"🚨 Новая жалоба от `{user.id}`\n\n"
            bot.send_message(admin_id, intro_text, parse_mode="Markdown")
            bot.forward_message(chat_id=admin_id,
                                from_chat_id=chat_id,
                                message_id=message_id_to_forward)
            forward_success_count += 1
        except Exception as e:
            print(e)
            bot.reply_to(message, f"⚠️ Произошла ошибка:\n\n`{e}`", parse_mode="Markdown")
            return

    if forward_success_count > 0:
        bot.reply_to(message, f"✅ Ваша жалоба отправлена и находится на рассмотрении. Спасибо!")
    else:
        bot.reply_to(message, "⚠️ Не удалось переслать ваше сообщение ни одному администратору")



@bot.message_handler(commands=['scamadd'])
def scamadd(message):
    if message.from_user.id not in admins:
        bot.reply_to(message, "⛔ У вас нет прав для использования этой команды")
        return

    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Идиот", parse_mode='Markdown')
        return

    try:
        add_id = int(parts[1])
    except ValueError:
        bot.reply_to(message, "Неверный формат ID")
        return

    scam_list = []
    try:
        if os.path.exists(scam_file):
            with open(scam_file, 'r', encoding='utf-8') as file:
                content = file.read()
                if content:
                    scam_list = json.loads(content)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Ошибка загрузки {scam_file} в /scamadd: {e}")
        bot.reply_to(message, f"⚠️ Произошла ошибка при чтении базы скамеров\nID `{add_id}` не добавлен", parse_mode='Markdown')
        return

    if add_id in scam_list:
        bot.reply_to(message, f"⚠️ ID `{add_id}` уже есть в базе скамеров", parse_mode='Markdown')
    else:
        scam_list.append(add_id)
        try:
            with open(scam_file, 'w', encoding='utf-8') as file:
                json.dump(scam_list, file, indent=4, ensure_ascii=False)
            bot.reply_to(message, f"✅ ID `{add_id}` успешно добавлен в базу скамеров", parse_mode='Markdown')
            logs.log(message.from_user, add_id)
        except Exception as e:
            print(f"Ошибка при сохранении файла {scam_file}: {e}")
            bot.reply_to(message, f"⚠️ Произошла ошибка при сохранении файла\nID `{add_id}` не добавлен", parse_mode='Markdown')



@bot.inline_handler(lambda query: True)
def query_text(inline_query):
    results = []
    query_text = inline_query.query.strip()

    try:
        if not query_text:
             results.append(types.InlineQueryResultArticle(
                id='1',
                title="введите ID/Username для поиска",
                input_message_content=types.InputTextMessageContent(
                    message_text="Введите ID/Username для поиска!"
                )
            ))
        else:
            if query_text.isdigit() == True:
                userid = int(query_text)
                usershow = f"id: <code>{query_text}</code>"
            else:
                if '@' not in query_text:
                    return
                time.sleep(1.3)
                userid = getids(query_text)
                usershow = query_text
            
            scam = load_scam()
            good = load_good()

            title = "🔎 Поиск"
            description = query_text
            message_text = ""

            if userid in scam:
                title = "🔴 Найден в базе СКАМЕРОВ"
                message_text = (f'🔴 ({usershow})\n\n'
                                f'⚠️ Данный пользователь мошенник. '
                                f'Сделки проводить не рекомендуется\n\n'
                                f'<blockquote>@AntiScamersRobot</blockquote>')
            elif userid in good:
                title = "🟢 Найден в базе НАДЕЖНЫХ"
                message_text = (f'🟢 ({usershow})\n\n'
                                f'✅ Данный пользователь надежный исполнитель. '
                                f'Можно доверять и проводить сделки\n\n'
                                f'<blockquote>@AntiScamersRobot</blockquote>')
            else:
                title = "🟡 Не найден в базе"
                message_text = (f'🟡 ({usershow})\n\n'
                                f'❓Пользователь не найден в базе данных. '
                                f'Рекомендуется проводить сделки через проверенных гарантов\n\n'
                                f'Этот человек мошенник?\nСообщите в боте 👇\n\n'
                                f'<blockquote>@AntiScamersRobot</blockquote>')

            results.append(types.InlineQueryResultArticle(
                id=str(userid),
                title=title,
                description=description,
                input_message_content=types.InputTextMessageContent(
                    message_text=message_text,
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )
            ))

    except ValueError:
        results.append(types.InlineQueryResultArticle(
            id='error',
            title="Неверный формат",
            description="Пожалуйста, введите только числовой ID пользователя",
            input_message_content=types.InputTextMessageContent(
                message_text="⚠️ Пожалуйста, введите корректный числовой ID пользователя для проверки"
            )
        ))
    except Exception as e:
        print(f"Ошибка в inline обработчике: {e}")
        results.append(types.InlineQueryResultArticle(
            id='fatal_error',
            title="Произошла ошибка",
            description="Не удалось обработать ваш запрос",
            input_message_content=types.InputTextMessageContent(
                message_text="⚠️ Произошла внутренняя ошибка"
            )
        ))

    bot.answer_inline_query(inline_query.id, results, cache_time=1)

@bot.message_handler(func=lambda message: True)
def check_number(message):
    if bot.get_chat_member(-1002574590619, message.from_user.id ).status == 'left': 
        bot.reply_to(message, "⚠️ *Вы не подписаны на канал!*\n\nЕдинственным условием использования бота является подписка на канал\n👇👇👇\n\n[Подписаться](t.me/AntiScamersCh)", parse_mode="Markdown", disable_web_page_preview=True)
        return
    try:
        if message.text.isdigit() == True:
            userid = int(message.text)
            usershow = f"id: `{userid}`"
        else:
            if '@' not in message.text:
                bot.reply_to(message, "⚠️ *Пожалуйста введите корректный ID/Username*\n\nЧтобы узнать ID можно воспользоваться [ботом](t.me/username_to_id_bot)", parse_mode='Markdown', disable_web_page_preview=True)
                return
            else:
                time.sleep(1.5)
                userid = getids(message.text)
                usershow = message.text
            
        scam = load_scam()
        good = load_good()

        if userid in scam:
            bot.reply_to(message, f'🔴 ({usershow})\n\n⚠️ Данный пользователь мошенник. Не доверять, сделки проводить не рекомендуется', parse_mode='Markdown')
        elif userid in good:
             bot.reply_to(message, f'🟢 ({usershow})\n\n✅ Данный пользователь надежный исполнитель. Можно доверять и проводить сделки', parse_mode='Markdown')
        else:
            bot.reply_to(message, f'🟡 ({usershow})\n\n❓Пользователь не найден в базе данных. Проводить сделку только через проверенных гарантов\n\nНашли мошенника? - /scam', parse_mode='Markdown')
    except ValueError:
        bot.reply_to(message, "⚠️ *Пожалуйста введите корректный ID/Username*\n\nЧтобы узнать ID можно воспользоваться [ботом](t.me/username_to_id_bot)", parse_mode='Markdown', disable_web_page_preview=True)

while True:
    try:
        bot.polling()
    except Exception as e:
        print(e)