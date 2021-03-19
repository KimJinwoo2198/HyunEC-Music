import subprocess
import sys

if sys.platform.startswith("win"):
    cmd = subprocess.Popen(
        ("python", "-m", "pip", "install", "-r", "requirements.txt"),
        stdout=subprocess.PIPE,
    )
    cmd.stdout.read()
    print("모듈 설치 완료")
else:
    print("윈도우가 아닌 다른 OS에서는 실행할 수 없습니다.")
    sys.exit()
