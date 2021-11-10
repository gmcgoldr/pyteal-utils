# algorithm quicksort(A, lo, hi) is
#  if lo >= 0 && hi >= 0 && lo < hi then
#    p := partition(A, lo, hi)
#
#    // Sort the two partitions
#    quicksort(A, lo, p - 1) // Left side of pivot
#    quicksort(A, p + 1, hi) // Right side of pivot

# algorithm partition(A, lo, hi) is
#  pivot := A[hi] // The pivot must be the last element
#
#  // Pivot index
#  i := lo - 1
#
#  for j := lo to hi do
#    if A[j] <= pivot then
#      i := i + 1
#      swap A[i] with A[j]
#  return i // the pivot index
