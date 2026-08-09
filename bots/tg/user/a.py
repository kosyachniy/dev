import re
import json

from libdev.time import get_time


def parse_message(msg: str) -> dict:
    # Get phone
    phone_pat = re.compile(r"(?<!\S)(\+?\d[\d\-\(\) ]{7,}\d)(?!\S)")
    phone_match = None
    for line in msg.splitlines():
        low = line.lower()
        if "id" in low or "телеграм" in low:
            continue
        m = phone_pat.search(line)
        if m:
            phone_match = m
            break
    if not phone_match:
        return None
    phone_digits = re.sub(r"\D", "", phone_match.group(1))
    if not 10 <= len(phone_digits) <= 12:
        return None

    result = {
        "sender": None,
        "receiver": None,
        "bill": None,
        "phone": int(phone_digits),
        "amount": None,
        "currency": None,
    }

    # шаблоны для остальных полей
    pats = {
        "sender": re.compile(r"^отпр[:：]\s*(.+)$"),
        "receiver": re.compile(r"^получ[:：]\s*(.+)$"),
        "bill": re.compile(r"^счет[^\d]*[:：]?\s*([\d\s]+)$"),
        "amount": re.compile(r"^сумма[:：]\s*([\d\s,\.]+)\s*(\S+)$"),
    }

    for line in msg.splitlines():
        text = line.strip()
        low = text.lower()
        # sender, receiver, bill, amount
        for key in ("sender", "receiver", "bill", "amount"):
            if result[key] is None:
                m = pats[key].match(low)
                if m:
                    val = m.group(1).strip()
                    if key == "bill":
                        result[key] = int(val.replace(" ", ""))
                    elif key == "amount":
                        amt = val.replace(" ", "").replace(",", ".")
                        result["amount"] = float(amt)
                        raw_cur = m.group(2)
                        cur = re.sub(r"[^a-zA-Zа-яА-Я]", "", raw_cur)
                        result["currency"] = cur.lower()
                    elif key in {"sender", "receiver"}:
                        result[key] = val.title()
                    else:
                        result[key] = val
                    break
    return result


def main(msgs):
    stop = None
    full = []

    for msg in msgs:
        if not msg or not msg["data"]:
            continue
        if not stop:
            stop = msg["message"]
        elif stop == msg["message"]:
            break

        if data := parse_message(msg["data"]):
            full.append(
                f"{get_time(msg['created'], tz=3)}"
                f",+{data['phone']}"
                f",{data['amount']}"
                f",{data['currency']}"
                f",{data['sender'] or ''}"
                f",{data['receiver'] or ''}"
                f",{data['bill'] or ''}"
            )

    with open("res.csv", "w") as file:
        print("\n".join(full), file=file)


with open("8127764238.json", "r") as file:
    msgs = []
    for row in file:
        msgs.append(json.loads(row))
    main(msgs)
