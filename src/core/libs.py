from core import arithmetic, condition, io, pylTypes

# A lookup table for all the libraries. This method requires more manual
# maintenance, but is more streamlined than other methods
libs = {
    "arithmetic": arithmetic.arithmetic,
    "condition": condition.condition,
    "types": pylTypes.pyl_types,
    "io": io.io
}
