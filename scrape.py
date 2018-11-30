from lxml import html
import requests, os

# scrape rooster tooths for RvB scripts
PATH = 'scripts.txt'

with open(PATH, 'w') as f:
    for i in [x for x in range(347)]:
        page = requests.get('http://roostertooths.com/transcripts.php?eid={}'.format(i+1))
        tree = html.fromstring(page.content)
        lines = []
        f.write('\n\n'+tree.xpath('//p[@class="breadcrumbs"]/a//text()')[1]
              +'\n'+tree.xpath('//h1//text()')[0]+'\n\n')
        for row in tree.xpath('//table[@class="script"]/tr'):
            f.write(''.join(row.xpath('.//td//text()'))+'\n')

text = open(PATH).read()
for line in text.split('\n'):
    # only get spoken lines from RvB
    if line.startswith(' '):
        line = line[1:]
        # remove last line if captioned
        if line.startswith('caption'):
            line = lines[-1].split(':',1)[0].upper() + ':' + line.split(':',1)[1].lower()
            lines = lines[:-1]
        else:
            line = line.split(':',1)[0].upper() + ':' + line.split(':',1)[1].lower()
        lines.append(line)

replacemap = {"\x91": '"', "\x93": '"', "\x92": "'", "\x94": "'",
              '[': '(', ']': ')', '\x85': '\n', '\xa0': ' ', '\x96': ''}
text = '\n'.join(lines)
for k, v in replacemap.items():
    text = text.replace(k, v)

with open(PATH, 'w') as f:
    f.write(text)
