import requests
import json
import os
import time

BASE_URL = "https://api.scb.se/OV0104/v1/doris/sv/ssd"
TABLE_ID = "AM0211E"
OUTPUT_FILE = os.path.expanduser("~/SCB_strcture_AM0211E.txt")

def get_table_metadata(table_id):
    """
    Hämtar metadata/datastruktur för en specifik tabell från SCB API.

    Args:
        table_id: Tabell-ID (t.ex. 'AM0211E')

    Returns:
        dict: Metadata i JSON-format
    """
    # Endpoint för att hämta metadata
    metadata_url = f"{BASE_URL}/AM/AM0211/{table_id}"

    print(f"Hämtar metadata från: {metadata_url}")

    try:
        response = requests.get(metadata_url)
        response.raise_for_status()
        metadata = response.json()
        return metadata
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"Tabellen {table_id} hittades inte. Kontrollera tabell-ID och sökväg.")
        elif e.response.status_code == 429:
            print("För många förfrågningar. Väntar 5 sekunder...")
            time.sleep(5)
            return get_table_metadata(table_id)
        else:
            print(f"HTTP-fel: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Anslutningsfel: {e}")
        return None

def save_metadata_to_file(metadata, filepath):
    """
    Sparar metadata till fil i JSON-format.

    Args:
        metadata: Metadata-dict att spara
        filepath: Sökväg till output-fil
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            # Skriv metadata som formaterad JSON
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Resultat sparat till: {filepath}")
    except IOError as e:
        print(f"Fel vid skrivning till fil: {e}")

def print_structure_summary(metadata):
    """
    Skriver ut en sammanfattning av tabellstrukturen.
    """
    if not metadata:
        return

    print("\n" + "=" * 80)
    print(f"DATASTRUKTUR FÖR TABELL: {TABLE_ID}")
    print("=" * 80)

    # Titel
    if 'title' in metadata:
        print(f"\nTitel: {metadata['title']}")

    # Variabler/dimensioner
    if 'variables' in metadata:
        print(f"\nAntal variabler: {len(metadata['variables'])}")
        print("\nVariabler:")
        for var in metadata['variables']:
            var_code = var.get('code', 'N/A')
            var_text = var.get('text', 'N/A')
            num_values = len(var.get('values', []))
            print(f"  - {var_code}: {var_text} ({num_values} värden)")

    # Uppdateringsinformation
    if 'updated' in metadata:
        print(f"\nSenast uppdaterad: {metadata['updated']}")

    print("\n" + "=" * 80)

def main():
    """
    Huvudfunktion som kör scriptet.
    """
    print(f"Hämtar datastruktur för tabell {TABLE_ID}...")
    print(f"API Base URL: {BASE_URL}\n")

    # Hämta metadata
    metadata = get_table_metadata(TABLE_ID)

    if metadata:
        # Skriv ut sammanfattning
        print_structure_summary(metadata)

        # Visa JSON i konsolen (begränsat)
        print("\nJSON-data (förhandsvisning):")
        print(json.dumps(metadata, indent=2, ensure_ascii=False)[:1000] + "...")

        # Spara till fil
        save_metadata_to_file(metadata, OUTPUT_FILE)

        print(f"\nFullständig JSON-struktur finns i filen.")
    else:
        print("\n✗ Kunde inte hämta metadata.")

if __name__ == "__main__":
    main()
