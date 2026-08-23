[app]
title = StockFlow Pro
package.name = stockflow
package.domain = org.stockflow
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0
requirements = python3,kivy,pyzbar,pillow
orientation = portrait
fullscreen = 0

android.permissions = INTERNET, CAMERA
android.api = 33
android.minapi = 21
android.arch = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
