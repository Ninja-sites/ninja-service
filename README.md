# NINJA — site vitrine (FR · NL · AR)

Site statique d'une page, publié sur GitHub Pages : <https://ninja-sites.github.io/ninja-service/>

## Structure

| Chemin | Rôle |
|---|---|
| `index.html` | **Source maîtresse** — version française (racine). Contient les textes des **trois langues** dans les attributs `data-fr` / `data-nl` / `data-ar`. |
| `nl/index.html`, `ar/index.html` | Pages **générées** (ne pas éditer à la main) : textes figés dans une seule langue, `lang`/`dir` corrects, `canonical` + `hreflang`. |
| `build.py` | Générateur : reconstruit `nl/`, `ar/`, `sitemap.xml`, `robots.txt` depuis `index.html`. |
| `assets/` | Images de partage (`og-cover-*.png`), fiches A4 imprimables (`fiche-ninja-*.pdf`) et leurs gabarits HTML. |
| `images/` | Visuels du site (capture du site d'Al-Saouda). |
| `preview/` | Captures de contrôle (hors dépôt). |

## Modifier le contenu

1. Éditer **`index.html`** uniquement — pour chaque texte, remplir les trois attributs :
   `data-fr="…" data-nl="…" data-ar="…"` (le texte entre les balises sert de contenu français par défaut).
2. Régénérer les pages linguistiques :

   ```bash
   python3 build.py
   ```

3. Vérifier, committer, pousser : GitHub Pages republie automatiquement (~1 min).

## Activer les canaux de contact

Tout est dans l'objet `CHANNELS` du script en bas de `index.html` (et des pages générées après `build.py`) :

```js
var CHANNELS = {
  formEndpoint: "",  // URL qui reçoit le formulaire en POST JSON — vide = section formulaire masquée
  whatsapp: ""       // numéro international sans « + », ex. "32488123456" — vide = boutons WhatsApp inactifs
};
```

- `whatsapp` renseigné ⇒ les boutons WhatsApp et le bouton d'appel du site deviennent fonctionnels (message pré-rempli dans la langue du visiteur).
- `formEndpoint` renseigné ⇒ le formulaire « demander votre site » s'affiche et envoie `{nom, tel, type, msg}` en JSON.
- Tant que les deux sont vides, la section formulaire reste masquée : aucun visiteur ne peut envoyer une demande dans le vide.

## Fiches imprimables & images de partage

Générées depuis les gabarits HTML (`assets/fiche.html`, `assets/og-cover.html`) via un navigateur headless
(impression PDF + rasterisation). Après modification d'un gabarit, régénérer les 3 langues et replacer les
fichiers dans `assets/`.
