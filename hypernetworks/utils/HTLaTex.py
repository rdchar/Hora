import re


from hypernetworks.core.Hypersimplex import ALPHA, BETA, VERTEX, NONE


def _latex(hs):
    bres = ""

    if hs.simplex:
        if hs.hstype == ALPHA:
            bres = "\left<"
        elif hs.hstype == BETA:
            bres = "\left\{"
        else:
            bres = ""

        new_simplex = []
        for v in hs.simplex:
            # if v[:4] == "SEQ@":
            #     v = "\\underline{" + v[4:len(v)] + "}"
            if v[:4] == "IMM@":
                v = "\\overline{" + v[4:len(v)] + "}"
            if v[:4] == "MAN@":
                v = "!" + v[4:len(v)]

            new_simplex.append(v)

        bres += ", ".join(new_simplex)

        if hs.hstype == ALPHA:
            bres += "; R" + (("" if hs.R.name == " " else "_{") + hs.R.name + "}") if hs.R.name else ""
            bres += ("; t_{" + str(hs.t) + "}") if hs.t >= 0 else ""
            bres += ("; B_{\\testit{" + ", ".str(hs.B) + "}}") if hs.B else ""
            bres += "\\right>"
            bres += ("^{" + hs.N + "}") if hs.N else ""

        elif hs.hstype == BETA:
            bres += "\\right\}" + (("^{" + hs.N + "}") if hs.N else "")

        else:
            bres = ""

    vert = hs.vertex.replace('-', "\\mbox{-}")
    bres = bres.replace('-', "\\mbox{-}")

    return vert + "=&" + bres


def latex(hn):
    res = "\\begin{align}"

    for (key, hs) in hn.hypernetwork.items():
        if hs.hstype not in [NONE, VERTEX]:
            res += _latex(hs) + "\\\\"

    def repl(m):
        inner_word = m.group(0)
        return "_{" + inner_word[1:] + "}"

    res = re.sub("_[0-9]+\-[0-9]+", repl, res)

    return res + "\\end{align}"
