from PyQt5.QtGui import QMovie
movie = QMovie("/Volumes/ORICO-PT/pongthai/projects/ai-assistant-platform/mira_client_pi/assets/avatar_pingping_v3.gif")
print("✅" if movie.isValid() else "❌ QMovie failed")