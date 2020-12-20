import logging
from datetime import datetime

import mysql.connector
from aiogram import Bot, Dispatcher, executor, types

# import telegrambot1
mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="root",
    database="maxtrack",

)
# Bot token that is given by FatherBot
API_TOKEN = '1301774278:AAGU_ol-YWwIbUfsyOyYDd_LFo6xOReHHlQ'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

time = datetime.now()

# Message that wiil reply when you start bot
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply(f"Hi! Here you can check car status, put at least 5 last digits of your imei")


@dp.message_handler()
async def echo(message: types.Message):
    input_msg = message.text
    if input_msg.isdigit():
        # Giving detailed information if you write full IMEI
        if len(input_msg) == 15:
            mycursor = mydb.cursor()
            # decode if there garbage words
            mycursor.execute("SET NAMES cp1251;")
            imei1 = f"%{input_msg}%"
            # Query for taking detailed information should be optimized
            sql1 = f"""SELECT u.id, u.imei, u.name, u.number, u.sms_number,
                (SELECT cs.time FROM max_car_statuses cs WHERE cs.id = u.id) AS TIME,
                (SELECT cs.sat FROM max_car_statuses cs WHERE cs.id = u.id) AS sat,
                (SELECT cs.longitude FROM max_car_statuses cs WHERE cs.id = u.id) AS longitude,
                (SELECT cs.latitude FROM max_car_statuses cs WHERE cs.id = u.id) AS latitude,
                (SELECT cs.additional FROM max_car_statuses cs WHERE cs.id = u.id) AS additional
                FROM max_units u 
                WHERE u.imei LIKE '{imei1}' limit 10 """

            mycursor.execute(sql1)
            myresult = mycursor.fetchall()
            # loop for Imei that can be repeated
            if myresult:
                for temp, x1 in enumerate(myresult):
                    # print(temp, x1)
                    if temp > 10:
                        break
                        # send message back to user in telegram
                    await bot.send_message(message.chat.id,
                                           f" {temp + 1}) imei: {x1[1]}\nname: {x1[2]}\nnumber: {x1[3]} "
                                           f"\nobject number {x1[4]} "
                                           f" \ntime: {x1[5]} \nnumber of satellite {x1[6]} \nlongitude "
                                           f"{x1[7]} \nlatitude {x1[8]}\n {x1[9]}")
            # send message if It could not find Imei
            else:
                await message.reply(f"No such Imei have found!")
                # Giving information of car if user write part of imei at least 5 now
        else:
            if len(input_msg) >= 5:
                mycursor1 = mydb.cursor()
                mycursor1.execute("SET NAMES cp1251;")
                imei1 = f"%{input_msg}%"
                # query for taking some information
                sql1 = f"""SELECT u.id, u.imei, u.name, u.number, 
                (SELECT cs.time FROM max_car_statuses cs WHERE cs.id = u.id) AS time FROM max_units u 
                WHERE u.imei LIKE '{imei1}' limit 10; """
                mycursor1.execute(sql1)
                x = mycursor1.fetchall()
                # print(x)

                if x:
                    for i in range(len(x)):
                        if x[i][-1] is None:
                            # send message if only in max_units data is correct

                            await bot.send_message(message.chat.id,
                                                   f"No new data found!\n"
                                                   f"imei: {x[i][1]} \nname: {x[i][2]}\nnumber:{x[i][3]}")
                            continue
                            # send message if there are no problems with imei
                        difference = time - x[i][4]
                        # print(difference)
                        days = difference.total_seconds() // 60 ** 2 // 24
                        hours = difference.total_seconds() // 60 ** 2 % 24
                        minutes = difference.total_seconds() //60 % 60

                        await bot.send_message(message.chat.id,

                                               f"imei: {x[i][1]}\n"
                                               f"name: {x[i][2]}\nnumber: {x[i][3]}\ntime: {x[i][4]}\n"
                                               f"last signal was {int(days)} days {int(hours)}"
                                               f" hours {int(minutes)} minutes ago")



                # If there are no information about Imei at all
                else:
                    await message.reply(f"No such Imei have found!")
            # if Imei is less than 5 digits write this
            else:
                await message.reply(f"Imei length is less than you need!")
    else:
        await message.reply(f"User input is not correct. Please write imei")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
