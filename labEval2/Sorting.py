"""
        SHASHAANK MK-CB.SC.U4CSE24048
"""
def insertionSortByIndex( arr: list[tuple[int,int]], index: int):
    """
    Sorts list of (i,j) tuples by index 0 (row) or 1 (col)
        Uses insertion sort (O(n^2)) – fine for very small n
    """
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1

        while j >= 0 and arr[j][index] > key[index]:
            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = key

    return arr

def insertionSortDescending(arr):
    if len(arr) == 0:
        return arr

    # Step 1: Find maximum value to know number of buckets needed
    max_val = max(arr)

    # Step 2: Create buckets
    buckets = [[] for _ in range(max_val + 1)]

    # Step 3: Put elements into their respective buckets
    for num in arr:
        buckets[num].append(num)

    # Step 4: Collect elements from buckets in descending order
    sorted_arr = []
    for i in range(max_val, -1, -1):
        for num in buckets[i]:
            sorted_arr.append(num)

    return sorted_arr

