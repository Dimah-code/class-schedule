text = "۱۲:۰۰ یکشنبه ۱ مهر ۱۴۰۴"

fa_to_en = {
    "۱": "1",
    "۲": "2",
    "۳": "3",
    "۴": "4",
    "۵": "5",
    "۶": "6",
    "۷": "7",
    "۸": "8",
    "۹": "9",
    "۰": "0"
}

result = ""

for char in text:
    if char in fa_to_en:
        result += fa_to_en[char]
    else:
        result += char

print(result)