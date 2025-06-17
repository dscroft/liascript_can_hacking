import base64
import json
import sys

markdown_url = "https://dscroft.github.io/liascript_can_hacking/classroom.md"
preffix = "Breakout Room "

try:
    num = int(sys.argv[1])
except IndexError:
    num = 100

print( f"# {preffix} Links" )
print()
print( f"For [{markdown_url}]({markdown_url})" )
print()

for i in range(1, num +1 ):
    room = f"{preffix}{i}"
    data = {"backend":"GUN|f|https://peer.wallie.io/gun",
            "course":markdown_url,
            "room":room}
    encoded = base64.b64encode(json.dumps(data).encode()).decode()
    url = f"https://liascript.github.io/course/?{encoded}"

    print(f"[{room}]({url})")
    print()
    