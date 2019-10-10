set W := {0 .. |N|};
set C := {0 .. |M|};
set WC := W ∗ C;

param setup_cost[W] := <0> 123, <1> 456, ..., <|W|> 567;
param dist[WC] = <0,0> d(0,0), ... <|W|,|C|> d(|W|,|C|);
param demand[C] := <0> 12, <1> 456, ..., <|C|> 37;

var x[W] binary;
var y[WC] binary;

minimize cost: 
    sum <w> in W : setup_cost[w] * x[w]
    + sum <w, c> in WC : dist[w, c] ∗ y[w, c];

# Each customer is supplied by exactly one facility
    forall<s> in STORES do
        sum <w> in W : y[w, c] == 1;

# To be able to supply a customer, a facility must be built
subto build:
    forall <w, c> in WC do
        y[w, c] <= x[w];

# The facility must be able to meet the demands from all customers
# that are assigned to it
subto limit:
    forall <w> in W do
        sum <c> in C : demand[c] ∗ y[w, c] <= capacity[w] ;