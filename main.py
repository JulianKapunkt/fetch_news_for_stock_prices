import requests
import csv

COMPANY = "Tesla"
COMPANY_ABBREVIATION = "TSLA"
ALPHA_VANTAGE_API_KEY = "66OA2S45MNLW1BJR"
ALPHA_VANTAGE_API_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_API_KEY = "0d97240bd1144c04900b028570dc0d0b"
NEWS_API_ENDPOINT = "https://newsapi.org/v2/everything"

ALPHA_VANTAGE_API_REQUEST_PARAMS = {
    "function" : "TIME_SERIES_DAILY_ADJUSTED",
    "symbol" : COMPANY_ABBREVIATION,
    "outputsize" : "compact",
    "apikey" : ALPHA_VANTAGE_API_KEY,
    "datatype" : "json"
}


NEWS_API_REQUESTS_PARAMS = {
    "q" : COMPANY,
    "sortBy" : "popularity",
    "apiKey" : NEWS_API_KEY,
    "domains" : "handelsblatt.com"
}


def calculate_percentage_change(close_current_day, close_previous_day):
    veränderung = (float(close_previous_day) / float(close_current_day)) * 100
    veränderung = 100 - veränderung
    return veränderung


def write_to_csv(keys, output):
    with open("stock_trading_news_alert.csv", "w", newline="") as f:
        csv_writer = csv.DictWriter(f, keys)
        csv_writer.writeheader()
        csv_writer.writerows(output)


def get_news(key):
    NEWS_API_REQUESTS_PARAMS["from"] = key
    response_news = requests.get(NEWS_API_ENDPOINT, params=NEWS_API_REQUESTS_PARAMS)
    news = response_news.json()
    return news


output = []

#Ruft die Aktienkurse für das Unternehmen ab, das Format ist JSON
response = requests.get(ALPHA_VANTAGE_API_ENDPOINT, params=ALPHA_VANTAGE_API_REQUEST_PARAMS)
data = response.json()["Time Series (Daily)"]

#data.keys() returnt ein Objekt, welches alle Schlüssel eines dictonaries beinhaltet
list_of_data_keys = list(data.keys())

#Iteriert über 20 Tage, und schreibt für jeden Tag einen Eintrag in das output dictionary
#20 Tage, da die NewsAPI in der kostenlosen Version nicht für ältere Daten funktioniert
for index, key in enumerate(list_of_data_keys[:20]):
    close_current_day = data[key]['4. close']

    output.append({"Tag" : key,
                   "Close" : close_current_day,
                   "Prozentuale Veränderung" : " ",
                   "Artikel 1" : " ",
                   "Link 1" : " ",
                   "Artikel 2" : " ",
                   "Link 2" : " ",
                   "Artikel 3" : " ",
                   "Link 3" : " "})

    #Findet den vorherig eingetragenen Tag, damit wir dessen Close Wert ermitteln können
    previous_day = list_of_data_keys[index + 1]
    close_previous_day = data[previous_day]['4. close']

    #Berechnet die prozentuale Veränderung vom  Close-Wert des Vortages zum aktuellen Wert
    veränderung = calculate_percentage_change(close_current_day, close_previous_day)
    output[-1]["Prozentuale Veränderung"] = veränderung

    #Wenn es eine Veränderung von min. +- 5 % gibt, werden News-Artikel bzgl. der Company an dem Tag ausgegeben
    if abs(veränderung) > 5:

        news = get_news(key)

        print(news)

        news = news["articles"]

        #Schreibt die gefundenen Newsartikel in das Dict
        output[-1]["Artikel 1"] = f"{news[0]['title']}"
        output[-1]["Link 1"] = f"{news[0]['url']}"
        output[-1]["Artikel 2"] = f"{news[1]['title']}"
        output[-1]["Link 2"] = f"{news[1]['url']}"
        output[-1]["Artikel 3"] = f"{news[2]['title']}"
        output[-1]["Link 3"] = f"{news[2]['url']}"

    keys = output[0].keys()

    #Ausgabe als CSV File
    write_to_csv(keys, output)
