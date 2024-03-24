# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: model_service.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13model_service.proto\x12!com.tsingj.me.api.mlmodel.manager\"\x18\n\x05Party\x12\x0f\n\x07partyId\x18\x01 \x03(\t\"*\n\tLocalInfo\x12\x0c\n\x04role\x18\x01 \x01(\t\x12\x0f\n\x07partyId\x18\x02 \x01(\t\"1\n\tModelInfo\x12\x11\n\ttableName\x18\x01 \x01(\t\x12\x11\n\tnamespace\x18\x02 \x01(\t\"\xcf\x01\n\rRoleModelInfo\x12Z\n\rroleModelInfo\x18\x01 \x03(\x0b\x32\x43.com.tsingj.me.api.mlmodel.manager.RoleModelInfo.RoleModelInfoEntry\x1a\x62\n\x12RoleModelInfoEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12;\n\x05value\x18\x02 \x01(\x0b\x32,.com.tsingj.me.api.mlmodel.manager.ModelInfo:\x02\x38\x01\"5\n\rUnloadRequest\x12\x11\n\ttableName\x18\x01 \x01(\t\x12\x11\n\tnamespace\x18\x02 \x01(\t\"5\n\x0eUnloadResponse\x12\x12\n\nstatusCode\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\"H\n\rUnbindRequest\x12\x11\n\tserviceId\x18\x01 \x01(\t\x12\x11\n\ttableName\x18\x02 \x01(\t\x12\x11\n\tnamespace\x18\x03 \x01(\t\"5\n\x0eUnbindResponse\x12\x12\n\nstatusCode\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\"\x85\x01\n\x11QueryModelRequest\x12\x11\n\tserviceId\x18\x01 \x01(\t\x12\x11\n\ttableName\x18\x02 \x01(\t\x12\x11\n\tnamespace\x18\x03 \x01(\t\x12\x12\n\nbeginIndex\x18\x04 \x01(\x05\x12\x10\n\x08\x65ndIndex\x18\x05 \x01(\x05\x12\x11\n\tqueryType\x18\x06 \x01(\x05\"\x0f\n\rModelBindInfo\"f\n\x0bModelInfoEx\x12\x11\n\ttableName\x18\x01 \x01(\t\x12\x11\n\tnamespace\x18\x02 \x01(\t\x12\x11\n\tserviceId\x18\x03 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x04 \x01(\t\x12\r\n\x05index\x18\x05 \x01(\x05\"z\n\x12QueryModelResponse\x12\x0f\n\x07retcode\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x42\n\nmodelInfos\x18\x03 \x03(\x0b\x32..com.tsingj.me.api.mlmodel.manager.ModelInfoEx\"\xf9\x03\n\x0ePublishRequest\x12;\n\x05local\x18\x01 \x01(\x0b\x32,.com.tsingj.me.api.mlmodel.manager.LocalInfo\x12I\n\x04role\x18\x02 \x03(\x0b\x32;.com.tsingj.me.api.mlmodel.manager.PublishRequest.RoleEntry\x12K\n\x05model\x18\x03 \x03(\x0b\x32<.com.tsingj.me.api.mlmodel.manager.PublishRequest.ModelEntry\x12\x11\n\tserviceId\x18\x04 \x01(\t\x12\x11\n\ttableName\x18\x05 \x01(\t\x12\x11\n\tnamespace\x18\x06 \x01(\t\x12\x10\n\x08loadType\x18\x07 \x01(\t\x12\x10\n\x08\x66ilePath\x18\x08 \x01(\t\x1aU\n\tRoleEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x37\n\x05value\x18\x02 \x01(\x0b\x32(.com.tsingj.me.api.mlmodel.manager.Party:\x02\x38\x01\x1a^\n\nModelEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12?\n\x05value\x18\x02 \x01(\x0b\x32\x30.com.tsingj.me.api.mlmodel.manager.RoleModelInfo:\x02\x38\x01\"S\n\x0fPublishResponse\x12\x12\n\nstatusCode\x18\x01 \x01(\x05\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\r\n\x05\x65rror\x18\x03 \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\x04 \x01(\x0c\x32\xcb\x05\n\x0cModelService\x12t\n\x0bpublishLoad\x12\x31.com.tsingj.me.api.mlmodel.manager.PublishRequest\x1a\x32.com.tsingj.me.api.mlmodel.manager.PublishResponse\x12t\n\x0bpublishBind\x12\x31.com.tsingj.me.api.mlmodel.manager.PublishRequest\x1a\x32.com.tsingj.me.api.mlmodel.manager.PublishResponse\x12v\n\rpublishOnline\x12\x31.com.tsingj.me.api.mlmodel.manager.PublishRequest\x1a\x32.com.tsingj.me.api.mlmodel.manager.PublishResponse\x12y\n\nqueryModel\x12\x34.com.tsingj.me.api.mlmodel.manager.QueryModelRequest\x1a\x35.com.tsingj.me.api.mlmodel.manager.QueryModelResponse\x12m\n\x06unload\x12\x30.com.tsingj.me.api.mlmodel.manager.UnloadRequest\x1a\x31.com.tsingj.me.api.mlmodel.manager.UnloadResponse\x12m\n\x06unbind\x12\x30.com.tsingj.me.api.mlmodel.manager.UnbindRequest\x1a\x31.com.tsingj.me.api.mlmodel.manager.UnbindResponseB\x13\x42\x11ModelServiceProtob\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'model_service_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'B\021ModelServiceProto'
  _ROLEMODELINFO_ROLEMODELINFOENTRY._options = None
  _ROLEMODELINFO_ROLEMODELINFOENTRY._serialized_options = b'8\001'
  _PUBLISHREQUEST_ROLEENTRY._options = None
  _PUBLISHREQUEST_ROLEENTRY._serialized_options = b'8\001'
  _PUBLISHREQUEST_MODELENTRY._options = None
  _PUBLISHREQUEST_MODELENTRY._serialized_options = b'8\001'
  _PARTY._serialized_start=58
  _PARTY._serialized_end=82
  _LOCALINFO._serialized_start=84
  _LOCALINFO._serialized_end=126
  _MODELINFO._serialized_start=128
  _MODELINFO._serialized_end=177
  _ROLEMODELINFO._serialized_start=180
  _ROLEMODELINFO._serialized_end=387
  _ROLEMODELINFO_ROLEMODELINFOENTRY._serialized_start=289
  _ROLEMODELINFO_ROLEMODELINFOENTRY._serialized_end=387
  _UNLOADREQUEST._serialized_start=389
  _UNLOADREQUEST._serialized_end=442
  _UNLOADRESPONSE._serialized_start=444
  _UNLOADRESPONSE._serialized_end=497
  _UNBINDREQUEST._serialized_start=499
  _UNBINDREQUEST._serialized_end=571
  _UNBINDRESPONSE._serialized_start=573
  _UNBINDRESPONSE._serialized_end=626
  _QUERYMODELREQUEST._serialized_start=629
  _QUERYMODELREQUEST._serialized_end=762
  _MODELBINDINFO._serialized_start=764
  _MODELBINDINFO._serialized_end=779
  _MODELINFOEX._serialized_start=781
  _MODELINFOEX._serialized_end=883
  _QUERYMODELRESPONSE._serialized_start=885
  _QUERYMODELRESPONSE._serialized_end=1007
  _PUBLISHREQUEST._serialized_start=1010
  _PUBLISHREQUEST._serialized_end=1515
  _PUBLISHREQUEST_ROLEENTRY._serialized_start=1334
  _PUBLISHREQUEST_ROLEENTRY._serialized_end=1419
  _PUBLISHREQUEST_MODELENTRY._serialized_start=1421
  _PUBLISHREQUEST_MODELENTRY._serialized_end=1515
  _PUBLISHRESPONSE._serialized_start=1517
  _PUBLISHRESPONSE._serialized_end=1600
  _MODELSERVICE._serialized_start=1603
  _MODELSERVICE._serialized_end=2318
# @@protoc_insertion_point(module_scope)