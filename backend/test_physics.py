from app.services.cern_client import CERNClient

print("Testing CERN Client...")
df = CERNClient.get_data()

if df is not None:
    print(f"Success! Found {len(df)} rows of particle data.")
    print(df.head()) # Shows the first 5 rows