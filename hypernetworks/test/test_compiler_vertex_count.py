from hypernetworks.core.Hypernetwork import Hypernetwork
from hypernetworks.utils.HTCompiler import load_parser, compile_hn

# Expect "WARNING: w, x failed the vertex check!"
if __name__ == "__main__":
    parser = load_parser()
    hn = Hypernetwork()

    compile_hn(hn, parser, """
        w=<a1, b1, a2, b2; R_w>
        x=<a1, b1, a2, b2; R_x>
        y=<a1, b1, a2, b2; R_y>
    
        w -> (v_1 /above/ v_2) /next/ (v_3 /above/ v_4) /next/ v_5;
        x -> v_1 /above/ v_2 /above/ v_3;
        x -> (v_1 /above/ v_2) AND (v_2 /above/ v_3);
        y -> (v_1 /above/ v_2) /next/ (v_3 /above/ v_4);
        
        z=<a, b, c; R_z|v_1 /connectedTo/ v_2 /connectedTo/ v_3 /connectedTo/ v_1>
    """)
