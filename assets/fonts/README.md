# Fonts

Place bundled Chinese fonts in this directory so the game renders text consistently across Windows, macOS, and Linux.

Recommended files:

- `NotoSansCJKsc-Regular.otf`
- `NotoSansCJKsc-Bold.otf` (optional, used for menu titles)

Recommended source:

- Noto CJK: https://github.com/notofonts/noto-cjk

`settings.py` loads fonts from this directory before falling back to system fonts.
