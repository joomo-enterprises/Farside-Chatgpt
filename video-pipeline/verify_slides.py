import sys, json, re
sys.path.insert(0, 'video-pipeline/scripts')
from script_parser import parse_fallback_script
from slidemaker import extract_narration_points

with open('/mnt/c/k/author/farside-chatgpt/episodes/episode-01/SCRIPT.md') as f:
    content = f.read()

scenes = parse_fallback_script(content, '01')

issues = []
for i in range(1, len(scenes)):
    s = scenes[i]
    narr = s.get('narration', '')
    ext = extract_narration_points(narr)

    tw = ext['takeaway']
    if len(tw) > 240 and tw[-1] not in '.!?"\'':
        issues.append('Scene %d: takeaway may be truncated: ...%s' % (i, tw[-30:]))

    for p in ext['points']:
        if 'expensive at scale' in p.lower() or 'data leaves your machine' in p.lower():
            issues.append('Scene %d: bad bullet fragment: %s' % (i, p[:80]))

    for sec in ext['sections']:
        body = sec['body']
        if body.endswith('...') or body.endswith(' th') or body.endswith(' pr'):
            issues.append('Scene %d: section body truncated: ...%s' % (i, body[-30:]))

if issues:
    print('ISSUES FOUND:')
    for iss in issues:
        print(' !', iss)
else:
    print('ALL SLIDES VERIFIED: No truncation, no bad bullet fragments')

print()
for i in range(1, len(scenes)):
    s = scenes[i]
    narr = s.get('narration', '')
    ext = extract_narration_points(narr)
    print('Scene %d (%s): %d points, takeaway=%.60s...' % (i, s.get('heading', '')[:30], len(ext['points']), ext['takeaway']))
