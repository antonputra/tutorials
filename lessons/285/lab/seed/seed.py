"""Deterministic seed for the Juniper Market lab. The same arguments always give the same data.

    python -m seed.seed                      create the three databases and load them, once
    python -m seed.seed --reset              drop and rebuild juniper and receiving
    python -m seed.seed --reset-activity     empty payments, holds and access_log; every invoice is open again
    python -m seed.seed --reset-agent        drop and recreate the agent database (LangGraph's tables)
    python -m seed.seed --invoices 80 --doc-words 900 --reset     a longer job with longer papers

Everything is fictional. Planted problems (each only when its invoice number is in range):
    1042  Cascade Packaging bills 55 cases of cups at $38.00; PO-2207 ordered 50 and 50 arrived
    1049  one unit price is $0.75 above its purchase order
    1058  a duplicate of invoice 1037: same supplier, same purchase order, same amount
    1063  no purchase order
    1055  20 ordered and billed, 12 arrived: only the receiving database knows
    Cascade Packaging's invoices carry a freight line that is not on the purchase order
"""
import argparse
import os
import random
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import psycopg

HERE = Path(__file__).parent
ADMIN_URL = os.environ.get("PG_ADMIN_URL", "postgresql://postgres@postgres:5432/postgres")
JUNIPER_URL = os.environ.get("JUNIPER_DB_URL", "postgresql://postgres@postgres:5432/juniper")
RECEIVING_URL = os.environ.get("RECEIVING_DB_URL", "postgresql://postgres@postgres:5432/receiving")

DUE = date(2026, 11, 27)          # the Friday of the payment run
FIRST_INVOICE = 1031
FIRST_PO = 2196                   # invoice 1042 gets PO-2207
BUYER = ("Juniper Market", "410 Alder Street", "Bend, OR 97701", "ap@junipermarket.example")

# name | street | city | state | zip | phone | mail domain | terms in days | SKU prefix
SUPPLIERS = """
Cascade Packaging|2210 Harbor Way|Tacoma|WA|98402|(253) 555-0142|cascadepackaging.example|30|CP
Blue Heron Dairy|87 Creamery Road|Eugene|OR|97402|(541) 555-0117|blueherondairy.example|15|BH
Sunridge Produce|1500 Orchard Lane|Yakima|WA|98901|(509) 555-0163|sunridgeproduce.example|15|SR
Harbor Light Seafood|12 Pier Street|Astoria|OR|97103|(503) 555-0188|harborlightseafood.example|15|HL
Three Rivers Bakery Supply|640 Mill Avenue|Spokane|WA|99201|(509) 555-0129|threeriversbakery.example|30|TR
Golden Prairie Grains|305 Elevator Road|Boise|ID|83702|(208) 555-0154|goldenprairiegrains.example|30|GP
Maple Hollow Farms|9 Hollow Creek Road|Salem|OR|97301|(503) 555-0171|maplehollowfarms.example|21|MH
Summit Beverage Distributors|4400 Canal Street|Bend|OR|97702|(541) 555-0136|summitbeverage.example|30|SB
Evergreen Cleaning Supply|77 Capitol Way|Olympia|WA|98501|(360) 555-0108|evergreencleaning.example|30|EC
Lakeside Frozen Foods|2800 Marina Drive|Sandpoint|ID|83864|(208) 555-0195|lakesidefrozen.example|21|LF
Redwood Coffee Roasters|518 Main Street|Medford|OR|97501|(541) 555-0122|redwoodcoffee.example|30|RC
Pioneer Paper & Office|1020 Foundry Street|Portland|OR|97209|(503) 555-0149|pioneerpaper.example|30|PP
""".strip().splitlines()

# description | unit | unit price, twelve per supplier, in the order of SUPPLIERS
CATALOG = {
    "CP": """12 oz paper cups (case of 1,000)|case|38.00
16 oz paper cups (case of 1,000)|case|44.00
Cup lids, 12 to 16 oz (case of 1,000)|case|24.00
8 oz deli containers (case of 500)|case|31.50
16 oz deli containers (case of 500)|case|36.00
Deli container lids (case of 500)|case|18.00
Paper grocery bags, large (bundle of 500)|bundle|42.00
Paper grocery bags, small (bundle of 500)|bundle|27.50
Produce bags on a roll (case of 4 rolls)|case|22.00
Bakery boxes, 10 inch (bundle of 100)|bundle|35.00
Kraft paper napkins (case of 6,000)|case|29.00
Wooden cutlery kits (case of 500)|case|26.50""",
    "BH": """Whole milk, 1 gallon (crate of 4)|crate|12.50
2% milk, 1 gallon (crate of 4)|crate|12.50
Half and half, 1 quart (case of 12)|case|21.00
Heavy cream, 1 pint (case of 12)|case|27.00
Salted butter, 1 lb (case of 36)|case|96.00
Unsalted butter, 1 lb (case of 36)|case|96.00
Plain yogurt, 32 oz (case of 6)|case|15.00
Greek yogurt, 5.3 oz (case of 12)|case|11.50
Sharp cheddar, 8 oz (case of 12)|case|33.00
Mozzarella, 16 oz (case of 12)|case|39.00
Sour cream, 16 oz (case of 12)|case|19.50
Large eggs, 15 dozen (case)|case|34.00""",
    "SR": """Honeycrisp apples (40 lb case)|case|46.00
Gala apples (40 lb case)|case|32.00
Bartlett pears (36 lb case)|case|34.50
Yellow onions (50 lb sack)|sack|19.00
Russet potatoes (50 lb case)|case|21.50
Carrots (25 lb bag)|bag|14.00
Romaine hearts (case of 12)|case|24.50
Roma tomatoes (25 lb case)|case|28.00
Lemons (case of 115)|case|37.00
Navel oranges (40 lb case)|case|30.00
Green cabbage (45 lb case)|case|17.50
Sweet corn (case of 48)|case|22.00""",
    "HL": """Wild salmon fillets (10 lb case)|case|128.00
Pacific cod fillets (10 lb case)|case|74.00
Cooked shrimp, 31 to 40 count (5 lb bag)|bag|52.00
Dungeness crab meat (5 lb tub)|tub|165.00
Smoked salmon, 4 oz packs (case of 12)|case|66.00
Albacore tuna loins (10 lb case)|case|98.00
Rockfish fillets (10 lb case)|case|58.00
Bay scallops (5 lb bag)|bag|61.00
Clam chowder base (case of 4 tubs)|case|43.50
Oysters in the shell (bag of 60)|bag|48.00
Fish stock, 1 quart (case of 12)|case|36.00
Seafood seasoning, 12 oz (case of 12)|case|25.00""",
    "TR": """Bread flour (50 lb bag)|bag|23.00
All-purpose flour (50 lb bag)|bag|19.50
Whole wheat flour (50 lb bag)|bag|24.50
Granulated sugar (50 lb bag)|bag|31.00
Brown sugar (50 lb bag)|bag|35.50
Instant yeast, 1 lb (case of 20)|case|58.00
Baking powder, 5 lb (case of 6)|case|41.00
Chocolate chips (25 lb case)|case|72.00
Rolled oats (50 lb bag)|bag|27.00
Vanilla extract, 32 oz (case of 6)|case|89.00
Parchment sheets (case of 1,000)|case|47.50
Sea salt (25 lb bag)|bag|12.00""",
    "GP": """Long grain rice (50 lb bag)|bag|26.00
Brown rice (25 lb bag)|bag|18.50
Pinto beans (50 lb bag)|bag|33.00
Black beans (50 lb bag)|bag|35.00
Green lentils (25 lb bag)|bag|21.00
Quinoa (25 lb bag)|bag|54.00
Pearl barley (25 lb bag)|bag|16.50
Yellow cornmeal (50 lb bag)|bag|22.50
Split peas (25 lb bag)|bag|17.00
Garbanzo beans (50 lb bag)|bag|38.00
Popcorn kernels (50 lb bag)|bag|29.50
Steel cut oats (25 lb bag)|bag|20.00""",
    "MH": """Raw honey, 12 oz (case of 12)|case|62.00
Maple syrup, 8 oz (case of 12)|case|84.00
Strawberry jam, 10 oz (case of 12)|case|39.00
Marionberry jam, 10 oz (case of 12)|case|42.00
Apple butter, 10 oz (case of 12)|case|36.50
Dill pickles, 24 oz (case of 12)|case|33.00
Roasted hazelnuts, 8 oz (case of 12)|case|57.00
Dried cherries, 6 oz (case of 12)|case|49.50
Granola, 12 oz (case of 12)|case|44.00
Apple cider, half gallon (case of 6)|case|25.50
Pasture eggs, dozen (case of 15)|case|52.50
Goat cheese, 4 oz (case of 12)|case|47.00""",
    "SB": """Sparkling water, 12 oz cans (case of 24)|case|9.50
Spring water, 16.9 oz (case of 24)|case|5.50
Orange juice, 52 oz (case of 6)|case|21.00
Apple juice, 64 oz (case of 6)|case|16.50
Cold brew coffee, 32 oz (case of 6)|case|27.00
Kombucha, 16 oz (case of 12)|case|28.50
Root beer, 12 oz bottles (case of 24)|case|19.00
Lemonade, 52 oz (case of 6)|case|15.00
Iced tea, 18.5 oz (case of 12)|case|13.50
Oat milk, 32 oz (case of 6)|case|18.00
Tomato juice, 46 oz (case of 6)|case|14.50
Ginger beer, 12 oz bottles (case of 24)|case|23.50""",
    "EC": """Floor cleaner, 1 gallon (case of 4)|case|34.00
Glass cleaner, 32 oz (case of 12)|case|28.00
Disinfectant wipes (case of 6 tubs)|case|31.50
Hand soap refill, 1 gallon (case of 4)|case|26.00
Paper towels (case of 30 rolls)|case|39.00
Trash bags, 33 gallon (case of 100)|case|24.00
Nitrile gloves, medium (case of 1,000)|case|58.00
Dish soap, 1 gallon (case of 4)|case|22.50
Mop heads (pack of 12)|pack|45.00
Scrub sponges (case of 40)|case|17.50
Toilet tissue (case of 80 rolls)|case|47.00
Sanitizer concentrate, 1 gallon (case of 4)|case|52.00""",
    "LF": """Frozen peas, 2 lb (case of 12)|case|27.00
Frozen corn, 2 lb (case of 12)|case|25.50
Frozen blueberries, 3 lb (case of 6)|case|48.00
Frozen strawberries, 3 lb (case of 6)|case|42.00
French fries, 5 lb (case of 6)|case|33.00
Cheese pizza, 12 inch (case of 12)|case|56.00
Vanilla ice cream, 3 gallon tub|tub|29.50
Chicken pot pies (case of 12)|case|44.00
Vegetable dumplings (case of 10 bags)|case|51.00
Hash browns, 3 lb (case of 6)|case|21.00
Fruit bars (case of 24)|case|19.50
Pie shells, 9 inch (case of 20)|case|37.50""",
    "RC": """House blend, whole bean, 12 oz (case of 12)|case|78.00
Dark roast, whole bean, 12 oz (case of 12)|case|78.00
Decaf, whole bean, 12 oz (case of 12)|case|81.00
Espresso blend, 5 lb bag|bag|49.00
Breakfast blend, ground, 12 oz (case of 12)|case|75.00
Cold brew packs (case of 24)|case|54.00
Paper filters, basket (case of 1,000)|case|16.00
Loose leaf black tea, 1 lb bag|bag|22.00
Herbal tea bags (case of 6 boxes)|case|27.50
Chai concentrate, 32 oz (case of 6)|case|38.50
Hot chocolate mix, 2 lb (case of 6)|case|43.00
Vanilla syrup, 750 ml (case of 6)|case|46.50""",
    "PP": """Receipt paper rolls (case of 50)|case|37.00
Shelf labels (box of 2,000)|box|18.50
Price gun labels (case of 16 rolls)|case|24.00
Copy paper, letter (case of 10 reams)|case|52.00
Ballpoint pens (box of 60)|box|11.00
Packing tape (case of 36 rolls)|case|64.00
Sign holders, 8.5 by 11 (pack of 10)|pack|29.50
Dry erase markers (box of 12)|box|13.50
File folders, letter (box of 100)|box|15.00
Thermal labels, 4 by 6 (case of 12 rolls)|case|58.00
Clipboards (pack of 12)|pack|21.00
Chalk markers (box of 8)|box|16.50""",
}

NOTES = [
    "Delivered on our own truck. The driver counted each pallet with your receiving clerk at the dock, and the signed delivery slip is on file at our office.",
    "Chilled goods left our dock at 36 degrees Fahrenheit. Please move them to cold storage as soon as they arrive, and write any warm case on the delivery slip.",
    "This order shipped complete from our main warehouse. Pallets and crates stay our property and go back with the driver on the next delivery.",
    "Thank you for your order. Your account manager can answer any question about this invoice on the phone number at the top of this page.",
    "Goods were packed and checked by two people before loading. The packing list rode with the shipment, in the pouch on the first pallet.",
    "Prices on this invoice are the prices we confirmed when the purchase order was accepted. A new price list takes effect on the first day of next quarter.",
]

CLAUSES = [
    "Payment is due in full on the due date printed above. The term starts on the invoice date, not on the day the goods arrive, unless both companies agreed on other terms in writing before the order was placed.",
    "Please pay by bank transfer to the account we already have on file for you. We never change our bank details by email. If a message asks you to pay a new account, call the phone number on this invoice before you pay.",
    "A late fee of 1.5 percent a month is charged on any amount that is still open thirty days after the due date. The fee is added to the next statement and shown on its own line.",
    "Tell us about a shortage, a damaged case or a wrong item within five business days of delivery. After five days we treat the delivery as complete and correct, and this invoice is owed in full.",
    "Goods may come back only with a return number from our office. Fresh, chilled and frozen goods cannot come back once they have left our truck, except when they arrived damaged or below standard.",
    "A credit memo is the only way we correct an invoice. Do not change the amount by hand. Pay the amount you agree with, write the reason on the remittance, and we will send a credit memo for the rest.",
    "Title to the goods passes to the buyer on delivery. The risk of loss passes when the receiving clerk signs the delivery slip. Until the invoice is paid we keep a security interest in the goods.",
    "Prices do not include sales tax. Goods bought for resale are not taxed when a valid resale certificate is on file. If your certificate has expired, tax is added to the next invoice.",
    "Freight is billed only when it is listed on the purchase order or in a signed supplier agreement. Fuel surcharges, pallet fees and liftgate fees are shown on their own lines when they apply.",
    "Quantities on this invoice are the quantities loaded on the truck. If the delivery slip shows a different count, the delivery slip signed at your dock is the record both companies use.",
    "This invoice, the purchase order it names and our price confirmation are the whole agreement for this order. Terms printed on other forms do not change it unless both companies sign them.",
    "Keep this invoice with your records. A statement of open invoices is mailed on the first business day of each month, and a copy of any invoice is free for seven years.",
    "Questions about this invoice go to our accounts office, Monday to Friday, 8:00 AM to 4:30 PM Pacific time. Have the invoice number and the purchase order number ready when you call.",
    "We may hold new orders when an account has an invoice more than forty-five days past its due date. Orders are released the day the payment arrives.",
    "Product weights are net weights at packing. Fresh produce and seafood may lose a little weight in transit, and a difference of up to two percent is normal and not a shortage.",
    "If any part of these terms cannot be enforced, the rest still applies. These terms follow the laws of the state named in our address at the top of this invoice.",
]

RECEIVERS = ["M. Ortiz", "J. Park", "L. Nguyen"]


def money(value) -> str:
    return f"${Decimal(value):,.2f}"


def long_date(d: date) -> str:
    return f"{d:%B} {d.day}, {d.year}"


def build_world(invoices: int, doc_words: int, seed: int):
    """Return (suppliers, purchase orders, invoices, receipts) as plain dicts and lists."""
    rng = random.Random(seed)
    suppliers = []
    for i, row in enumerate(SUPPLIERS, start=1):
        name, street, city, state, zip_, phone, domain, terms, prefix = row.split("|")
        catalog = []
        for j, item in enumerate(CATALOG[prefix].splitlines(), start=101):
            desc, unit, price = item.split("|")
            catalog.append({"sku": f"{prefix}-{j}", "description": desc, "unit": unit, "unit_price": Decimal(price)})
        suppliers.append({"supplier_id": i, "name": name, "street": street, "city": city, "state": state, "zip": zip_,
                          "phone": phone, "email": f"accounts@{domain}", "terms_days": int(terms), "catalog": catalog})
    cascade, others = suppliers[0], suppliers[1:]
    cascade_numbers = {1034, 1042, 1051, 1066}
    freight_prices = [Decimal("45.00"), Decimal("60.00"), Decimal("75.00"), Decimal("52.50")]

    pos, invs, receipts = {}, [], []
    other_i = cascade_i = 0
    for i in range(invoices):
        number = FIRST_INVOICE + i
        if number in cascade_numbers or (number > 1070 and i % 10 == 1):
            sup, is_cascade = cascade, True
        else:
            sup, is_cascade = others[other_i % len(others)], False
            other_i += 1
        if number == 1058 and any(v["invoice_number"] == 1037 for v in invs):
            original = next(v for v in invs if v["invoice_number"] == 1037)     # the duplicate
            copy = dict(original, invoice_number=number, lines=[dict(l) for l in original["lines"]])
            invs.append(copy)
            continue
        count = rng.randint(3, 12)
        picked = sorted(rng.sample(range(12), count))
        if number == 1042 and 0 not in picked:
            picked = [0] + picked[:-1]
        if number == 1063:
            picked = picked[:3]
        po_lines = []
        for line_no, idx in enumerate(picked, start=1):
            item = sup["catalog"][idx]
            qty = rng.choice([4, 5, 6, 8, 10, 12, 15, 20, 24, 30, 40])
            po_lines.append({"line_no": line_no, **item, "quantity": qty})
        if number == 1042:
            po_lines[0]["quantity"] = 50
        if number == 1055:
            po_lines[0]["quantity"] = 20
        if number == 1063:
            for line in po_lines:
                line["quantity"] = max(line["quantity"], 8)
        invoice_date = DUE - timedelta(days=sup["terms_days"])
        inv_lines = [dict(l) for l in po_lines]
        if number == 1042:
            inv_lines[0]["quantity"] = 55                       # 5 cases more than ordered
        if number == 1049:
            inv_lines[0]["unit_price"] += Decimal("0.75")       # not the price on the purchase order
        if is_cascade:
            inv_lines.append({"line_no": len(inv_lines) + 1, "sku": "FREIGHT", "description": "Freight",
                              "unit": "each", "unit_price": freight_prices[cascade_i % 4], "quantity": 1})
            cascade_i += 1
        po_number = None
        if number != 1063:                                      # 1063 has no purchase order
            po_number = f"PO-{FIRST_PO + i}"
            pos[po_number] = {"po_number": po_number, "supplier_id": sup["supplier_id"],
                              "order_date": invoice_date - timedelta(days=rng.randint(7, 12)),
                              "status": "received", "lines": po_lines}
            got = [dict(l) for l in po_lines]
            if number == 1055:
                got[0]["quantity"] = 12                         # 8 of the 20 never arrived
            receipts.append({"receipt_id": 5000 + i, "po_number": po_number,
                             "received_date": invoice_date - timedelta(days=rng.randint(1, 4)),
                             "dock": f"Dock {rng.randint(1, 3)}", "received_by": rng.choice(RECEIVERS), "lines": got})
        invs.append({"invoice_number": number, "supplier": sup, "po_number": po_number, "invoice_date": invoice_date,
                     "due_date": DUE, "lines": inv_lines, "note": rng.choice(NOTES),
                     "target_words": doc_words + rng.randint(-90, 90), "clause_start": rng.randrange(len(CLAUSES))})
    for inv in invs:
        inv["total"] = sum((l["quantity"] * l["unit_price"] for l in inv["lines"]), Decimal("0"))
        inv["document_text"] = document(inv)
    return suppliers, pos, invs, receipts


def document(inv) -> str:
    """The text of the paper invoice, as a supplier would print it."""
    sup = inv["supplier"]
    out = [sup["name"].upper(), f"{sup['street']}, {sup['city']}, {sup['state']} {sup['zip']}",
           f"Phone {sup['phone']}   {sup['email']}", "",
           f"INVOICE {inv['invoice_number']}",
           f"Invoice date: {long_date(inv['invoice_date'])}",
           f"Due date: {long_date(inv['due_date'])}",
           f"Terms: Net {sup['terms_days']}",
           f"Purchase order: {inv['po_number'] or 'none given'}", "",
           "Bill to:", f"{BUYER[0]}, Accounts Payable", BUYER[1], BUYER[2], BUYER[3], "",
           "Ship to:", f"{BUYER[0]}, Receiving Dock", f"{BUYER[1]} (rear entrance)", BUYER[2], "",
           f"{'Line':<5}{'SKU':<9}{'Description':<44}{'Qty':>4}  {'Unit':<7}{'Unit price':>11}{'Amount':>12}"]
    for l in inv["lines"]:
        out.append(f"{l['line_no']:<5}{l['sku']:<9}{l['description']:<44}{l['quantity']:>4}  {l['unit']:<7}"
                   f"{money(l['unit_price']):>11}{money(l['quantity'] * l['unit_price']):>12}")
    out += ["", f"Subtotal: {money(inv['total'])}", "Sales tax: $0.00 (goods for resale, certificate on file)",
            f"Total due: {money(inv['total'])}", "", f"Notes: {inv['note']}", "", "Terms and conditions"]
    k = 0
    while len(" ".join(out).split()) < inv["target_words"]:
        out.append(f"{k + 1}. {CLAUSES[(inv['clause_start'] + k) % len(CLAUSES)]}")
        k += 1
    out += ["", f"Thank you for your business. {sup['name']}, {sup['city']}, {sup['state']}."]
    return "\n".join(out)


def ensure_database(admin, name: str, drop: bool) -> bool:
    """Create the database when it is missing. Return True when it is new."""
    if drop:
        admin.execute(f"DROP DATABASE IF EXISTS {name} WITH (FORCE)")
    if admin.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,)).fetchone():
        return False
    admin.execute(f"CREATE DATABASE {name}")
    return True


def load(args):
    suppliers, pos, invs, receipts = build_world(args.invoices, args.doc_words, args.seed)
    with psycopg.connect(JUNIPER_URL) as db:
        db.execute((HERE / "juniper.sql").read_text())
        for s in suppliers:
            db.execute("INSERT INTO suppliers VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                       (s["supplier_id"], s["name"], s["street"], s["city"], s["state"], s["zip"], s["phone"],
                        s["email"], s["terms_days"]))
        for po in pos.values():
            db.execute("INSERT INTO purchase_orders VALUES (%s,%s,%s,%s)",
                       (po["po_number"], po["supplier_id"], po["order_date"], po["status"]))
            for l in po["lines"]:
                db.execute("INSERT INTO po_lines VALUES (%s,%s,%s,%s,%s,%s,%s)",
                           (po["po_number"], l["line_no"], l["sku"], l["description"], l["quantity"], l["unit"],
                            l["unit_price"]))
        for v in invs:
            db.execute("INSERT INTO invoices (invoice_number, supplier_id, po_number, invoice_date, due_date,"
                       " total_usd, document_text) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                       (v["invoice_number"], v["supplier"]["supplier_id"], v["po_number"], v["invoice_date"],
                        v["due_date"], v["total"], v["document_text"]))
            for l in v["lines"]:
                db.execute("INSERT INTO invoice_lines VALUES (%s,%s,%s,%s,%s,%s,%s)",
                           (v["invoice_number"], l["line_no"], l["sku"], l["description"], l["quantity"], l["unit"],
                            l["unit_price"]))
    with psycopg.connect(RECEIVING_URL) as db:
        db.execute((HERE / "receiving.sql").read_text())
        for r in receipts:
            db.execute("INSERT INTO receipts VALUES (%s,%s,%s,%s,%s)",
                       (r["receipt_id"], r["po_number"], r["received_date"], r["dock"], r["received_by"]))
            for l in r["lines"]:
                db.execute("INSERT INTO receipt_lines VALUES (%s,%s,%s,%s,%s,%s)",
                           (r["receipt_id"], l["line_no"], l["sku"], l["description"], l["quantity"], l["unit"]))
    words = [len(v["document_text"].split()) for v in invs]
    print(f"seeded: {len(suppliers)} suppliers, {len(pos)} purchase orders, {len(invs)} invoices due {DUE}, "
          f"{len(receipts)} receipts; paper invoices {min(words)} to {max(words)} words "
          f"(seed {args.seed}, --invoices {args.invoices}, --doc-words {args.doc_words})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--invoices", type=int, default=int(os.environ.get("SEED_INVOICES", "40")))
    ap.add_argument("--doc-words", type=int, default=int(os.environ.get("SEED_DOC_WORDS", "550")))
    ap.add_argument("--seed", type=int, default=20261127)
    ap.add_argument("--reset", action="store_true")
    ap.add_argument("--reset-activity", action="store_true")
    ap.add_argument("--reset-agent", action="store_true")
    args = ap.parse_args()

    if args.reset_activity:
        with psycopg.connect(JUNIPER_URL) as db:
            db.execute("TRUNCATE payments, holds, access_log RESTART IDENTITY")
            db.execute("UPDATE invoices SET status = 'open'")
        print("activity reset: payments, holds and access_log are empty; every invoice is open")
        return
    with psycopg.connect(ADMIN_URL, autocommit=True) as admin:
        if args.reset_agent:
            ensure_database(admin, "agent", drop=True)
            print("agent database: dropped and created empty")
            return
        ensure_database(admin, "agent", drop=False)
        new = [ensure_database(admin, name, drop=args.reset) for name in ("juniper", "receiving")]
    if any(new):
        load(args)
    else:
        print("already seeded: nothing changed (use --reset to rebuild)")


if __name__ == "__main__":
    main()
