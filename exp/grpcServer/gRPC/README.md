# gRPC / protobuf3 

## Python
python -m grpc_tools.protoc --proto_path=. --python_out=python --grpc_python_out=python hypernetwork.proto

## JavaScript / Node.js
npm install -g grpc-tools

./node_modules/.bin/grpc_tools_node_protoc --js_out=import_style=commonjs,binary:js --grpc_out=js --plugin=protoc-gen-grpc=./node_modules/.bin/grpc_tools_node_protoc_plugin hypernetwork.proto

