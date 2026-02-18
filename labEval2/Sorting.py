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
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1

        # Move elements smaller than key one step right
        while j >= 0 and arr[j] < key:
            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = key

    return arr
