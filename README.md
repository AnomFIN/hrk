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
