import time
from concurrent import futures
from exp.grpcServer.gRPC.python.hypernetwork_pb2_grpc import *

import grpc

from hypernetworks.core.Hypernetwork import Hypernetwork


class HypernetworkService(HnServicer):
    def __init__(self):
        self.hn = Hypernetwork()

    def HelloMsg(self, request, context):
        response = HelloMsg()
        response.hello = "HELLO " + request.hello
        return response

    def GetHs(self, request, context):
        vertex = request.vertex
        response = HnMsg()
        response.vertex = vertex
        response.simplex = self.hn[vertex].simplex
        response.partOf = self.hn[vertex].partOf
        response.hstype = self.hn[vertex].hstype
        response.R = self.hn[vertex].R
        response.t = self.hn[vertex].t
        response.M = self.hn[vertex].M
        response.N = self.hn[vertex].N
        response.psi = self.hn[vertex].psi
        return response

    def AddHs(self, request, context):
        vertex = self.hn.insert(vertex=request.vertex, hstype=request.hstype, simplex=request.simplex,
                                R=request.R, t=request.t, M=request.M, N=request.N, psi=request.psi,
                                partOf=request.partOf)
        response = VertexMsg()
        response.vertex = vertex
        return response

    def DeleteHs(self, request, context):
        self.hn.delete(vertex=request.vertex, R=request.R)
        response = EmptyMsg()
        return response

    def GetHn(self, request, context):
        response = HnMsg()
        response.name = self.hn.name
        response.hypernetwork = self.hn.hypernetwork
        return response

    def CreateHnByString(self, request, context):
        print(request)
        # hn_compile(request.)
        response = HnMsg()
        response.name = self.hn.name
        response.hypernetwork = self.hn.hypernetwork
        return response


def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_HnServicer_to_server(HypernetworkService(), server)
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    print("Starting HnServer on", port)

    try:
        while True:
            time.sleep(10000)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    serve(6000)
