# 🎨 Guide Technique - Site Web Workly

Guide de référence rapide pour modifier et personnaliser le site web.

---

## 📋 Table des matières

1. [Modifier les couleurs](#modifier-les-couleurs)
2. [Ajouter une nouvelle page](#ajouter-une-nouvelle-page)
3. [Modifier les animations](#modifier-les-animations)
4. [Ajouter des images](#ajouter-des-images)
5. [Personnaliser le footer](#personnaliser-le-footer)
6. [Responsive Design](#responsive-design)

---

## 🎨 Modifier les couleurs

### Variables CSS (`assets/css/style.css` lignes 8-21)

```css
:root {
    --primary-color: #903f9e;      /* Violet principal - Change ici */
    --primary-dark: #6d2d77;       /* Violet foncé */
    --primary-light: #b05baf;      /* Violet clair */
    --secondary-color: #1a1a2e;    /* Couleur secondaire */
    --background: #0f0f1e;         /* Fond de page */
    --surface: #1a1a2e;            /* Fond des cartes */
    --text-primary: #ffffff;       /* Texte principal */
    --text-secondary: #b8b8d1;     /* Texte secondaire */
    --accent: #ff6b9d;             /* Couleur accent (rose) */
    --success: #4ecca3;            /* Vert succès */
}
```

**Pour changer le thème :**
1. Ouvre `assets/css/style.css`
2. Modifie `--primary-color` (ligne 10)
3. Ajuste `--primary-dark` et `--primary-light` si nécessaire
4. Rafraîchis la page (Ctrl+F5)

**Exemples de palettes alternatives :**

```css
/* Thème bleu */
--primary-color: #3498db;
--primary-dark: #2980b9;
--primary-light: #5dade2;

/* Thème vert */
--primary-color: #2ecc71;
--primary-dark: #27ae60;
--primary-light: #58d68d;

/* Thème orange */
--primary-color: #e67e22;
--primary-dark: #d35400;
--primary-light: #f39c12;
```

---

## 📄 Ajouter une nouvelle page

### Étape 1 : Créer le fichier HTML

**Emplacement :** `web/pages/nouvelle-page.html`

**Template de base :**

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Description de la page">
    <title>Titre | Workly</title>
    <link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>
    <!-- NAVIGATION -->
    <nav class="navbar">
        <div class="container">
            <a href="../index.html" class="logo">🎭 Workly</a>
            
            <ul class="nav-links">
                <li><a href="../index.html">Accueil</a></li>
                <li><a href="about.html">À propos</a></li>
                <li><a href="nouvelle-page.html">Nouvelle Page</a></li>
                <li><a href="terms.html">CGU</a></li>
                <li><a href="privacy.html">Confidentialité</a></li>
            </ul>
            
            <div class="mobile-menu-toggle">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    </nav>

    <!-- HEADER -->
    <section class="hero" style="min-height: 50vh;">
        <div class="hero-content">
            <h1>Titre de la page</h1>
            <p class="subtitle">Sous-titre</p>
        </div>
    </section>

    <!-- CONTENT -->
    <section class="section">
        <div class="container">
            <div class="card fade-in">
                <h2 style="color: var(--primary-light);">Section 1</h2>
                <p style="color: var(--text-secondary);">
                    Contenu de la page...
                </p>
            </div>
        </div>
    </section>

    <!-- FOOTER -->
    <footer class="footer">
        <div class="footer-content">
            <div class="footer-links">
                <a href="../index.html">Accueil</a>
                <a href="about.html">À propos</a>
                <a href="nouvelle-page.html">Nouvelle Page</a>
                <a href="terms.html">CGU</a>
                <a href="privacy.html">Confidentialité</a>
            </div>
            <p>&copy; 2025 Workly. Développé avec 💜 par Xyon15</p>
        </div>
    </footer>

    <script src="../assets/js/main.js"></script>
</body>
</html>
```

### Étape 2 : Ajouter le lien dans les autres pages

**Fichiers à modifier :**
- `index.html` (ligne ~25)
- `pages/about.html` (ligne ~15)
- `pages/terms.html` (ligne ~15)
- `pages/privacy.html` (ligne ~15)

**Ajouter dans `<ul class="nav-links">` :**
```html
<li><a href="pages/nouvelle-page.html">Nouvelle Page</a></li>
```

### Étape 3 : Ajouter dans le footer

**Ajouter dans `<div class="footer-links">` :**
```html
<a href="pages/nouvelle-page.html">Nouvelle Page</a>
```

---

## ✨ Modifier les animations

### Vitesse d'apparition au scroll

**Fichier :** `assets/js/main.js` (lignes 29-31)

```javascript
const observerOptions = {
    threshold: 0.05,                    // 5% de l'élément visible
    rootMargin: '0px 0px 100px 0px'    // Déclenche 100px avant
};
```

**Pour déclencher plus tôt :**
```javascript
threshold: 0.01,                    // 1% visible
rootMargin: '0px 0px 200px 0px'    // 200px avant
```

**Pour déclencher plus tard :**
```javascript
threshold: 0.2,                     // 20% visible
rootMargin: '0px 0px 0px 0px'      // Au moment où visible
```

### Délai en cascade des cartes

**Fichier :** `assets/js/main.js` (ligne 52)

```javascript
card.style.transitionDelay = `${index * 0.1}s`;
```

**Plus rapide (50ms entre chaque) :**
```javascript
card.style.transitionDelay = `${index * 0.05}s`;
```

**Plus lent (200ms entre chaque) :**
```javascript
card.style.transitionDelay = `${index * 0.2}s`;
```

**Désactiver complètement :**
```javascript
// Commenter ou supprimer cette ligne
// card.style.transitionDelay = `${index * 0.1}s`;
```

### Vitesse de transition au hover

**Fichier :** `assets/css/style.css`

**Cartes générales (ligne 293) :**
```css
.card {
    transition: all 0.3s ease;  /* Change 0.3s */
}
```

**Cartes de fonctionnalités (ligne 359) :**
```css
.feature-item {
    transition: all 0.3s ease;  /* Change 0.3s */
}
```

**Cartes de phases (ligne 473) :**
```css
.endpoint-card {
    transition: all 0.3s ease;  /* Change 0.3s */
}
```

**Valeurs recommandées :**
- `0.15s` : Très rapide
- `0.3s` : Normal (défaut)
- `0.5s` : Lent

---

## 🖼️ Ajouter des images

### Étape 1 : Placer les images

**Emplacement :** `web/assets/images/`

**Exemple :**
```
web/assets/images/
├── logo.png
├── favicon.png
├── screenshot1.jpg
└── screenshot2.jpg
```

### Étape 2 : Utiliser dans HTML

**Image simple :**
```html
<img src="assets/images/logo.png" alt="Logo Workly">
```

**Depuis une page dans `pages/` :**
```html
<img src="../assets/images/logo.png" alt="Logo Workly">
```

### Étape 3 : Ajouter un favicon

**Dans `<head>` de toutes les pages :**
```html
<link rel="icon" type="image/png" href="assets/images/favicon.png">
```

**Ou depuis `pages/` :**
```html
<link rel="icon" type="image/png" href="../assets/images/favicon.png">
```

### Optimisation images

**Recommandations :**
- **Format :** WebP pour meilleure compression
- **Taille max :** 1920px de largeur
- **Compression :** 80-90% qualité
- **Outils :** TinyPNG, Squoosh

---

## 🦶 Personnaliser le footer

### Modifier le copyright

**Fichier :** Tous les fichiers HTML (section `<footer>`)

```html
<p>&copy; 2025 Workly. Développé avec 💜 par Xyon15</p>
```

**Exemples de variations :**
```html
<!-- Sans emoji -->
<p>&copy; 2025 Workly. Développé par Xyon15</p>

<!-- Avec date dynamique (JavaScript requis) -->
<p>&copy; <span id="year"></span> Workly. Développé par Xyon15</p>
<script>document.getElementById('year').textContent = new Date().getFullYear();</script>

<!-- Avec lien -->
<p>&copy; 2025 Workly. Développé par <a href="https://github.com/Xyon15">Xyon15</a></p>
```

### Ajouter des liens sociaux

**Après les liens existants :**
```html
<div class="footer-links">
    <a href="index.html">Accueil</a>
    <a href="pages/about.html">À propos</a>
    <a href="pages/terms.html">CGU</a>
    <a href="pages/privacy.html">Confidentialité</a>
    
    <!-- Nouveaux liens sociaux -->
    <a href="https://github.com/Xyon15/desktop-mate" target="_blank">GitHub</a>
    <a href="https://discord.gg/votre-serveur" target="_blank">Discord</a>
    <a href="https://twitter.com/votre-compte" target="_blank">Twitter</a>
</div>
```

---

## 📱 Responsive Design

### Breakpoints actuels

**Fichier :** `assets/css/style.css` (ligne 423+)

```css
@media (max-width: 768px) {
    /* Styles mobile */
}
```

### Ajouter un breakpoint tablette

```css
/* Tablette */
@media (max-width: 1024px) and (min-width: 769px) {
    .hero h1 {
        font-size: 3rem;
    }
    
    .cards-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}
```

### Tester le responsive

**Option 1 : DevTools**
- F12 → Toggle device toolbar (Ctrl+Shift+M)
- Sélectionner un device (iPhone, iPad, etc.)

**Option 2 : Redimensionner navigateur**
- Redimensionner la fenêtre manuellement
- Observer les changements

**Option 3 : Responsive Design Mode**
- Firefox : Ctrl+Shift+M
- Chrome : F12 → Device Toggle

---

## 🛠️ Dépannage rapide

### Les animations ne fonctionnent pas

**Vérifier :**
1. JavaScript chargé : `<script src="assets/js/main.js"></script>`
2. Console navigateur (F12) : pas d'erreurs ?
3. Classe `.fade-in` présente sur éléments
4. Navigateur supporte IntersectionObserver (Chrome 90+)

### Le menu mobile ne s'ouvre pas

**Vérifier :**
1. JavaScript chargé
2. Classes `.mobile-menu-toggle` et `.nav-links` présentes
3. Console : pas d'erreurs JavaScript

### Les couleurs ne changent pas

**Vérifier :**
1. Variables CSS modifiées dans `:root`
2. Cache navigateur vidé (Ctrl+Shift+R)
3. Fichier CSS bien chargé

### Les liens ne fonctionnent pas

**Vérifier :**
1. Chemins relatifs corrects (`pages/about.html` ou `../index.html`)
2. Fichiers existent aux emplacements spécifiés
3. Casse du nom de fichier (sensible sur Linux/Mac)

---

## 📚 Ressources utiles

### Documentation

- [MDN Web Docs](https://developer.mozilla.org/)
- [CSS-Tricks](https://css-tricks.com/)
- [W3Schools](https://www.w3schools.com/)

### Outils

- [TinyPNG](https://tinypng.com/) - Compression d'images
- [Coolors](https://coolors.co/) - Générateur de palettes
- [Google Fonts](https://fonts.google.com/) - Polices web
- [Font Awesome](https://fontawesome.com/) - Icônes

### Inspiration

- [Awwwards](https://www.awwwards.com/)
- [Dribbble](https://dribbble.com/)
- [Behance](https://www.behance.net/)

---

**Guide technique complet ! ✨**
