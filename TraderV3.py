

#!pip install python-binance
#!pip install panda
#!pip install ta
from binance.spot import Spot 
import pandas as pd
import ta
import numpy as np
import time 
from scipy.stats import linregress
from colorama import Fore, Back, Style, init
from datetime import datetime
from tabulate import tabulate
from pprint import pprint
import os
import requests
#import winsound
from dotenv import load_dotenv
from datetime import datetime
import pandas_ta 
load_dotenv()
init()
import click
import telegram_send
from telegram.ext import Updater, CommandHandler


client = Spot()
print(client.time())



TRADING = False
TYPE = False 
TARGET = 0
STOP_LOSS = 0
ORDER_TIME = 0
WIN = 0
LOSSES = 0
OLD_PRICE = 0
START_TIME = datetime.now()

#Telegram bot variables
Orders_dataframe = pd.DataFrame([], columns = ['Type of Order', 'Time','Stop-Loss','Target','Status'])
Orders_Status = pd.DataFrame([], columns = ['Pair', 'Time','Stop-Loss','Target','Status'])


sold = True
coin_quantity = 0
euro_quantity = 20

sold_price = 1000000000

print_ma13= 0
print_ma5= 0
print_ma8= 0
slope_print= 0
bol_avg_print = 0
rsi_diff_print = 0
buy_price= 0


pair_moedas = ""
time_interval = ""


TELE_API = os.getenv("TELE_API")
api_key = os.getenv("API_KEY")
api_secret = os.getenv('API_SECRET')
client = Spot(api_key,api_secret)



def getminutedata(Symbol, interval):
    
    response = requests.get("https://api.binance.com/api/v3/klines?symbol="+Symbol+"&interval="+interval)
    #r = requests.get("https://api.binance.com/api/v3/depth",params=dict(symbol=Symbol))    


    
    frame = pd.DataFrame(response.json())
    frame.columns = ['Time','Open','High','Low','Close','Volume',"1","Quote Asset Volume","2","2","3","4"]
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    frame = frame.drop(["1", "2", "3","4"],axis=1)

    
    return frame

def applytechnicals(df):
    df['RSI_Bad'] = ta.momentum.stochrsi_d(df.Close,
                                 window=14,
                                 smooth1 = 3)*100
    df['RSI_Good'] = ta.momentum.stochrsi_k(df.Close,
                                 window=14,
                                 smooth1 = 3)*100
    df['RSI_Diff'] = (ta.momentum.stochrsi_k(df.Close,
                                 window=14,
                                 smooth1 = 3) - ta.momentum.stochrsi_d(df.Close,
                                 window=14,
                                 smooth1 = 3))*100

    df['Bol_H'] = ta.volatility.bollinger_hband(df.Close, window = 20, window_dev = 2)
    df['Bol_L'] = ta.volatility.bollinger_lband(df.Close, window = 20, window_dev = 2)
    df['Bol_AVG'] = ta.volatility.bollinger_mavg(df.Close, window = 20)
    
    df['MA5'] = ta.trend.sma_indicator(df.Close, window = 5)
    df['MA8'] = ta.trend.sma_indicator(df.Close, window = 8)
    df['MA13'] = ta.trend.sma_indicator(df.Close, window = 13)


    df['ST_10_1'] = pandas_ta.supertrend(df.High, df.Low, df.Close, 10, 1)['SUPERT_10_1.0']
    df['ST_11_2'] = pandas_ta.supertrend(df.High, df.Low, df.Close, 11, 2)['SUPERT_11_2.0']
    df['ST_12_3'] = pandas_ta.supertrend(df.High, df.Low, df.Close, 12, 3)['SUPERT_12_3.0']
    df['EMA200'] = ta.trend.ema_indicator(df.Close, 200)
    
    

    #https://stackoverflow.com/questions/44935269/supertrend-code-using-pandas-python
    
    df.dropna(inplace=True)






def output(df, TRADING, interval,going_up):
    
    if df['EMA200'].iloc[-1] > df.Close.iloc[-1]:
        A = Fore.GREEN
    else:
        A = Fore.RED 
        
    if (df['RSI_Good'].iloc[-1] > 80):
        B = Fore.GREEN
    else:
        B = Fore.RED       
    
    if (df['RSI_Bad'].iloc[-1] > 80):
        C = Fore.GREEN
    else:
        C = Fore.RED  
        
    if df['RSI_Diff'].iloc[-1] < 0:
        D = Fore.GREEN
    else:
        D = Fore.RED    
        
    if (df['ST_10_1'].iloc[-1] > df.Close.iloc[-1]):
        E = Fore.GREEN
    else:
        E = Fore.RED   
        
    if (df['ST_11_2'].iloc[-1] > df.Close.iloc[-1]):
        F = Fore.GREEN
    else:
        F = Fore.RED   
        
    if (df['ST_12_3'].iloc[-1] > df.Close.iloc[-1]):
        G = Fore.GREEN
    else:
        G = Fore.RED    
        
        
        
    if df['EMA200'].iloc[-1] < df.Close.iloc[-1]:
        AA = Fore.GREEN
    else:
        AA = Fore.RED 
        
    if (df['RSI_Good'].iloc[-1] < 20):
        BB = Fore.GREEN
    else:
        BB = Fore.RED       
    
    if (df['RSI_Bad'].iloc[-1] < 20):
        CC = Fore.GREEN
    else:
        CC = Fore.RED  
        
    if df['RSI_Diff'].iloc[-1] > 0:
        DD = Fore.GREEN
    else:
        DD = Fore.RED    
        
    if (df['ST_10_1'].iloc[-1] < df.Close.iloc[-1]):
        EE = Fore.GREEN
    else:
        EE = Fore.RED   
        
    if (df['ST_11_2'].iloc[-1] < df.Close.iloc[-1]):
        FF = Fore.GREEN
    else:
        FF = Fore.RED   
        
    if (df['ST_12_3'].iloc[-1] < df.Close.iloc[-1]):
        GG = Fore.GREEN
    else:
        GG = Fore.RED 
    
    click.clear()
    if going_up:
        symbol = "↑"
        Symbol = Fore.GREEN 
    else:
        symbol = "↓"
        Symbol = Fore.RED 
    print(tabulate([["Pair", "Price", "Time Frame" ],[ pair_moedas ,Symbol + str(df.Close.iloc[-1]) + " " + str(symbol) + Style.RESET_ALL, str(interval)]], headers="firstrow", tablefmt="fancy_grid"))  
    print(tabulate([\
    ["Type", "Time","EMA200","RSI_K","RSI_D","RSI_Diff","STrend.10.1","STrend.11.2","STrend.12.3" ],\
    ##- Short apenas disponivel nos USA!
    #    
    #[Fore.CYAN +  "Short" + Style.RESET_ALL, \
    #str(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),\
    #A +  str(df['EMA200'].iloc[-1]) + Style.RESET_ALL, \
    #B +  str(df['RSI_Good'].iloc[-1]) + Style.RESET_ALL, \
    #C +  str(df['RSI_Bad'].iloc[-1]) + Style.RESET_ALL, \
    #D +  str(df['RSI_Diff'].iloc[-1]) + Style.RESET_ALL, \
    #E +  str(df['ST_10_1'].iloc[-1]) + Style.RESET_ALL, \
    #F +  str(df['ST_11_2'].iloc[-1]) + Style.RESET_ALL, \
    #G +  str(df['ST_12_3'].iloc[-1]) + Style.RESET_ALL, \
    #],
    #
    
    
    [Fore.CYAN +  "SPOT - Long" + Style.RESET_ALL, \
    str(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),\
    AA +  str(df['EMA200'].iloc[-1]) + Style.RESET_ALL, \
    BB +  str(df['RSI_Good'].iloc[-1]) + Style.RESET_ALL, \
    CC +  str(df['RSI_Bad'].iloc[-1]) + Style.RESET_ALL, \
    DD +  str(df['RSI_Diff'].iloc[-1]) + Style.RESET_ALL, \
    EE +  str(df['ST_10_1'].iloc[-1]) + Style.RESET_ALL, \
    FF +  str(df['ST_11_2'].iloc[-1]) + Style.RESET_ALL, \
    GG +  str(df['ST_12_3'].iloc[-1]) + Style.RESET_ALL, \
    ]], headers="firstrow", tablefmt="fancy_grid"))  
    
    print(tabulate([\
    ["Win - Loss Ration","Win","Losses"],\
    [  "" , \
    Fore.CYAN + str(WIN) + Style.RESET_ALL,\
    Fore.CYAN +  str(LOSSES) + Style.RESET_ALL, \
    ]], headers="firstrow", tablefmt="fancy_grid"))  
    
    if TRADING:
        if TYPE:
            type_of_order = "Short"
        else:
            type_of_order = "Long"
        print(tabulate([\
        ["Type of Order", "Time","Stop-Loss","Target"],\
        [Fore.CYAN +  type_of_order + Style.RESET_ALL, \
        Fore.CYAN + str(ORDER_TIME) + Style.RESET_ALL,\
        Fore.CYAN +  str(STOP_LOSS) + Style.RESET_ALL, \
        Fore.CYAN +  str(TARGET) + Style.RESET_ALL, \
        ]], headers="firstrow", tablefmt="fancy_grid")) 
        
        
        to_append = [type_of_order, str(ORDER_TIME),str(STOP_LOSS),str(TARGET),"Open"]
        df_length = len(Orders_dataframe)
        Orders_dataframe.loc[df_length] = to_append
        
        
        
    print(Fore.GREEN + " #### -> Requirement met")
    print(Fore.RED + " #### -> Requirement not met" + Style.RESET_ALL)

def write_file(df):
    if not sold:
        with open('BuySell.txt', 'a') as out:  
            pprint("Time: "+ str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), stream=out)
            pprint("Bought at "+ str(df.Close.iloc[-1]), stream=out)
            pprint("Lost to Fee "+ str(0.1/100*euro_quantity) + " €", stream=out)
            pprint("Balance: "+str(coin_quantity) + " coins", stream=out)
            pprint("", stream=out)
    else:
        with open('BuySell.txt', 'a') as out:
            pprint("Time: "+ str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), stream=out)
            pprint("Sold at "+ str(df.Close.iloc[-1]), stream=out)
            pprint("Lost to Fee "+ str(0.1/100*euro_quantity) + " €", stream=out)
            pprint("Balance: " + str(euro_quantity) + " €", stream=out)
            pprint("", stream=out)
    
def sound():
    #winsound.Beep(1000, 1000)
    pass
 
    

 
def run(): 
    global pair_moedas, time_interval, TRADING, TARGET, TYPE, OLD_PRICE, STOP_LOSS, ORDER_TIME
   # winsound.Beep(1000, 100)
   # time.sleep(0.1)
   # winsound.Beep(1000, 100)
    time.sleep(3)
    try:                                
       telegram_send.send(messages=["Trading bot Started trading:\n -> Pair:" + str(pair_moedas)+ "\n -> Time Interval:" + str(time_interval)])
    except:
        pass 
    while True:
        try:
            if df.Close.iloc[-1]:
                OLD_PRICE = df.Close.iloc[-1]
        except:
            pass
            
        df = getminutedata(pair_moedas, time_interval)
        applytechnicals(df)
        #slope = linregress([0,1], df[-2:]['RSI_Good'].to_numpy()).slope     
        if OLD_PRICE > df.Close.iloc[-1]:
            going_up = False
        else:  
            going_up = True
          
        output(df, TRADING, time_interval,going_up)
        
        if not TRADING:
        #SHORT
        #
        #    Short trading apenas funciona para futures que:
        #     -   Nao estao disponiveis em Euros
        #     -   Nao estao disponiveis para criacao de contas na europa
        #     -   Precisa-se de por dinheiro
        #     -   Pode-se no final ficar a dever ao binance
        #    
        #
        #    if df['EMA200'].iloc[-1] > df.Close.iloc[-1]:
        #        if (df['RSI_Good'].iloc[-1] > 80) and (df['RSI_Bad'].iloc[-1] > 80):
        #            if df['RSI_Diff'].iloc[-1] < 0:
        #                if ((df['ST_10_1'].iloc[-1] > df.Close.iloc[-1]) and (df['ST_11_2'].iloc[-1] > df.Close.iloc[-1])) \
        #                or ((df['ST_10_1'].iloc[-1] > df.Close.iloc[-1]) and (df['ST_12_3'].iloc[-1] > df.Close.iloc[-1])) \
        #                or ((df['ST_11_2'].iloc[-1] > df.Close.iloc[-1]) and (df['ST_12_3'].iloc[-1] > df.Close.iloc[-1])):
        #                        super_trend = []
        #                        super_trend.append(df['ST_10_1'].iloc[-1])
        #                        super_trend.append(df['ST_11_2'].iloc[-1])
        #                        super_trend.append(df['ST_12_3'].iloc[-1])
        #                        super_trend.sort()
        #                        STOP_LOSS = super_trend[1]
        #                        Stop_Loss_min = df.Close.iloc[-1]*0.65/100+df.Close.iloc[-1]
        #                        if  STOP_LOSS > Stop_Loss_min:
        #                            pass
        #                        else:
        #                            STOP_LOSS = Stop_Loss_min
        #                            
        #                        TARGET = (df.Close.iloc[-1]-STOP_LOSS)/0.75 + df.Close.iloc[-1]
        #                        TYPE = True
        #                        ORDER_TIME = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        #                        sound() # Beep
        #                        try:                                
        #                           telegram_send.send(messages=[["Time: "+ str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))],\
        #                           ["#### SHORT ####"],\
        #                           ["Target: " + str(TARGET)],\
        #                           ["Stop-Loss: "+ str(STOP_LOSS)]])
        #                        except:
        #                           pass                               
        #                        with open('BuySell.txt', 'a') as out: 
        #                            pprint("Time: "+ str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), stream=out)
        #                            pprint("#### SHORT ####", stream=out)
        #                            pprint("Target: " + str(TARGET), stream=out)
        #                            pprint("Stop-Loss: "+ str(STOP_LOSS), stream=out)
        #                        TRADING = True
        #                       
        #LONG
            if df['EMA200'].iloc[-1] < df.Close.iloc[-1]:
                if (df['RSI_Good'].iloc[-1] < 20) and (df['RSI_Bad'].iloc[-1] < 20):
                    if df['RSI_Diff'].iloc[-1] > 0:
                        if ((df['ST_10_1'].iloc[-1] < df.Close.iloc[-1]) and (df['ST_11_2'].iloc[-1] < df.Close.iloc[-1])) \
                        or ((df['ST_10_1'].iloc[-1] < df.Close.iloc[-1]) and (df['ST_12_3'].iloc[-1] < df.Close.iloc[-1])) \
                        or ((df['ST_11_2'].iloc[-1] < df.Close.iloc[-1]) and (df['ST_12_3'].iloc[-1] < df.Close.iloc[-1])):
                        
                            super_trend = []
                            super_trend.append(df['ST_10_1'].iloc[-1])
                            super_trend.append(df['ST_11_2'].iloc[-1])
                            super_trend.append(df['ST_12_3'].iloc[-1])
                            super_trend.sort()
                            
                            STOP_LOSS = super_trend[0]
                            Stop_Loss_min = df.Close.iloc[-1] - df.Close.iloc[-1]*0.65/100
                            if  STOP_LOSS < Stop_Loss_min:
                                pass
                            else:
                                STOP_LOSS = Stop_Loss_min
                                
                            TARGET = (df.Close.iloc[-1]-STOP_LOSS)/0.75 + df.Close.iloc[-1]
                            TYPE = False
                            ORDER_TIME = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            sound() # Beep
                            try:                                
                               telegram_send.send(messages=[["Time: "+ str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))],\
                               ["#### LONG ####"],\
                               ["Target: " + str(TARGET)],\
                               ["Stop-Loss: "+ str(STOP_LOSS)]])
                            except:
                               pass                            
                            with open('BuySell.txt', 'a') as out:  
                                pprint("Time: "+ str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), stream=out)
                                pprint("#### LONG ####", stream=out)
                                pprint("Target: " + str(TARGET), stream=out)
                                pprint("Stop-Loss: "+ str(STOP_LOSS), stream=out) 
                            TRADING = True
                                
                        elif (df['ST_10_1'].iloc[-1] < df.Close.iloc[-1]) \
                        and (df['ST_11_2'].iloc[-1] < df.Close.iloc[-1]) \
                        and (df['ST_12_3'].iloc[-1] < df.Close.iloc[-1]):
                        
                            super_trend = []
                            super_trend.append(df['ST_10_1'].iloc[-1])
                            super_trend.append(df['ST_11_2'].iloc[-1])
                            super_trend.append(df['ST_12_3'].iloc[-1])
                            super_trend.sort()
                            
                            
                            STOP_LOSS = super_trend[1]
                            Stop_Loss_min = df.Close.iloc[-1] - df.Close.iloc[-1]*0.45/100
                            if  STOP_LOSS < Stop_Loss_min:
                                pass
                            else:
                                STOP_LOSS = Stop_Loss_min
                            TARGET = (df.Close.iloc[-1]-STOP_LOSS)/0.75 + df.Close.iloc[-1]
                            TYPE = False
                            ORDER_TIME = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                            sound() # Beep
                            try:                                
                               telegram_send.send(messages=[["Time: "+ str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))],\
                               ["#### LONG ####"],\
                               ["Target: " + str(TARGET)],\
                               ["Stop-Loss: "+ str(STOP_LOSS)]])
                            except:
                               pass                             
                            with open('BuySell.txt', 'a') as out:  
                                pprint("Time: "+ str(datetime.now()), stream=out)
                                pprint("#### LONG ####", stream=out)
                                pprint("Target: " + str(TARGET), stream=out)
                                pprint("Stop-Loss: "+ str(STOP_LOSS), stream=out)
                            TRADING = True
                        
                    
        if TRADING:
        #TYPE = True -> Short Trading
        #TYPE = False -> Long Trading
            if TYPE: #short
                if df.Close.iloc[-1] > STOP_LOSS:
                    with open('BuySell.txt', 'a') as out:  
                        pprint("Time: "+ str(datetime.now()), stream=out)
                        LOSSES = LOSSES + 1
                        pprint("Lost to Stop-Loss"+ str(STOP_LOSS), stream=out)
                        pprint("Loss/Win Ration: "+ str(LOSSES) + "/" + str(WIN), stream=out)
                    try:    
                       Orders_dataframe['Status'] = df['Status'].replace(['Open'],'Closed')                    
                       telegram_send.send(messages=[["Time: "+ str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))],\
                       ["Lost to Stop-Loss" + str(STOP_LOSS)],\
                       ["Loss/Win Ration: "+ str(LOSSES) + "/" + str(WIN)]])
                    except:
                       pass 
                    TRADING = False
                elif df.Close.iloc[-1] < TARGET:
                    with open('BuySell.txt', 'a') as out:  
                        pprint("Time: "+ str(datetime.now()), stream=out)
                        WIN = WIN + 1
                        pprint("Won to Target"+ str(TARGET), stream=out)
                        pprint("Loss/Win Ration: "+ str(LOSSES) + "/" + str(WIN), stream=out)                  
                    try: 
                       Orders_dataframe['Status'] = df['Status'].replace(['Open'],'Closed')                    
                       telegram_send.send(messages=[["Time: "+ str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))],\
                       ["Won to Target" + str(TARGET)],\
                       ["Loss/Win Ration: "+ str(LOSSES) + "/" + str(WIN)]])
                    except:
                       pass 
                       
                    TRADING = False
            else: #long
                if df.Close.iloc[-1] < STOP_LOSS:
                    with open('BuySell.txt', 'a') as out:  
                        pprint("Time: "+ str(datetime.now()), stream=out)
                        LOSSES = LOSSES + 1
                        pprint("Lost to Stop-Loss"+ str(STOP_LOSS), stream=out)
                        pprint("Loss/Win Ration: "+ str(LOSSES) + "/" + str(WIN), stream=out)
                    try:
                       Orders_dataframe['Status'] = df['Status'].replace(['Open'],'Closed')                                        
                       telegram_send.send(messages=[["Time: "+ str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))],\
                       ["Lost to Stop-Loss" + str(STOP_LOSS)],\
                       ["Loss/Win Ration: "+ str(LOSSES) + "/" + str(WIN)]])
                    except:
                       pass 
                    TRADING = False
                elif df.Close.iloc[-1] > TARGET:
                    with open('BuySell.txt', 'a') as out:  
                        WIN = WIN + 1
                        pprint("Time: "+ str(datetime.now()), stream=out)
                        pprint("Won to Target"+ str(TARGET), stream=out) 
                        pprint("Loss/Win Ration: "+ str(LOSSES) + "/" + str(WIN), stream=out)
                    try:
                       Orders_dataframe['Status'] = df['Status'].replace(['Open'],'Closed')                                        
                       telegram_send.send(messages=[["Time: "+ str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))],\
                       ["Won to Target" + str(TARGET)],\
                       ["Loss/Win Ration: "+ str(LOSSES) + "/" + str(WIN)]])
                    except:
                       pass 
                
                







        time.sleep(2)



     


def change_coin(update, context):
    global pair_moedas
    user_says = " ".join(context.args)
    old_coin = pair_moedas
    pair_moedas = str(user_says)
    update.message.reply_text("Updating to " + user_says)
    time.sleep(0.5)
    update.message.reply_text("25%")
    time.sleep(0.5)
    update.message.reply_text("50%")
    time.sleep(0.5)
    update.message.reply_text("75%")
    time.sleep(0.5)
    update.message.reply_text("100%")
    time.sleep(0.5)
    df = getminutedata(pair_moedas, time_interval)
    applytechnicals(df) 
    
    try:                                
       telegram_send.send(messages=[["Coin Pair changed by user at "+ str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))], ["Coin pair changed from " + str(old_coin) + " to " + str(pair_moedas)], ["Use /status to get the new values"]])
    except:
       pass 



def return_orders():  
    return tabulate(Orders_dataframe, headers='keys', tablefmt='plain')
    
def orders(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=return_orders())

def return_status(): 
    global pair_moedas,time_interval

    df = getminutedata(pair_moedas, time_interval)
    applytechnicals(df)    
    return  tabulate([      ["Currently Trading->",str(pair_moedas)],\
                            ["Current Price ->",str(df.Close.iloc[-1])+"€"],\
                            ["Time interval ->",str(time_interval)], \
                            ["EMA 200 ->",str(df['EMA200'].iloc[-1])], \
                            ["Stoch RSI K ->",str(df['RSI_Good'].iloc[-1])], \
                            ["Stoch RSI D ->",str(df['RSI_Bad'].iloc[-1])], \
                            ["RSI Difference ->",str(df['RSI_Diff'].iloc[-1])], \
                            ["SuperTrend 10-1 ->",str(df['ST_10_1'].iloc[-1])], \
                            ["SuperTrend 11-2 ->",str(df['ST_11_2'].iloc[-1])], \
                            ["SuperTrend 12-3 ->",str(df['ST_12_3'].iloc[-1])], \
                            ],tablefmt='plain')

    
def uptime(update, context):

    time_delta = (datetime.now() - START_TIME)
    total_seconds = time_delta.total_seconds()

    
    if total_seconds/60 > 60:
        time = total_seconds/3600 
        update.message.reply_text(str(time) + " hours")
    elif total_seconds/60 > 1:
        time = total_seconds/60 
        update.message.reply_text(str(time) + " minutes")
    else:
        time = total_seconds 
        update.message.reply_text(str(time) + " seconds")
        
                
    
def status(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=return_status())
  
if __name__ == '__main__':
    global pair_moedas,time_interval
    pair_moedas = "DOTEUR" #input("Enter your pair: ")    
    time_interval = "15m" #input("Enter your time interval: ")  
    
    TOKEN = TELE_API
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    orders_handler = CommandHandler("orders", orders)
    dispatcher.add_handler(orders_handler)
    
    status_handler = CommandHandler("status", status)
    dispatcher.add_handler(status_handler)
    
    change_coin_handler = CommandHandler("change_coin", change_coin)
    dispatcher.add_handler(change_coin_handler)
    
    uptime_handler = CommandHandler("uptime", uptime)
    dispatcher.add_handler(uptime_handler)


    updater.start_polling()
   
    run()