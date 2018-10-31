import io, os.path, re
import requests, urllib
import numpy as np
from pandas import DataFrame

def getting_links(links_table):
    links = re.findall(r"<a class=\"href-link\" href=\"(.*?)\">", g.text)
    for x in range(len(links)):
        links[x] = "www.gumtree.pl" + links[x]
    return links_table.extend(links)

def getting_no_of_photos(no_of_photos_table): 
    no_of_photos = re.findall("Zdjęć: (.*?)<", g.text)
    #when "<li class=" starts with "pictures", the number of photos is presented; if not it is skipped and should be added
    zero_photos = re.findall(r"<li class=\"result (.*?)\"", g.text)
    for x in range(len(zero_photos)):
        if len(zero_photos[x]) == 0:
            no_of_photos.insert(x,"0")
    for x in range(len(no_of_photos)):
        no_of_photos[x] = int(no_of_photos[x])
    return no_of_photos_table.extend(no_of_photos)

def getting_prices(prices_table):
    #either there is a price shown in zł or there is the adnotation "Proszę o kontakt" (please contact me)
    prices_or_contact = re.findall(r"<span class=\"amount\">(.*?) zł</span>|<span class=\"value\">(.*?)</span>", g.text)
    prices = [i[0] for i in prices_or_contact]
    for x in range(len(prices)):
        if len(prices[x]) > 3:
            prices[x] = prices[x][0] + prices[x][2:5]
        elif len(prices[x]) == 0:
            prices[x] = "0"
        prices[x] = int(prices[x])
    return prices_table.extend(prices)

def getting_locations(locations_table):
    locations = re.findall(r"<span> pokoje do wynajęcia , (.*?)</span>", g.text)
    return locations_table.extend(locations)

def getting_interesting_locations(unique_locations):
    print("Masz ogłoszenia z dzielnic:", ",".join(unique_locations))
    print("Które dzielnice Cię interesują?")
    interesting_locations_string = input("Jeżeli wszystkie bez ograniczeń, napisz x i przyciśnij Enter. Jeżeli wybrane, napisz je oddzielając przecinkiem np: Bemowo,Włochy,Mokotów: ")
    interesting_locations = interesting_locations_string.split(",")
    
    mistake_in_locations = []
    if interesting_locations[0] != "x":
        for element in interesting_locations:
            if element not in unique_locations:
                mistake_in_locations.append(element)
        if len(mistake_in_locations) != 0:
            print("Dzielnica(e):", ",".join(mistake_in_locations), "nie są rozpoznana(e) (błąd, dodana spacja lub nie ma ich na liście). Spróbuj ponownie.", "\n")
            getting_interesting_locations(unique_locations)
            
    return interesting_locations

def getting_interesting_prices(prices):
    print("Ceny wahają się od", min(prices), "zł do", max(prices),"zł.")
    print("Jaki przedział cenowy Cię interesuje? 0 oznacza, że nie podano ceny (czyli proszą o kontakt). Wpisz cenę albo x, jeżeli bez ograniczeń, i wciśnij Enter.")
    interval_interesting_prices = [None, None]
    interval_interesting_prices[0] = input("Minimalna cena: ")
    interval_interesting_prices[1] = input("Maksymalna cena: ")
    
    for x in range(2):
        if interval_interesting_prices[x] != "x":
            try: 
                interval_interesting_prices[x] = int(interval_interesting_prices[x])
                if (interval_interesting_prices[x] < 0) or (interval_interesting_prices[x] > max(prices)):
                    print("Musisz podać liczbę z przedziału 0 do", max(prices),"! Spróbuj jeszcze raz.","\n")
                    getting_interesting_prices(prices)
            except ValueError:
                print("Musisz podać liczbę albo x, spróbuj jeszcze raz!","\n")
                getting_interesting_prices(prices)
            
    if (interval_interesting_prices[0] != "x") and (interval_interesting_prices[1] != "x"):
        if int(interval_interesting_prices[0]) > int(interval_interesting_prices[1]):
            print("Minimalna cena musi być mniejsza od maksymalnej! Spróbuj jeszcze raz.","\n")
            getting_interesting_prices(prices)
    
    return interval_interesting_prices

def getting_interesting_no_of_photos(no_of_photos):
    print("Ilość zdjęć waha się od", min(no_of_photos), "do", max(no_of_photos),".")
    print("Jaka ilość zdjęć Cię interesuje? Wpisz ilość albo x, jeżeli bez ograniczeń, i wciśnij Enter.")
    interval_interesting_no_of_photos = [None, None]
    interval_interesting_no_of_photos[0] = input("Minimalna ilość zdjęć: ")
    interval_interesting_no_of_photos[1] = input("Maksymalna ilość zdjęć: ")
    
    for x in range(2):
        if interval_interesting_no_of_photos[x] != "x":
            try: 
                interval_interesting_no_of_photos[x] = int(interval_interesting_no_of_photos[x])
                if (interval_interesting_no_of_photos[x] < 0) or (interval_interesting_no_of_photos[x] > int(max(no_of_photos))):
                    print("Musisz podać liczbę z przedziału 0 do", max(no_of_photos),"! Spróbuj jeszcze raz.","\n")
                    getting_interesting_no_of_photos(no_of_photos)
            except ValueError:
                print("Musisz podać liczbę albo x, spróbuj jeszcze raz!","\n")
                getting_interesting_no_of_photos(no_of_photos)
            
    if (interval_interesting_no_of_photos[0] != "x") and (interval_interesting_no_of_photos[1] != "x"):
        if int(interval_interesting_no_of_photos[0]) > int(interval_interesting_no_of_photos[1]):
            print("Minimalna cena musi być mniejsza od maksymalnej! Spróbuj jeszcze raz.","\n")
            getting_interesting_no_of_photos(no_of_photos)
        
    return interval_interesting_no_of_photos

def selecting_results():
    result =results.copy()
    if interesting_prices[0] != "x":
        result = result.loc[result["Cena w zł"] >= int(interesting_prices[0])]
    if interesting_prices[1] != "x":
        result = result.loc[result["Cena w zł"] <= int(interesting_prices[1])]
    if interesting_no_of_photos[0] != "x":
        result = result.loc[result["Ilość zdjęć"] >= int(interesting_no_of_photos[0])]
    if interesting_no_of_photos[1] != "x":
        result = result.loc[result["Ilość zdjęć"] <= int(interesting_no_of_photos[1])]
    if interesting_locations[0] != "x":
        return result.loc[result["Dzielnica"].isin(interesting_locations)]   
    return result



#main
links_table = []
no_of_photos_table = []
prices_table = []
locations_table = []

print('Ten program zbiera iformacje z gumtree odnośnie pokojów i pokazuje Ci wyniki spełniające Twoje kryteria wraz z linkami do ogłoszeń.')
print('Na każdej stronie znajduje się ponad 20 ogłoszeń. By nie były one nieaktualne, polecam sprawdzenie w ostatnich 10 stronach, maksymalnie 20.')
pages = int(input('Podaj liczbę, z ilu stron chciałbyś zebrać dane: '))
print('Zbieranie danych...')

for x in range(1,pages+1):
    gumtree_link = "https://www.gumtree.pl/s-pokoje-do-wynajecia/warszawa/page-" + str(x) + "/v1c9000l3200008p" + str(x)
    g = requests.get(gumtree_link)
    getting_links(links_table)
    getting_no_of_photos(no_of_photos_table)
    getting_prices(prices_table)
    getting_locations(locations_table)

unique_locations = sorted(list(set(locations_table)))
interesting_locations = getting_interesting_locations(unique_locations)
interesting_prices = list()
interesting_prices = getting_interesting_prices(prices_table)
interesting_no_of_photos = list()
interesting_no_of_photos = getting_interesting_no_of_photos(no_of_photos_table)

results = DataFrame({"Cena w zł" : prices_table, "Dzielnica" : locations_table,
                      "Ilość zdjęć" : no_of_photos_table, "Link" : links_table})

results = selecting_results()

prices_list = results["Cena w zł"].tolist()
locations_list = results["Dzielnica"].tolist()
no_of_photos_list = results["Ilość zdjęć"].tolist()
links_list = results["Link"].tolist()

print("\n","Świetnie :) Poniżej są pokoje do wynajęcia spełniające Twoje kryteria, wymienione w kolejności od najbardziej aktualnego (umieszczonego najpóźniej).","\n")
for x in range(len(locations_list)):
    print(locations_list[x],",",prices_list[x],"zł,",no_of_photos_list[x],"zdjęć, link:",links_list[x],"\n")

