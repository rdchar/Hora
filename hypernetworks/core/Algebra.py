
# def recurseHn(hn, v1, v2):
#     def _recurseHn(_v1):
#         found = False
#         hs = hn.hypernetwork[_v1]
#
#         if hs.partOf:
#             if v2 in hs.partOf:
#                 return True
#
#             else:
#                 for part in hs.partOf:
#                     if not found:
#                         found = _recurseHn(part)
#
#                     if found:
#                         return True
#
#         return found
#
#     return _recurseHn(v1)


def recurseHn(hn, v1, v2):
    def _recurseHn(_v1):
        found = False
        hs = hn.hypernetwork[_v1]

        if hs.partOf == set():
            return False

        if v2 in hs.partOf:
            return True

        for part in hs.partOf:
            if not found:
                found = _recurseHn(part)
                if not found:
                    break

            if found:
                break

        return found

    return _recurseHn(v1)


def memberOf(hn, elem, s):
    return recurseHn(hn, elem, s)


def contains(hn, s, elem):
    return recurseHn(hn, elem, s)
