def menghitung_volume_kubus(r):
    """function ini untuk menghitung volume kubus"""
    count_volume = r**3

    return count_volume



nama_bangun_ruang = input("Masukan Nama Bangun Ruang: ")

try:
    if nama_bangun_ruang == "kubus":
        r = int(input("Masukan nilai rusuk: "))
        print(menghitung_volume_kubus(r))
    

        
    else:
        raise Exception ("terjadi kesalahan input nama bangun ruang")
        
except ValueError:
      print("Nilai bukan tipe data integer!")
        
finally:
      print("Sekian dan terima kasih!")
