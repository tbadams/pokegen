
def get_length_stats(dataname, lines):
    count = 0
    total_length = 0
    min_length = 9999999
    max_length = 0
    for line in lines:
        count = count + 1
        entry_length = len(str(line))
        total_length = total_length + entry_length
        max_length = max(max_length, entry_length)
        min_length = min(min_length, entry_length)
    if dataname is not None:
        print(dataname + ":count - " + str(count) + ", min - " + str(min_length) + ", max - " + str(max_length)
              + ", average length = " + str(total_length / count))
    return {"count": count, "total": total_length, "min": min_length, "max": max_length, "average": total_length / count}