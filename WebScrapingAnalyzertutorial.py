import requests
from bs4 import BeautifulSoup

url = "https://news.detik.com/internasional"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Gunakan headers!
response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("✅ Berhasil mengambil halaman")
else:
    print("❌ Gagal, status code:", response.status_code)
    exit()

#parsing html
soup = BeautifulSoup(response.text, 'html.parser')

#cari semua artikel berita
artikel_list = soup.find_all('article', class_='list-content__item')
print(f"Ditemukan {len(artikel_list)} artikel")

judul_list = []
for artikel in artikel_list:
    judul = None
    judul_tag = artikel.find(class_='media__title')
    if judul_tag:
        a_tag = judul_tag.find('a')
        if a_tag:
           judul = a_tag.get_text(strip=True)

    #jika tidak ketemu
    if not judul:
        judul_tag = artikel.find('h3', class_='list-content__title')
        if judul_tag:
            a_tag = judul_tag.find('a')
            if a_tag:
                judul = a_tag.get_text(strip=True)

    #simpan jika judul berhasil ditemukan di pola manapun
    if judul:
        judul_list.append(judul)

#Output
print(f"\n Jumlah Judul Ditemukan : {len(judul_list)}")
print("Judul Pertama:")
for i, judul in enumerate(judul_list[:5]):
    print(f"{i+1}. {judul}")
    

print("\n🔍 Inspeksi Tipe Data:")
print("Tipe judul_list:", type(judul_list))
if judul_list:
    print("Tipe elemen pertama:", type(judul_list[0]))
    print("Contoh isi elemen pertama (string):", repr(judul_list[0]))
else:
    print("judul_list kosong, periksa selektor HTML kamu!") 

#lanjutan belajar fase 2
#membersihkan hasil scraping judul
judul_bersih = []
for judul in judul_list:
    #ubah ke lowercase
    judul = judul.lower()
    #hapus tanda baca
    judul =' '.join(judul.split())

    judul_bersih.append(judul)

print("\nJudul setelah dibersihkan:", judul_bersih[:3])

# Inspeksi tipe data
print("\nTipe judul_bersih:", type(judul_bersih))
print("Tipe elemen pertama:", type(judul_bersih[0]))
print("Contoh isi:", repr(judul_bersih[0]))

#extended fitur
#cek jumlah unik
judul_unik = len(set(judul_bersih))
print(f"\nJumlah judul setelah dibersihkan: {len(judul_bersih)}")
print(f"Jumlah judul unik: {judul_unik}")

if len(judul_bersih) != judul_unik:
    print("👉 Ada duplikat! Mari kita buat list tanpa duplikat.")
    judul_unik = list(set(judul_bersih)) 
    print(f"Contoh judul unik (3 pertama): {judul_unik[:3]}")
else:
    print("✅ Tidak ada duplikat.")

#cari artikel yang tanpa judul
print("\n Investigasi artikel tanpa judul:")
for i, artikel in enumerate(artikel_list):
    #cek apakah ada artikel ini tidak ada yang mempunyai class media title
    if not artikel.find(class_='media__title'):
        print(f"Artikel ke-{i} tidak memilik judul. Cuplikan HTML:")
        print(artikel.prettify()[:500])
        print("-" * 50)