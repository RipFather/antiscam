import telebot
import datetime

def get_user(user: telebot.types.User) -> str:
    if not user: 
        return "Неизвестный"
    name = user.first_name
    if user.last_name: 
        name += f" {user.last_name}"
    return f'<a href="tg://user?id={user.id}">{name}</a> (<code>{user.id}</code>)'

def send_log(message_text):
    try:
        telebot.TeleBot('7892869644:AAFTRPKR8fvYthxbQb4G8jm0xXxhUW2UeZw').send_message(
            chat_id=-1002554970644,
            text=message_text,
            parse_mode='HTML',
            disable_web_page_preview=True,
            disable_notification=True
        )
    except Exception as e:
        print(e)

def log(admin_user, added_id):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    admin_info = get_user(admin_user)
    log_message = (
        f"🔴 <b>Добавлен ID в SCAM базу</b>\n\n"
        f"<b>ID:</b> <code>{added_id}</code>\n"
        f"<b>Админ:</b> {admin_info}\n"
        f"<b>Время:</b> {timestamp}"
    )
    send_log(log_message)