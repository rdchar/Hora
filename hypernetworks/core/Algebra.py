
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
        # print("\tHELLO 5", _v1)

        if hs.partOf == set():
            # print("\t\tHELLO 7", hs.partOf)
            return False

        if v2 in hs.partOf:
            # print("\t\tHELLO 8")
            return True

        for part in hs.partOf:
            if not found:
                found = _recurseHn(part)
                # if not found:
                #     print("\t\tHELLO 9")
                #     break

            if found:
                # print("\t\tHELLO 10")
                break

        # print("\tHELLO 6", found)
        return found

    return _recurseHn(v1)


def memberOf(hn, elem, s):
    return recurseHn(hn, elem, s)


def contains(hn, s, elem):
    return recurseHn(hn, elem, s)
