
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests

# Función para manejar los mensajes
def handle_message(update: Update, context: CallbackContext) -> None:
    message = update.message.text
    chat_id = update.message.chat_id

    # Enviar el mensaje al orquestador
    try:
        response = requests.post('http://localhost:5000/derek', data={
            'input': message,
            'user_id': chat_id // Usar el chat_id como user_id
        })
        update.message.reply_text(response.json())
    except Exception as e:
        print(f"Error sending message to orchestrator: {e}")
        update.message.reply_text("Error al procesar el mensaje.")


def main() -> None:
    # Reemplazar con tu token de Telegram
    updater = Updater("YOUR_TELEGRAM_TOKEN")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
