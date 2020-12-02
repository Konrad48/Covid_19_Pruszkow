#Sanepid numbers

import requests
import csv
import os
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

def scrape_links(url_san = "http://pruszkow.psse.waw.pl/3367"): #scapuje linki do konkretnych komunikatów
    page_num = 2
    url = url_san
    r = requests.get(url)
    urls = []
    while r.status_code != 404:
        r_html = r.text
        soup = BeautifulSoup(r_html, features="html.parser")

        for h4_tag in soup.find_all("h4"): #szuka linku i czasu w każdym z tagów h4
            a_tag = h4_tag.find("a")
            date = h4_tag.find_previous_sibling("p").find("time").contents[0]
            if date == "26.03.2020":
                print("Koniec jednolitych komunikatów, kończę szukanie linków")
                return urls
            print("Pobieranie linku do komunikatu z dnia: ", date)

            filename = "old_san_data.csv"
            if not os.path.exists(filename):
                open(filename, 'w').close()
            with open(filename, "r", newline="") as csvfile: #szuka powtórek w pliku csv
                filereader = csv.reader(csvfile)
                if "sytuacja-epidemiologiczna" in a_tag.attrs["href"] or "sytuacje" in a_tag.attrs["href"] or "koronawirus-komunikat" in a_tag.attrs["href"]:
                    urls.append(url_san[:-4] + a_tag.attrs["href"])
                    for row in filereader:
                        if date in row and urls[-1] in row:
                            print("Znaleziono powtarzającą się datę, kończę szukanie linków")
                            csvfile.close()
                            return urls
        url = url_san + "?page_a4=%d" %page_num #przechodzi do kolejnej strony
        page_num += 1

        r = requests.get(url)
    return urls

def scrape_inf(url):
    #zapisuje do pliku informacje o zakażonych
    r = requests.get(url) # pobieranie strony
    r_html = r.text
    soup = BeautifulSoup(r_html, features="html.parser")
    print(url)
    filename = "old_san_data.csv"
    with open(filename, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)

        data = soup.find("time")
        data = data.contents[0]
        #Szukanie tagów <li>
        lintexts = soup.find_all(name='li')
        for lintext in lintexts:
            if "Łączna liczba przypadków" in lintext.text:
                infected = int(str(lintext.contents[-2].text).strip())
                print("Nowe dane na dzień", data, "\b:", infected)
                writer.writerow([data, url, infected])
            elif "potwierdzonych laboratoryjnie z wynikiem dodatnim" in lintext.text:
                infected = int(str(lintext.contents[-2].text).strip())
                print("Nowe dane na dzień", data, "\b:", infected)
                writer.writerow([data, url, infected])

    csvfile.close()

def main():
    #scrape_inf("http://pruszkow.psse.waw.pl/3367/sytuacja-epidemiologiczna-na-terenie-powiatu-pruszkowskiego-na-dzien-23-04-2020") #test
    # Tu dane ze strony są zapisywane do pliku csv jeśli występują nowe
    #Powiaty, na razie tylko Pruszkowski
    links = {"http://pruszkow.psse.waw.pl/3367": "Pruszkowski"}
    for link in links:
        print("Powiat", links.get(link))
        #Szukanie nowych linków i zapisywanie do listy
        archiwum = scrape_links(link)[::-1]
        #Szukanie liczby zakażonych w komunikatach
        for url in archiwum:
            scrape_inf(url)

    # Od tego momentu wszystkie dane są wyciągane z pliku csv
    fig, ax = plt.subplots()  # Tworzenie wykresu z pojedynczymi osiami.
    daysinf = []
    infected = []
    filename = "old_san_data.csv"
    with open(filename, "r", newline="") as csvfile:
        filereader = csv.reader(csvfile)
        for link in links:
            csvfile.seek(0)
            for row in filereader:
                if link in row[1]:
                    daysinf.append(row[0])
                    infected.append(int(row[2]))
            ax.plot(range(-len(daysinf)+1, 1), infected, label=links.get(link))  # Nanoszenie danych na wykres
            print("Na dzień", daysinf[-1], "w powiecie", links.get(link), "\bm zakażonych: ", infected[-1])
            daysinf.clear()
            infected.clear()


    ax.set_xlabel('Dzień')  # Add an x-label to the axes.
    ax.set_ylabel('Zakażeni')  # Add a y-label to the axes.
    plt.grid(True)
    ax.legend()
    plt.show()
if __name__ == "__main__":
    main()