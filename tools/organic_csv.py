#!/usr/bin/env python3
"""Shopify product-import CSV for the organic products that are not in the store yet.

The connector cannot run bulk mutations, so the new organic drafts go in through Shopify admin -> Products -> Import.
Products that already exist (organic_shopify.EXISTING, carried as 'id' in the inputs) are updated with productSet instead.

  tools/organic_shopify.py /tmp/organic_products.jsonl
  tools/organic_csv.py /tmp/organic_products.jsonl tools/organic_products_import.csv
"""
import csv, json, re, sys, unicodedata

HEAD = ['Handle', 'Title', 'Body (HTML)', 'Vendor', 'Type', 'Tags', 'Published', 'Option1 Name', 'Option1 Value', 'Variant SKU',
        'Variant Grams', 'Variant Inventory Tracker', 'Variant Inventory Qty', 'Variant Inventory Policy', 'Variant Fulfillment Service',
        'Variant Price', 'Variant Requires Shipping', 'Variant Taxable', 'Image Src', 'Image Position', 'Image Alt Text', 'Gift Card', 'Status']


def handle(title):
    t = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')


def ptype(i):
    t = i['tags']
    return 'Cap' if 'cap' in t else 'Beanie' if 'beanie' in t else 'T-shirt'


def rows(i):
    h = handle(i['title']); opt = i['productOptions'][0]['name']; files = i.get('files', [])
    n = max(len(i['variants']), len(files))
    for k in range(n):
        v = i['variants'][k] if k < len(i['variants']) else None
        f = files[k] if k < len(files) else None
        first = k == 0
        yield [h, i['title'] if first else '', i.get('descriptionHtml', '') if first else '', 'Doolittle Scuba' if first else '',
               ptype(i) if first else '', ', '.join(i['tags']) if first else '', 'FALSE' if first else '',
               opt if first else '', v['optionValues'][0]['name'] if v else '', v['sku'] if v else '',
               '0' if v else '', '', '0' if v else '', 'deny' if v else '', 'manual' if v else '', v['price'] if v else '',
               'TRUE' if v else '', 'TRUE' if v else '', f['originalSource'] if f else '', str(k + 1) if f else '',
               f.get('alt', '') if f else '', 'FALSE' if first else '', 'draft' if first else '']


if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else '/tmp/organic_products.jsonl'
    dst = sys.argv[2] if len(sys.argv) > 2 else '/tmp/DoolittleScuba_organic_products_import.csv'
    L = [json.loads(l)['input'] for l in open(src, encoding='utf-8')]
    new = [i for i in L if 'id' not in i]
    with open(dst, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(HEAD); c = 0
        for i in new:
            for r in rows(i): w.writerow(r); c += 1
    print(f'{len(new)} new products, {c} rows -> {dst}')
