import json
import pymongo

# Conectamos a la base de datos
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client.bolita
charada = db.charada

def buscar_charada(busqueda):

    # Lista para almacenar los resultados encontrados
    resultados = []

    # Buscamos la palabra clave en todos los simbolos de todas las charadas
    result = charada.find({ "simbolos": { "$regex": f".*{busqueda}.*", "$options": "i" } })

    # Agregamos los resultados a la lista
    for doc in result:
        resultados.append(doc)

    # Mostramos los resultados encontrados
    if resultados == [None]:
        resul = "No se encontraron resultados para la palabra clave"
    else:
        resul = ""
        for resultado in resultados:
            resul += f"Numero: {resultado['numero']} \n"
            resul += "Simbolos: \n"
            for simbolo in resultado['simbolos']:
                resul += f"\t{simbolo}, "
                
            resul += f"\n\n"

    return resul

def buscar_numero(busqueda):

    # Lista para almacenar los resultados encontrados
    resultados = []

    # Buscamos la palabra clave en todos los simbolos de todas las charadas
    result = charada.find_one({'numero': int(busqueda)})

    # Agregamos los resultados a la lista
    resultados.append(result)
    print(resultados)

    # Mostramos los resultados encontrados
    if resultados == [None]:
        resul = "No se encontraron resultados para este número"
    else:
        resul = ""
        for resultado in resultados:
            resul += f"Numero: {resultado['numero']} \n"
            resul += "Simbolos: \n"
            for simbolo in resultado['simbolos']:
                resul += f"\t{simbolo}, "

    return resul