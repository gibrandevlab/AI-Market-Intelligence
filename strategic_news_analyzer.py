import requests
from bs4 import BeautifulSoup
import re
import google.genai as genai 
import os
import json
from dotenv import load_dotenv

# Load Environment
load_dotenv()

# Konfigurasi Gemini AI
api_key_gemini = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key_gemini)
MODEL_NAME = "gemini-2.5-flash"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Scraping List Berita
def get_indeks_berita():
    url = "https://news.detik.com/internasional"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        artikel_list = soup.find_all('article', class_='list-content__item')
        
        results = []
        seen = set()
        
        for artikel in artikel_list:
            judul_tag = artikel.find(class_='media__title') or artikel.find('h3', class_='list-content__title')
            if judul_tag and judul_tag.find('a'):
                a_tag = judul_tag.find('a')
                judul_teks = re.sub(r'\s+', ' ', a_tag.get_text(strip=True))
                url_news = a_tag['href']
                
                if judul_teks.lower() not in seen:
                    seen.add(judul_teks.lower())
                    results.append({
                        "id": len(results) + 1,
                        "judul": judul_teks,
                        "url": url_news
                    })
        return results
    except Exception as e:
        print(f"❌ Error Scraping Indeks: {e}")
        return []

def pilih_berita_terbaik(daftar_berita):
    # Kita hanya kirim ID dan Judul biar hemat token
    formatted_list = "\n".join([f"{b['id']}. {b['judul']}" for b in daftar_berita])
    
    prompt = f"""Analisis daftar judul berita internasional berikut.
Pilih 1 berita yang memiliki dampak paling signifikan terhadap EKONOMI GLOBAL, GEOPOLITIK, atau PASAR MODAL.

Daftar Berita:
{formatted_list}

Berikan respons hanya dalam format JSON:
{{
  "id_terpilih": nomor_id,
  "alasan": "penjelasan singkat",
  "kategori": "ekonomi/geopolitik/keduanya"
}}
"""
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"❌ Error AI Selection: {e}")
        return None

def scrape_konten_detail(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        # Selector body berita
        body = soup.find('div', class_='detail__body-text')
        if body:
            # Hapus elemen yang tidak perlu
            for extra in body.find_all(['table', 'script', 'style']):
                extra.decompose()
            return body.get_text(separator=' ', strip=True)
        return None
    except Exception as e:
        print(f"❌ Error Detail Scraping: {e}")
        return None

def analisis_mendalam(judul, konten, alasan):
    prompt = f"""
Tugas: Analisis dampak berita berikut terhadap pasar saham Indonesia (IHSG).
Judul: {judul}
Alasan Pemilihan: {alasan}

Konten Berita:
{konten[:4000]}

Berikan analisis mendalam dalam format JSON:
{{
    "ringkasan": "3 kalimat ringkasan",
    "analisis_sektor": "sektor apa yang terpengaruh",
    "rekomendasi_saham": {{
        "positif": [{{"kode": "TIKER", "alasan": "..."}}],
        "negatif": [{{"kode": "TIKER", "alasan": "..."}}]
    }},
    "skor_dampak": "1-10"
}}
"""
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e)}

# ===== MAIN EXECUTION =====
def main():
    print("🚀 Memulai pencarian berita 'High Impact'...")
    
    # 1. Scrape Indeks
    daftar = get_indeks_berita()[:15] # Ambil 15 berita terbaru
    if not daftar:
        print("❌ Tidak ada berita ditemukan.")
        return

    # 2. Minta Gemini pilih 1 yang paling oke
    print("🧠 AI sedang memilih berita paling berpengaruh...")
    pilihan = pilih_berita_terbaik(daftar)
    
    if not pilihan:
        print("❌ AI gagal memilih berita.")
        return

    # 3. Cari URL berdasarkan ID yang dipilih AI
    berita_final = next((b for b in daftar if b['id'] == pilihan['id_terpilih']), None)
    
    if berita_final:
        print(f"✅ Terpilih: {berita_final['judul']}")
        
        # 4. Scrape Detail
        print("📄 Mengambil konten lengkap...")
        konten = scrape_konten_detail(berita_final['url'])
        
        if konten:
            # 5. Analisis Akhir
            print("📊 Melakukan analisis dampak pasar...")
            hasil = analisis_mendalam(berita_final['judul'], konten, pilihan['alasan'])
            
            # 6. Output Final
            final_report = {
                "info_dasar": berita_final,
                "alasan_pilih": pilihan['alasan'],
                "analisis_ai": hasil
            }
            print("\n" + "="*50)
            print("🏆 LAPORAN ANALISIS STRATEGIS")
            print("="*50)
            print(json.dumps(final_report, indent=2, ensure_ascii=False))
        else:
            print("❌ Gagal mengambil detail konten.")
    else:
        print("❌ ID yang dipilih AI tidak valid.")

if __name__ == "__main__":
    main()