import re,json
with open('index.html','r') as f: h=f.read()
ms=list(re.finditer(r'<script type="application/ld\+json">\s*\{[^<]*"@type"\s*:\s*"FAQPage"[^<]*</script>',h,re.DOTALL))
print(f'Found {len(ms)} FAQPage schemas')
if len(ms)>1:
    best=None; best_count=0
    for m in ms:
        try:
            t=m.group(0)
            j=t[t.index('>')+1:t.rindex('<')]
            d=json.loads(j)
            c=len(d.get('mainEntity',[]))
            print(f'  Schema at pos {m.start()}: {c} questions')
            if c>best_count: best=m; best_count=c
        except Exception as e: print(f'  Error: {e}')
    for m in reversed(ms):
        if m!=best:
            h=h[:m.start()]+h[m.end():]
            print(f'  Removed duplicate schema')
    with open('index.html','w') as f: f.write(h)
    print(f'Saved. File size: {len(h):,} bytes')
else:
    print('No duplicates found')
