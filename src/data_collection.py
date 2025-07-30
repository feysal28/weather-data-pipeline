import requests
import json
from datetime import datetime, timezone
import pandas as pd 
import time 
import csv
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

def weather () :
    # Configuration
    API_KEY = ""  # Replace by your key api 
    CITIES = ["Paris", "Moscow", "London", "Madrid", "Monaco", "Berlin", "Warsaw", "Hambourg", 
              "Rome", "Amsterdam", "Florence", "Oslo", "Venise","Lisbonne","Budapest",
                "Dublin", "Milan", "Prague", "Munich", "Turin", "Marseille", "Palerme", "Riga", "Dortmund",
                    "Sofia"]

    weather_city = {}
    for city in CITIES :
        reponses = requests.get(
                f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
            )
        if reponses.status_code == 200: 
            weather_city[city] = reponses.json()
            print(f"data_{city} saved")
        else :
            print(f" error {city} : {reponses.status_code}")

    for city, data in weather_city.items() :
        filename = f"weather_{city}.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent= 3)
            print(f"data{filename} saved with succes ")




    file_weather_json = [f"weather_{city}.json" for city in CITIES]

    data_weather_csv = []

    for file in file_weather_json :
        with open(file, "r") as f :
            data = json.load(f)

        dt_timestamp = data["dt"]
        update_date = datetime.fromtimestamp(dt_timestamp, tz =timezone.utc).strftime("%d/%m/%Y, %H:%M:%S")


        data_weather_csv.append({
            "town" : data.get("name", "N/A"),
            "update_date" : update_date,
            "Temperature" : data["main"].get("temp", "N/A"),
            "feels_like" : data["main"].get("feels_like", "N/A"),
            "Temp min (°C)": data["main"].get("temp_min", "N/A"),
            "Temp max (°C)": data["main"].get("temp_max", "N/A"),
            "Pressure (hPa)": data["main"].get("pressure", "N/A"),
            "Humidity (%)": data["main"].get("humidity", "N/A"),
            "speed wind (m/s)": data["wind"].get("speed", "N/A"),
            "Direction wind (°)": data["wind"].get("deg", "N/A"),
            "longitude" : data["coord"].get("lon", "N/A"),
            "latitude" : data["coord"].get("lat", "N/A"),
            "Description": data["weather"][0].get("description") if data.get("weather") else "N/A"
        })

    # for create unique file for each time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"weather_data_{timestamp}.csv"

    with open(csv_filename, "w", newline= "", encoding= "utf-8") as csvfile :
        column = ["town", "update_date", "Temperature", "feels_like",
        "Temp min (°C)", "Temp max (°C)", "Pressure (hPa)", "Humidity (%)",
        "speed wind (m/s)", "Direction wind (°)", "longitude", "latitude", "Description"
        ]

        writer = csv.DictWriter(csvfile, fieldnames=column)
        writer.writeheader()
        writer.writerows(data_weather_csv)
        print(f"Fichier CSV {csv_filename} sauvegardé avec succès. {len(data_weather_csv)} entrées.")
    
    load_dotenv()
    df = pd.read_csv(csv_filename)
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS =  os.getenv("DB_PASSWORD", "Faltimes")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = "weather"

    CONN_STRING = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    table_name = f"weather{timestamp}"

    # 5. Connect to PostgreSQL and load
    engine = create_engine(CONN_STRING)

    df.to_sql(
        name=table_name,          # name the table
        con=engine,             # Connexion
        if_exists='replace',    # Options: 'fail', 'replace', 'append'
        index=False,            # don't include l'index pandas
        method='multi'          # Insertion by lots 
    )

    print("✅ Data saved with succes in PostgreSQL !")

    return csv_filename

if __name__ == "__main__" :
    while True :
        weather()
        time_wait = 3600
        print(f"time wait {time_wait} secondes or  one heures for next update ")
        time.sleep(time_wait)


