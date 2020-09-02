// GENERATED CODE -- DO NOT EDIT!

'use strict';
var grpc = require('grpc');
var hypernetwork_pb = require('./hypernetwork_pb.js');

function serialize_Hn_EmptyMsg(arg) {
  if (!(arg instanceof hypernetwork_pb.EmptyMsg)) {
    throw new Error('Expected argument of type Hn.EmptyMsg');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_Hn_EmptyMsg(buffer_arg) {
  return hypernetwork_pb.EmptyMsg.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_Hn_HelloMsg(arg) {
  if (!(arg instanceof hypernetwork_pb.HelloMsg)) {
    throw new Error('Expected argument of type Hn.HelloMsg');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_Hn_HelloMsg(buffer_arg) {
  return hypernetwork_pb.HelloMsg.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_Hn_HnByStringMsg(arg) {
  if (!(arg instanceof hypernetwork_pb.HnByStringMsg)) {
    throw new Error('Expected argument of type Hn.HnByStringMsg');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_Hn_HnByStringMsg(buffer_arg) {
  return hypernetwork_pb.HnByStringMsg.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_Hn_HnMsg(arg) {
  if (!(arg instanceof hypernetwork_pb.HnMsg)) {
    throw new Error('Expected argument of type Hn.HnMsg');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_Hn_HnMsg(buffer_arg) {
  return hypernetwork_pb.HnMsg.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_Hn_HsMsg(arg) {
  if (!(arg instanceof hypernetwork_pb.HsMsg)) {
    throw new Error('Expected argument of type Hn.HsMsg');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_Hn_HsMsg(buffer_arg) {
  return hypernetwork_pb.HsMsg.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_Hn_VertexMsg(arg) {
  if (!(arg instanceof hypernetwork_pb.VertexMsg)) {
    throw new Error('Expected argument of type Hn.VertexMsg');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_Hn_VertexMsg(buffer_arg) {
  return hypernetwork_pb.VertexMsg.deserializeBinary(new Uint8Array(buffer_arg));
}


var HnService = exports.HnService = {
  helloWorld: {
    path: '/Hn.Hn/HelloWorld',
    requestStream: false,
    responseStream: false,
    requestType: hypernetwork_pb.HelloMsg,
    responseType: hypernetwork_pb.HelloMsg,
    requestSerialize: serialize_Hn_HelloMsg,
    requestDeserialize: deserialize_Hn_HelloMsg,
    responseSerialize: serialize_Hn_HelloMsg,
    responseDeserialize: deserialize_Hn_HelloMsg,
  },
  getHs: {
    path: '/Hn.Hn/GetHs',
    requestStream: false,
    responseStream: false,
    requestType: hypernetwork_pb.VertexMsg,
    responseType: hypernetwork_pb.HsMsg,
    requestSerialize: serialize_Hn_VertexMsg,
    requestDeserialize: deserialize_Hn_VertexMsg,
    responseSerialize: serialize_Hn_HsMsg,
    responseDeserialize: deserialize_Hn_HsMsg,
  },
  addHs: {
    path: '/Hn.Hn/AddHs',
    requestStream: false,
    responseStream: false,
    requestType: hypernetwork_pb.HsMsg,
    responseType: hypernetwork_pb.VertexMsg,
    requestSerialize: serialize_Hn_HsMsg,
    requestDeserialize: deserialize_Hn_HsMsg,
    responseSerialize: serialize_Hn_VertexMsg,
    responseDeserialize: deserialize_Hn_VertexMsg,
  },
  deleteHs: {
    path: '/Hn.Hn/DeleteHs',
    requestStream: false,
    responseStream: false,
    requestType: hypernetwork_pb.HsMsg,
    responseType: hypernetwork_pb.VertexMsg,
    requestSerialize: serialize_Hn_HsMsg,
    requestDeserialize: deserialize_Hn_HsMsg,
    responseSerialize: serialize_Hn_VertexMsg,
    responseDeserialize: deserialize_Hn_VertexMsg,
  },
  getHn: {
    path: '/Hn.Hn/GetHn',
    requestStream: false,
    responseStream: false,
    requestType: hypernetwork_pb.EmptyMsg,
    responseType: hypernetwork_pb.HsMsg,
    requestSerialize: serialize_Hn_EmptyMsg,
    requestDeserialize: deserialize_Hn_EmptyMsg,
    responseSerialize: serialize_Hn_HsMsg,
    responseDeserialize: deserialize_Hn_HsMsg,
  },
  createHnByString: {
    path: '/Hn.Hn/CreateHnByString',
    requestStream: false,
    responseStream: false,
    requestType: hypernetwork_pb.HnByStringMsg,
    responseType: hypernetwork_pb.HnMsg,
    requestSerialize: serialize_Hn_HnByStringMsg,
    requestDeserialize: deserialize_Hn_HnByStringMsg,
    responseSerialize: serialize_Hn_HnMsg,
    responseDeserialize: deserialize_Hn_HnMsg,
  },
};

exports.HnClient = grpc.makeGenericClientConstructor(HnService);
