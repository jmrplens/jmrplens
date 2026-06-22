# Rediseño del README de perfil (autogenerado por CI/CD)

**Fecha:** 2026-06-22
**Repo:** `jmrplens/jmrplens` (README que se muestra en el perfil de GitHub)
**Estado:** Diseño aprobado, pendiente de plan de implementación

## Problema

El README se autogenera cada 12 h vía GitHub Actions (`generate_stats.py`). Tres problemas detectados (verificados con Playwright sobre `https://github.com/jmrplens` en escritorio 1280px y móvil 390px):

1. **Posts del blog**: tabla HTML de 3 columnas (`width="33%"`). En escritorio queda apretada; en móvil **desborda horizontalmente** y el 3er post se corta fuera de pantalla, con títulos partidos palabra por palabra. Las tablas markdown no reflowean en GitHub.
2. **Panel de estadísticas (SVG)**: "Most Used Languages" pondera por **bytes globales**, así que uno o dos repos de tooling con código generado/vendado aplastan todo (`C 117M · C++ 33M · Go 23M`). Malrepresenta al usuario (cuyo trabajo real es acústica/embebido/research). Además inventa datos: "líneas" = bytes÷50, y "commits estimados" = eventos×10.
3. **Falta un flujo repetible** para visualizar el resultado como lo ve un visitante (escritorio + móvil) antes de commitear.

## Restricciones conocidas

- **GitHub sanea HTML/CSS en `.md`**: no `style`, ni clases, ni `grid`, ni media queries. Lo único responsive de verdad es `<table>` y el apilado vertical. Los SVG sí los controlamos por completo (los generamos nosotros), pero **escalan de forma uniforme** con el ancho (en móvil el texto se ve más pequeño; no reflowea como el HTML).
- **Imágenes en markdown**: una `<img>` no permite enlaces internos ni texto seleccionable. Pero `[![alt](card.svg)](url)` hace **toda la imagen clicable** hacia una URL.
- **GitHub no permite crear PATs por API**: el token de CI para repos privados lo crea el usuario manualmente en la web.

## Decisiones (acordadas con el usuario)

| Tema | Decisión |
|------|----------|
| Posts | 3 tarjetas **SVG apiladas verticalmente**, cada una envuelta en enlace al post (clicable entera). dark/light en dos archivos. |
| Lenguajes | Métrica **normalizada** (cuota de cada lenguaje *dentro de cada repo*, promediada entre repos → ningún repo domina), mostrada en **% honesto**, top 8. |
| Privados | Incluidos **solo en lenguajes** (agregado, no revela nombres). Los recuentos visibles (repos, stars) se quedan en datos públicos. |
| Métricas actividad | Añadir fila con datos **reales vía GraphQL**: Repos (públicos), Stars, Seguidores, Commits (último año), Contribuciones (último año). Eliminar números inventados. |
| Theming | **Dos archivos** por elemento (`*-dark.svg` / `*-light.svg`) con `#gh-dark-mode-only` / `#gh-light-mode-only`. Patrón probado actual. |
| Token CI | Secret `GH_STATS_TOKEN` (fine-grained PAT read-only, todos los repos). Lo crea el usuario. Fallback a `GITHUB_TOKEN` (solo público) si no existe. |
| Mirror Gitea | **Eliminar** el workflow deshabilitado `update-blog.yml.disabled` (el destino ya no existe). |
| Nº posts | 3. |

## Arquitectura

### Datos: por qué la métrica normalizada funciona

Verificado con datos reales (GraphQL, públicos + privados):

```
lang        bytes (hoy)   normalizado(+priv)
MATLAB           2.3M           8.56   ← research/acústica arriba, como debe
Python           2.4M           4.76
Go              23.3M           3.30   ← honesto: 2 repos Go, ya no aplasta
TeX                 -           2.80
C              117.9M           2.54   ← embebido (privados) aparece
C++             33.8M           1.96   ← Kleidos/Anechoic_Robot aparecen
Shell               -           1.97
```

Normalización: para cada repo se calcula `size_lang / size_total_repo`; se suman esas cuotas entre todos los repos no-fork. Para mostrar, se reescala el top-8 a sumar 100% → porcentajes limpios.

### Componentes (refactor de `generate_stats.py` en módulos con responsabilidad única)

El script monolítico actual se descompone en piezas que se entienden y prueban por separado:

1. **`fetch.py` — obtención de datos** (GraphQL, una/dos llamadas):
   - `fetch_languages(token)` → dict normalizado `{lang: weight}` usando `viewer.repositories(ownerAffiliations:OWNER, isFork:false)` con `isPrivate` incluido si el token lo permite. Si el token solo ve público, degrada a público.
   - `fetch_activity(token)` → `{public_repos, total_stars, followers, commits_year, contributions_year}` desde campos públicos (`user(login:"jmrplens")`).
   - `fetch_blog_posts(n=3)` → del RSS `https://jmrp.io/rss.xml` (reutiliza parser actual; añade fecha del item).
   - Qué hace: convierte API → estructuras planas. Depende de: `requests`, token. Testeable con respuestas mock.

2. **`render_stats.py` — panel de estadísticas SVG**:
   - `render_stats_svg(lang_pcts, activity, theme)` → string SVG.
   - Fila superior: Repos · Stars · Seguidores · Commits (año) · Contribuciones (año).
   - Lista de lenguajes: icono + nombre + barra proporcional + `%`. Sin "líneas".
   - Depende de: iconos en `assets/icons/lang/`, paleta `LANG_COLORS`.

3. **`render_blog.py` — tarjetas de blog SVG**:
   - `render_blog_card_svg(post, index, theme)` → string SVG de una tarjeta (índice/fecha, título con wrapping a N líneas, extracto 1–2 líneas, "Read more →").
   - Una tarjeta por post; el README las envuelve en enlace.
   - Diseño coherente con el panel (gradiente `#667eea→#764ba2`, fuentes Segoe UI, esquinas redondeadas, mismos colores de tema).

4. **`update_readme.py` — montaje del README**:
   - Reemplaza el bloque entre `<!-- BLOG-POSTS:START -->` / `END` por las 3 tarjetas apiladas:
     ```
     [![Post 1](generated/blog-1-dark.svg#gh-dark-mode-only)](url1)
     [![Post 1](generated/blog-1-light.svg#gh-light-mode-only)](url1)
     ```
     (cada par de líneas = una tarjeta; el badge "Read all posts" se mantiene debajo).
   - El bloque del panel de stats ya existe en el README y no cambia su ubicación.

5. **`generate_stats.py` — orquestador** (entrypoint que CI ejecuta): llama fetch → render → escribe `generated/*.svg` → update_readme.

### Salidas en `generated/`

- `github-stats-dark.svg`, `github-stats-light.svg` (se mantienen nombres).
- `blog-1-dark.svg` … `blog-3-dark.svg` y `…-light.svg` (6 archivos).
- Borrar artefactos obsoletos: `github-stats.svg`, `github-stats-backup.svg`.

### Verificación con Playwright (paso repetible)

Script de preview local (`preview_readme.py` o similar) que:
1. Renderiza `README.md` a HTML vía la API `POST /markdown` de GitHub (fiel al render real).
2. Lo envuelve con `github-markdown-css` y rutas locales a `generated/*.svg`.
3. Playwright captura escritorio (1280px) y móvil (390px).

Se ejecuta manualmente al iterar diseño; no forma parte del commit de CI.

### CI/CD (`.github/workflows/generate-stats.yml`)

- Mantener triggers: `push` a main, cron `0 0,12 * * *`, `workflow_dispatch`.
- Paso de generación usa `GH_STATS_TOKEN` si existe, si no `GITHUB_TOKEN`:
  ```yaml
  env:
    GH_TOKEN_STATS: ${{ secrets.GH_STATS_TOKEN || secrets.GITHUB_TOKEN }}
  ```
- `git add generated/*.svg README.md` (incluye las nuevas tarjetas).
- **Borrar** `.github/workflows/update-blog.yml.disabled`.

### Acción manual del usuario (documentada, no automatizable)

Crear el secret para incluir privados en lenguajes:
1. GitHub → Settings → Developer settings → **Fine-grained tokens** → Generate new token.
2. Resource owner: `jmrplens`. Repository access: **All repositories**. Permissions: Repository → **Metadata: Read-only** (y **Contents: Read-only** si hiciera falta para languages). Sin permisos de escritura.
3. Copiar el token → repo `jmrplens/jmrplens` → Settings → Secrets and variables → Actions → New repository secret → nombre **`GH_STATS_TOKEN`**.

Si no se crea, el generador funciona en modo solo-público (degradación limpia).

## Criterios de éxito

- En móvil 390px: los 3 posts se ven completos, apilados, sin desborde horizontal, legibles. Toda la tarjeta es clicable al post.
- El panel de lenguajes muestra MATLAB/Python/C/C++ representativos (no un Go/C dominante por bytes), en % que suman 100%.
- El panel muestra métricas reales (commits/contribuciones del año), sin números inventados.
- Lenguajes incluyen repos privados (agregado) cuando `GH_STATS_TOKEN` está presente; degradan a público si no.
- CI sigue corriendo en cron 12h y commitea solo si hay cambios.
- Verificado visualmente con Playwright en escritorio y móvil antes de dar por bueno.

## Fuera de scope

- Mirror a Gitea/Forgejo (se elimina).
- Cambiar las secciones curadas (About Me, Tech Stack icons, Connect With Me).
- Métricas que requieran servicios externos o bases de datos.
