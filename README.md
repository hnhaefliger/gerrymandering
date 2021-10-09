# Gerrymandering

A gerrymanding algorithm based on [OpenPrecincts](https://openprecincts.org/)' state of Pennsylvania voter data.

###

To prepare the data we:
1. Determine all of the polygons in a voting precinct.
2. Find all of the neighbors for each precinct checking if any sides are touching.
3. Generate random districts by 'growing out' from a starting precinct.

The algorithm the swaps precincts between districts randomly while optimizing for:
- Equal populations (lower difference is better)
- Predetermined voter ratios in each district (lower MSE is better)
- Average precinct distance from district center of gravity (lower distance is better) (Substitutes A:P ratio because it is much faster)
- Area to perimeter ratio (higher is better) (Current implementation is very slow due to union of irregular polygons)

Issues that still need to be addressed:
- Speed of area an perimeter calculations
- Problem where one district will cut another district in half by growing through it