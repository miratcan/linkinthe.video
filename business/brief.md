# linkinthe.video - Video İçerik Üreticileri İçin Akıllı Gelir Platformu

## Proje Adı
`linkinthe.video` (Önceki adı: `curated.guide` - Domainin boşta bulunmasıyla stratejik pivot yapıldı.)

## Temel Problem (Influencer'ın Acısı)
Hailey Bieber örneğinde gördüğümüz gibi, video içerik üreticileri (Influencer'lar, yani "Sarah" personamız), videolarında bahsettikleri ürünleri açıklama kısmına manuel olarak eklemekte büyük zorluk çekiyorlar:
*   **Zaman Kaybı:** Bir videodaki ürünleri tek tek bulmak, linklerini kopyalamak, affiliate kodlarını eklemek saatler süren bir angarya.
*   **Verimlilik Kaybı:** Bu zahmet yüzünden birçok ürün listelenmiyor, bu da gelir kaybına yol açıyor.
*   **Marka İmajı:** YouTube açıklama kutusundaki alt alta sıralanmış ham linkler, profesyonel görünmüyor ve yaratıcının markasını zedeliyor.
*   **Satış Kaybı:** Linkler uluslararası takipçiler için optimize değilse (örn. Amazon.com.tr yerine Amazon.com linki), satışlar kaçırılıyor.

## Hedef Persona
**Sarah (Tech Review Mikro YouTuber):**
*   **Segment:** 10K-100K abone arası (mikro influencer)
*   **Niche:** Tech review (gadget, yazılım, setup videoları)
*   **Platform:** YouTube (tek platform odağı)
*   **Neden bu segment?**
    *   Tech review'cılar yeni araçlara yatkın (early adopter)
    *   Mikro segment kendi işini kendisi yapıyor (editör/asistan yok)
    *   Amazon affiliate zaten doğal bir gelir kaynağı
*   Kendi markasına ve estetiğine önem veren.
*   Affiliate linkler aracılığıyla gelir elde etmek isteyen.
*   Zamanı kısıtlı ve angaryalardan nefret eden.

## Çözümümüz: Video-to-Guide Sihirbazı (V1 Stratejisi)

`linkinthe.video`, video içerik üreticilerinin (Sarah'nın) videolarındaki ürünleri saniyeler içinde tespit edip, otomatik olarak affiliate linkleriyle donatarak, şık ve profesyonel bir "ürün rehberi sayfası" oluşturan akıllı bir platformdur.

### Temel İş Akışı ve Sihir:
1.  **Video Yükle/Link Ver:** Sarah, YouTube videosunun linkini yapıştırır veya video dosyasını yükler (Instagram/TikTok videoları için).
2.  **AI Analizi (Asenkron):** Platform, videoyu "Akıllı Göz" boru hattı ile analiz eder:
    *   Videodaki sesleri metne dönüştürür (Speech-to-Text).
    *   Metinden potansiyel ürün adlarını ve markaları çıkarır (LLM).
    *   Marka adı net olmayan ürünler için, ilgili zaman damgasındaki video karesini yakalar ve görsel analizi yapar (Vision API).
    *   Tespit edilen ürünler için Amazon API gibi kaynaklardan yüksek kaliteli görseller ve temiz linkler bulur.
    *   Sarah'nın daha önce girdiği affiliate kodlarını bu linklere otomatik olarak ekler.
3.  **Rehber Taslağı Oluştur:** Tüm bu bilgilerle, ürünlerin listelendiği şık bir rehber sayfası taslağı otomatik olarak oluşturulur.
4.  **Kullanıcı Gözden Geçirme Modu:** Sarah'ya bir bildirim gönderilir. Platforma döndüğünde, oluşturulan taslağı adım adım kolayca gözden geçirebilir:
    *   AI'ın doğru tespit ettiği ürünleri onaylar.
    *   AI'ın kaçırdığı veya yanlış tahmin ettiği ürünleri (akıllı arama kutusu desteğiyle) birkaç saniyede düzeltir.
    *   Her ürün için kendi "Neden seviyorum?" notunu yazar (AI yazmaz, insan yazar).
    *   Taslağı yayınlar ve `linkinthe.video/sarah/video-adi` gibi tek bir şık linke sahip olur.
5.  **YouTube Açıklama Entegrasyonu:** Sarah, bu tek linki YouTube videosunun açıklama kısmına yapıştırır. Takipçiler artık dağınık bir metin yerine, onun markasını yansıtan profesyonel bir rehber sayfasına ulaşır.

### Değer Vaadi (Neden Biz, Linktree Değil?):
*   **Zahmetsiz Kârlılık:** Saatler süren manuel link ekleme işini 1-2 dakikalık bir gözden geçirme işine dönüştürür. Kaybedilen gelir potansiyelini maksimize eder.
*   **Marka Değeri:** Dağınık link listeleri yerine, profesyonel ve estetik bir "ürün rehberi sayfası" sunarak yaratıcının marka imajını güçlendirir.
*   **Artan Dönüşüm:** Akıllı, yerelleştirilmiş (geo-aware) affiliate linkleri sayesinde, uluslararası takipçilerden bile maksimum komisyon geliri elde etmesini sağlar.
*   **Odaklanmış Mükemmellik:** Yaratıcının en büyük angaryasını (video içi ürünleri listeleme ve monetize etme) çözmeye odaklanmış, sihirli bir deneyim sunar.

## İş Modeli
*   **Kredi Bazlı Sistem:** Kullanıcılar kredi satın alır, her video analizi sabit kredi harcar.
*   **Video Başı Sabit Kredi:** Videonun uzunluğu veya karmaşıklığı ne olursa olsun, her video analizi aynı krediyi harcar. (Arkada maliyet değişse de kullanıcı için basit ve öngörülebilir.)
*   **Free Tier:** Kayıt olan her kullanıcıya **3 video bedava**. (Cold DM için güçlü hook: "İlk 3 video bedava, denemek ister misin?")
*   **Kredi Paketleri:** 500 / 2500 / 5000 kredi paketleri (fiyatlar sonra belirlenecek)

## Go-to-Market (GTM) Stratejisi
*   **Kanal:** Cold DM (Twitter/X + Reddit)
*   **Pazar:** Global (İngilizce)
*   **Tempo:** Günde maksimum 10 kişiselleştirilmiş DM (spam değil, kaliteli)
*   **Hedefleme:**
    *   Son videosunun açıklamasında link eksik olan tech YouTuber'lar
    *   Veya dağınık/düzensiz link listesi olanlar
    *   10K-100K abone arası, aktif video yükleyen
*   **Örnek DM yapısı:** Kişiselleştirilmiş (son videodan bahset) + değer önerisi + "3 video bedava" hook

## Başarı Metrikleri
*   **Ana metrik:** Retention (geri dönüş)
*   **Başarı kriteri:** 10 kişi sabit olarak geri gelip kullanıyorsa → başarı
*   **Beklenti:** Arada video üretip gidebilirler, önemli olan geri dönmeleri

## Zen Prensipleri (Bu Projeyi Şekillendirenler)
*   `[ZEN-SOLO-FIT]`: Tek bir geliştiricinin yönetebileceği, aşamalı ve ölçeklenebilir bir yapı.
*   `[ZEN-COURAGE]`: Çözüme değil, probleme aşık olma cesareti; V1 için büyük bir pivot yapıldı.
*   `[ZEN-EASIEST-PATH]`: Kullanıcı için en tembel yolu (en az eforu) mükemmel hale getirme hedefi.
*   `[ZEN-PROUD-FIRST]`: Yaratıcının kendi rehberinden gurur duymasını sağlama ana hedefi.
*   `[ZEN-MEASURE-FIRST]`: Kararları veriyle destekleme.

---
