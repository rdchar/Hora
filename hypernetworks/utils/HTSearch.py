from hypernetworks.utils.HTPaths import HsPath, find_head


def get_peak_path(hn, from_vertex, ignore_sb=False, sb=None):
    if not ignore_sb and not sb:
        sb = hn.hypernetwork[from_vertex].B

    path = HsPath(hn.hypernetwork, vertex=from_vertex)

    if from_vertex in hn.hypernetwork:
        path.gen_path(from_vertex, "", sb)
    else:
        path.paths = []

    return path


def get_search_paths(hn, ignore_sb=False, *vertex_list):
    # Side-effects: changes temp.paths; new; existing
    paths = []

    if ignore_sb:
        sb = None
    else:
        sb = hn.hypernetwork[vertex_list[0]].B

    if len(vertex_list) == 1:
        paths.update({vertex_list[0]: [[vertex_list[0]]]})

    elif len(vertex_list) > 1:
        for vertex in vertex_list:
            paths.append(get_peak_path(hn, vertex, ignore_sb, sb))

    return paths


def what_is_it(hn, ignore_sb=False, *vertex_list):
    objects = set()
    groups = {}
    paths = get_search_paths(hn, ignore_sb, *vertex_list)

    for path in paths:
        for pth in path:
            if len(pth) == 1:
                groups.update({pth[0]: [[pth[0]]]})
            else:
                if pth[0] not in groups:
                    groups.update({pth[0]: [pth[1:]]})
                else:
                    groups[pth[0]].append(pth[1:])

    for k, group in groups.items():
        temp = set()
        for grp in group:
            temp.update(grp)

        if len(objects) == 0:
            objects = temp.copy()
        else:
            objects = objects.intersection(temp)

    return list(objects)
