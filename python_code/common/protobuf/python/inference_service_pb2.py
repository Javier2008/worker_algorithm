# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: inference_service.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x17inference_service.proto\x12\x19\x63om.tsingj.me.api.serving\"0\n\x10InferenceMessage\x12\x0e\n\x06header\x18\x01 \x01(\x0c\x12\x0c\n\x04\x62ody\x18\x02 \x01(\x0c\x32\xd8\x02\n\x10InferenceService\x12\x65\n\tinference\x12+.com.tsingj.me.api.serving.InferenceMessage\x1a+.com.tsingj.me.api.serving.InferenceMessage\x12m\n\x11startInferenceJob\x12+.com.tsingj.me.api.serving.InferenceMessage\x1a+.com.tsingj.me.api.serving.InferenceMessage\x12n\n\x12getInferenceResult\x12+.com.tsingj.me.api.serving.InferenceMessage\x1a+.com.tsingj.me.api.serving.InferenceMessageB\x17\x42\x15InferenceServiceProtob\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'inference_service_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'B\025InferenceServiceProto'
  _INFERENCEMESSAGE._serialized_start=54
  _INFERENCEMESSAGE._serialized_end=102
  _INFERENCESERVICE._serialized_start=105
  _INFERENCESERVICE._serialized_end=449
# @@protoc_insertion_point(module_scope)
