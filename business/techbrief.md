# linkinthe.video - Teknik Brief

This document is the single source of truth for all technical decisions.
**AI agents / future contributors: Follow these rules religiously. No exceptions.**

---

## Core Principles (non-negotiable)

- **Solo-founder forever** → stack must be simple, fast, cheap, and executable by one person.
- **No bloat** → if we can solve it without a new dependency, we do.
- **LLM-friendly** → choose technologies that AI assistants know well.
- **Success-ready** → plan for scale and security from day one.
- **No Docker** → keep development simple and fast.

---

## Proje Yapısı (Monorepo)

```
/
├── src/
│   ├── backend/        # Django
│   └── frontend/       # Next.js (React)
└── business/           # Tüm dokümanlar
```

---

## Tech Stack

| Katman | Teknoloji |
|--------|-----------|
| **Backend** | Django |
| **API** | django-shinobi (django-ninja fork) |
| **Frontend** | Next.js (React) |
| **Styling** | Tailwind + shadcn/ui |
| **Database** | Local: SQLite, Prod: PostgreSQL (VPS'te) |
| **Background Jobs** | Modal |
| **Auth** | django-allauth headless + Google OAuth |
| **Ödeme** | Stripe |
| **Email** | django-anymail + Resend |

### Django Kütüphaneleri

| Kütüphane | Ne İşe Yarar |
|-----------|--------------|
| **django-shinobi** | API framework (django-ninja fork) |
| **django-environ** | Environment variables (.env) |
| **django-allauth** | Auth + Google OAuth (headless mode) |
| **django-anymail** | Email (Resend) |
| **litellm** | LLM abstraction (adapter içinde) |

---

## Altyapı

| Alan | Karar |
|------|-------|
| **Hosting** | netvay.com VPS (4GB) |
| **CDN/Koruma** | Cloudflare DNS |
| **Admin** | Gizli URL (/admin/ değil) |
| **Storage (kalıcı)** | Cloudflare R2 (ürün görselleri) |
| **Storage (geçici)** | Modal Volumes (video/audio) |
| **Redis** | Yok (Modal handles jobs) |

---

## Ekranlar

| # | Ekran | Açıklama |
|---|-------|----------|
| 1 | **Auth** | Kayıt / Giriş |
| 2 | **Dashboard (Ana)** | Google-tarzı input, sidebar (geçmiş/aktif videolar) |
| 3 | **Review** | Bulunan ürünler tablosu, checkbox'lar, onay |
| 4 | **Success** | Oluşan link + kopyala/git butonları |
| 5 | **Public Product Page** | `linkinthe.video/sarah/video-id` - takipçilerin gördüğü sayfa |

---

## Frontend Features

| Feature | Detay |
|---------|-------|
| **Auth sistemi** | Kayıt, giriş, kredi gösterimi |
| **Video input** | YouTube link paste + Analyze butonu |
| **Real-time progress** | Progress bar + state text (Inspecting video, Deep search vs.) |
| **Sidebar** | Aktif + tamamlanan analizler listesi |
| **Review tablosu** | Timestamp, ürün adı, ASIN, checkbox. Found + lost ürünler birlikte gösterilir. |
| **Manuel ürün ekleme** | Amazon linki yapıştır → ASIN parse → ürün bilgisi çek. Timestamp yok. |
| **Drag-and-drop sıralama** | Ürün sıralaması değiştirilebilir |
| **Onay mekanizması** | Tüm ürünler review edilmeden buton disabled |
| **Link paylaşım** | Kopyala + Sayfaya Git |
| **Post-publish düzenleme** | Yayın sonrası ürün ekle/çıkar, sırala, açıklama düzenle |

---

## Backend Pipeline

```
1. Video indir (yt-dlp)
        ↓
2. Ses ayır (ffmpeg)
        ↓
3. Transkripsiyon (Whisper API)
        ↓
4. LLM → Ürün isimleri çıkar
   - Bulduklarını döndür
   - Bulamadıklarını timestamp ile bildir
        ↓
5. Bulanık ürünler için frame extract (ffmpeg)
        ↓
6. Vision API → Frame'den ürün tanı
   - Tanıdı → found listesine
   - Tanımadı → ±1 sn retry → hala yok → lost listesine
        ↓
7. Fuzzy match (yerel DB)
        ↓
8. Threshold altı → Amazon Search API
        ↓
9. Sonuç: {found: [...], lost: [...]}
```

Pipeline Modal üzerinde çalışır. Django sadece job'u tetikler ve durumu takip eder.

---

## Pipeline Çıktı Formatı

```json
{
   "found": [
      {
         "id": "local-product-id",
         "name": "Product Name",
         "source": ["audio", "video"],
         "markets": {
            "amazon": {"asin": "B00XXXXX"}
         },
         "timestamp": "03:11"
      }
   ],
   "lost": [
      {
         "name": "kablo",
         "timestamp": "12:45"
      }
   ]
}
```

---

## Veri Modelleri

```
User
├── id
├── email
├── credits
└── videos[]

Video
├── id
├── user_id
├── youtube_url
├── status (processing, completed, failed)
├── slug
└── video_products[]

Product (global ürün DB)
├── id
├── name
└── product_markets[]

ProductMarket (M2M - ürün ↔ market)
├── id
├── product_id (FK → Product)
├── market (enum: amazon, trendyol, ...)
├── market_product_id (ASIN, Trendyol ID, ...)

VideoProduct (video ↔ ürün ilişkisi)
├── id
├── video_id (FK → Video)
├── product_id (FK → Product, nullable - lost ise yok)
├── name (lost ise sadece bu var)
├── timestamp (nullable - manuel eklenen ürünlerde yok)
├── source (audio/video/subtitle/manual)
├── is_reviewed
├── is_found
├── sort_order (sıralama için)
```

---

## Real-time Updates

- **Yöntem:** Polling (2-3 sn aralıkla)
- **Akış:** Modal → Django (durum güncelle) → Frontend (GET /api/video/{id}/status)
- WebSocket/SSE şimdilik yok, gerekirse eklenir

---

## API Soyutlama (Adapter Pattern)

Tüm external API'ler adapter pattern ile soyutlanır. LiteLLM uygun yerlerde kullanılır.

```python
# Base interface
class LLMProvider(ABC):
    @abstractmethod
    def extract_products(self, transcript: str) -> list[dict]:
        pass

    @abstractmethod
    def analyze_image(self, image_path: str, prompt: str) -> str:
        pass

# OpenAI adapter (LiteLLM ile)
class OpenAIProvider(LLMProvider):
    def extract_products(self, transcript: str) -> list[dict]:
        response = litellm.completion(
            model="gpt-4",
            messages=[...]
        )
        return self._parse_response(response)

# Test için mock
class MockLLMProvider(LLMProvider):
    def extract_products(self, transcript: str) -> list[dict]:
        return [{"name": "Test Product", "timestamp": "01:23"}]
```

**Faydaları:**
- Provider değiştirmek kolay (OpenAI → Gemini)
- Test için mock provider
- Fallback eklemek kolay (ileride gerekirse)

---

## Test Stratejisi

| Katman | Araç | Yöntem |
|--------|------|--------|
| **Backend Unit** | pytest + pytest-django + factory-boy | MockProvider |
| **Backend Integration** | pytest + VCR.py (pytest-recording) | Kayıt/oynat |
| **Frontend Unit** | Jest + React Testing Library | Component test |
| **Frontend E2E** | Playwright | Tam akış testi |

**External API Mocking:**
- **Unit test:** MockProvider (hızlı, ücretsiz, deterministic)
- **Integration test:** VCR.py (bir kere gerçek API, sonra kayıttan oynat)

---

## Development Workflow

```bash
# Backend
cd src/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend
cd src/frontend
npm install
npm run dev
```

**No Docker** (keeps onboarding instant).

---

## Ürün Kararları

1. **"Yeni Ürün Ekle"** → Amazon linki yapıştır, ASIN parse et, ürün bilgisi çek. Timestamp yok.
2. **Lost ürünler** → Review ekranında gösterilecek. Kullanıcı Amazon linki yapıştırarak tamamlayabilir.
3. **Public sayfa tasarımı** → Liste görünümü (ikon + ad + açıklama). Fiyat yok (güncel tutma derdi). Görsel detayları tasarım aşamasında.
4. **Edit sonrası** → Evet, yayın sonrası düzenleme yapılabilir (ürün ekle/çıkar, sırala, açıklama düzenle).

---

## Forbidden Technologies

❌ No Docker in development
❌ No Redis (Modal handles jobs)
❌ No GraphQL (REST is enough)
❌ No microservices (monolith forever)
❌ No CSS-in-JS (Tailwind only)
❌ No complex state management (React state + context enough)

---

## The Rule

> **"Pick boring technology. Ship fast. Stay solo. Plan for success."**
