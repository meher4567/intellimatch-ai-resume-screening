"""Quick check of sample resume extraction"""
import json

with open('data/training/parsed_resumes_all.json', 'r') as f:
    data = json.load(f)

# Find specific resume
r = [x for x in data if x.get('file_name') == '10554236.pdf'][0]

print("Experience entries for 10554236.pdf:")
for e in r.get('experience', []):
    print(f"  - {e.get('title')} @ {e.get('company')}")
    print(f"    Dates: {e.get('start_date')} - {e.get('end_date')}")
