# Logo Assets Documentation

## ✅ Official Logos Downloaded

All logos have been downloaded from their official sources and adapted to a consistent 48x48px format.

### Tech Stack Icons (`assets/icons/tech/`)

| Technology | Source | Status |
|------------|--------|--------|
| **MikroTik** | [mikrotik.com](https://mikrotik.com/logo/library/logo/SVG/MT_Symbol_Black.svg) | ✅ Official |
| **Matrix** | [simpleicons.org](https://simpleicons.org/icons/matrix.svg) | ✅ Official |
| **Mastodon** | [Wikimedia Commons](https://upload.wikimedia.org/wikipedia/commons/4/48/Mastodon_Logotype_%28Simple%29.svg) | ✅ Official |
| **Home Assistant** | [Wikimedia Commons](https://upload.wikimedia.org/wikipedia/commons/a/ab/New_Home_Assistant_logo.svg) | ✅ Official |
| **Meshtastic** | [GitHub meshtastic/design](https://github.com/meshtastic/design) | ✅ Official |
| **Docker** | [SimpleIcons](https://cdn.simpleicons.org/docker/2496ED) | ✅ Official |
| **Node.js** | [SimpleIcons](https://cdn.simpleicons.org/nodedotjs/339933) | ✅ Official |
| **Nginx** | [SimpleIcons](https://cdn.simpleicons.org/nginx/009639) | ✅ Official |
| **Linux** | [SimpleIcons](https://cdn.simpleicons.org/linux/FCC624) | ✅ Official |
| **Git** | [SimpleIcons](https://cdn.simpleicons.org/git/F05032) | ✅ Official |

### Language Icons (`assets/icons/lang/`)

| Language | Source | Status |
|----------|--------|--------|
| **Python** | [SimpleIcons](https://cdn.simpleicons.org/python/3776AB) | ✅ Official |
| **C++** | [SimpleIcons](https://cdn.simpleicons.org/cplusplus/00599C) | ✅ Official |
| **C** | [SimpleIcons](https://cdn.simpleicons.org/c/A8B9CC) | ✅ Official |
| **JavaScript** | [SimpleIcons](https://cdn.simpleicons.org/javascript/F7DF1E) | ✅ Official |
| **HTML5** | [SimpleIcons](https://cdn.simpleicons.org/html5/E34F26) | ✅ Official |
| **CSS3** | [SimpleIcons](https://cdn.simpleicons.org/css3/1572B6) | ✅ Official |
| **Shell** | [SimpleIcons](https://cdn.simpleicons.org/shell/89E051) | ✅ Official |
| **TypeScript** | [SimpleIcons](https://cdn.simpleicons.org/typescript/3178C6) | ✅ Official |
| **Astro** | [SimpleIcons](https://cdn.simpleicons.org/astro/FF5D01) | ✅ Official |

## ⚠️ Logos Not Found / Special Cases

### MATLAB
- **Issue**: MATLAB logo is proprietary and not freely available
- **Current Solution**: Using stylized representation in generate_stats.py
- **Recommendation**: User should check MATLAB brand guidelines or use text-only representation

### Pascal
- **Issue**: No official Pascal logo exists (language is historical)
- **Current Solution**: Using generic circle with "P" letter in generate_stats.py
- **Recommendation**: Keep current approach or use Delphi logo if relevant

### TeX/LaTeX
- **Issue**: TeX logo is text-based and doesn't have an official SVG icon
- **Current Solution**: Using stylized representation in generate_stats.py
- **Recommendation**: Could use LaTeX project logo if preferred

## 📋 Format Specifications

All icons follow these specifications:
- **Size**: 48x48 pixels
- **Format**: SVG (Scalable Vector Graphics)
- **Border Radius**: 8px rounded corners for tech stack icons
- **Colors**: Official brand colors maintained
- **Optimization**: Minimal/clean SVG code

## 🔄 Future Updates

To update any logo:
1. Download from official source
2. Adapt to 48x48px format with 8px border radius
3. Ensure colors match official branding
4. Save to appropriate directory (`tech/` or `lang/`)
5. Test rendering in both light and dark modes

## 📝 Notes

- SimpleIcons (cdn.simpleicons.org) provides consistent, up-to-date logos for most technologies
- All icons are stored locally to avoid external dependencies
- Some logos were adapted from Wikimedia Commons (licensed for reuse)
- Official brand guidelines were followed for all logos where available
