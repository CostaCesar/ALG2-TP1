import time
import csv
from geopy.geocoders import Nominatim

geo = Nominatim(user_agent='teste')


# Esse módulo serve pra converter o butecos_bh.csv em coordenadas (lat, lon) e armazena em locations.csv

with open('../data/butecos_bh.csv', mode='r', encoding='utf-8') as input:
    csvfile = csv.reader(input, delimiter=';')
    
    with open('../data/teste_geocoded.csv', mode='w', newline='', encoding='utf-8') as output:

        writer = csv.writer(output, delimiter=';')        
        next(csvfile)

        for line in csvfile:
            bar_name = line[0]
            address = line[1]

            try:
                
                nominatim_query = {
                    'amenity': None,
                    'street': None,
                    'city': 'Belo Horizonte',
                    'state': 'Minas Gerais',
                    'country': 'Brazil',
                    'postalcode': None # Extremamente importante para achar a coordenada exata
                    } # Formato da busca estruturada

                parts = address.split(',')

                nominatim_query['postalcode'] = parts[-1]
                nominatim_query['amenity'] = bar_name
                nominatim_query['street'] = parts[0] + parts[1]

                print(nominatim_query)


                location = geo.geocode(nominatim_query) # Tenta primeiro com dicionário

                if location == None:
                    print(f" Erro no structured: {nominatim_query}")
                    time.sleep(1)
                    location = geo.geocode(address)
                    if location == None:
                        print(f' Erro no simple: {address}')
                        continue

                writer.writerow([bar_name, location.latitude, location.longitude]) # type: ignore

            except Exception as e:
                print(f"Erro: {e}")

            finally:
                time.sleep(1)
