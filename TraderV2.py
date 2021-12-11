

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
import winsound
from dotenv import load_dotenv
from datetime import datetime
import pandas_ta as talib
load_dotenv()
init()


client = Spot()
print(client.time())




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
STOP_LOSS = 0

pair_moedas = ""
time_interval = ""



api_key = os.getenv("API_KEY")
api_secret = os.getenv('API_SECRET')
client = Spot(api_key,api_secret)



def getminutedata(Symbol, interval, lookback):
    
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
    #print( talib.supertrend(df.High, df.Low, df.Close, 7, 3).trend())
    #https://stackoverflow.com/questions/44935269/supertrend-code-using-pandas-python
    
    df.dropna(inplace=True)





def output(sold, df, slope,slope_print,bol_avg_print,rsi_diff_print, buy_price, sold_price, print_ma13, print_ma5, print_ma8):

    if sold is True:
        if  (slope != slope_print) or ((df.Close.iloc[-1] - df['Bol_H'].iloc[-1]) != bol_avg_print) or (df['RSI_Diff'].iloc[-1] != rsi_diff_print) or (df['MA5'].iloc[-1] != print_ma5) or (df['MA8'].iloc[-1] != print_ma8) or (df['MA13'].iloc[-1] != print_ma13):
            slope_print = slope
            bol_avg_print = df.Close.iloc[-1] - df['Bol_H'].iloc[-1]
            rsi_diff_print = df['RSI_Diff'].iloc[-1] 
            
            if slope > 0:
                A = Fore.GREEN
            else:
                A = Fore.RED
            
            if df.Close.iloc[-1] < df['Bol_H'].iloc[-1]:
                B = Fore.GREEN
            else:
                B = Fore.RED
            
            if df['RSI_Diff'].iloc[-1] > RSI_Diff_greater:
                C = Fore.GREEN
            else:
                C = Fore.RED
            
            if df['MA5'].iloc[-1] > df['MA8'].iloc[-1]:
                D = Fore.GREEN
            else:
                D = Fore.RED
                
            if df['MA5'].iloc[-1] > df['MA13'].iloc[-1]:
                E = Fore.GREEN
            else:
                E = Fore.RED
                
                
            print(tabulate([["Pair", "Price" ],[ pair_moedas , str(df.Close.iloc[-1]) ]], headers="firstrow", tablefmt="fancy_grid"))  
            print(tabulate([["Type","Time","Slope","Boll High - Price", "RSI_Diff","MA5","MA8", "MA13"],[Fore.GREEN + "BUY"+ Style.RESET_ALL,Style.RESET_ALL +str(datetime.now())+ Style.RESET_ALL,A + str(slope)+ Style.RESET_ALL, B + str(df['Bol_H'].iloc[-1]-df.Close.iloc[-1])+ Style.RESET_ALL, C + str(df['RSI_Diff'].iloc[-1]) + Style.RESET_ALL, Fore.CYAN + str(df['MA5'].iloc[-1]) + Style.RESET_ALL, D + str(df['MA8'].iloc[-1]) + Style.RESET_ALL, E + str(df['MA13'].iloc[-1]) + Style.RESET_ALL]], headers="firstrow", tablefmt="fancy_grid"))
            print(Fore.GREEN + " #### -> Requirement met")
            print(Fore.YELLOW + " #### -> Don't Care")
            print(Fore.RED + " #### -> Requirement not met" + Style.RESET_ALL)
    else:   
        if  (slope != slope_print) or ((df.Close.iloc[-1] - df['Bol_H'].iloc[-1]) != bol_avg_print) or (df['RSI_Diff'].iloc[-1] != rsi_diff_print) or (df['MA5'].iloc[-1] != print_ma5) or (df['MA8'].iloc[-1] != print_ma8) or (df['MA13'].iloc[-1] != print_ma13):
            slope_print = slope
            bol_avg_print = df.Close.iloc[-1] - df['Bol_H'].iloc[-1]
            rsi_diff_print = df['RSI_Diff'].iloc[-1] 
            
            if slope <= 0:
                A = Fore.GREEN
            else:
                A = Fore.RED
            
            if df.Close.iloc[-1] >= df['Bol_H'].iloc[-1]:
                B = Fore.GREEN
            else:
                B = Fore.YELLOW
            
            if df['RSI_Diff'].iloc[-1] < RSI_Diff_smaller:
                C = Fore.GREEN
            else:
                C = Fore.RED             
            if df['MA5'].iloc[-1] <= df['MA8'].iloc[-1]:
                D = Fore.GREEN
            else:
                D = Fore.RED
                
            if df['MA5'].iloc[-1] <= df['MA13'].iloc[-1]:
                E = Fore.GREEN
            else:
                E = Fore.RED
            
            
            print(tabulate([["Pair", "Price" ],[ pair_moedas , str(df.Close.iloc[-1]) ]], headers="firstrow", tablefmt="fancy_grid"))           
            print(tabulate([["Type","Time","Slope","Boll High - Price", "RSI_Diff","MA5","MA8", "MA13"],[Fore.RED + "SELL"+ Style.RESET_ALL,Style.RESET_ALL +str(datetime.now())+ Style.RESET_ALL,A + str(slope)+ Style.RESET_ALL, B + str(df['Bol_H'].iloc[-1]-df.Close.iloc[-1])+ Style.RESET_ALL, C + str(df['RSI_Diff'].iloc[-1]) + Style.RESET_ALL, Fore.CYAN + str(df['MA5'].iloc[-1]) + Style.RESET_ALL, D + str(df['MA8'].iloc[-1]) + Style.RESET_ALL, E + str(df['MA13'].iloc[-1]) + Style.RESET_ALL]], headers="firstrow", tablefmt="fancy_grid"))
            print(Fore.GREEN + " #### -> Requirement met") 
            print(Fore.YELLOW + " #### -> Don't Care")
            print(Fore.RED + " #### -> Requirement not met" + Style.RESET_ALL)
  
    return slope_print, bol_avg_print, rsi_diff_print, print_ma13, print_ma5, print_ma8

def write_file(df):
    if not sold:
        with open('BuySell.txt', 'a') as out:  
            pprint("Time: "+ str(datetime.now()), stream=out)
            pprint("Bought at "+ str(df.Close.iloc[-1]), stream=out)
            pprint("Lost to Fee "+ str(0.1/100*euro_quantity) + " €", stream=out)
            pprint("Balance: "+str(coin_quantity) + " coins", stream=out)
            pprint("", stream=out)
    else:
        with open('BuySell.txt', 'a') as out:
            pprint("Time: "+ str(datetime.now()), stream=out)
            pprint("Sold at "+ str(df.Close.iloc[-1]), stream=out)
            pprint("Lost to Fee "+ str(0.1/100*euro_quantity) + " €", stream=out)
            pprint("Balance: " + str(euro_quantity) + " €", stream=out)
            pprint("", stream=out)
    
def sound():
    winsound.Beep(1000, 1000)
 
    

 
def run(): 
    global sold, slope_print, bol_avg_print, rsi_diff_print, RSI_Diff_greater, RSI_Diff_smaller, pair_moedas, time_interval, euro_quantity, coin_quantity, sold_price, buy_price,  print_ma13, print_ma5, print_ma8
    winsound.Beep(1000, 100)
    time.sleep(0.1)
    winsound.Beep(1000, 100)
    time.sleep(0.1)
    while True:
        
        df = getminutedata(pair_moedas, time_interval, '500')
        applytechnicals(df)
        slope = linregress([0,1], df[-2:]['RSI_Good'].to_numpy()).slope                 
        slope_print, bol_avg_print, rsi_diff_print, print_ma13, print_ma5, print_ma8 = output(sold, df, slope,slope_print,bol_avg_print,rsi_diff_print, buy_price, sold_price, print_ma13, print_ma5, print_ma8)
        
        

        if sold:
            if slope > 0:
                if df['RSI_Diff'].iloc[-1] > RSI_Diff_greater:
                    if df.Close.iloc[-1]<df['Bol_H'].iloc[-1]:
                        #if sold_price > df.Close.iloc[-1]:
                        if df['MA5'].iloc[-1] > df['MA8'].iloc[-1] and df['MA5'].iloc[-1] > df['MA13'].iloc[-1]:
                            sold = False
                            coin_quantity = (euro_quantity-0.1/100*euro_quantity)/df.Close.iloc[-1]
                            write_file(df)
                            buy_price = df.Close.iloc[-1]
                            sound()
                            STOP_LOSS = 0.975*df.Close.iloc[-1]
                            

                    
            
         
        if not sold:
            if (df['RSI_Diff'].iloc[-1] <= RSI_Diff_smaller) or slope <= 0:
                if df['MA5'].iloc[-1] <= df['MA8'].iloc[-1] or df['MA5'].iloc[-1] <= df['MA13'].iloc[-1]:
                    euro_quantity = coin_quantity*df.Close.iloc[-1]
                    euro_quantity = (euro_quantity-0.1/100*euro_quantity)
                    sold = True
                    write_file(df)
                    sold_price = df.Close.iloc[-1]
                    sound()
                    
                    
        if not sold:
            if STOP_LOSS > df.Close.iloc[-1]:
                euro_quantity = coin_quantity*df.Close.iloc[-1]
                euro_quantity = (euro_quantity-0.1/100*euro_quantity)
                sold = True
                with open('BuySell.txt', 'a') as out:
                    pprint("STOPLOSS: ", stream=out)
                write_file(df)
                sold_price = df.Close.iloc[-1]
                sound()
        time.sleep(2)



from selenium import webdriver
from time import sleep

  
if __name__ == '__main__':


    driver = webdriver.Firefox()
    driver.get('https://www.python.org')
    sleep(1)

    driver.get_screenshot_as_file("screenshot.png")
    driver.quit()
    print("end...")