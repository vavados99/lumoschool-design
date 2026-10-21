#!/usr/bin/env python3
"""Лист в контексте (PNG): шапка desktop 1440 / mobile 390, вкладка Chrome светлая/тёмная с фавиконом 16 px, аватар 110 px."""
import os
from playwright.sync_api import sync_playwright
import build3 as B
D = B.D; F = B.FONTS if hasattr(B, 'FONTS') else None
import wordmark3 as WM
FONTS = WM.FONTS
def u(n): return 'file://' + D + '/' + n
CSS = """
@font-face{font-family:G;src:url('file://%(f)s/golos-text-cyrillic-wght-normal.woff2');font-weight:100 900;unicode-range:U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116}
@font-face{font-family:G;src:url('file://%(f)s/golos-text-latin-wght-normal.woff2');font-weight:100 900;unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
*{box-sizing:border-box}body{margin:0;background:#8a8a8a;font-family:G,sans-serif;padding:24px 40px 40px}
h3{font:600 14px G;color:#fff;margin:26px 0 8px;letter-spacing:.02em}
.hd{display:flex;align-items:center;justify-content:space-between;height:88px;padding:0 64px}
.hd.m{height:64px;padding:0 20px}
.dk{background:#1E1424;color:#FBEFDF}.lt{background:#FBEFDF;color:#2A1A2E}
.nav{display:flex;gap:32px;align-items:center;font:500 16px G}
.btn{padding:12px 20px;border-radius:999px;font:600 16px G}
.dk .btn{background:#FF7A45;color:#2A1A2E}.lt .btn{background:#2A1A2E;color:#FBEFDF}
.burger{width:26px;height:18px;border-top:2px solid currentColor;border-bottom:2px solid currentColor;position:relative}.burger:after{content:'';position:absolute;left:0;right:0;top:6px;border-top:2px solid currentColor}
.tabs{display:inline-block;padding:8px 8px 0;width:560px;vertical-align:top}
.tab{display:inline-flex;align-items:center;gap:8px;height:34px;width:200px;padding:0 12px;border-radius:8px 8px 0 0;font:12px/1 Roboto,Arial,sans-serif;margin-right:2px;vertical-align:bottom}
.tab img{width:16px;height:16px;image-rendering:pixelated}
.tab span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1}
.tabsL{background:#DEE1E6}.tabsL .a{background:#fff;color:#3c4043}.tabsL .i{color:#3c4043}
.tabsD{background:#202124}.tabsD .a{background:#35363A;color:#e8eaed}.tabsD .i{color:#e8eaed}
.tabsL2{background:#DEE1E6}.tabsD2{background:#35363A}
.zoom{display:inline-block;margin-left:16px;vertical-align:top;padding:8px;border-radius:6px}
.zoom img{width:64px;height:64px;image-rendering:pixelated;display:block}
.av{display:inline-block;border-radius:50%%;overflow:hidden;margin-right:24px;vertical-align:middle}
.av img{width:100%%;height:100%%;display:block}
.feed{display:inline-flex;align-items:center;gap:12px;background:#fff;color:#111;padding:14px 18px;border-radius:12px;font:14px Arial;margin-right:24px}
.row{display:flex;gap:24px;align-items:flex-start}
"""
def lock(suffix, h): return '<img src="%s" style="height:%dpx;display:block">' % (u('lumo-v5r3-wordmark-small%s.svg' % suffix), h)
def build():
    def header(cls, suf, mobile=False):
        if mobile:
            return '<div class="hd m %s" style="width:390px">%s<div class="burger"></div></div>' % (cls, lock(suf, 43))
        return '<div class="hd %s" style="width:1440px">%s<div class="nav"><span>Курси</span><span>Ціни</span><span>Про нас</span><span>Блог</span><span class="btn">Пробний урок</span></div></div>' % (cls, lock(suf, 61))
    def tabs(c, favs, title='Lumoschool: англійська онлайн'):
        return ('<div class="tabs %s"><div class="tab a"><img src="%s"><span>%s</span><b>×</b></div><div class="tab i"><img src="%s"><span>Lumoschool — ціни</span><b>×</b></div></div>' % (c, favs, title, favs))
    h = ['<style>%s</style>' % (CSS % {'f': FONTS})]
    h.append('<h3>1. Шапка сайта desktop 1440 (знак упрощённый, ~48 px в шапке, без сердцевины) — тёмная и светлая</h3>' + header('dk', '') + '<div style="height:10px"></div>' + header('lt', '-onlight'))
    h.append('<h3>2. Шапка mobile 390</h3><div class="row">%s%s</div>' % (header('dk', '', True), header('lt', '-onlight', True)))
    h.append('<h3>3. Вкладка Chrome: светлая (#DEE1E6 полоса / белая вкладка) и тёмная (#202124 / #35363A), фавикон 16 px 1:1 + увеличение ×4</h3>')
    fd, fl = u('favicon-v5r3-16-dark.png'), u('favicon-v5r3-16-light.png')
    h.append('<div class="row"><div>%s<div style="height:14px"></div>%s</div><div>'
             '<div class="zoom tabsL2"><img src="%s"></div><div class="zoom tabsD2"><img src="%s"></div></div>'
             '<div class="tabs tabsL" style="width:240px;padding:0"><div class="tab i tabsL2" style="width:100%%"><img src="%s"><span>на #DEE1E6</span></div></div>'
             '<div class="tabs tabsD" style="width:240px;padding:0"><div class="tab i tabsD2" style="width:100%%;color:#e8eaed"><img src="%s"><span>на #35363A</span></div></div></div>'
             % (tabs('tabsL', fl), tabs('tabsD', fd), fl, fd, fl, fd))
    h.append('<h3>4. Аватар Instagram/Telegram: 110 px (круг), 56, 40</h3><div>'
             '<div class="av" style="width:110px;height:110px"><img src="%s"></div><div class="av" style="width:56px;height:56px"><img src="%s"></div><div class="av" style="width:40px;height:40px"><img src="%s"></div>'
             '<span class="feed"><span class="av" style="width:40px;height:40px;margin:0"><img src="%s"></span><b>lumoschool</b> <span style="color:#666">· ліфт для англійської</span></span></div>' % (u('lumo-v5r3-avatar.svg'), u('lumo-v5r3-avatar-small.svg'), u('lumo-v5r3-avatar-small.svg'), u('lumo-v5r3-avatar-small.svg')))
    h.append('<h3>5. Полная сборка со знаком-огнём (≥ 64 px высоты), kerning GPOS + ручная доводка</h3><div class="dk" style="padding:24px 40px;width:1100px">%s</div><div class="lt" style="padding:24px 40px;width:1100px;margin-top:8px">%s</div>'
             % ('<img src="%s" style="height:150px;display:block">' % u('lumo-v5r3-wordmark.svg'), '<img src="%s" style="height:150px;display:block">' % u('lumo-v5r3-wordmark-onlight.svg')))
    open('/root/.hermes/cache/scratch/sheet.html', 'w').write('<html><body>' + ''.join(h) + '</body></html>')
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1520, 'height': 900}, device_scale_factor=1)
        pg.goto('file:///root/.hermes/cache/scratch/sheet.html'); pg.wait_for_timeout(800)
        pg.screenshot(path=D + '/лист-в-контексте.png', full_page=True); b.close()
if __name__ == '__main__': build(); print('sheet ok')
