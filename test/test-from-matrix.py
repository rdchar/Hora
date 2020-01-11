import unittest
import numpy as np

from utils.HTMatrix import matrix_to_string

M1 = [
    ['e', 's', 'r'],
    ['e', 'f', 'r'],
    ['e', 'f', 'sq']
]

M2 = [
    ['e', 's', 'r'],
    ['e', 'f', 'r'],
    ['e', 'f', 'sq'],
    ['e', 'x', 'y']
]

M3 = [
    ['a', 'x', 'b', 'c', 'd', 'e', 'f'],
    ['a', 'x', 'g', 'c', 'd', 'h', 'f']
]

M4 = [
    ['a', 'b', 'c'],
    ['d', 'e', 'f'],
    ['g', 'h', 'i']
]

M5 = [
    ['a', 'b', 'c'],
    ['a', 'b', 'c'],
    ['a', 'b', 'c']
]

M6 = [
    ['e', 's', 'r'],
    ['e', 'f', 'r'],
    ['e', 'f', 'sq'],
    ['b', 'f', 'r']
]

M7 = [
    ['e', 's', 'r', 'x'],
    ['e', 'f', 'r', 'x'],
    ['e', 'f', 'sq', 'x'],
    ['b', 'f', 'r', 'x']
]

M8 = [['b', 'g', 'i', 'k', 'o'],
      ['d', 'g', 'i', 'l', 'm'],
      ['a', 'f', 'j', 'k', 'o'],
      ['b', 'f', 'h', 'k', 'm'],
      ['a', 'e', 'h', 'k', 'o'],
      ['a', 'g', 'i', 'k', 'm'],
      ['d', 'g', 'j', 'k', 'n'],
      ['d', 'e', 'i', 'l', 'p'],
      ['c', 'f', 'i', 'l', 'n']
      ]

M9 = [
    ['e', 's', 'r'],
    ['e', 'f', 'r'],
    ['e', 'f', 'sq'],
    ['e', 's', 'sq']
]

"""
print("M1: " + str(M1) + " => \n\t\t" + from_matrix(np.array(M1).T) + "\n")
print("M2: " + str(M2) + " => \n\t\t" + from_matrix(np.array(M2).T) + "\n")
print("M3: " + str(M3) + " => \n\t\t" + from_matrix(np.array(M3).T) + "\n")
print("M4: " + str(M4) + " => \n\t\t" + from_matrix(np.array(M4).T) + "\n")
print("M5: " + str(M5) + " => \n\t\t" + from_matrix(np.array(M5).T) + "\n")
print("M6: " + str(M6) + " => \n\t\t" + from_matrix(np.array(M6).T) + "\n")
print("M7: " + str(M7) + " => \n\t\t" + from_matrix(np.array(M7).T) + "\n")
print("M8: " + str(M8) + " => \n\t\t" + from_matrix(np.array(M8).T) + "\n")
print("M9: " + str(M9) + " => \n\t\t" + from_matrix(np.array(M9).T) + "\n")
"""


class test_HnTools(unittest.TestCase):
    def test_from_matrix1(self):
        self.assertEqual(matrix_to_string(np.array(M1).T), "<e,{<{s,f},r>,<f,{r,sq}>}>", "M1 Failed!")

    def test_from_matrix2(self):
        self.assertEqual(matrix_to_string(np.array(M2).T), "<e,{<{s,f},r>,<f,{r,sq}>,<x,y>}>", "M2 Failed!")

    def test_from_matrix3(self):
        self.assertEqual(matrix_to_string(np.array(M3).T), "<a,x,{<b,c,d,e>,<g,c,d,h>},f>", "M3 Failed!")

    def test_from_matrix4(self):
        self.assertEqual(matrix_to_string(np.array(M4).T), "{<a,b,c>,<d,e,f>,<g,h,i>}", "M4 Failed!")

    def test_from_matrix5(self):
        self.assertEqual(matrix_to_string(np.array(M5).T), "<a,b,c>", "M5 Failed!")

    def test_from_matrix6(self):
        self.assertEqual(matrix_to_string(np.array(M6).T), "{<e,{<{s,f},r>,<f,{r,sq}>}>,<{<e,{s,f}>,<{e,b},f>},r>}",
                         "M6 Failed!")

    def test_from_matrix7(self):
        self.assertEqual(matrix_to_string(np.array(M7).T), "<{<e,{<{s,f},r>,<f,{r,sq}>}>,<{<e,{s,f}>,<{e,b},f>},r>},x>",
                         "M7 Failed!")

    def test_from_matrix8(self):
        self.assertEqual(matrix_to_string(np.array(M8).T),
                         "{<b,{<g,i,k,o>,<f,h,k,m>}>,<{<b,g,i>,<a,{<f,j>,<e,h>}>},o,k>,"
                         "<d,{<g,{<i,l,m>,<j,k,n>}>,<e,i,l,p>}>,<{<d,g,i,l>,<{<b,f,h>,"
                         "<a,g,i>},k>},m>,<a,{<{<f,j>,<e,h>},o,k>,<g,i,k,m>}>,<{<d,g,j,k>,<c,f,i,l>},n>}",
                         "M8 Failed!")

    def test_from_matrix9(self):
        self.assertEqual(matrix_to_string(np.array(M9).T), "<e,<{f,s},{r,sq}>>", "M9 Failed!")
        

if __name__ == '__main__':
    unittest.main()

