# TechCorp VPN Bağlantı Rehberi

**Departman:** IT
**Erişim Seviyesi:** Genel (Tüm Çalışanlar)
**Son Güncelleme:** Şubat 2026

## VPN Neden Gerekli?

TechCorp'un iç sistemlerine (Confluence, iç API'ler, dosya sunucuları) ofis dışından erişmek için şirket VPN'i kullanılmalıdır. VPN olmadan bu sistemlere erişim güvenlik politikaları gereği engellenmiştir.

## Kurulum Adımları

1. **Yazılımı indirin**: IT Portal > Araçlar > "TechCorp VPN Client" bağlantısından işletim sisteminize uygun sürümü indirin (Windows, macOS, Linux destekleniyor).
2. **Kurulumu tamamlayın**: İndirilen dosyayı çalıştırın ve varsayılan ayarlarla kurulumu tamamlayın.
3. **Giriş yapın**: Şirket e-posta adresiniz ve Okta SSO şifrenizle giriş yapın.
4. **İki faktörlü doğrulama**: Telefonunuza gelen Okta Verify bildirimini onaylayın.
5. **Bağlan**: "TechCorp-Main" sunucusunu seçip "Connect" butonuna basın.

## Sık Karşılaşılan Sorunlar

**"Sunucuya bağlanılamıyor" hatası alıyorum:**
- İnternet bağlantınızı kontrol edin.
- VPN istemcisini güncel sürüme yükseltin (IT Portal'dan).
- Sorun devam ederse IT destek ticket'ı açın.

**Bağlantı çok yavaş:**
- "TechCorp-Main" yerine bölgenize en yakın sunucuyu (TechCorp-EU, TechCorp-US) deneyin.
- Yoğun saatlerde (09:00-10:00 arası) bağlantı hızı düşebilir, bu normaldir.

**Okta doğrulama bildirimi gelmiyor:**
- Telefonunuzda internet bağlantısını kontrol edin.
- Okta Verify uygulamasını yeniden başlatın.
- 5 dakika içinde bildirim gelmezse IT'ye başvurun.

## Güvenlik Kuralları

- VPN'i herkese açık Wi-Fi ağlarında (kafe, havalimanı) mutlaka kullanın.
- VPN bağlantınızı kullanmadığınız zamanlarda kapatın.
- VPN erişim bilgilerinizi hiçbir zaman başkalarıyla paylaşmayın.
- Şüpheli bir bağlantı uyarısı görürseniz derhal IT Security ekibine bildirin.

## Destek

Sorun yaşarsanız IT Portal üzerinden ticket açabilir veya #it-support Slack kanalından yardım isteyebilirsiniz.
