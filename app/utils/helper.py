
def create_id_filter(incoming: str) -> str:
    """Create a `or` style FQL filter based upon the ID(s) provided."""
    generated = ""
    delim = ""
    left = ""
    right = ""
    for d_id in incoming.split(","):
        if len(d_id) > 2:
            left = "("
            right = ")"
        if generated:
            delim = ","
        generated = f"{left}{generated}{delim}detection_id:*'*{d_id}'{right}"

    return generated


def clean_status_string(incoming: str) -> str:
    """Format the status string for output."""
    stats = []
    stat_val = incoming.replace("_", " ").split()
    for val in stat_val:
        new_val = val.title()
        stats.append(new_val)

    return " ".join(stats)


def clean_result(itm: dict, extend: bool = False) -> dict:
    """Clean an individual result."""
    fields = [
        "display_id", "status", "id", "device_id", "hostname", "tactic", "technique", "timestamp"
        ]
    cln = {}
    if extend:
        cln["behaviors"] = []
        fields.pop()
        fields.pop()
        fields.pop()
    for field in fields:
        cln[field] = ""

    cln["status"] = itm["status"]
    cln["id"] = itm["detection_id"]
    if not extend:
        cln["id"] = cln["id"].split(":")[2]
        clor = itm["status"]
        cln["display_id"] = f"{clor}{clean_status_string(itm['status'])}\n{cln['id']}"
        if itm.get("assigned_to_name", None):
            nam = itm["assigned_to_name"]
            cln["display_id"] = f"{cln['display_id']}\n{nam}"
    cln["device_id"] = itm["device"]["device_id"]
    cln["hostname"] = itm["device"].get("hostname", cln["device_id"])
    bcnt = 0
    for beh in itm["behaviors"]:
        if bcnt == 0:
            cln["first_occurrence"] = beh["timestamp"]
            bcnt += 1
        if extend:
            behave = {}
            behave["description"] = beh["description"]
            behave["tactic"] = beh["tactic"]
            behave["tactic_id"] = beh["tactic_id"]
            behave["technique"] = beh["technique"]
            behave["technique_id"] = beh["technique_id"]
            behave["timestamp"] = beh["timestamp"]
            cln["behaviors"].append(behave)
        else:
            cln["tactic"] = f"{cln['tactic']}\n{beh['tactic']} ({beh['tactic_id']})"
            cln["technique"] = f"{cln['technique']}\n{beh['technique']} ({beh['technique_id']})"
            cln["timestamp"] = f"{cln['timestamp']}\n{beh['timestamp']}"

    if extend:
        cln["assigned"] = itm.get("assigned_to_name", "Unassigned")
        cln["external_ip"] = itm["device"].get("external_ip", "Not available")
        cln["local_ip"] = itm["device"].get("local_ip", "Not available")
        cln["platform_name"] = itm["device"].get("platform_name", "Not available")
        cln["os_version"] = itm["device"].get("os_version", "Not available")
        cln["agent_version"] = itm["device"].get("agent_version", "Not available")
    else:
        cln["hostname"] = f"{cln['hostname']}\n{itm['device']['device_id']}"

    return cln

def clean_description(incoming: str) -> str:
    """Format behavior description strings for output."""
    description = []
    for desc in incoming.split("\n"):
        part = ""
        for piece in desc.split():
            delim = ""
            if len(part) > 60:
                description.append(part)
                part = ""
            if part:
                delim = " "
            part = f"{part}{delim}{piece}"
        description.append(part)

    return "\n".join(description)

