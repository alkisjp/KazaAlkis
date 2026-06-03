"""Conservative cultural reflections for daily Greek calendar messages."""


def build_cultural_reflection(today_data):
    """Return bilingual meaning text derived from reviewed daily signals."""
    if not today_data:
        return None

    traditions = today_data.get("parallel_traditions") or []
    if traditions:
        return _reflection_from_tradition(traditions[0])

    fasting = today_data.get("fasting")
    if fasting:
        return _reflection_from_fasting(fasting)

    holidays = today_data.get("holidays") or []
    if holidays:
        return _reflection_from_holiday(holidays[0])

    namedays = today_data.get("namedays") or []
    if namedays:
        return _reflection_from_nameday(namedays[0])

    return None


def _reflection_from_tradition(item):
    orthodox_title = item.get("orthodox_title") or "today's Orthodox tradition"
    orthodox_description = item.get("orthodox_description") or ""
    ancient_title = item.get("ancient_title") or "an ancient Greek parallel"
    ancient_description = item.get("ancient_description") or ""
    relationship = item.get("relationship_note") or (
        "This is a thematic cultural comparison, not proof of direct continuity."
    )
    region = item.get("region")
    region_en = f" in {region}" if region else ""
    region_gr = f" στην περιοχή {region}" if region else ""

    english = (
        f"Today’s Orthodox note looks at {orthodox_title}{region_en}. "
        f"{orthodox_description} "
        f"The ancient Greek parallel is {ancient_title}: {ancient_description} "
        f"{relationship}"
    )
    greek = (
        f"Το σημερινό ορθόδοξο σημείωμα κοιτάζει το {orthodox_title}{region_gr}. "
        f"{orthodox_description} "
        f"Ο αρχαιοελληνικός παραλληλισμός είναι το {ancient_title}: {ancient_description} "
        f"{relationship}"
    )
    return _clean_reflection(english, greek)


def _reflection_from_fasting(fasting):
    name = fasting.get("name") or "Orthodox fasting"
    description = fasting.get("description") or ""
    fasting_type = str(fasting.get("fasting_type") or "").lower()

    if "apostles" in name.lower():
        english = (
            "The Orthodox meaning of the Apostles' Fast is preparation after Pentecost: "
            "less noise, simpler food, prayer, and readiness for the feast of Saints Peter and Paul. "
            "A close seasonal ancient Greek parallel is Thargelia, a late-May festival of Apollo and Artemis "
            "with purification and first-fruits themes; nearby in the old Athenian year, Skira also belongs "
            "to the May/June turn of season. "
            "KazaALKIS treats this as a cultural parallel, not a claim that one custom directly became the other."
        )
        greek = (
            "Το ορθόδοξο νόημα της Νηστείας των Αγίων Αποστόλων είναι η προετοιμασία μετά την Πεντηκοστή: "
            "λιγότερος θόρυβος, πιο απλή τροφή, προσευχή και ετοιμότητα για τη μνήμη των Αγίων Πέτρου και Παύλου. "
            "Ένας κοντινός εποχικός αρχαιοελληνικός παραλληλισμός είναι τα Θαργήλια, γιορτή του τέλους Μαΐου "
            "για τον Απόλλωνα και την Άρτεμη με θέματα καθαρμού και πρώτων καρπών· κοντά στον ίδιο κύκλο "
            "του αθηναϊκού έτους βρίσκονται και τα Σκίρα, δεμένα με τη μετάβαση Μαΐου/Ιουνίου. "
            "Το KazaALKIS το παρουσιάζει ως πολιτιστικό παραλληλισμό, όχι ως απόδειξη άμεσης συνέχειας."
        )
        return _clean_reflection(english, greek)

    if "great lent" in name.lower() or fasting_type == "major_fast":
        english = (
            f"{name} gives the day an Orthodox tone of repentance, simplicity, and preparation. "
            f"{description} "
            "The ancient Greek parallel is not a single identical rite, but the wider pattern of seasonal purification "
            "and communal renewal before important feasts."
        )
        greek = (
            f"Το {name} δίνει στη μέρα ορθόδοξο τόνο μετάνοιας, απλότητας και προετοιμασίας. "
            f"{description} "
            "Ο αρχαιοελληνικός παραλληλισμός δεν είναι μία ίδια τελετή, αλλά το ευρύτερο μοτίβο του εποχικού καθαρμού "
            "και της κοινοτικής ανανέωσης πριν από σημαντικές γιορτές."
        )
        return _clean_reflection(english, greek)

    english = (
        f"Today falls within {name}. In Orthodox practice, fasting is not only about food; "
        "it is a way to make the day quieter, more attentive, and more communal. "
        "The ancient Greek comparison is thematic: many older Greek rituals also used rhythm, season, "
        "and shared discipline to give ordinary time a sacred shape."
    )
    greek = (
        f"Η σημερινή ημέρα βρίσκεται μέσα στην περίοδο: {name}. Στην ορθόδοξη πράξη, η νηστεία δεν αφορά μόνο την τροφή· "
        "είναι ένας τρόπος να γίνει η μέρα πιο ήσυχη, πιο προσεκτική και πιο κοινοτική. "
        "Ο αρχαιοελληνικός παραλληλισμός είναι θεματικός: πολλές παλαιότερες ελληνικές τελετές χρησιμοποιούσαν ρυθμό, εποχή "
        "και κοινή πειθαρχία για να δώσουν ιερό σχήμα στον καθημερινό χρόνο."
    )
    return _clean_reflection(english, greek)


def _reflection_from_holiday(holiday):
    name = holiday.get("name") or "today's feast"
    lower_name = name.lower()
    if "easter" in lower_name or "pascha" in lower_name or "πάσχα" in lower_name:
        english = (
            "For Orthodox Easter, the heart of the day is Resurrection: light after darkness, red eggs, "
            "family tables, lamb, and the greeting Christos Anesti. "
            "Ancient Greek spring festivals also used light, offerings, and communal meals to mark renewal. "
            "The comparison is about shared human patterns around spring and return, not a claim of direct identity."
        )
        greek = (
            "Στο ορθόδοξο Πάσχα, η καρδιά της ημέρας είναι η Ανάσταση: φως μετά το σκοτάδι, κόκκινα αυγά, "
            "οικογενειακό τραπέζι, αρνί και ο χαιρετισμός Χριστός Ανέστη. "
            "Οι αρχαιοελληνικές ανοιξιάτικες γιορτές χρησιμοποιούσαν επίσης φως, προσφορές και κοινά γεύματα για να σημάνουν ανανέωση. "
            "Η σύγκριση αφορά κοινά ανθρώπινα μοτίβα γύρω από την άνοιξη και την επιστροφή, όχι άμεση ταύτιση."
        )
        return _clean_reflection(english, greek)

    return _clean_reflection(
        f"Today’s public calendar note is {name}. KazaALKIS can connect this with Orthodox and ancient Greek tradition once a reviewed local custom is selected.",
        f"Η σημερινή δημόσια ημερολογιακή αναφορά είναι: {name}. Το KazaALKIS μπορεί να τη συνδέσει με ορθόδοξη και αρχαιοελληνική παράδοση όταν επιλεγεί ελεγμένο τοπικό έθιμο.",
    )


def _reflection_from_nameday(nameday):
    saint = nameday.get("saint") or "the commemorated saint"
    names = nameday.get("names") or nameday.get("name") or ""
    return _clean_reflection(
        f"The name-day note remembers {saint}. For the people named {names}, the tradition is personal: a blessing, a visit, a call, and a shared wish for many years.",
        f"Το εορτολογικό σημείωμα θυμάται: {saint}. Για τα ονόματα {names}, η παράδοση γίνεται προσωπική: ευχή, επίσκεψη, τηλεφώνημα και κοινό Χρόνια πολλά.",
    )


def _clean_reflection(english, greek):
    return {
        "english": " ".join(str(english).split()),
        "greek": " ".join(str(greek).split()),
    }
