import unittest

from core.Hypernetwork import Hypernetwork
from utils.HTString import load_parser, from_string


class MyTestCase(unittest.TestCase):
    def test_string1(self):
        face = Hypernetwork()
        self.assertEqual(from_string(face, parser, "face=<eyes, smile, round; R_face; t_0>^N").test_str(),
                         "face=<eyes, smile, round; R_face; t_0>^N")

    def test_string2(self):
        face = Hypernetwork()
        self.assertEqual(from_string(face, parser, "face=<eyes, smile, round; R_face; t_0>^N"
                                                   "face=<eyes, frown, round; R_face; t_0>^N").test_str(),
                         "face=<eyes, hs_0={smile, frown}, round; R_face>")

    def test_string3(self):
        face = Hypernetwork()
        self.assertEqual(from_string(face, parser, "face=<eyes, smile, round; R_face; t_0>^N"
                                                   "face=<eyes, frown, round; R_face; t_0>^N"
                                                   "face=<eyes, frown, square; R_face; t_0>^N").test_str(),
                         "face=<eyes, hs_5={hs_2=<hs_1={smile, frown}, round>, "
                         "hs_4=<frown, hs_3={round, square}>}; R_face>")

    def test_string4(self):
        face = Hypernetwork()
        self.assertEqual(from_string(face, parser, "face=<eyes, smile, round; R_face; t_0>^N"
                                                   "face=<eyes, frown, round; R_face; t_0>^N"
                                                   "face=<eyes, frown, square; R_face; t_0>^N"
                                                   "face=<eyes, smile, square; R_face; t_0>^N").test_str(),
                         "face=<eyes, hs_6={frown, smile}, hs_7={round, square}; R_face>")

    def test_string5(self):
        face = Hypernetwork()
        self.assertEqual(from_string(face, parser, "face=<<eyes, smile; R_above>, round; R_inside>"
                                                   "face=<<eyes, frown; R_above>, round; R_inside>").test_str(),
                         "face=<{<eyes, smile>, <eyes, frown>}; R_above>, round; R_inside>")
                        # TODO of face=<<eyes, {smile, frown}>; R_above>, round; R_inside> 
                        #  - note: this could only be true if the values in N+1 match, e.g. round 
                        #          becuase, <<eyes, smile>, round> U <<eyes, frown>, square> 
                        #                       != <<eyes, {smile, frown}>, {round, square}>
                        #                   face={<<eyes, smile>, round>, <<eyes, frown>, square>}


parser = load_parser()

if __name__ == '__main__':
    unittest.main()
