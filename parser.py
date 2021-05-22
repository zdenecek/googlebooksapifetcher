import csv, sys, requests, json


def exit():
    inp = input(f"Opravdu si prejete ukoncit skript? (y = ano) Pocet ulozenych zapisu: {str(len(data))} \n")
    if(inp == "y"):
        quit()

def getFileName():
    return input('Zadejte soubor (nazev souboru ve slozce skriptu nebo s cestou)\n')

def searchISBNFromInput():
    for n in input('Zadejte isbn jako čísla oddělená čárkou\n').split(","):
        searchISBN(n)

def searchFromInput():
    searchText(input('Zadejte text, podle kterého budete hledat\n'))

def searchISBNFromFile():
    name = getFileName()
    with open(name, newline='', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter = ";")
        for row in reader:
            searchISBN(row[0])

def saveToFile():
    with open(getFileName(), 'w', newline='') as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerows([book.values() for book in data])

def searchISBN(isbn):
    print(f"Hledám data ke knize s ISBN: {str(isbn)}")
    response = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}')
    workResponse(response)

def searchText(q, page = 0):
    print(f"Hledám data ke knize pomocí řetězce: {q}")
    url = f'https://www.googleapis.com/books/v1/volumes?startIndex={page*40}&maxResults=40&q={requests.utils.quote(q)}'
    print(url)
    response = requests.get(url)
    next = workResponse(response)
    if(next):
        return searchText(q, page+1)

def workResponse(response):
    res = response.json()
    l = res['totalItems']
    if(l == 1):
        print("Byl nalezen jeden výsledek:")
        book = parseBook(res['items'][0])
        print(" - " + printBook(book))
    elif(l > 1):
        print(f"Bylo nalezeno více výsledků ({l}):")
        books = list(map(lambda d: parseBook(d), res['items']))
        printBooks(books)
        try:
            inp = input("Zadejte číslo vybrané knihy, d pro další stranu výsledků, x pro zrušení\n")
            if(inp == 'd'):
                return True
            index = int(inp)
            book = books[index-1]
        except Exception:
            print("Zrušeno")
            return False
    else:
        print("Kniha nebyla nalezena...")
        return false
    data.append(book)
    return False

def parseBook(jsonData):
    isbn = "*Nemá isbn"
    for e in jsonData["volumeInfo"]["industryIdentifiers"]:
        if e['type'] == "ISBN_13":
            isbn = e["identifier"]

    authors = ",".join(jsonData["volumeInfo"]['authors']) if 'authors' in jsonData["volumeInfo"] else "*Nemá autora"

    return {
        "title" : f"{jsonData['volumeInfo']['title']}",
        "isbn" : isbn,
        "authors": f"{authors}"
    }

def printBook(book):
    return(f"název: {book['title']} | autor/ři: {book['authors']} | isbn: {book['isbn']}")

def printBooks(books):
    for index, book in enumerate(books):
        left = str(index+1).rjust(4, " ")
        print(f"{left}.: {printBook(book)}")
    print('   '+'-'*60)

def deleteEntry():
    try:
        index = int(input("zadejte cislo zaznamu, ktery chcete smazat\n"))
        del data[index-1]
    except:
        print("## Chyba při mazání")


def test():
    print("** Spouštím test")
    searchISBN(9781338160215)
    searchText("Harry , Potter")
    print("** Konec testu")


data = []

options = {
    "1": searchISBNFromFile,
    "2": searchISBNFromInput,
    "3": searchFromInput,
    "p": lambda: printBooks(data),
    "s": saveToFile,
    "d": deleteEntry,
    "x": exit,
    "t": test
}

desc = f'''

Zadejte cislo pozadovane akce:
1 - hledat ISBN z csv souboru
2 - hledat ISBN zadáním
3 - hledat pomoci textu
p - ukazat dosavadní výsledky
s - uložit dosavadní výsledky do csv souboru
d - smazat jeden z výsledků v paměti
x - konec \n'''

while True:
    current = input(desc)
    options.get(current, lambda: print("Špatná možnost"))()
    print(f"** Aktuální počet prvků v paměti: {str(len(data))}")
