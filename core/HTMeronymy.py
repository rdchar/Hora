import numpy as np

MERONYMY = [
    "component",
    "member",
    "portion",
    "stuff",
    "feature",
    "place",
    "in",
    "is-a",
    "attribute",
    "attached",
    "belongs-to"
]

M_UNKNOWN = -1
M_COMPONENT = 0
M_MEMBER = 1
M_PORTION = 2
M_STUFF = 3
M_FEATURE = 4
M_PLACE = 5
M_IN = 6
M_IS_A = 7
M_ATTRIBUTE = 8
M_ATTACHED = 9
M_BELONGS_TO = 10


# Meronymy compatibility matrix
meronymy_matrix = np.full((11, 11), False)
meronymy_matrix[0, 0] = True
meronymy_matrix[1, 1] = True
meronymy_matrix[2, 2] = True
meronymy_matrix[3, 3] = True
meronymy_matrix[4, 4] = True
meronymy_matrix[5, 5] = True
meronymy_matrix[6, 6] = True
meronymy_matrix[7, 7] = True
meronymy_matrix[8, 8] = True
meronymy_matrix[9, 9] = True
meronymy_matrix[10, 10] = True

meronymy_matrix[M_IS_A, M_COMPONENT] = True
meronymy_matrix[M_COMPONENT, M_IS_A] = True

