#!/usr/bin/env python3
"""Круг 8: чистый лист для Влада — знак только в контексте, БЕЗ технических подписей.
/usr/local/lib/hermes-agent/venv/bin/python sheet8.py  -> r8-лист-для-Влада.png"""
from playwright.sync_api import sync_playwright
import build3 as B, wordmark3 as WM
D = B.D; FONTS = WM.FONTS
def u(n): return 'file://' + D + '/' + n
CSS = """
@font-face{font-family:G;src:url('file://%(f)s/golos-text-cyrillic-wght-normal.woff2');font-weight:100 900;unicode-range:U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116}
@font-face{font-family:G;src:url('file://%(f)s/golos-text-latin-wght-normal.woff2');font-weight:100 900;unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
*{box-sizing:border-box}body{margin:0;background:#8a8a8a;font-family:G,sans-serif;padding:32px 40px 40px;width:1520px}
.half{width:708px;flex:none}.full{width:1440px}
.gap{height:28px}
.hd{display:flex;align-items:center;justify-content:space-between;height:88px;padding:0 64px}
.hd.m{height:64px;padding:0 20px}
.dk{background:#1E1424;color:#FBEFDF}.lt{background:#FBEFDF;color:#2A1A2E}
.nav{display:flex;gap:32px;align-items:center;font:500 16px G}
.btn{padding:12px 20px;border-radius:999px;font:600 16px G}
.dk .btn{background:#FF7A45;color:#2A1A2E}.lt .btn{background:#2A1A2E;color:#FBEFDF}
.burger{width:26px;height:18px;border-top:2px solid currentColor;border-bottom:2px solid currentColor;position:relative}.burger:after{content:'';position:absolute;left:0;right:0;top:6px;border-top:2px solid currentColor}
.tabs{padding:8px 8px 0;width:708px;height:42px}
.tab{display:inline-flex;align-items:center;gap:8px;height:34px;width:220px;padding:0 12px;border-radius:8px 8px 0 0;font:12px/1 Roboto,Arial,sans-serif;margin-right:2px;vertical-align:bottom}
.tab img{width:16px;height:16px;image-rendering:pixelated}
.tab span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1}
.tabsL{background:#DEE1E6}.tabsL .a{background:#fff;color:#3c4043}.tabsL .i{color:#3c4043}
.tabsD{background:#202124}.tabsD .a{background:#35363A;color:#e8eaed}.tabsD .i{color:#e8eaed}
.av{display:inline-block;border-radius:50%%;overflow:hidden;margin-right:24px;vertical-align:middle}
.av img{width:100%%;height:100%%;display:block}
.feed{display:inline-flex;align-items:center;gap:12px;padding:14px 18px;border-radius:12px;font:14px Arial;margin-right:24px}
.feed.l{background:#fff;color:#111}.feed.d{background:#2E2238;color:#e8eaed;box-shadow:inset 0 0 0 1px rgba(255,255,255,.08)}
.row{display:flex;gap:24px;align-items:flex-start}
.pane{padding:24px 32px;display:flex;align-items:center;gap:0}.pane .av{margin-right:20px}.pane .feed{margin-right:0}
.favs{display:flex;align-items:flex-end;gap:28px}.favs img{display:block}
"""
def lock(suffix, h): return '<img src="%s" style="height:%dpx;display:block">' % (u('lumo-v5r8-wordmark-small%s.svg' % suffix), h)
def header(cls, suf, mobile=False):
    if mobile:
        return '<div class="hd m %s" style="width:708px">%s<div class="burger"></div></div>' % (cls, lock(suf, 43))
    return '<div class="hd %s" style="width:1440px">%s<div class="nav"><span>Курси</span><span>Ціни</span><span>Про нас</span><span>Блог</span><span class="btn">Пробний урок</span></div></div>' % (cls, lock(suf, 61))
def tabs(c, fav, title='Lumoschool: англійська онлайн'):
    return '<div class="tabs %s"><div class="tab a"><img src="%s"><span>%s</span><b>×</b></div><div class="tab i"><img src="%s"><span>Lumoschool — ціни</span><b>×</b></div></div>' % (c, fav, title, fav)
def avs(pref, suf, bg_cls, text_color):
    big = u('lumo-v5r8-avatar%s.svg' % suf); small = u('lumo-v5r8-avatar-small%s.svg' % suf)
    return ('<div class="pane half" style="background:%s">'
            '<div class="av" style="width:110px;height:110px"><img src="%s"></div><div class="av" style="width:56px;height:56px"><img src="%s"></div><div class="av" style="width:40px;height:40px"><img src="%s"></div>'
            '<span class="feed %s"><span class="av" style="width:40px;height:40px;margin:0 0 0 0"><img src="%s"></span><b>lumoschool</b> <span style="opacity:.6">· англійська онлайн</span></span></div>'
            % (pref, big, small, small, bg_cls, small))
def build():
    h = ['<style>%s</style>' % (CSS % {'f': FONTS})]
    h.append(header('dk', '') + '<div style="height:10px"></div>' + header('lt', '-onlight'))
    h.append('<div class="gap"></div><div class="row">%s%s</div>' % (header('dk', '', True), header('lt', '-onlight', True)))
    fd, fl = u('r8-favicon-16-dark.png'), u('r8-favicon-16-light.png')
    h.append('<div class="gap"></div><div class="row">%s%s</div>' % (tabs('tabsL', fl), tabs('tabsD', fd)))
    h.append('<div class="gap"></div><div class="row">%s%s</div>' % (avs('#FBEFDF', '-onlight', 'l', '#111'), avs('#1E1424', '', 'd', '#e8eaed')))
    def favs(bg, th):
        return '<div class="pane half" style="background:%s;height:120px"><div class="favs">%s</div></div>' % (bg, ''.join('<img src="%s">' % u('r8-favicon-%d-%s.png' % (n, th)) for n in (16, 32, 64)))
    h.append('<div class="gap"></div><div class="row">%s%s</div>' % (favs('#FBEFDF', 'light'), favs('#1E1424', 'dark')))
    h.append('<div class="gap"></div><div class="dk pane full">%s</div><div class="lt pane full" style="margin-top:8px">%s</div>'
             % ('<img src="%s" style="height:150px;display:block">' % u('lumo-v5r8-wordmark.svg'), '<img src="%s" style="height:150px;display:block">' % u('lumo-v5r8-wordmark-onlight.svg')))
    open('/root/.hermes/cache/scratch/sheet8.html', 'w').write('<html><body>' + ''.join(h) + '</body></html>')
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1600, 'height': 900}, device_scale_factor=1)
        pg.goto('file:///root/.hermes/cache/scratch/sheet8.html'); pg.wait_for_timeout(800)
        pg.screenshot(path=D + '/r8-лист-для-Влада.png', full_page=True); b.close()
if __name__ == '__main__': build(); print('sheet ok')
