# docs-site

Static site source for the mellea-contribs GitHub Pages index. Built by
`.github/workflows/pages.yml` on push to `main`, on release-tag pushes
(`mellea-*/v*`), and on manual dispatch.

## Build locally

```bash
uv pip install --system Jinja2 markdown Pygments packaging
python docs-site/build.py --output _site
python -m http.server -d _site 8000
```

All install commands emitted on the site go through `pip install
"git+https://github.com/<repo>.git@<tag>#subdirectory=<pkg_dir>"`. Wheels
attached to GitHub Releases are not referenced — the git tag is the single
source of install identity.
