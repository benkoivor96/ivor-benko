# ivorbenko.com

Dvojezična (EN/HR) statična web stranica. Nema baze, nema CMS-a, nema JavaScripta, zato je brza i lako je indeksiraju i Google i AI tražilice.

## Što je gdje

- `site/` — gotova stranica. Ovo se objavljuje na hosting.
- `source/` — izvor: tekstovi blogova (`content/en`, `content/hr`), dizajn (`static/style.css`) i `build.py` koji sve generira.

## Struktura URL-ova

| Engleski | Hrvatski |
|---|---|
| `/` | `/hr/` |
| `/skipper/` | `/hr/skiper/` |
| `/booking/` | `/hr/najam-broda/` |
| `/about/` | `/hr/o-meni/` |
| `/blog/` | `/hr/blog/` |
| `/blog/<slug>/` | `/hr/blog/<slug>/` |

Engleski je na korijenu domene (`x-default`) jer je većina gostiju chartera stranaca, a i AI tražilice najviše pretražuju na engleskom.

## Fotografije

Stavi fotke u `source/static/photos/` pa pokreni `python build.py`:

- `hero.jpg`: velika fotka za pozadinu naslovnog dijela (najbolje 2000 px širine, more/brod)
- `ivor.jpg`: tvoja veća slika (zamjenjuje malu `ivor-benko.jpg`)
- `gallery/*.jpg`: galerija na početnoj stranici (pojavi se sama kad ima fotki)

Build ih sam smanji i optimizira. Bez fotki stranica koristi morski gradijent.

## Objava (najlakše: Cloudflare Pages ili Netlify, oboje besplatno)

1. Napravi račun na pages.cloudflare.com ili netlify.com.
2. "Upload / Deploy manually" i povuci mapu `site/`.
3. U postavkama projekta dodaj custom domain `ivorbenko.com` (i `www.ivorbenko.com` kao preusmjeravanje na glavnu) i slijedi upute za DNS kod registrara domene.

## Odmah nakon objave

1. **Google Search Console**: dodaj domenu i pošalji `https://ivorbenko.com/sitemap.xml`.
2. **Bing Webmaster Tools**: isto (može uvesti iz Search Consolea). Bing indeks koriste ChatGPT pretraga i Copilot.
3. **Profili (`SAME_AS` u `build.py`)**: upiši linkove na Instagram, LinkedIn, Facebook, profil na charter platformama… i ponovno pokreni build. Na svakom od tih profila stavi link natrag na ivorbenko.com. To je najvažniji korak da AI poveže "Ivor Benko" s ovom stranicom.
4. Provjeri strukturirane podatke na search.google.com/test/rich-results.

## Novi blog

1. Kopiraj postojeći `.md` u `source/content/en/` i/ili `source/content/hr/`.
2. Promijeni front matter. `key` mora biti isti u EN i HR verziji da se povežu kao prijevodi. `category: skiing` za skijaške tekstove (sekcija na blogu već postoji). `summary` je kratki odgovor na vrhu teksta — to AI najčešće citira, pa neka bude jasan i samostalan.
3. `pip install markdown pillow` pa `python build.py` u mapi `source/`.
4. Ponovno objavi mapu `site/`.

## SEO / GEO koji je već ugrađen

- title, meta description, canonical, hreflang (en, hr, x-default), Open Graph i Twitter kartice na svakoj stranici
- JSON-LD: Person (kvalifikacije, jezici, brodovi, znanja), WebSite, ProfilePage, Service, FAQPage, Blog, BlogPosting, BreadcrumbList
- `sitemap.xml` s hreflang alternativama, RSS feedovi za oba jezika
- `robots.txt` koji eksplicitno dopušta AI crawlere (GPTBot, ClaudeBot, PerplexityBot, Google-Extended…)
- `llms.txt` i `llms-full.txt` — sažetak činjenica i puni tekstovi za AI modele
- "Ukratko / Short answer" na vrhu svakog bloga, "Quick facts" na stranici O meni
- fontovi hostani lokalno (bez Google Fonts poziva, GDPR)

Fontovi Newsreader i Hanken Grotesk su pod SIL Open Font License.
