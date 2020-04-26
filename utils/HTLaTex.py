import re
from core.Hypersimplex import ALPHA, BETA, NONE, VERTEX


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
            if v[:4] == "SEQ@":
                v = "\\underline{" + v[4:len(v)] + "}"
                v = v.replace('-', "\\mbox{-}")

            new_simplex.append(v)

        bres += ", ".join(new_simplex)

        if hs.hstype == ALPHA:
            bres += "; R" + (("" if hs.R == " " else "_{") + hs.R + "}") if hs.R else ""
            bres += ("; t_{" + str(hs.t) + "}") if hs.t >= 0 else ""
            bres += "\\right>"
            bres += ("^{" + hs.N + "}") if hs.N else ""

        elif hs.hstype == BETA:
            bres += "\\right\}" + (("^{" + hs.N + "}") if hs.N else "")

        else:
            bres = ""

    vert = hs.vertex.replace('-', "\\mbox{-}")

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


