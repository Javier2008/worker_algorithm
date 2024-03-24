# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import data_meta_pb2 as data__meta__pb2
import data_proxy_pb2 as data__proxy__pb2


class DataTransferServiceStub(object):
    """data transfer service
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.push = channel.stream_unary(
                '/com.tsingj.me.api.networking.proxy.DataTransferService/push',
                request_serializer=data__proxy__pb2.Packet.SerializeToString,
                response_deserializer=data__proxy__pb2.Metadata.FromString,
                )
        self.pull = channel.unary_stream(
                '/com.tsingj.me.api.networking.proxy.DataTransferService/pull',
                request_serializer=data__proxy__pb2.Metadata.SerializeToString,
                response_deserializer=data__proxy__pb2.Packet.FromString,
                )
        self.unaryCall = channel.unary_unary(
                '/com.tsingj.me.api.networking.proxy.DataTransferService/unaryCall',
                request_serializer=data__proxy__pb2.Packet.SerializeToString,
                response_deserializer=data__proxy__pb2.Packet.FromString,
                )


class DataTransferServiceServicer(object):
    """data transfer service
    """

    def push(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def pull(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def unaryCall(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_DataTransferServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'push': grpc.stream_unary_rpc_method_handler(
                    servicer.push,
                    request_deserializer=data__proxy__pb2.Packet.FromString,
                    response_serializer=data__proxy__pb2.Metadata.SerializeToString,
            ),
            'pull': grpc.unary_stream_rpc_method_handler(
                    servicer.pull,
                    request_deserializer=data__proxy__pb2.Metadata.FromString,
                    response_serializer=data__proxy__pb2.Packet.SerializeToString,
            ),
            'unaryCall': grpc.unary_unary_rpc_method_handler(
                    servicer.unaryCall,
                    request_deserializer=data__proxy__pb2.Packet.FromString,
                    response_serializer=data__proxy__pb2.Packet.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'com.tsingj.me.api.networking.proxy.DataTransferService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class DataTransferService(object):
    """data transfer service
    """

    @staticmethod
    def push(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_unary(request_iterator, target, '/com.tsingj.me.api.networking.proxy.DataTransferService/push',
            data__proxy__pb2.Packet.SerializeToString,
            data__proxy__pb2.Metadata.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def pull(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/com.tsingj.me.api.networking.proxy.DataTransferService/pull',
            data__proxy__pb2.Metadata.SerializeToString,
            data__proxy__pb2.Packet.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def unaryCall(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/com.tsingj.me.api.networking.proxy.DataTransferService/unaryCall',
            data__proxy__pb2.Packet.SerializeToString,
            data__proxy__pb2.Packet.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class RouteServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.query = channel.unary_unary(
                '/com.tsingj.me.api.networking.proxy.RouteService/query',
                request_serializer=data__proxy__pb2.Topic.SerializeToString,
                response_deserializer=data__meta__pb2.Endpoint.FromString,
                )


class RouteServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def query(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RouteServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'query': grpc.unary_unary_rpc_method_handler(
                    servicer.query,
                    request_deserializer=data__proxy__pb2.Topic.FromString,
                    response_serializer=data__meta__pb2.Endpoint.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'com.tsingj.me.api.networking.proxy.RouteService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class RouteService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def query(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/com.tsingj.me.api.networking.proxy.RouteService/query',
            data__proxy__pb2.Topic.SerializeToString,
            data__meta__pb2.Endpoint.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
