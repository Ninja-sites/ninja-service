#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
يبني صفحتَي اللغتين الثابتتين (nl/ و ar/) + sitemap.xml + robots.txt من الملفّ الأمّ index.html.

الملفّ الأمّ `index.html` هو النسخة الفرنسية (الرئيسية) ويحمل نصوص اللغات الثلاث
في سمات data-fr / data-nl / data-ar. هذا السكربت:
  1) يثبّت نصوص لغة واحدة في الصفحة ويحذف السمات،
  2) يضبط <html lang/dir> والعنوان والوصف و og/pages,
  3) يضبط مبدّل اللغات وروابط hreflang/canonical ومسارات الأصول النسبية.

الاستعمال:  python3 build.py
أي تعديل على المحتوى يجب أن يُجرى في index.html ثم يُعاد البناء، وإلّا تفرّقت النسخ.
"""
import os
import re
from html.parser import HTMLParser

BASE = "https://ninja-sites.github.io/ninja-service"
ROOT = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(ROOT, "index.html")

META = {
    "fr": {
        "title": "NINJA — Sites web pour commerces de quartier · 0 € de création, 20 €/mois",
        "desc": "Votre commerce mérite d'être trouvé. Nous créons votre site professionnel : 0 € de création, puis 20 €/mois tout compris — hébergement, mises à jour, Google, WhatsApp. Bruxelles.",
        "locale": "fr_BE",
        "dir": "ltr",
    },
    "nl": {
        "title": "NINJA — Websites voor buurtzaken · 0 € opstartkost, daarna 20 €/maand",
        "desc": "Uw zaak verdient het om gevonden te worden. Wij maken uw professionele website: 0 € opstartkost, daarna 20 €/maand alles inbegrepen — hosting, updates, Google, WhatsApp. Brussel.",
        "locale": "nl_BE",
        "dir": "ltr",
    },
    "ar": {
        "title": "نينجا — مواقع لمحلات الحيّ · 0 € للبناء ثم 20 € شهريًا",
        "desc": "محلّك يستحقّ أن يُوجَد. نبني موقعك الاحترافي: 0 € للبناء ثم 20 € شهريًّا شاملة كل شيء — الاستضافة، التحديثات، جوجل، واتساب. بروكسل.",
        "locale": "ar_BE",
        "dir": "rtl",
    },
}

SWITCHERS = {
    "fr": ('<div class="langs">'
           '<a class="lang" href="./" hreflang="fr" aria-current="true">FR</a>'
           '<a class="lang" href="nl/" hreflang="nl">NL</a>'
           '<a class="lang" href="ar/" hreflang="ar">العربية</a>'
           '</div>'),
    "nl": ('<div class="langs">'
           '<a class="lang" href="../" hreflang="fr">FR</a>'
           '<a class="lang" href="./" hreflang="nl" aria-current="true">NL</a>'
           '<a class="lang" href="../ar/" hreflang="ar">العربية</a>'
           '</div>'),
    "ar": ('<div class="langs">'
           '<a class="lang" href="../" hreflang="fr">FR</a>'
           '<a class="lang" href="../nl/" hreflang="nl">NL</a>'
           '<a class="lang" href="./" hreflang="ar" aria-current="true">العربية</a>'
           '</div>'),
}

LANGFILE = {"fr": "", "nl": "nl/", "ar": "ar/"}
REDIRECTS = {
    "fr": "{fr:'.',nl:'nl/',ar:'ar/'}",
    "nl": "{fr:'../',ar:'../ar/'}",
    "ar": "{fr:'../',nl:'../nl/'}",
}


class _Localize(HTMLParser):
    """يجمع عناصر data-fr/nl/ar مع مواضع نصّها الداخلي (يتحمّل وسومًا متداخلة)."""

    def __init__(self, lang, src):
        super().__init__(convert_charrefs=False)
        self.lang = lang
        self.src = src
        self.offsets = [0]
        for line in src.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        self.stack = []
        self.spans = []

    def _pos(self):
        line, col = self.getpos()
        return self.offsets[line - 1] + col

    def handle_starttag(self, tag, attrs):
        raw = self.get_starttag_text()
        start = self._pos()
        has = {k: v for k, v in attrs if k in ("data-fr", "data-nl", "data-ar")}
        self.stack.append((tag, start, raw, has))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                t, start, raw, has = self.stack.pop(i)
                key = "data-" + self.lang
                if key in has:
                    self.spans.append((start, start + len(raw), self._pos(), raw, has[key]))
                del self.stack[i:]
                return


def localize(src, lang):
    """يثبّت نصوص لغة واحدة داخل عناصر data-* ويحذف السمات، باحترام الوسوم المتداخلة."""
    par = _Localize(lang, src)
    par.feed(src)
    par.close()
    edits = []
    for tag_start, content_start, content_end, raw, value in par.spans:
        clean = re.sub(r'\s+data-(fr|nl|ar)="[^"]*"', "", raw)
        edits.append((tag_start, content_end, clean + value))
    for start, end, rep in sorted(edits, key=lambda e: e[0], reverse=True):
        src = src[:start] + rep + src[end:]
    assert len(edits) == 97, "expected 97 localized elements, got %d" % len(edits)
    return src


def alt_links(lang):
    out = []
    for l in ("fr", "nl", "ar"):
        out.append('<link rel="alternate" hreflang="%s" href="%s/%s">' % (l, BASE, LANGFILE[l]))
    out.append('<link rel="alternate" hreflang="x-default" href="%s/">' % BASE)
    out = "\n".join(out)
    canonical = '<link rel="canonical" href="%s/%s">' % (BASE, LANGFILE[lang])
    return canonical, out


def build_lang(src, lang, out_path):
    m = META[lang]
    s = src
    s = s.replace('<html lang="fr" dir="ltr">', '<html lang="%s" dir="%s">' % (lang, m["dir"]), 1)

    # 1) fixer les textes de la langue + retirer les attributs data-*
    s = localize(s, lang)
    assert "data-fr=" not in s and "data-nl=" not in s and "data-ar=" not in s, "leftover data-* attributes"

    # 2) titre / description / og
    s = re.sub(r"<title>.*?</title>", "<title>%s</title>" % m["title"], s, count=1, flags=re.S)
    s = re.sub(r'<meta name="description" content="[^"]*">',
               '<meta name="description" content="%s">' % m["desc"], s, count=1)
    s = re.sub(r'<meta property="og:title" content="[^"]*">',
               '<meta property="og:title" content="%s">' % m["title"], s, count=1)
    s = re.sub(r'<meta property="og:description" content="[^"]*">',
               '<meta property="og:description" content="%s">' % m["desc"], s, count=1)
    s = re.sub(r'<meta property="og:locale" content="[^"]*">',
               '<meta property="og:locale" content="%s">' % m["locale"], s, count=1)
    s = s.replace("og-cover-fr.png", "og-cover-%s.png" % lang, 1)

    # 3) canonical + hreflang
    canonical, alts = alt_links(lang)
    s = re.sub(r'<link rel="canonical"[^>]*>\n(<link rel="alternate"[^>]*>\n)+', canonical + "\n" + alts + "\n", s, count=1)
    s = re.sub(r'(<meta property="og:url" content=")[^"]*(">)', r"\1%s/%s\2" % (BASE, LANGFILE[lang]), s, count=1)

    # 4) meneur de langues + redirections ?lang
    s = re.sub(r'<div class="langs">.*?</div>', SWITCHERS[lang].replace("\\", "\\\\"), s, count=1, flags=re.S)
    s = s.replace("{fr:'.',nl:'nl/',ar:'ar/'}", REDIRECTS[lang], 1)

    # 5) chemins relatifs (pages en sous-dossier)
    s = s.replace('src="images/', 'src="../images/').replace('href="assets/', 'href="../assets/')
    s = s.replace("fiche-ninja-fr.pdf", "fiche-ninja-%s.pdf" % lang)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(s)
    return len(s.encode("utf-8"))


def build_sitemap():
    rows = []
    for l in ("fr", "nl", "ar"):
        alts = "".join(
            '\n    <xhtml:link rel="alternate" hreflang="%s" href="%s/%s"/>' % (o, BASE, LANGFILE[o])
            for o in ("fr", "nl", "ar")
        )
        rows.append(
            "  <url>\n    <loc>%s/%s</loc>%s\n    <changefreq>monthly</changefreq>\n"
            "    <priority>%s</priority>\n  </url>"
            % (BASE, LANGFILE[l], alts, "1.0" if l == "fr" else "0.8")
        )
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
           'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(rows) + "\n</urlset>\n")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(xml)
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % BASE)


def main():
    with open(MASTER, encoding="utf-8") as fh:
        src = fh.read()
    for lang, rel in (("nl", "nl/index.html"), ("ar", "ar/index.html")):
        n = build_lang(src, lang, os.path.join(ROOT, rel))
        print("built %-16s %6d bytes" % (rel, n))
    build_sitemap()
    print("built sitemap.xml + robots.txt")


if __name__ == "__main__":
    main()
