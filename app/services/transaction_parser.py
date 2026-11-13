
import re


NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
    "hundred": 100,
    "thousand": 1000,
}

TRANSACTION_WORDS = [
    "credit", "credited", "add", "added",
    "udhar", "ಕೊಟ್ಟ", "ಸಾಲ",
    "payment", "paid", "pay", "received",
    "debit", "ಕಟ್ಟಿದ"
]

CURRENCY_WORDS = [
    "rupees", "rupee", "rs", "रुपी", "रूपी",
    "रुपये", "रुपया", "ರೂಪಾಯಿ", "ರೂಪಾಯಿಗಳು"
]


def words_to_number(words):
    total = 0
    current = 0

    for word in words:
        value = NUMBER_WORDS.get(word, 0)

        if word == "hundred":
            current = max(current, 1) * 100
        elif word == "thousand":
            total += max(current, 1) * 1000
            current = 0
        else:
            current += value

    return total + current


def parse_transaction(transcript):

    if not transcript or not transcript.strip():
        return {
            "success": False,
            "error": "Empty transcript."
        }

    original_text = transcript.strip()
    lower_text = original_text.lower()

    # Detect transaction type
    credit_found = bool(
        re.search(r"\b(credit|credited|add|added|udhar)\b", lower_text)
    )

    payment_found = bool(
        re.search(r"\b(payment|paid|pay|received|debit)\b", lower_text)
    )

    if credit_found and payment_found:
        return {
            "success": False,
            "error": "Transaction type is ambiguous."
        }

    if not credit_found and not payment_found:
        return {
            "success": False,
            "error": "Transaction type unclear."
        }

    transaction_type = "CREDIT" if credit_found else "PAYMENT"

    # Extract numeric amount first
    amount_match = re.search(
        r"\b\d+(?:,\d{3})*(?:\.\d{1,2})?\b",
        lower_text
    )

    amount_words = []

    if amount_match:
        amount = float(amount_match.group(0).replace(",", ""))
    else:
        number_sequence = re.findall(
            r"\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|"
            r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|"
            r"eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|"
            r"eighty|ninety|hundred|thousand)\b",
            lower_text
        )

        if not number_sequence:
            return {
                "success": False,
                "error": "Amount not found."
            }

        amount_words = number_sequence
        amount = float(words_to_number(number_sequence))

    if amount <= 0:
        return {
            "success": False,
            "error": "Amount must be greater than zero."
        }

    # Remove transaction words from customer name
    customer_name = original_text

    for word in TRANSACTION_WORDS:
        customer_name = re.sub(
            r"\b" + re.escape(word) + r"\b",
            " ",
            customer_name,
            flags=re.IGNORECASE
        )

    # Remove numeric amount
    customer_name = re.sub(
        r"\b\d+(?:,\d{3})*(?:\.\d{1,2})?\b",
        " ",
        customer_name
    )

    # Remove English number words
    for word in NUMBER_WORDS:
        customer_name = re.sub(
            r"\b" + re.escape(word) + r"\b",
            " ",
            customer_name,
            flags=re.IGNORECASE
        )

    # Remove currency words and symbols
    for word in CURRENCY_WORDS:
        customer_name = re.sub(
            re.escape(word),
            " ",
            customer_name,
            flags=re.IGNORECASE
        )

    customer_name = re.sub(
        r"₹|rs\.?",
        " ",
        customer_name,
        flags=re.IGNORECASE
    )

    # Remove extra spaces and punctuation
    customer_name = " ".join(customer_name.split())
    customer_name = customer_name.strip(" ,.-।")

    if not customer_name:
        return {
            "success": False,
            "error": "Customer name not found."
        }

    return {
        "success": True,
        "customer_name": customer_name,
        "transaction_type": transaction_type,
        "amount": amount
    }
