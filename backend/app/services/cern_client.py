import pandas as pd
import requests
import io
import os

class CERNClient:
    @staticmethod
    def extract_record_id(url: str) -> str | None:
        """Extract a CERN Open Data record ID from a record or file URL."""
        if not url:
            return None

        try:
            cleaned = url.strip()
            if "/record/" not in cleaned:
                return None

            parts = [part for part in cleaned.split("/") if part]
            if "record" not in parts:
                return None

            record_index = parts.index("record")
            if record_index + 1 >= len(parts):
                return None

            record_id = parts[record_index + 1]
            return record_id.split("?")[0].split("#")[0]
        except Exception:
            return None

    @staticmethod
    def get_data(url: str = "https://opendata.cern.ch/record/700/files/MuRun2010B_0.csv"):
        # Derive filename from the URL and save to backend/data/
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.normpath(os.path.join(base_dir, "..", "..", "data"))
        os.makedirs(data_dir, exist_ok=True)
        filename = os.path.join(data_dir, url.split("/")[-1])

        # 1. Always check if the file is already here first
        if os.path.exists(filename):
            print(f"Found {filename} locally. Skipping download.")
            return pd.read_csv(filename)

        # 2. If not local, try the CERN link with a 'Browser' identity
        try:
            print(f"Downloading from CERN: {url}")
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            with open(filename, "w", encoding="utf-8") as f:
                f.write(response.text)

            df = pd.read_csv(io.StringIO(response.text))
            print(f"Success! Data loaded and saved as {filename}")
            return df

        except Exception as e:
            print(f"CERN Server Error: {e}")
            print("\nTIP: If the download fails, open the link in your browser,")
            print(f"   save the file as '{filename}' in D:\\particlesight\\backend\\")
            return None

    @staticmethod
    def fetch_dataset_metadata(record_id: str) -> dict:
        """
        Fetches metadata for a CERN Open Data record by its ID.
        Automatically extracts the DOI, title, experiment, and year.

        Uses the CERN Open Data REST API:
        GET https://opendata.cern.ch/api/records/{record_id}

        Returns a dict with keys: title, doi, doi_url, experiment, year, description
        Returns an empty dict if the request fails.
        """
        url = f"https://opendata.cern.ch/api/records/{record_id}"
        headers = {
            "User-Agent": "ParticleSight/1.0 (independent open-source project; not affiliated with CERN)"
        }

        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()

            metadata = data.get("metadata", {})

            # Extract DOI — stored under "doi" in the metadata
            doi = metadata.get("doi", None)
            doi_url = f"https://doi.org/{doi}" if doi else None

            # Extract experiment name from the "experiment" list
            experiments = metadata.get("experiment", [])
            experiment = experiments[0] if experiments else None

            # Extract year from "date_published"
            date_published = metadata.get("date_published", None)
            year = int(date_published[:4]) if date_published else None

            # Extract description
            description = metadata.get("description", None)

            print(f"Fetched metadata for record {record_id}: DOI={doi}")

            return {
                "title": metadata.get("title", f"CERN Dataset {record_id}"),
                "doi": doi,
                "doi_url": doi_url,
                "experiment": experiment,
                "year": year,
                "description": description,
            }

        except Exception as e:
            print(f"Could not fetch metadata for record {record_id}: {e}")
            return {}
