for f in "${PROTO_DIR}"*.proto
do
    protoc \
      --plugin="protoc-gen-ts=${PROTOC_GEN_TS_PATH}" \
      --proto_path="${PROTO_DIR}" \
      --js_out=import_style=commonjs,binary:${OUT_DIR}/js \
      --ts_out=${OUT_DIR}/js \
      "${f}"
done


for f in "${OUT_DIR}"/js/*.js
do
    echo '/* eslint-disable */' | cat - "${f}" > temp && mv temp "${f}"
done
