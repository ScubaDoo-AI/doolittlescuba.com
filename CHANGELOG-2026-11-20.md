# Changelog — 20 Nov 2026

## Organic cards: the whole shirt in frame
Eric: *"Organic Thistlegorm back looks bad on the website."*

- The organic page showed its Printful mockups (`img/organic/`, replaced 19 Nov) with the old zoom-and-crop (cover at 118%), so the back print lost its right edge (the Egypt block), the collar and both sleeves. `css/site.css` now gives `img/organic/` the same treatment as the other Printful images: the whole square shot in frame (contain, 125%). Affects every organic card (front, sleeve, back), not just the Thistlegorm.
