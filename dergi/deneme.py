import np


aip = 159; # bekleyen makale sayısı # article in press sayısı
aaa = 38.89; # ortalama makale sayısı # Pblshd.Art.Average
b = 1.85; # ortalama volume sayısı # Volume Average

omv = aaa / b ; # ortalama makale / volume   # volume başına ortalama makale

bolme = aip / omv # bekleyen makale sayısı / volume başına ortalama makale sayısı

mod = np.divmod(aip, omv)  # bölüm ve kalanı bulmak için mod alma

basilacakmakale = round(aip - 1.9675675675675848) # önümüzdeki basılacak volumelerde 152 tane makale basılacak
#1.9675675675675848   bölümden kalan sayısı formüle entegre etmemiz lazım nasıl edeceğiz. Değişken olarak gelecek

volumebekleyenmakalesayisi = round(aip - basilacakmakale)

volbaski = np.ceil(bolme) # yukarı yuvarlama işlemi # ihtiyaç olan toplam volume sayısını bulduk

sonbaskiay = 12 / b * volbaski # bir sonraki baskının kaç ay sonra basılacağı

print("Bekleyen makale sayısı :")
print(aip)
print("Volume basına ortalama makale sayısı :")
print(omv)
print("Bölme işlemi sonucu:")
print(bolme)
print("Bölüm ve kalan:")
print(mod)
print("Volumede yer alacak makale sayısı")
print(basilacakmakale)
print("Son volumede bekleyen makale sayısı")
print(volumebekleyenmakalesayisi)
print("***************")
print("Baskı için gereken volume sayısı :")
print(volbaski)
print("Tahmini son baskı kaç ay sonra :")
print(sonbaskiay)


