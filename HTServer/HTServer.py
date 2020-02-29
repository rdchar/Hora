from core.Hypernetwork import Hypernetwork, Hypersimplex
from hypernetwork_pb2 import *
from hypernetwork_pb2_grpc import *
from concurrent import futures

import grpc
import time


class HypernetworkService(HTServicer):
    def __init__(self):
        self.hn = Hypernetwork()

    def GetHypersimplex(self, request, context):
        vertex = request.vertex
        response = HypernetworkMessage()
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

    def AddHypersimplex(self, request, context):
        vertex = self.hn.insert(vertex=request.vertex, hstype=request.hstype, simplex=request.simplex,
                                R=request.R, t=request.t, M=request.M, N=request.N, psi=request.psi,
                                partOf=request.partOf)
        response = VertexMessage()
        response.vertex = vertex
        return response

    def DeleteHypersimplex(self, request, context):
        self.hn.delete(vertex=request.vertex, R=request.R)
        response = EmptyMessage()
        return response

    def GetHypernetwork(self, request, context):
        response = HypernetworkMessage()
        response.name = self.hn.name
        response.hypernetwork = self.hn.hypernetwork
        return response


def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_HTServicer_to_server(HypernetworkService(), server)
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    print("Sarting HTServer on", port)

    try:
        while True:
            time.sleep(10000)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    serve(6000)
