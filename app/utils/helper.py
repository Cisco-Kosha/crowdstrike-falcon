
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