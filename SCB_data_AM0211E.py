import requests
import json
import os
import time

BASE_URL = "https://api.scb.se/OV0104/v1/doris/sv/ssd"
TABLE_GROUP = "AM0211E"
# De två tabellerna under AM0211E
TABLES = ["LonForArbSkattSektor", "LonForArbSkattNaring"]
OUTPUT_FILE = os.path.expanduser("~/mix/SCB_data_AM0211E.txt")

def find_table_in_hierarchy(table_id):
    """
    Söker igenom SCB API-hierarkin för att hitta en tabell.
    """
    # Börja med AM-huvudkategorin
    print(f"Söker efter tabell {table_id} i API-hierarkin...")

    try:
        # Hämta alla undergrupper i AM
        am_url = f"{BASE_URL}/AM"
        response = requests.get(am_url)
        response.raise_for_status()
        am_groups = response.json()

        print(f"Hittar {len(am_groups)} grupper i AM")

        # Sök igenom varje undergrupp
        for group in am_groups:
            group_id = group.get('id')
            print(f"  Kontrollerar grupp: {group_id} - {group.get('text')}")

            time.sleep(0.3)  # Rate limiting

            group_url = f"{BASE_URL}/AM/{group_id}"
            group_resp = requests.get(group_url)
            group_resp.raise_for_status()
            items = group_resp.json()

            # Kolla om något av items är vår tabell
            for item in items:
                if item.get('id') == table_id:
                    print(f"\n✓ Hittade tabellen i: AM/{group_id}/{table_id}")
                    print(f"  Titel: {item.get('text')}")
                    return f"AM/{group_id}/{table_id}"

        print(f"\n✗ Tabellen {table_id} hittades inte i AM-hierarkin")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Fel vid sökning: {e}")
        return None

def get_table_structure(table_path):
    """
    Hämtar tabellstruktur för att se vilka variabler som finns.

    Args:
        table_path: Full sökväg till tabellen (t.ex. "AM/AM0211/AM0211E/LonForArbSkattSektor")
    """

    metadata_url = f"{BASE_URL}/{table_path}"

    try:
        print(f"\nHämtar metadata från: {metadata_url}")
        response = requests.get(metadata_url)
        response.raise_for_status()
        result = response.json()

        # Kontrollera om vi fick metadata (dict med 'variables') eller en lista
        if isinstance(result, dict) and 'variables' in result:
            return result
        elif isinstance(result, list):
            print(f"Fick en lista med {len(result)} objekt:")
            for item in result[:5]:  # Visa första 5
                print(f"  - {item.get('id')}: {item.get('text')}")
            return None
        else:
            print(f"Oväntat format: {type(result)}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Fel vid hämtning av struktur: {e}")
        return None

def get_metadata_for_table(table_id):
    """
    Hämtar metadata för en specifik tabell genom att göra en tom POST-förfrågan.
    """
    metadata_url = f"{BASE_URL}/AM/AM0211/{table_id}"

    try:
        # SCB API returnerar metadata när man gör GET på tabell-endpoint
        response = requests.get(metadata_url)
        response.raise_for_status()
        result = response.json()

        # Om vi fortfarande får en lista, kolla om det är metadata-struktur
        if isinstance(result, dict) and 'variables' in result:
            return result
        else:
            print(f"Oväntat format från API: {type(result)}")
            print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Fel vid hämtning av metadata: {e}")
        return None

def create_query(metadata, limit_values=True):
    """
    Skapar en query baserat på tabellens metadata.

    Args:
        metadata: Metadata från tabellen
        limit_values: Om True, begränsa antalet värden per variabel

    Returns:
        dict: Query-objekt för POST-förfrågan
    """
    query = {
        "query": [],
        "response": {
            "format": "json"
        }
    }

    if not metadata or 'variables' not in metadata:
        return query

    for var in metadata['variables']:
        var_code = var.get('code')
        var_values = var.get('values', [])

        # För tidsdimensioner eller om vi vill ha all data
        if var_code == 'Tid' or var_code == 'ContentsCode':
            # Ta alla värden
            selected_values = var_values
        elif limit_values and len(var_values) > 10:
            # Begränsa till senaste/första 10 värdena för stora dimensioner
            selected_values = var_values[-10:]
        else:
            selected_values = var_values

        query["query"].append({
            "code": var_code,
            "selection": {
                "filter": "item",
                "values": selected_values
            }
        })

    return query

def get_table_data(table_id, query, table_path):
    """
    Hämtar data från tabellen med specificerad query.

    Args:
        table_id: Tabell-ID
        query: Query-objekt
        table_path: Full sökväg till tabellen

    Returns:
        dict: Data från tabellen
    """
    data_url = f"{BASE_URL}/{table_path}"

    print(f"Skickar POST-förfrågan till: {data_url}")
    print(f"Query innehåller {len(query.get('query', []))} variabler")

    try:
        response = requests.post(data_url, json=query)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print("För många förfrågningar. Väntar 5 sekunder...")
            time.sleep(5)
            return get_table_data(table_id, query, table_path)
        elif e.response.status_code == 413:
            print("Förfrågan för stor. Försök begränsa datamängden.")
            return None
        else:
            print(f"HTTP-fel {e.response.status_code}: {e}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Anslutningsfel: {e}")
        return None

def process_single_table(table_id, table_path, limit_values=True):
    """
    Hämtar och returnerar data för en enskild tabell.

    Returns:
        dict: Data från tabellen eller None om det misslyckades
    """
    print(f"\n{'='*80}")
    print(f"Bearbetar tabell: {table_id}")
    print(f"{'='*80}")

    # 1. Hämta tabellstruktur
    print("Steg 1: Hämtar tabellstruktur...")
    metadata = get_table_structure(table_path)

    if not metadata:
        print("✗ Kunde inte hämta tabellstruktur.")
        return None

    # Kontrollera att vi har rätt format
    if not isinstance(metadata, dict):
        print(f"✗ Oväntat format på metadata: {type(metadata)}")
        return None

    if 'variables' not in metadata:
        print("✗ Metadata saknar 'variables' fält")
        print(f"Tillgängliga fält: {list(metadata.keys())}")
        return None

    print(f"✓ Struktur hämtad. Tabellen innehåller {len(metadata.get('variables', []))} variabler.")

    # Visa variabler
    print("\nVariabler i tabellen:")
    for var in metadata.get('variables', []):
        var_code = var.get('code')
        var_text = var.get('text')
        num_values = len(var.get('values', []))
        print(f"  - {var_code}: {var_text} ({num_values} värden)")

    # 2. Skapa query
    print("\nSteg 2: Skapar datahämtnings-query...")
    query = create_query(metadata, limit_values=limit_values)
    print(f"✓ Query skapad")

    # 3. Hämta data
    print("\nSteg 3: Hämtar data från API (detta kan ta en stund)...")
    data = get_table_data(table_id, query, table_path)

    if not data:
        print("✗ Kunde inte hämta data.")
        return None

    print(f"✓ Data hämtad!")
    if 'data' in data:
        print(f"  Antal datapunkter: {len(data['data']):,}")

    return {
        'table_id': table_id,
        'metadata': metadata,
        'data': data
    }

def save_all_data_to_file(all_table_data, filepath):
    """
    Sparar data från alla tabeller till en fil.
    """
    try:
        output = []
        output.append("=" * 100)
        output.append(f"DATA FRÅN TABELLGRUPP: {TABLE_GROUP}")
        output.append(f"Genererad: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"Antal tabeller: {len(all_table_data)}")
        output.append("=" * 100)
        output.append("")

        for table_info in all_table_data:
            table_id = table_info['table_id']
            data = table_info['data']

            output.append("\n" + "=" * 100)
            output.append(f"TABELL: {table_id}")
            output.append("=" * 100)
            output.append("")

            # Tabell-information
            if 'columns' in data:
                output.append(f"Antal kolumner: {len(data['columns'])}")
                output.append("Kolumner:")
                for col in data['columns']:
                    output.append(f"  - {col.get('code', 'N/A')}: {col.get('text', 'N/A')}")
                output.append("")

            # Data summary
            if 'data' in data:
                output.append(f"Antal datapunkter: {len(data['data']):,}")
                output.append("")
                output.append("DATA (första 20 raderna):")
                output.append("-" * 100)

                # Visa först 20 rader som exempel
                for i, row in enumerate(data['data'][:20]):
                    key_parts = []
                    if 'key' in row:
                        key_parts = row['key']
                    values = row.get('values', [])
                    output.append(f"  {' | '.join(key_parts)} => {values}")

                if len(data['data']) > 20:
                    output.append(f"  ... ({len(data['data']) - 20} fler rader)")

            output.append("")
            output.append("-" * 100)
            output.append("FULLSTÄNDIG JSON-DATA FÖR DENNA TABELL:")
            output.append("-" * 100)
            output.append(json.dumps(data, indent=2, ensure_ascii=False))
            output.append("")

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(output))

        print(f"\n✓ All data sparad till: {filepath}")

        # Visa filstorlek
        file_size = os.path.getsize(filepath)
        print(f"  Filstorlek: {file_size:,} bytes ({file_size / 1024:.1f} KB)")

    except IOError as e:
        print(f"Fel vid skrivning till fil: {e}")

def main():
    """
    Huvudfunktion - hämtar data från alla tabeller i AM0211E.
    """
    print(f"Hämtar data från tabellgrupp {TABLE_GROUP}...")
    print(f"Detta kommer att hämta data från {len(TABLES)} tabeller:")
    for table in TABLES:
        print(f"  - {table}")
    print()

    # Hitta bas-sökvägen
    base_path = find_table_in_hierarchy(TABLE_GROUP)
    if not base_path:
        print("✗ Kunde inte hitta tabellgruppen i API-hierarkin")
        return

    all_table_data = []

    # Hämta data från varje tabell
    for table_id in TABLES:
        table_path = f"{base_path}/{table_id}"

        # limit_values=True för att begränsa datamängden (ändra till False för all data)
        table_data = process_single_table(table_id, table_path, limit_values=True)

        if table_data:
            all_table_data.append(table_data)

        # Paus mellan tabeller för att respektera rate limits
        if table_id != TABLES[-1]:  # Inte sista tabellen
            print("\nVäntar 2 sekunder innan nästa tabell...")
            time.sleep(2)

    if not all_table_data:
        print("\n✗ Kunde inte hämta data från någon tabell.")
        return

    # Spara all data till fil
    print(f"\n{'='*80}")
    print("Sparar all data till fil...")
    print(f"{'='*80}")
    save_all_data_to_file(all_table_data, OUTPUT_FILE)
    print()
    print("✓ Klart! All data från båda tabellerna är sparad.")

if __name__ == "__main__":
    main()
