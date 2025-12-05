import requests
import time
import os

BASE_URL = "https://api.scb.se/OV0104/v1/doris/sv/ssd"  # engelska
# Du kan byta till svenska genom att använda "/sv/ssd" i stället för "/en/ssd"

OUTPUT_FILE = os.path.expanduser("~/mix/SCB_data.txt")
REQUEST_DELAY = 0.5  # Delay between requests in seconds

def write_output(file, message):
    """Helper function to write to both console and file."""
    print(message)
    file.write(message + "\n")

def list_scb_databases():
    """
    Hämtar och skriver ut alla 'databaser' i SCB:s API enligt hierarkin:
    Subject (huvudområde) -> Subgroup (underområde) -> Table (tabellkod).
    Sparar resultatet till ~/mix/SCB_data.txt
    """
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            write_output(f, f"SCB API Data Structure - Generated at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            write_output(f, "=" * 80)

            response = requests.get(BASE_URL)
            response.raise_for_status()
            subjects = response.json()

            for subject in subjects:
                subject_code = subject.get("id")
                subject_text = subject.get("text")
                write_output(f, f"\n=== {subject_code}: {subject_text} ===")

                # Add delay to respect rate limits
                time.sleep(REQUEST_DELAY)

                # Hämta underområden (subgroups) för varje subject
                subgroup_url = f"{BASE_URL}/{subject_code}"
                try:
                    subgroup_resp = requests.get(subgroup_url)
                    subgroup_resp.raise_for_status()
                    subgroups = subgroup_resp.json()
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:
                        write_output(f, "  Rate limit reached, waiting 5 seconds...")
                        time.sleep(5)
                        continue
                    else:
                        raise

                for subgroup in subgroups:
                    subgroup_code = subgroup.get("id")
                    subgroup_text = subgroup.get("text")
                    write_output(f, f"  - {subgroup_code}: {subgroup_text}")

                    # Add delay to respect rate limits
                    time.sleep(REQUEST_DELAY)

                    # (Valfritt) hämta tabeller inom varje subgroup
                    table_url = f"{subgroup_url}/{subgroup_code}"
                    try:
                        table_resp = requests.get(table_url)
                        table_resp.raise_for_status()
                        tables = table_resp.json()
                        for table in tables:
                            table_id = table.get("id")
                            table_text = table.get("text")
                            write_output(f, f"      * {table_id}: {table_text}")
                    except requests.exceptions.HTTPError as e:
                        if e.response.status_code == 429:
                            write_output(f, f"    Rate limit reached for {subgroup_code}, skipping...")
                            time.sleep(2)
                            continue
                        else:
                            write_output(f, f"    Error fetching tables for {subgroup_code}: {e}")
                            continue

            write_output(f, f"\n{'=' * 80}")
            write_output(f, f"Data saved to {OUTPUT_FILE}")

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to SCB API: {e}")
    except IOError as e:
        print(f"Error writing to file: {e}")


if __name__ == "__main__":
    list_scb_databases()
