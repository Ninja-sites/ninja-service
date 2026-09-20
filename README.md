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

- `whatsapp` renseigné ⇒ le formulaire ouvre WhatsApp sur le téléphone du visiteur avec la demande déjà rédigée (`nom · activité · adresse · e-mail · téléphone · langue · message`).
- `formEndpoint` renseigné ⇒ le formulaire envoie la même demande en JSON (POST).
- Tant que les deux sont vides, le bouton d'envoi reste **désactivé** avec une note honnête (« envoi en cours d'activation ») : aucun visiteur ne peut envoyer une demande dans le vide, et rien n'est perdu silencieusement.

## Fonctionnement commercial reflété par le site
1. Le commerçant **laisse sa demande** (formulaire : nom, activité, adresse, e-mail, téléphone, langue de contact, message). **Pas d'appel, pas de rendez-vous.**
2. **Nous créons une démonstration gratuite** de son site et lui envoyons le lien par écrit.
3. S'il l'active : abonnement **20 €/mois tout compris** ; **0 € de création**.
4. **Domaine** : enregistré aux coordonnées du commerce mais **propriété du prestataire** tant qu'il n'est pas payé — **25 €/an** (montant qui suit le prix du service d'enregistrement), facturé dès le premier mois si le client veut en être propriétaire. En cas d'arrêt, le domaine reste chez nous, inutilisé, jusqu'à la fin de son enregistrement, puis redevient libre.

## Autres fichiers
- `manifest.webmanifest` · `assets/favicon.svg` + `assets/icon-*.png` : icône d'onglet et d'écran d'accueil.
- `404.html` : page d'erreur trilingue servie automatiquement par GitHub Pages.

## Fiches imprimables & images de partage

Générées depuis les gabarits HTML (`assets/fiche.html`, `assets/og-cover.html`) via un navigateur headless
(impression PDF + rasterisation). Après modification d'un gabarit, régénérer les 3 langues et replacer les
fichiers dans `assets/`.
