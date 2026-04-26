import time
import csv
from geopy.geocoders import Nominatim

geo = Nominatim(user_agent='teste')

# Esse módulo serve pra converter o butecos_bh.csv em coordenadas (lat, lon) e armazena em locations.csv

with open('butecos_bh.csv', mode='r') as input:
    csvfile = csv.reader(input, delimiter=';')
    
    with open('butecos_geocoded.csv', mode='w', newline='') as output:

        writer = csv.writer(output, delimiter=';')        
        next(csvfile) # Pula name;address

        for line in csvfile:
            bar_name = line[0]
            address = line[1]

            try:
                location = geo.geocode(address) # 
                
                if location == None: 
                    continue

                writer.writerow([bar_name, location.latitude, location.longitude]) # type: ignore

            except Exception as e:
                print(f"Erro: {e}")

            finally:
                time.sleep(1)
