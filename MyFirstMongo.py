import pymongo

myclient = pymongo.MongoClient('mongodb://localhost:27017/')

mydb = myclient['test']

employee_data = {
    "name": "Astrid Lindgren",
    "position": "Författare",

    # Första nivån av nästling (Nested Document)
    "address": {
        "street": "Vulcans Väg 12",
        "city": "Vimmerby",
        "zip": "598 33",
        "country": "Sverige"
    },

    # Andra nivån av nästling (Array of Embedded Documents)
    "skills": [
        {"name": "Storytelling", "level": "Expert"},
        {"name": "Editing", "level": "Advanced"}
    ],

    "start_year": 1944
}

# Använda PyMongo (antar att 'db' är din databas)
mydb.olle.insert_one(employee_data)
