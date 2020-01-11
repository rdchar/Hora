import random as random

import numpy as np


def get_incidence_matrix(m):
    mt = np.array(m).T
    Y = np.unique(np.reshape(mt, np.size(mt)))
    res = np.zeros([len(m), len(Y)], int)

    for i, line in enumerate(m):
        for elem in line:
            if elem is not None:
                lst = list(Y)
                pos = lst.index(elem)
                res[i][pos] = 1

    return res, Y


"""
def get_variants(m):
    var = list(m[0])

    for simplex in m:
        for i, vertex in enumerate(simplex):
            if var[i] != vertex:
                if isinstance(var[i], list):
                    if vertex not in var[i]:
                        if vertex is not None:
                            var[i].append(vertex)

                else:
                    if var[i] is None:
                        var[i] = vertex

                    elif vertex is not None:
                        var[i] = list([var[i], vertex])

    return var
"""


def generate_test_matrix(size_x, size_y, max=-1):
    possibilities = [
        ['a', 'b', 'c', 'd'],
        ['a', 'b', 'e', 'f', 'g', 'h', 'i'],
        ['h', 'i', 'j'],
        ['k', 'l'],
        ['m', 'n', 'o', 'p', 'q', 'r', 's'],
        ['r', 's', 't', 'u'],
        ['v', 'w', 'x'],
        ['y', 'z']
    ]

    m = []

    if size_x <= len(possibilities):
        for y in range(size_y):
            temp = []

            for x in range(size_x):
                l = len(possibilities[x]) - 1
                max = l if max == -1 else max if l >= max else l
                temp.append(possibilities[x][random.randint(0, l)])

            m.append(temp)

    return m


class QAnalysis:
    def __init__(self, im, titles):
        self._titles = titles
        # self._M = m
        # self._var = get_variants(self._M)
        self._IM = im
        self._shared_faces = self._find_shared_faces()
        self._K = self._findK()
        self._Qsize = self._find_Qsize()
        self._Q, self._obstruction, self._components = self._q_analysis()
        self._top_q, self._bottom_q, self._ecc = self._eccentricity()

    @property
    def qcomponents(self):
        return self._components

    @property
    def Q(self):
        return self._Q

    @property
    def K(self):
        return self._K

    @property
    def ecc(self):
        return self._ecc

    @property
    def top_q(self):
        return self._top_q

    @property
    def bottom_q(self):
        return self._bottom_q

    # @property
    # def variants(self):
    #     return self._var

    def _eccentricity(self):
        ecc = []
        q_top = []
        q_bottom = []

        l = len(self._titles)

        for i in range(l):
            qt = self.K[i][i]
            qb = 0

            for j in range(l):
                if i != j and qb < self.K[i][j]:
                    qb = self.K[i][j]

            e = (float(qt-qb)) / (float(qb+1))

            q_top.append(qt)
            q_bottom.append(qb)
            ecc.append(e)

        return np.array(q_top), np.array(q_bottom), np.array(ecc)

    def _findK(self):
        l = len(self._IM)
        k = np.array([[-1 for i in range(l)] for j in range(l)])

        for s1, simplex1 in enumerate(self._IM):
            indices = _get_indices(simplex1, lambda x: x == 1)

            for idx in indices:
                for s2, simplex2 in enumerate(self._IM):
                    if simplex2[idx] == 1:
                        k[s1][s2] += 1

        return k

    def _find_Qsize(self):
        largest = -1

        for x in self._K:
            for y in x:
                largest = y if y > largest else largest

        return largest

    def _find_shared_faces(self):
        x = len(self._titles)
        sf = np.full((x, x), -1)

        """
        for line in self._IM:
            for v1 in line:
                for v2 in line:
                    if 
                        print(j)
        """
        return sf

    def _q_analysis(self):
        largest = self._Qsize + 1
        q_components = [[] for i in range(largest)]

        for q in range(largest):
            temp_shared_faces = []
            shared_faces = []

            for simplex in self._K:
                indices = _get_indices(simplex, lambda x: x >= q)
                face = set()

                for idx in indices:
                    face.add(self._titles[idx])

                if face:
                    # ***** PORTED TO THIS POINT
                    for f in temp_shared_faces:
                        if f.intersection(face):
                            face = face.union(f)

                    if temp_shared_faces:
                        for i, f in enumerate(temp_shared_faces):
                            if f.issubset(face) or face.issubset(f):
                                face = face.union(f)
                                temp_shared_faces[i] = face

                            else:
                                temp_shared_faces.append(face)

                    else:
                        temp_shared_faces.append(face)

            for f in temp_shared_faces:
                if f not in shared_faces:
                    shared_faces.append(f)

            q_components[q] = shared_faces

        _Q = []
        _obstruction = []

        for q in q_components:
            _Q.append(len(q))
            _obstruction.append(len(q) - 1)

        return _Q, _obstruction, q_components


def _get_indices(m, v):
    if isinstance(v, str):
        return [i for i, x in enumerate(m) if x == v]

    return [i for i, x in enumerate(m) if v(x)]