import os

path = r'C:\ksp.json'

if os.path.exists(path):
    print("✅ הקובץ נמצא במסלול שצוין.")
else:
    print("❌ הקובץ לא נמצא במסלול הזה.")
