[app]

title = Expense Tracker
package.name = expensetracker
package.domain = org.engineerj344

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

# Include KivyMD in the requirements
requirements = python3,kivy

orientation = portrait
fullscreen = 0

android.accept_sdk_license = True
android.arch = armeabi-v7a

[buildozer]

log_level = 2
warn_on_root = 1
