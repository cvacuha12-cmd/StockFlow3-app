[app]
title = StockFlow Pro
package.name = stockflow
package.domain = org.stockflow
source.dir = .
source.include_exts = py
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0

android.permissions = INTERNET, CAMERA
android.api = 30
android.minapi = 21
android.arch = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
