

def remove_outliers(hn, N="N", smallest_nary=2):
    for vertex in hn.hypernetwork:
        hs = hn.hypernetwork[vertex]

        if hs.N == N:
            if len(hs.simplex) > smallest_nary:
                for s in hs.simplex:
                    if len(hn.hypernetwork[s].partOf) == 1:
                        hn.delete(vertex=s)
