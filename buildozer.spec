[app]

# (string) Title of your application
title = Snakes and Ladders

# (string) Package name
package.name = snakesladders

# (string) Package domain (needed for android package identifier)
package.domain = org.example

# (string) Source code directory
source.dir = .

# (list) Source files to include (extensions separated by commas)
source.include_exts = py,png,jpg,kv,atlas

# (string) Application version
version = 0.1

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy

# (str) Supported orientation (one of landscape, portrait or all)
orientation = landscape

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Android architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# =============================================================================
# Google Play Store Production Settings
# =============================================================================

# (string) Format to build (apk or aab). Google Play requires aab for new apps!
android.release_artifact = aab

# (string) python-for-android branch to use
p4a.branch = master

# =============================================================================
# Digital Security Signing Key Configurations
# =============================================================================

# (str) The name of your keystore file uploaded to your repository
android.keystore = my-release-key.keystore

# (str) The password you created for your keystore file
android.keystore_password = mysecretpassword

# (str) The alias name inside your keystore file
android.keyalias = my-key-alias

# (str) The alias password (usually the same as the keystore password)
android.keyalias_password = mysecretpassword

# (bool) Automatically accept the Android SDK licenses in the cloud runner
android.accept_sdk_license = True

# =============================================================================
# Default System Settings (Leave as default)
# =============================================================================
android.api = 33
android.minapi = 21
android.ndk_api = 21
log_level = 2
warn_on_root = 1
