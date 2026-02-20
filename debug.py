import requests
from bs4 import BeautifulSoup

url = "https://news.detik.com/internasional"
print(f"📡 Mengakses {url}...")
response = requests.get(url)

print(f"📊 Status Code: {response.status_code}")
if response.status_code != 200:
    print("❌ Gagal mengambil halaman.")
    exit()

print("📄 Cuplikan HTML (500 karakter pertama):")
print(response.text[:500])
print("="*50)

soup = BeautifulSoup(response.text, 'html.parser')

# Cari elemen dengan class media__link
print("🔍 Mencari <a class='media__link'>...")
judul_element = soup.find('a', class_='media__link')

print(f"🔎 Apakah judul_element None? {judul_element is None}")
if judul_element:
    print("✅ Elemen DITEMUKAN!")
    # Tampilkan atribut dan struktur dalamnya
    print("Tag:", judul_element.name)
    print("Class:", judul_element.get('class'))
    print("Href:", judul_element.get('href'))
    print("Isi HTML dalam elemen:\n", judul_element.prettify()[:500])
    
    # Ambil teks dengan berbagai cara
    teks_dengan_get_text = judul_element.get_text(strip=True)
    teks_langsung = judul_element.text.strip()
    print(f"📝 Teks dengan get_text(strip=True): '{teks_dengan_get_text}'")
    print(f"📝 Teks dengan .text.strip(): '{teks_langsung}'")
    
    # Coba cari div di dalamnya
    div_dalam = judul_element.find('div', class_='replace_title')
    if div_dalam:
        print("✅ Div replace_title ditemukan di dalam!")
        print("📝 Teks dari div:", div_dalam.get_text(strip=True))
    else:
        print("❌ Div replace_title tidak ditemukan di dalam.")
else:
    print("❌ Elemen tidak ditemukan. Coba cari semua elemen dengan class media__link:")
    semua_link = soup.find_all('a', class_='media__link')
    print(f"Ditemukan {len(semua_link)} elemen.")
    for i, link in enumerate(semua_link[:3]):  # tampilkan 3 pertama
        print(f"Elemen ke-{i+1}: {link.prettify()[:100]}...")

print("\n🔬 Inspeksi Tipe Data (selalu):")
print("Tipe response:", type(response))
print("Tipe soup:", type(soup))
print("Tipe judul_element:", type(judul_element))
if 'teks_dengan_get_text' in locals():
    print("Tipe teks:", type(teks_dengan_get_text))