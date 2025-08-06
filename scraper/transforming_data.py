import pandas as pd

df = pd.read_csv("data.csv")

def normalize_div(df):
    if 'ï»¿Div' in df.columns:
        df['Div'] = df['ï»¿Div'].combine_first(df.get('Div'))
        df.drop(columns='ï»¿Div', inplace=True)
    return df

def throw_lines(df, min_value=3):
    return df[df.count(axis=1) >= min_value]

def normalize_year(df):
    df['Date'] = df['Date'].astype(str)
    def change_year(date_str):
        parts = date_str.split('/')
        if len(parts) != 3:
            return None 
        day, month, year = parts
        if len(year) == 2:
            year_int = int(year)
            if 0 <= year_int <= 26:
                year = f"20{year}"
            else:
                year = f"19{year}"

        return f"{day}/{month}/{year}"
    df['Date'] = df['Date'].apply(change_year)
    df = df[df['Date'].notna()]
    return df

def keep_years(df, min_y=2020, max_y=2026):
    return df[df['Date'].str.endswith(tuple(str(y) for y in range(min_y, max_y+1)))]

def throw_unamed(df):
    return df.loc[:, df.columns.notna() & ~df.columns.str.startswith('Unnamed')]

#df = normalize_div(df)
df = throw_lines(df)
df = normalize_year(df)
df = keep_years(df)
df = throw_unamed(df)

df.to_csv("data_2020_2026.csv")