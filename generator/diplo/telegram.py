# -*- coding: utf-8 -*-
"""
Created on Sun Dec  3 14:14:04 2023

@author: jksls
"""

from email import message
import telebot
from telebot import types
import pandas as pd
import numpy as np
import xlrd
from datetime import datetime as dt
import glob
import os
import time

bot = telebot.TeleBot('6792996021:AAFA6IMuRfHQonrYzw3u6hsDqCvH4zJp8m4')


@bot.message_handler(commands=['start'])
def welcome(message):
    user_id = str(message.from_user.id)
    user_name = str(message.from_user.first_name)

    # xls = pd.ExcelFile(f'Tasks_{id}.xlsx')
    # xls_sheets = xls.sheet_names

    current_directory = os.path.dirname(os.path.abspath(__file__))
    excel_files = [file for file in os.listdir(current_directory) if file.endswith('.xlsx')]

    if str('Tasks_' + str(user_id) + '.xlsx') in excel_files:
        bot.reply_to(message, f"Привет, {user_name}! Работаем с вашим списком задач.")
    else:
        bot.reply_to(message, f"Привет, {user_name}! Новый список задач создан.")
        df = pd.DataFrame(columns=['tasks', 'deadline', 'done'])
        with pd.ExcelWriter(f'Tasks_{user_id}.xlsx', mode='w') as writer:
            df.to_excel(writer, sheet_name=str(user_name), index=False)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    but1 = types.KeyboardButton('Tasks')
    but2 = types.KeyboardButton('Report')
    but3 = types.KeyboardButton('Meetings')
    markup.add(but1, but2, but3)

    bot.send_message(message.chat.id,
                     f"{message.from_user.first_name} \n Программа работает и сейчас период отчетности или же встреч",
                     reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def menu(message):
    if message.chat.type == 'private':
        if message.text == 'Tasks':
            name = str(message.from_user.first_name)
            id = str(message.from_user.id)
            inMurkup = types.InlineKeyboardMarkup(row_width=1)
            but1 = types.InlineKeyboardButton('My Tasks', callback_data='Tasks')
            but2 = types.InlineKeyboardButton('Add Task', callback_data='Adding')
            but3 = types.InlineKeyboardButton('Done Tasks', callback_data='done')
            # but4 = types.KeyboardButton('')
            # but5 = types.KeyboardButton('Exit')
            inMurkup.add(but1, but2, but3)  # ,but4,but5)
            bot.send_message(message.chat.id, "Выберите действие", reply_markup=inMurkup)
        elif message.text == 'Report':
            name = str(message.from_user.first_name)
            id = str(message.from_user.id)
            df = pd.read_excel(f'Tasks_{id}.xlsx', sheet_name=name)
            tasks = np.array(df['tasks'])
            done = np.array(df['done'])
            done = done[done != '24.07.2022']
            bot.send_message(message.chat.id,
                             f'Отчетность: \n Количество поставленных задач : {len(tasks)} \n Количество завершенных задач : {len(done)} \n Количество незавершенных задач : {len(tasks) - len(done)}')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:

            name = str(call.from_user.first_name)
            id = str(call.from_user.id)
            df = pd.read_excel(f'Tasks_{str(id)}.xlsx', sheet_name=name)
            if call.data == 'Tasks':
                bot.send_message(call.message.chat.id, f'Выберите действие \n {df}')

            elif call.data == 'Adding':
                bot.send_message(call.message.chat.id, 'Впишите в данном формате [задание] - [дедлайн]')

                @bot.message_handler(func=lambda message: True)
                def handle_user_input(message):
                    if message.chat.type == 'private':
                        id = str(message.from_user.id)
                        name = str(message.from_user.first_name)
                        inp = message.text.strip()
                        inp = inp.split('-')
                        bot.send_message(call.message.chat.id, f"Received input: {inp}")
                        new_row = pd.DataFrame({'tasks': [inp[0]], 'deadline': [float(inp[1])], 'done': ['24.07.2022']})
                        df = pd.read_excel(f'Tasks_{id}.xlsx', sheet_name=name)
                        df = pd.concat([df, new_row], ignore_index=True)
                        with pd.ExcelWriter(f'Tasks_{id}.xlsx', mode='w') as writer:
                            df.to_excel(writer, sheet_name=name, index=False)
                        bot.send_message(call.message.chat.id, 'Dataset updated!')

                bot.register_next_step_handler(call.message, handle_user_input)

            elif call.data == 'done':

                df = pd.read_excel(f'Tasks_{id}.xlsx', sheet_name=id)
                bot.send_message(call.message.chat.id, f'Сколько задач было выполнено? \n {df}')

                @bot.message_handler(func=lambda message: True)
                def handle_user_input(message):
                    if message.chat.type == 'private':
                        name = message.from_user.first_name
                        id = message.from_user.id
                        bot.send_message(call.message.chat.id, 'Укажите строку задачи, которая была выполнена?')
                        done = int(message.text.strip())
                        df = pd.read_excel(f'Tasks_{id}.xlsx', sheet_name=id)
                        done_np = np.array(df['done'])
                        done_np[int(done) - 1] = dt.today().strftime('%d.%m.%y')
                        df['done'] = done_np
                        with pd.ExcelWriter(f'Tasks_{id}.xlsx', mode='w') as writer:
                            df.to_excel(writer, sheet_name=id, index=False)

                bot.register_next_step_handler(call.message, handle_user_input)
    except Exception as e:
        print(repr(e))


while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(repr(e))
        time.sleep(5)
