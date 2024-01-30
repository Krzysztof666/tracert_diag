# -*- utf-8 -*-
'''
    Program wykonuje polecenie systemowe tracert <nazwa.domeny>
    Pobiera wszystkie adresy IP z wyjścia polecenia i przedstawia
    mapę z drogami transmisji pakietów.
    Brak podania nazwy domeny spowoduje wykonanie polecenia tracert dla
    domeny: interia.pl
'''

import os
import subprocess
import re
from rich import print as rprint
from rich.status import Status

import time

import socket
import requests
from ip2geotools.databases.noncommercial import DbIpCity
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt





# Linia rozdzielająca wyświetlane elementy
def linijka():
    rprint(f'[magenta]='*80)

def sprawdz_domenę(nazwa_domeny):
    '''
    Funckcja sprawdza, czy podana nazwa domeny jest prawidłowa
    '''
    wzorzec = re.compile(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(wzorzec.match(nazwa_domeny))
    
def printDetails(ip):
    '''
    Funkacja wyznacza wspołrzędne GPS na podstawie przekazanego IP

    Output:
        (longitude, latitude, city)
    '''
    try: 
        res = DbIpCity.get(ip, api_key="free")
        rprint(f'Adres IP: {res.ip_address}')
        rprint(f'Lokalizacja: {res.city}, {res.region}, {res.country}')
        rprint(f'Współrzędne GPS: (Lat: {res.latitude}, Lng: {res.longitude})')

        lat_dms = decimal_to_dms(res.latitude)
        lng_dms = decimal_to_dms(res.longitude)

        rprint(f"[green]Współrzędne GPS DMS (Lat): [yellow]{lat_dms[0]}° {lat_dms[1]}' {lat_dms[2]:.2f}\"")
        rprint(f"[green]Współrzędne GPS DMS (Lng): [yellow]{lng_dms[0]}° {lng_dms[1]}' {lng_dms[2]:.2f}\"")
    except:
        rprint('[red] Odczytano błędne dane. Spróbuj jeszcze raz')
        exit(1)

    return (res.longitude, res.latitude, res.city)     
    



def decimal_to_dms(decimal_coordinates):
    '''
    W tej funkcji decimal_to_dms, współrzędne dziesiętne są przeliczane 
    na stopnie, minuty i sekundy. 
    Wyniki są następnie wyświetlane w postaci tekstowej, 
    reprezentującej współrzędne w formacie stopnie, minuty, sekundy.
    Zauważ, że ta funkcja zakłada, że współrzędne są dodatnie dla półkuli północnej i wschodniej, 
    a ujemne dla półkuli południowej i zachodniej. Jeśli współrzędne są ujemne, 
    można to dostosować w kodzie według potrzeb.
    '''

    degrees = int(decimal_coordinates)
    minutes_float = (decimal_coordinates - degrees) * 60
    minutes = int(minutes_float)
    seconds = (minutes_float - minutes) * 60

    degrees = abs(degrees)
    minutes = abs(minutes)
    seconds = abs(seconds)

    return degrees, minutes, seconds

# Współrzędne GPS w postaci dziesiętnej
# lat_decimal = 53.3493795
# lng_decimal = -6.2605593          

# Przelicz współrzędne na stopnie, minuty, sekundy
# lat_dms = decimal_to_dms(lat_decimal)
# lng_dms = decimal_to_dms(lng_decimal)

# Wyświetl wyniki
# print(f"Współrzędne GPS (Lat): {lat_dms[0]}° {lat_dms[1]}' {lat_dms[2]:.2f}\"")
# print(f"Współrzędne GPS (Lng): {lng_dms[0]}° {lng_dms[1]}' {lng_dms[2]:.2f}\"")


      
    

def tracert_ip_addresses(target_host='interia.pl'):
    '''
        Funkcja - za pomocą wyrażenia regularnego - pobiera wszystkie adresy IP
        zwracane przez polecenie systemowe tracert, które znajdują się w nawiasach [ ]
    '''
    try:
        # Uruchomienie polecenia tracert i przechwycenie wyników
        result = subprocess.check_output(["tracert", target_host], universal_newlines=True)

        # Wyrażenie regularne do wyodrębnienia adresów IP
        ip_pattern = re.compile(r'\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]')

        # Znajdź wszystkie pasujące adresy IP w wynikach
        ip_addresses = ip_pattern.findall(result)

        return ip_addresses

    except subprocess.CalledProcessError as e:
        rprint(f"[red]Błąd podczas wykonania polecenia tracert: {e}")
        return []




# Czyszczenie ekranu
os.system('cls')

# Podajemy nazwę domeny dla polecenia tracert

while True:
    target_host = str(input(f'Podaj domenę: '))

    if sprawdz_domenę(target_host):
        break
    else:
        rprint('[red]Błędna nazwa domeny. Spróbuj ponownie.')
        continue
    
       
# Start liczenia czasu
start_time = time.time()

# Spinner animacja
with Status('Pobieranie adresów') as status:

    ip_addresses = tracert_ip_addresses(target_host)

    status.update()
# Koniec liczenia czasu
end_time = time.time()

delta_time = end_time - start_time

rprint(f'Czas wykonania polecenia tracert: [yellow]{delta_time:.1f} sekund.')
    


if ip_addresses:
    rprint(f"[yellow]Pobrane adresy IP w tracert dla [green]{target_host}:")
        
    hosts = []
    for ip in ip_addresses:
        rprint(f'[blue]{ip}')
        hosts.append(ip)
else:
        printf(f"[magenta]Nie znaleziono adresów IP w tracert dla {target_host}.")

del hosts[0:1]   # Pomijamy adres hosta docelowego i własny komputera
    
rprint(f'Host: {hosts}')
linijka()
rprint(f'Liczba hostów pośredniczących: {len(hosts)}')


lon_lat_city = []
for host in hosts:
    lon_lat_city.append(printDetails(host))  # Tworzymy listę krotek (lon, lat, city) dla wszystkich znalezionych hostów
linijka()



rprint(f'Lon_lat: {lon_lat_city}')

# Inicjowanie mapy
m = Basemap(projection='mill',llcrnrlat=-60,urcrnrlat=90,\
        llcrnrlon=-180,urcrnrlon=180,resolution='c')

# Tworzenie wykresu o rozmiarze 10 na 8 cali
fig = plt.figure(figsize=(12, 5))

# Ustawienia mapy
m.drawcoastlines()
m.drawcountries()
m.drawmapboundary(linewidth=1.5)

# Przykładowe współrzędne punktu w formie dziesiętnej
# lat = 53.343955  # szerokość geograficzna
# lon = -6.235744  # długość geograficzna

# Dodawanie punktów do mapy
for lon, lat, city in lon_lat_city:
       x, y = m(lon, lat)
       m.plot(x, y, 'ro', markersize=8)  # Rysowanie punktów
       plt.annotate(city, (x, y), textcoords="offset points", xytext=(0, 10), ha='center') # Dodanie nazw miast


# Przekształcanie współrzędnych na mapie, tworzenie list x i y
x, y = m([point[0] for point in lon_lat_city], [point[1] for point in lon_lat_city])

# Rysowanie linii na mapie pomiędzy kolejnymi punktami
for i in range(len(lon_lat_city) - 1):
       plt.annotate('', xy=(x[i + 1], y[i + 1]), xytext=(x[i], y[i]),
               arrowprops=dict(facecolor='magenta', edgecolor='magenta', arrowstyle='->'))

# Łączenie punktów liniami
m.plot(x, y, 'b-')

# Dodanie tytułu
plt.title('Trasy pakietów.')

# Zapis wykresu do pliku w rozdzielczości 300dpi
plt.savefig('mapa.png', dpi=300) 

# Pokazanie mapy
plt.show()

    