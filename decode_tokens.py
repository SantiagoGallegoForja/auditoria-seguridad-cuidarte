import json, base64, sys

import os
with open(os.environ['TEMP'] + '/tokens.json') as f:
    d = json.load(f)

apps = d.get('apps', {})

known = {
    '14f25924-5664-31b2-9568-f9c5ed98c9b1': 'Wix Members Area',
    'f4d83b06-b408-4f3b-afd4-de8db311d7d8': 'Wix Notifications',
    '8725b255-2aa2-4a53-b76d-7d3c363aaeea': 'Wix Triggers & Automations',
    'e593b0bd-b783-45b8-97c2-873d42aacaf4': 'Wix Engage (CRM)',
    '139ef4fa-c108-8f9a-c7be-d5f492a2c939': 'Wix Site Search',
    '13e8d036-5516-6104-b456-c8466db39542': 'Wix Datasets (REST Pro)',
    '14271d6f-ba62-d045-549b-ab972ae1f70e': 'Wix Social (Activity Feed)',
    '141fbfae-511e-6817-c9f0-48993a7547d1': 'Wix Chat',
    '64e6bcf3-b6e2-456a-81f9-b0cfbdd5c2c3': 'Wix Inbox',
    '2bef2abe-7abe-43da-889c-53c1500a328c': 'Wix Multilingual',
    'd70b68e2-8d77-4e0c-9ef4-b5e2e6db0b44': 'Wix FAQ',
    '1475ab65-206b-d79a-856d-316c0a453ef6': 'Wix Cloud Backend (REST Pro)',
    '14409595-f076-4753-8303-76d14c1c0df0': 'Wix Video',
    '1365f9c7-cd93-bab2-d3e6-6e0c5d3e6f5b': 'Wix Analytics / BI',
    '13aa9735-aa50-4bdb-82a1-5052c434d8f5': 'Wix Forms',
    '50d8c12f-715e-41ad-b694-6e5e2b750498': 'Wix Workflows',
    '146c0d71-352e-4464-9a03-2e3028024023': 'Wix File Share',
    '9699c03d-5c19-4a7c-a498-5f1b6b57a5aa': 'Wix Accessibility',
    'f9c07de2-5341-40c6-bf71-2c8df64e5e1b': 'Wix Challenges',
    'fc9314bc-a317-4a2b-a05f-cefe01cbe27a': 'Wix Portfolio',
    '4aebd0cb-fbdb-4da7-b5a1-d05d67a3e2a3': 'Wix Pro Gallery',
    '307ba931-689c-4b55-b455-3a4ad5567b88': 'Wix Music',
    '1537b24e-29d1-6d8f-b8e1-d5a6e40b7833': 'Wix Events',
    'edd04d8e-3c81-46d7-b3e0-2efbd3e49a6e': 'Wix Loyalty',
    '4b10fcce-732d-4be3-9d1c-b2a0c28e61c0': 'Wix Pricing Plans',
    '1505b775-e885-eb1b-b665-1e485d1a4f24': 'Wix Table Reservations',
    '14d7032a-0a65-5270-c72e-1b3a71a6b827': 'Wix Restaurants Orders',
    '14dbefd2-01b4-fb61-32a7-3abd44ccc488': 'Wix Restaurants Menus',
    '129acb44-2c8a-8314-f796-4bfce8a8e36d': 'Wix SEO Tools',
    '14cc59bc-f0b7-15b8-e1c7-89ce41d0e0c9': 'Wix Ascend',
    'eec3496e-44a8-45ac-9f46-dd7b4db1a7b7': 'Wix Marketplace',
    '14b89688-9b25-5214-d1cb-a3fb51c39571': 'Wix Blog',
    'ea2821fc-7d97-40a9-9f5e-e84ee1e77b41': 'Wix Groups',
    'a322993b-2c74-426f-b6f8-e8cc5b1f3596': 'Wix Bookings Calendar',
    '1973457f-c021-4da5-91a9-f0a29f727e4e': 'Wix Gift Cards',
    'bbe1406a-31f5-4f3f-9e78-3b37d7c14a65': 'Wix App Market Widget',
    '57d13128-4a4c-494b-8f56-e5c13e989538': 'Wix Online Programs',
    '28b3fe48-a2d4-4e5c-a98a-a09a7ae2d024': 'Wix Shipping',
    '14dbef06-cc42-5583-32a7-3abd44ccc488': 'Wix Content Manager',
    '55cd9036-36bb-480b-8ddc-afda3cb2eb8d': 'Wix Site Members',
    '9142e27e-2e30-4948-a7d6-155e6b1a2a69': 'Wix Domain Connect',
    '9bead16f-1c73-4cda-bf39-2463e0887811': 'Wix Email Marketing',
    '7516f85b-0868-4c23-9a28-d8e1a67f55e8': 'Wix Subscriptions',
    '1480c568-5cbd-9392-5604-4144e12aad5c': 'Wix Contacts',
    '05509e60-039b-471d-8e9a-5a7f3e5fb034': 'Wix Invoices',
    '1522827f-c56c-a5c9-2ac9-00f9e6ae12d3': 'Wix Site Monitoring',
    '14cffd81-5215-0a7f-22f8-074b0e2401fb': 'Wix Promote SEO',
    '13ee94c1-b635-8505-3391-97919052c16f': 'Wix Stores (Dashboard)',
    'eb5611ad-ef33-4aa9-bbd4-42c0f96bf68e': 'Wix Tips',
    '140603ad-af8d-84a5-2c80-a0f60cb47351': 'Wix Site History',
    '22bef345-3c5b-4c18-b782-74d4085112ff': 'Wix Dev Mode / Velo',
    '94bc563b-675f-41ad-a2a7-87bbfbb8bfca': 'Wix Coupons',
    '14517e1a-3ff0-af98-408e-2bd6953c36a2': 'Wix Contacts (Legacy)',
    '14f25dc5-6af3-5420-9568-f9c5ed98c9b1': 'Wix Members (Backend)',
    'e4b5f1bc-c77a-4319-a4ff-7e48e1e2e90e': 'Wix Payments',
    '2f70e2b4-ff36-472e-b0d4-4ab748e15db7': 'Wix Tax',
    '14e12b04-943e-fd32-4b3c-d9aa3a235c50': 'Wix Back Office',
    '14bca956-e09f-f4d6-14d7-466cb3f09103': 'Wix Blog (Frontend)',
    '45c44b27-ca7b-4891-8a30-b09d8348f38d': 'Wix Fulfillment',
    '14c92d28-031e-7910-c228-1a1cfc2b40a6': 'Wix Promote Home',
    '35aec784-bbec-4e6e-aee1-3e0b3c9f1da0': 'Wix Badges',
    '14ce1214-b278-a7e4-1373-00cebd1bef7c': 'Wix Social Posts',
    '6580b7e9-4031-4a62-acc8-be1380361f79': 'Wix Activity Counters',
    '14bcded7-0066-7c35-14d7-466cb3f09103': 'Wix Blog (Node API)',
    '1484cb44-49cd-5b39-9681-75a89c3dd5d7': 'Wix Blog (Categories)',
    '1380b703-ce81-ff05-f115-39571d94dfcd': 'Wix Stores',
    '675bbcef-18d8-41f5-8526-716c2aa92af1': 'Wix Code / Corvid',
    '14ce28f7-7eb0-3745-22f8-074b0e2401fb': 'Wix SEO Patterns',
    '135c3d92-0fea-1f9d-2a41-75a0e3bf5694': 'Wix Forum',
    '150ae7ee-c74a-eecd-d3c5-4bab798d1915': 'Wix Inbox (Messages)',
    'f123e8f1-4350-4c9b-b269-a2c5dca3e5e3': 'Wix Countdown Timer',
    '13d21c63-b5ec-5912-8397-c3a5ddb27a97': 'Wix Bookings',
    '8ea9df15-9ff6-4acf-b0c6-537b3f8ee859': 'Wix Pricing Plans (Backend)',
    '67da2ec3-539a-4c9b-82a4-dac7d0ad2a04': 'Wix Risk & Fraud',
}

cats_kw = {
    'AUTENTICACION Y MIEMBROS': ['member', 'site members', 'badges', 'groups'],
    'E-COMMERCE Y PAGOS': ['store', 'payment', 'shipping', 'invoice', 'coupon', 'gift', 'tax', 'fulfillment', 'subscript', 'pricing plan'],
    'DATOS Y BACKEND': ['data', 'rest', 'code', 'corvid', 'velo', 'dev mode', 'cloud', 'content manager', 'back office'],
    'COMUNICACION': ['chat', 'inbox', 'email', 'notification', 'message'],
    'BLOG Y CONTENIDO': ['blog', 'forum', 'faq', 'social', 'portfolio', 'gallery', 'countdown', 'music'],
    'MARKETING Y SEO': ['seo', 'promote', 'ascend', 'engage', 'crm', 'workflow', 'automat', 'tips'],
    'RESERVAS Y SERVICIOS': ['booking', 'restaurant', 'reservation', 'event', 'calendar', 'challenge', 'program'],
    'ANALYTICS Y MONITOREO': ['analytics', 'bi', 'monitor', 'history', 'risk', 'fraud', 'accessibility'],
    'MEDIA Y ARCHIVOS': ['video', 'file share'],
}

results = {k: [] for k in list(cats_kw.keys()) + ['OTROS']}

for app_id, app_data in apps.items():
    int_id = app_data.get('intId', 'N/A')
    name = known.get(app_id, 'Desconocida (' + app_id[:16] + '...)')

    at = app_data.get('accessToken', '')
    vendor = ''
    inst_id = ''
    parts = at.split('.')
    if len(parts) >= 2:
        try:
            payload = parts[1] + '=' * (4 - len(parts[1]) % 4)
            pd = json.loads(base64.b64decode(payload))
            vendor = pd.get('vendorProductId', '')
            inst_id = pd.get('instanceId', '')
        except:
            pass

    entry = (int_id, name, vendor, app_id, inst_id)
    placed = False
    nl = name.lower()
    for cat, kws in cats_kw.items():
        if any(kw in nl for kw in kws):
            results[cat].append(entry)
            placed = True
            break
    if not placed:
        results['OTROS'].append(entry)

print('=' * 100)
print(' INVENTARIO COMPLETO: %d APPS CON TOKENS EXPUESTOS' % len(apps))
print(' Endpoint: /_api/v1/access-tokens (sin autenticacion)')
print('=' * 100)

for cat, entries in results.items():
    if not entries:
        continue
    entries.sort(key=lambda x: str(x[0]))
    print()
    print('-' * 80)
    print(' %s (%d apps)' % (cat, len(entries)))
    print('-' * 80)
    for int_id, name, vendor, aid, iid in entries:
        v = '  [producto: %s]' % vendor if vendor else ''
        print('  intId: %6s  |  %s%s' % (str(int_id), name, v))
        print('             appDefId:   %s' % aid)
        if iid:
            print('             instanceId: %s' % iid)

print()
print('=' * 100)
print('TOKENS GLOBALES (no asociados a apps):')
print('  visitorId:      %s' % d['visitorId'])
print('  metaSiteId:     %s' % d['metaSiteId'])
print('  svSession:      %s...' % d['svSession'][:60])
print('  ctToken:        %s...' % d['ctToken'][:60])
print('  mediaAuthToken: %s...' % d['mediaAuthToken'][:60])
print('=' * 100)
