import datetime as dt
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

#Görev 1 - Veriyi anlama ve hazırlama

#Online Retail II excelindeki 2010-2011 verisini okuyunuz. Oluşturduğunuz dataframe’in kopyasını oluşturunuz.
df_ = pd.read_excel("pythonProject/datasets/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()

#Veri setinin betimsel istatistiklerini inceleyiniz.
df.head()
df.shape
df.info()
df.describe().T

#Veri setinde eksik gözlem var mı? Varsa hangi değişkende kaç tane eksik gözlem vardır?
df.isnull().sum()

#Eksik gözlemleri veri setinden çıkartınız. Çıkarma işleminde ‘inplace=True’ parametresini kullanınız.
df.dropna(inplace=True)

#Eşsiz ürün sayısı kaçtır?
df["Description"].nunique()

#Hangi üründen kaçar tane vardır?
df["Description"].value_counts().head()

#En Çok sipariŞ edilen 5 ürünü çoktan aza doğru sıralayınız.
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head(5)

#Faturalardaki ‘C’ iptal edilen işlemleri göstermektedir. İptal edilen işlemleri veri setinden çıkartınız.
df = df[~df["Invoice"].str.contains("C", na=False)]

#Fatura başına elde edilen toplam kazancı ifade eden ‘TotalPrice’ adında bir değişken oluşturunuz.
df["TotalPrice"] = df["Quantity"] * df["Price"]

df.head()
df.shape

#df = df[(df['Quantity'] > 0)]
#df = df[(df['Price'] > 0)]


#Görev 2 - RFM Metriklerinin Hesaplanması

#Recency, Frequency ve Monetary tanımlarını yapınız.
#Recency  Sıcaklık (Müşteri kaç gün önce geldi?)
#Frequency  Frekans (Müşteri kaç tane alışveriş yaptı?)
#Monetary  Parasal (Müşterinin bıraktığı parasal değer?)

# Müşteri özelinde Recency, Frequency ve Monetary metriklerini groupby, agg ve lambda ile hesaplayınız.
# Hesapladığınız metrikleri rfm isimli bir değişkene atayınız.
today_date = dt.datetime(2011, 12, 11)

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})
rfm.head()

# Oluşturduğunuz metriklerin isimlerini recency, frequency ve monetary olarak değiştiriniz.
rfm.columns = ['recency', 'frequency', 'monetary']

# rfm dataframe’ini oluşturduktan sonra veri setini "monetary>0" olacak şekilde filtreleyiniz.
rfm = rfm[(rfm['monetary'] > 0)]


#Görev 3 - RFM skorlarının oluşturulması ve tek bir değişkene çevrilmesi

# Recency, Frequency ve Monetary metriklerini qcut yardımı ile 1-5 arasında skorlara çeviriniz.
# Bu skorları recency_score, frequency_score ve monetary_score olarak kaydediniz.
rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm['monetary_score'] = pd.qcut(rfm['monetary'], 5, [1, 2, 3, 4, 5])

# Oluşan 2 farklı değişkenin değerini tek bir değişken olarak ifade ediniz ve RFM_SCORE olarak kaydediniz.
rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))
rfm.head()


# Görev 4 - RFM skorlarının segment olarak tanımlanması

#Oluşturulan RFM skorların daha açıklanabilir olması için segment tanımlamaları
#yapınız.
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}
rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
rfm.head()


# Görev 5 - Aksiyon Zamanı

# Önemli bulduğunuz 3 segmenti seçiniz. Bu üç segmenti;
# - Hem aksiyon kararları açısından,
# - Hem de segmentlerin yapısı açısından (ortalama RFM değerleri) yorumlayınız.

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

# 'cant loose' grubu yani uzun süredir alışveriş yapmamış fakat eskiden sıkça
# alışveriş gerçekleştirmiş olanlar. Bu segmentte 63 kişi bulunmakta,
# ortalama olarak en son alışverişleri 132 gün önce gerçekleşmiş,
# alışveriş sıklıkları 8, 2796 birim harcamaları olmuş.
# Bu segment için yeni ürünleri onlara önererek veya bu sınıfa özel promosyonlar,
# küçük çaplı para puanlar verilerek geri kazanabiliriz.

#'need attention' segmentinde 187 kişi bulunmakta, ortalama olarak en son alışverişleri
# 52 gün önce gerçekleşmiş, alışveriş sıklıkları 2, 897 birim harcamaları olmuş. Yeniden etkinleştirerek
# alışveriş yapmalarını sağlamak için sınırlı süreli indirimler veya geçmiş satın
# almalarına göre öneriler sunulabilir.

#'Champions' segmentindeki kişiler ile iletişim kurmak kendilerini değerli ve takdir edilmiş kişiler
# olarak hissettirecektir. Bu müşteriler muhtemelen toplam gelirlerin orantısız olarak yüksek bir yüzdesini
# oluşturmaktadır ve bu nedenle onları mutlu etmeye odaklanmak en büyük öncelik olmalıdır. Bireysel tercihlerini
# ve yakınlıklarını daha fazla analiz ederek, daha kişiselleştirilmiş mesajlaşma için ek fırsatlar sağlayacaktır.

#"Loyal Customers" sınıfına ait customer ID'leri seçerek excel çıktısını alınız.
new_df = pd.DataFrame()
new_df['new_customer_id'] = rfm[rfm['segment'] == 'loyal_customers'].index
new_df.to_excel('new_excel.xlsx')
