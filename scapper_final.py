import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os # Avem nevoie de asta pentru a verifica fișierul

# --- CONFIGURĂRI ---
num_pages_to_scrape = 250 
base_url = "https://www.themoviedb.org"
list_url_base = "https://www.themoviedb.org/movie/top-rated?page="
filename = "tmdb_5000_movies.csv"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.5"
}

# --- LOGICĂ DE RESUME (RELUARE) ---
movies_data = []
start_page = 1

if os.path.exists(filename):
    # Citim fișierul existent să vedem câte filme avem
    try:
        df_existing = pd.read_csv(filename)
        existing_count = len(df_existing)
        # Calculăm pagina de la care să continuăm (20 filme pe pagină)
        start_page = (existing_count // 20) + 1
        print(f"🔄 Am găsit {existing_count} filme deja salvate.")
        print(f"⏩ Continuăm scraping-ul de la Pagina {start_page}...")
    except pd.errors.EmptyDataError:
        print("Fișierul există dar e gol. Începem de la 1.")
        start_page = 1
else:
    print("🆕 Fișier nou. Începem de la Pagina 1.")

def get_tmdb_movie_details(movie_url):
    try:
        response = requests.get(movie_url, headers=headers)
        if response.status_code != 200: return None
        soup = BeautifulSoup(response.content, "html.parser")
        
        # 1. Titlu & An
        title_section = soup.find("div", class_="title")
        if title_section:
            title_tag = title_section.find("h2").find("a")
            title = title_tag.text.strip() if title_tag else "N/A"
            year_tag = title_section.find("span", class_="release_date")
            year = year_tag.text.strip().replace('(', '').replace(')', '') if year_tag else "N/A"
        else: title, year = "N/A", "N/A"

        # 2. Rating
        rating_div = soup.find("div", class_="user_score_chart")
        rating = rating_div['data-percent'] if rating_div and 'data-percent' in rating_div.attrs else "0"
        
        # 3. Genuri
        genres_list = [g.text.strip() for g in soup.select("span.genres a")]
        genres_str = ", ".join(genres_list)

        # 4. Descriere
        overview_div = soup.find("div", class_="header_info")
        overview = "N/A"
        if overview_div:
            overview_title = overview_div.find("h3", string="Overview")
            if overview_title:
                # Căutăm următorul element, ignorând newline-uri goale
                sibling = overview_title.find_next_sibling()
                if sibling: overview = sibling.text.strip()

        # 5. Keywords
        keywords_list = [k.text.strip() for k in soup.select("section.keywords li")]
        keywords_str = ", ".join(keywords_list)

        return {
            "Title": title, "Year": year, "Rating": rating,
            "Description": overview, "Keywords": keywords_str, "Genre": genres_str
        }
    except Exception as e:
        return None

# --- LOOP PRINCIPAL ---
for page_num in range(start_page, num_pages_to_scrape + 1):
    print(f"\n📄 Procesez Pagina {page_num} din {num_pages_to_scrape}...")
    
    try:
        res = requests.get(f"{list_url_base}{page_num}", headers=headers)
    except:
        print("⚠️ Eroare conexiune. Aștept 10 secunde...")
        time.sleep(10)
        continue
    
    if res.status_code != 200:
        print(f"Skipping page {page_num} (Status {res.status_code})")
        continue
        
    soup_list = BeautifulSoup(res.content, "html.parser")
    movie_cards = soup_list.find_all("div", class_="card style_1")
    
    page_movies = [] # Stocăm doar filmele de pe pagina curentă
    
    for card in movie_cards:
        link_tag = card.find("div", class_="content").find("h2").find("a")
        if link_tag:
            full_link = base_url + link_tag['href']
            details = get_tmdb_movie_details(full_link)
            
            if details:
                page_movies.append(details)
                print(f"   [OK] {details['Title'][:25]}...")
            
            time.sleep(random.uniform(0.1, 0.3))

    # --- SALVARE IMEDIATĂ DUPĂ FIECARE PAGINĂ ---
    if page_movies:
        df_page = pd.DataFrame(page_movies)
        # Dacă fișierul nu există, scriem header-ul. Dacă există, nu scriem header.
        header_mode = not os.path.exists(filename)
        
        df_page.to_csv(filename, mode='a', header=header_mode, index=False)
        print(f"💾 Pagina {page_num} salvată în CSV.")
    
    time.sleep(random.uniform(1.0, 2.0))

print("\n✅ Scraping finalizat!")