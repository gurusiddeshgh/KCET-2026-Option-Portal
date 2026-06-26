import pandas as pd

df = pd.read_excel('KEA_2025_Master_GM_CutOffs_Round123.xlsx')
df['course_code'] = df['Course Name'].str[:10].str.upper().str.replace(' ', '_')

# Check for college-course-round combinations
df['key'] = df['College Name'].str.extract(r'\((\w+)\)')[0] + '|' + df['course_code']

print("Checking for duplicate college-course combinations...")
print()

# Check Round 1 duplicates
for round_col in ['Round 1 Rank', 'Round 2 Rank', 'Round 3 Rank']:
    round_no = round_col.split()[1]
    df_valid = df[df[round_col] != '--'].copy()
    dupes = df_valid[df_valid.duplicated(subset=['key', round_col], keep=False)].sort_values('key')
    print(f"\n{round_col}: {len(dupes)} potential duplicates")
    if len(dupes) > 0:
        print(dupes[['College Name', 'Course Name', round_col]].head(20))

# More detailed check
print("\n\nDetailed check for E004 ELECTRONIC:")
df_e004 = df[df['College Name'].str.contains('E004', na=False)]
print(f"Total E004 entries: {len(df_e004)}")
e004_elec = df_e004[df_e004['Course Name'].str.contains('ELECTRONIC', na=False, case=False)]
print(f"E004 with ELECTRONIC: {len(e004_elec)}")
print(e004_elec[['College Name', 'Course Name', 'Round 1 Rank', 'Round 2 Rank', 'Round 3 Rank']])
