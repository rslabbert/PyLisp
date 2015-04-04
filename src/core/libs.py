from core import arithmetic, condition, pylMath, io, pylTypes

# A lookup table for all the libraries. This method requires more manual
# maintenance, but is more streamlined than other methods
libs = {
    "arithmetic": arithmetic.arithmetic,
    "condition": condition.condition,
    "types": pylTypes.pylTypes,
    "math": pylMath.pylMath,
    "io": io.io
}
