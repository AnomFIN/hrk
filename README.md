# Harjun Raskaskone Oy (HRK) verkkosivusto

Static site for showcasing Harjun Raskaskone Oy services, rental catalogue and company information. The project only contains hand-authored HTML, CSS and vanilla JavaScript with no build tooling.

## Rakenne

- `index.html` – pääsivu, joka kokoaa yrityksen esittelyn, palvelut, vuokra- ja myyntikaluston sekä yhteydenottolomakkeen.
- `assets/css/` – tyylit, mukaan lukien väripaletit, layoutit ja responsiiviset ratkaisut.
- `assets/js/` – kevyt interaktio (navigaatio, tuotefiltterit, UKK-accordion).

## Kehitysvinkit

1. **Hinnoittelun hallintapaneeli** – lisää JSON/CSV-pohjainen sisältösyöttö tai helppo päivityslomake, jotta vuokraushinnasto pysyy ajan tasalla ilman HTML-muokkauksia.
2. **Monikielisyys** – toteuta kielivalitsin (suomi/englanti) ja rakenna sisältö data-objektien varaan, jotta kielilaajennokset ovat jatkossa suoraviivaisia.
3. **Saavutettavuusraportointi** – liitä kevyt testi (esim. Pa11y CLI) osaksi paikallista tarkistusta ennen tuotantoon vientiä.

## Julkaisu

Automaattiset GitHub Actions -workflowt on poistettu, jotta ristiriitaiset asetukset eivät enää katkaise julkaisuja. Sivusto voidaan julkaista manuaalisesti GitHub Pagesiin seuraavasti:

1. Rakenna repositorio (ei erillistä buildia).
2. Ota käyttöön Pages `Settings → Pages` -osiosta ja osoita se `main`-haaran juureen.
3. Paina **Save** – muutokset tulevat näkyviin muutaman minuutin kuluessa.

> **Huom.** Mikäli automaatio halutaan palauttaa, kannattaa aloittaa GitHubin virallisesta Pages-workflow-pohjasta ja varmistaa, ettei rinnakkaisia julkaisuja ole käynnissä.

— AnomFIN | AnomTools

# Helsinki eBike-Service Oy

Moderni yhden sivun verkkosivusto Helsinki eBike-Service Oy:lle. Sivusto sisältää sähköpyörähuollon palvelukuvaukset, huoltopaketit sekä interaktiivisen verkkokauppakokemuksen, jossa voi koostaa ostoskorin ja jättää yhteydenottopyynnön.

## Why this design

- Single-page arkkitehtuuri, jossa verkkokauppa avautuu overlayn päälle – navigointi on saumaton eikä erillistä `verkkokauppa.html`-tiedostoa tarvita.
- jQuery-pohjaiset fade- ja scroll-animaatiot varmistavat, että siirtymät toimivat tasaisesti myös vanhemmissa selaimissa.
- Ostoskori säilytetään `localStorage`-avaimessa (`helsinki-ebike-cart`), joten tuotetiedot pysyvät session yli ilman palvelinlogiikkaa.
- Verkkokauppa ohjaa oletuksena **Mallisto → Kassa** -polulle: Mallisto-näkymä vastaa hero-osiossa mainittuja Specialized-, Trek-, Riese & Müller-, Gazelle- ja Giant-kumppaneita ja kassavaiheessa piilotetaan tuotevalinta kokonaan.
- Turvallinen oletus: ei evalia, ei dynaamisia skriptejä ja kaikki mail-/tel-linkit ovat suoraviivaisia.

## Setup & local development

1. Asenna kehitysriippuvuudet: `npm install`.
2. Käynnistä kevyt palvelin projektin juuresta: `python3 -m http.server 4173`.
3. Avaa selain ja siirry osoitteeseen `http://localhost:4173/index.html`.
4. Muutosten aikana selain päivittyy automaattisesti; selainvälimuistin voi tyhjentää `Cmd+Shift+R` / `Ctrl+Shift+R`.

### Komennot

- `python3 -m http.server 4173` – palvelee staattisen sivuston paikallisesti.
- `npm run lint` – suorittaa ESLintin JavaScript-tiedostoille.
- `npm run lint:fix` – korjaa automaattisesti yleisimmät lint-ongelmat.
- `npm test` – ajaa Vitest-yksikkötestit (jsdom-ympäristö).

## Verification steps

1. Avaa pääsivu ja varmista, että hero-osio ja mittarit animoituvat näkyviin.
2. Klikkaa ylävalikon **Verkkokauppa**-painiketta: overlayn tulee fadeutua esiin, `Mallisto`-pilotti on aktiivinen ja tuotelistauksessa näkyvät Specialized, Trek, Riese & Müller, Gazelle ja Giant -mallit.
3. Lisää tuote koriin (esim. "Specialized Turbo Vado 5.0 IGH") ja tarkista, että laskuri päivittyy sekä navissa että oikean reunan yhteenvetopaneelissa.
4. Paina **Siirry kassalle**: Mallisto- ja tuote-paneelit katoavat, `Kassa`-pilotti aktivoituu ja lomake pyytää yritys-, yhteys- ja toimitustietoja.
5. Täytä kassalomake esimerkkitiedoilla (esim. yritys "Testi Oy", Y-tunnus `1234567-8`) ja lähetä – lomakkeen alle ilmestyy yhteenveto, joka listaa valitut tuotteet ja vahvistaa AnomFIN Concierge -kuittauksen.
6. Sulje overlay `Sulje`-painikkeella tai Escillä – taustasivun tulee palautua kirkkaaksi ja fokus palata viimeksi käytettyyn elementtiin.

## Pääominaisuudet

- Responsiivinen hero-osio, jossa yrityksen ydintiedot ja mittarit
- Palvelu- ja huoltopakettikortit sähköpyörille ja yritysfloteille
- Yhdistetty verkkokauppa-overlay, jossa on ostoskorilaskuri ja maksutavan valinta
- Ajantasaiset yritystiedot (Y-tunnus 3496925-8, Aarteenetsijäntie 4 E, Helsinki)
- Yhteydenottolomake ja call-to-action -painikkeet nopeaan kontaktinottoon

## Admin-hallintapaneeli (PHP)

AnomFINin HRK Admin -kokonaisuus mahdollistaa koko sivuston sisällön, tuotteiden ja tilausten hallinnan ilman tietokantaa. Ratkaisu toimii puhtaasti JSON-tiedostojen varassa ja soveltuu sekä kehitys- että tuotantokäyttöön pienillä ympäristövaatimuksilla.

### Rakenne

```
admin/
  index.php          # Dashboard ja näkymät
  login.php          # Kirjautuminen password_hash/password_verify -tuella
  logout.php         # Istunnon sulkeminen
  api.php            # AJAX-rajapinta (tuotteet, asetukset, sivut, tilaukset, logit)
  upload.php         # Turvallinen kuvien lataus ja thumbnailien generointi
  create_admin.php   # Uusien admin-käyttäjien luonti suojatulla lomakkeella
  init.php, save.php # Yleiset apufunktiot ja session asetukset
  assets/css/        # Bootstrap-tyylinen käyttöliittymä
  assets/js/         # Hallintalogiikka, fetch-pohjaiset API-kutsut
data/
  products.json      # Tuoteinventaario (esimerkkidata mukana)
  categories.json    # Kategoriat
  settings.json      # Sivuston asetukset (hero, SEO, maksutavat)
  pages.json         # Kotisivun osiot ja mukautetut sivut
  orders.json        # Tilausexamplet ja tilaseuranta
  users.json         # Admin-käyttäjät (bcrypt-hashatut salasanat)
uploads/
  images/            # Tuotekuvat ja thumbnailit (sisältää .htaccessin suojaukseen)
logs/
  admin.log          # Audit-logi kaikista toimenpiteistä
```

### Asennus ja käyttöönotto

1. **PHP-versio**: Vähintään PHP 8.0, GD-laajennos mahdollistaa pikkukuvat (muutoin lataus toimii ilman niitä).
2. **Kansio-oikeudet**: Varmista että `data/`, `uploads/` ja `logs/` ovat web-palvelimen käyttäjän kirjoitettavissa. Aja tarvittaessa `php admin/test_permissions.php` varmistaaksesi oikeudet.
3. **Kirjautuminen**: Esimerkkikäyttäjä löytyy `data/users.json`-tiedostosta käyttäjänimellä `admin`. Vaihda salasana välittömästi kirjautumisen jälkeen.
4. **HTTPS**: Ota käyttöön HTTPS tuotannossa, jotta sessiocookie pysyy suojattuna (`SameSite=Strict`, `HttpOnly`).
5. **Ensimmäiset stepit**: Kirjaudu `admin/login.php`-osoitteessa, päivitä asetukset, lisää tuotteita ja tarkista audit-logi.

### Turvallisuus ja auditointi

- Kaikissa POST-pyynnöissä on CSRF-tarkistus ja istunnon aikakatkaisu (30 minuuttia).
- Audit-logi (`logs/admin.log`) kirjaa käyttäjän, toimenpiteen, kohteen ja IP-osoitteen.
- Kuvien latauksessa sallitaan vain JPG, PNG ja WebP -tiedostot enintään 5 MB:n kokoisina, ja latauskansio on suojattu `.htaccess`-tiedostolla.
- JSON-tiedostot kirjoitetaan lukituksella (flock) ja atomisella `rename`-operaatiolla korruption välttämiseksi.

### Manuaaliset testit

1. Kirjaudu sisään `admin/login.php` ja tarkista, että väärä salasana tuottaa virheilmoituksen.
2. Lisää uusi tuote hallintapaneelissa, vie CSV ja varmista päivitys `data/products.json` -tiedostoon.
3. Lataa tuotekuva `admin/upload.php`-lomakkeella ja varmista, että kuva sekä thumbnail tallentuvat `uploads/images/`-kansioon.
4. Päivitä hero-asetukset ja SEO-tiedot ja varmista muutokset `data/settings.json` -tiedostossa.
5. Muuta tilauksen tila Tilaukset-välilehdeltä ja tarkista merkintä audit-logista.

## TODO – seuraavat askeleet

- Lisää tuotteiden haku ja suodatuksen muistaminen `sessionStorage`-avaimella.
- Kytke kassapainikkeisiin webhook-pohjainen maksulinkin luonti (esim. Stripe Payment Links API).
- Toteuta a11y-audit (esim. Pa11y CLI) osaksi julkaisuprosessia.
