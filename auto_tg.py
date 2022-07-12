import requests
import telebot
from bs4 import BeautifulSoup
import unicodedata
import fake_useragent
from telebot import types

bot = telebot.TeleBot('key', parse_mode=None)

@bot.message_handler(commands=['start', 'help'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🔎 Пробить по номерам")
    btn2 = types.KeyboardButton("🚗 Узнать стоимость авто.")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, text='Привет! Выбери действие, которое хочешь сделать.'.format(message.from_user), reply_markup=markup)

@bot.message_handler(content_types=['text'])
def func(message):

    if(message.text == "🔎 Пробить по номерам"):
        msg = bot.reply_to(message, 'Введите серию, номер, регион автомобиля через запятую.\nПример: aaa,777,123')
        bot.register_next_step_handler(msg, input_number)

    elif(message.text == "🚗 Узнать стоимость авто."):
        msg = bot.reply_to(message, 'Введите марку, модель, мин.год, макс.год через запятую.\nПример: ford,focus,2015,2020')
        bot.register_next_step_handler(msg, input_car)

    else:
        bot.send_message(message.chat.id, text='Я не понимаю введенную команду.\n\nВыберите желаемое действие с помощью кнопок снизу.')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("🔎 Пробить по номерам")
        btn2 = types.KeyboardButton("🚗 Узнать мин. стоимость авто.")
        markup.add(btn1, btn2)

def input_car(message):
    car_input = message.text
    car_input_s = car_input.split(',')

    limit_cars = 5
    i = -1

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.116 YaBrowser/22.1.1.1544 Yowser/2.5 Safari/537.36',
        'Accept': '*/*'
    }
    try:
        url = f'https://auto.drom.ru/{car_input_s[0]}/{car_input_s[1]}/?minyear={car_input_s[2]}&maxyear={car_input_s[3]}&ph=1&damaged=2&order=price'

        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')

        all_cars = soup.find_all(class_='css-5l099z ewrty961')
        for car in all_cars:
            i = i + 1
            if i == limit_cars:
                break
            else:
                car_price = car.find_next(class_='css-46itwz e162wx9x0').text
                car_price_clean = unicodedata.normalize('NFKD', car_price)
                car_price_clean = int(car_price_clean.replace('₽', '').replace(' ', ''))
                car_year = car.find_next(class_='css-17lk78h e3f4v4l2').text
                car_link = car.get('href')
                bot.send_message(message.chat.id, f'{car_year} сейчас продаётся за {car_price_clean}₽.\nПодробнее: {car_link}\n')

    except AttributeError:
        bot.send_message(message.chat.id, 'Произошла ошибка, попробуйте ещё раз.')

def input_number(message):
    number_input = message.text
    number_list = number_input.split(',')

    session = requests.Session()
    user = fake_useragent.UserAgent().random
    headers = {'user-agent': user}
    data = {'tokens[series]': number_list[0], 'tokens[number]': number_list[1], 'tokens[region_code]': number_list[2]}
    r_link_nubmer = session.post('https://www.nomerogram.ru/search/', data=data, headers=headers).json()

    link_number = r_link_nubmer['redirectUrl']

    r_car_nubmer = requests.get(link_number, headers=headers)
    soup = BeautifulSoup(r_car_nubmer.text, 'lxml')
    try:
        car_name = soup.find(class_='car_info__title').text
        bot.send_message(message.chat.id, car_name)
        spec = soup.find(class_='car_info__specifications desktop')
        bot.send_message(message.chat.id, f'{spec.text}\nУзнать подробнее про авто: {link_number}')
    except AttributeError:
        bot.send_message(message.chat.id, f'Данный автомобиль не найден, либо информация недостоверная.\n{link_number}')

bot.infinity_polling()
