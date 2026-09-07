import pandas as pd


df = pd.read_csv("data/Invoice.csv")

# Build a mapping: each unique real Customer Name -> a fake label
unique_names = df["Customer Name"].dropna().unique()
name_map = {name: f"Customer {chr(65+i)}" if i < 26 else f"Customer {i+1}" 
            for i, name in enumerate(unique_names)}

df["Customer Name"] = df["Customer Name"].map(name_map).fillna(df["Customer Name"])

# Remove personal contact info (emails/phone numbers) found in these columns
sensitive_contact_cols = [
    "Primary Contact EmailID",
    "Primary Contact Mobile",
    "Primary Contact Phone"
]
for col in sensitive_contact_cols:
    if col in df.columns:
        df[col] = None

# Save anonymized version with the SAME filename, into sample_data/
df.to_csv("sample_data/Invoice.csv", index=False)

print("Name mapping used (keep this local, don't commit it):")
print(name_map)
print("\nBlanked sensitive contact columns:", sensitive_contact_cols)

sample = pd.read_csv("sample_data/Invoice.csv")
print("Sample shape:", sample.shape)                          # should be (160, 112) - same as original
print("Sample Product ID non-null:", sample['Product ID'].notna().sum())  # should be 156
print("Sample Item Total sum:", sample['Item Total'].sum())   # should be 2235380.0 - identical