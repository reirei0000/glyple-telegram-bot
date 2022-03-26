import fire
import logging
import pickle
import tempfile
import time
import random
from PIL import Image
from telegram.ext import Updater, CommandHandler

from draw import draw_glyph, draw_bg
from data import glyphs


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

user_data = {}


def save_user_data():
    global user_data
    with open('user_data.bin', 'wb') as fp:
        pickle.dump(user_data, fp)


def _reset(chat_id):
    global user_data
    user_data[chat_id] = {
        'question': glyphs[random.randint(0, len(glyphs))],
        'answers': '',
        'matches': '',
        'count': 6
    }
    save_user_data()
    logger.info(user_data[chat_id])


def reset(update, context):
    chat_id = update.effective_chat.id
    _reset(chat_id)

    im = Image.new('RGBA', (256, 256))
    draw_bg(im, (0, 0))

    with tempfile.TemporaryFile() as fp:
        fp.seek(0)
        im.save(fp, 'png')
        fp.seek(0)
        context.bot.send_photo(
            chat_id=chat_id, caption='Please /glyple glyphname.', photo=fp)


def glyphmask(qpoints, apoints):
    logger.info(qpoints)
    logger.info(apoints)
    points = ''

    for i in range(0, len(apoints), 2):
        a1 = apoints[i]
        a2 = apoints[i + 1]
        for j in range(0, len(qpoints), 2):
            q1 = qpoints[j]
            q2 = qpoints[j + 1]
            if (a1 == q1 and a2 == q2) or (a1 == q2 and a2 == q1):
                points += f'{a1}{a2}'

    return points


def answer(update, context):
    global user_data
    chat_id = update.effective_chat.id
    text = update.message.text
    data = user_data[chat_id]
    logger.info(data)

    if ' ' in text:
        answer = text.split()[1]
    else:
        answer = text

    logger.info(answer)
    glyph = next(filter(lambda g: answer.lower() in g[1], glyphs), None)
    if data['count'] <= 0:
        update.message.reply_text('Expoit!\nPlease /reset')
        return
    elif glyph is None:
        update.message.reply_text('No such glyph.')
        return

    data['count'] -= 1

    points = glyphmask(data['question'][0], glyph[0])
    data['matches'] += points
    data['answers'] += glyph[0]
    save_user_data()
    logger.info(glyph)
    logger.info(points)

    im = Image.new('RGBA', (256, 256))
    draw_bg(im, (0, 0))
    draw_glyph(im, (0, 0), (0xca, 0xb5, 0x58, 255), data['answers'])
    draw_glyph(im, (0, 0), (0x6a, 0xac, 0x64, 255), data['matches'])

    message = ''
    if data['question'][0] == glyph[0]:
        message = '🎉\nCongraturation. Reset the game.'

    with tempfile.TemporaryFile() as fp:
        fp.seek(0)
        im.save(fp, 'png')
        fp.seek(0)
        time.sleep(1)
        context.bot.send_photo(chat_id=chat_id, caption=message, photo=fp)

    if message != '':
        _reset(chat_id)
    elif data['count'] <= 0:
        message = 'Expoit!\nPlease /reset'


def bot(telegram_api_token):
    global user_data
    try:
        with open('user_data.bin', 'rb') as fp:
            user_data = pickle.load(fp)
            logger.info(user_data)
    except Exception as e:
        logger.error(e)
        user_data = {}

    updater = Updater(telegram_api_token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('glyple', answer))
    dispatcher.add_handler(CommandHandler('start', reset))
    dispatcher.add_handler(CommandHandler('reset', reset))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    fire.Fire(bot)
