import requests
import json

# getFarmacia fetches the data from Paginas Amarelas and returns the fields we want.
def getFarmacia():
    session = requests.session()
    lista_farmacia = []
    index = 0

    print('Getting data from PAI...\n')

    # While there are pages to be parsed increment the page number.
    while index >= 0:
        url = ('http://www.pai.pt/q/ajax/business?contentErrorLinkEnabled=true&'
        'input=Farm%C3%A1cias&what=Farm%C3%A1cias&where=&type=DOUBLE&sort=&refi'
        'ne=&char=&location=&address=&resultlisttype=A_AND_B&page={}'
        '&originalContextPath=http%3A%2F%2Fwww.pai.pt%2Fq%2Fbusiness%2Fadvanc'
        'ed%2Fwhat%2FFarm%25C3%25A1cias%2F%3FcontentErrorLin'
        'kEnabled%3Dtrue').format(index)
        result = session.get(url)
        data = json.loads(result.text)
        print(data['parameters'])
        # If flyouts list is empty it means there is no JSON data.
        if not data['data']['flyouts']:
            break;
        try:
            for farmacia in data['data']['flyouts']:
                lista_farmacia.append({'nome': farmacia['name'],
                                      'morada': farmacia['address'],
                                      'contacto': farmacia['contactDetails']['phone'],
                                      'coordenadas': farmacia['coordinate'],
                                      })
            index += 1

        except KeyError:
            break

    return lista_farmacia

 # Write data to the json file
def writeFile(lista):
    print('Writing file...\n')
    with open('farmacias.json', mode='w') as f:
        return json.dump(lista, f, ensure_ascii=False)

# Uses Google's Geocoding API to get the address details.
def getMorada(lat, lon):
    url = 'http://maps.googleapis.com/maps/api/geocode/json?latlng={},{}&sensor=true'.format(lat,lon)
    session = requests.session()
    result = session.get(url)
    data = json.loads(result.text)

    freguesia = ""
    cidade = ""
    distrito = ""

    if data['results']:
        morada = data['results'][0]['formatted_address']
        for tipo in data['results'][0]['address_components']:
            if tipo['types'][0] == 'locality':
                freguesia = tipo['long_name']
            if tipo['types'][0] == 'administrative_area_level_2':
                cidade = tipo['long_name']
            if tipo['types'][0] == 'administrative_area_level_1':
                distrito = tipo['long_name']

        print(morada)
        return {'completa': morada,
                'freguesia': freguesia,
                'cidade': cidade,
                'distrito': distrito}

# Gets the list of 'Farmacias' and the full address from google then writes it to a file.
def startGeoConvertion():
    farmacias = getFarmacia();
    new_file = []
    print('Getting address from GoogleAPI\n')
    for farmacia in farmacias:
        if farmacia['coordenadas']:
            lat = farmacia['coordenadas']['x']
            lon = farmacia['coordenadas']['y']
            morada = getMorada(lat,lon)
            if morada:
                new_file.append({'nome': farmacia['nome'],
                                 'morada': getMorada(lat,lon),
                                 'contacto': farmacia['contacto'],
                                })

    writeFile(new_file)


def main():
    startGeoConvertion()


if __name__ == "__main__":
    main()
