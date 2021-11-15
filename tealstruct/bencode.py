# Bencode
# https://en.wikipedia.org/wiki/Bencode

integer     - i [-]base10 e         i:42:e
bytestring  - lenght:content        12:deadbeefdead
list        - l bencoded_content e  l4:spami42ee
dictionary  - d bencoded_content e  d3:bar4:spam3:fooi42ee
