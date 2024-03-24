#
#  Created by yuyunfu
#   2022/9/28 
#
import time

import pulsar

from common.federation.pulsar._mq_channel import MQChannel


class Test:
    def get_channel(self, host, port, mng_port, tenant, namespace, send_top, recv_top, party_id, role, conf=None):
        return MQChannel(
            host=host,
            port=port,
            mng_port=mng_port,
            pulsar_tenant=tenant,
            pulsar_namespace=namespace,
            pulsar_send_topic=send_top,
            pulsar_receive_topic=recv_top,
            party_id=party_id,
            role=role,
            credential=None,
            extra_args=conf,
        )
    
    def receive_obj(self, channel_info, name, tag):
        party_id = channel_info._party_id
        role = channel_info._role
        
        while True:
            message = channel_info.consume()
            # return None indicates the client is closed
            body = message.data()
            print(body)
            properties = message.properties()
    
    def send_obj(self, name, tag, data, channel_infos):
        for info in channel_infos:
            # selfmade properties
            properties = {
                "content_type": "text/plain",
                "app_id": info.party_id,
                "message_id": name,
                "correlation_id": tag,
            }
            info.basic_publish(body=data, properties=properties)


if __name__ == '__main__':
    # t = Test()
    # c = t.get_channel("192.168.200.88", "26650", "28080", "tenant11", "namespace", "123^opic_send1", "123^topic_recv1", "123", "guest", {})
    #
    # pulsar_manager = PulsarManager(
    #     host="192.168.200.88", port="28080", runtime_config={"topic_ttl": 5, "cluster": "standalone","cores_per_node": 20,
    #         "nodes": 1}
    # )
    #
    # # init tenant
    # tenant_info = pulsar_manager.get_tenant(tenant="tenant11").json()
    # if tenant_info.get("allowedClusters") is None:
    #     pulsar_manager.create_tenant(
    #         tenant="tenant11", admins=[], clusters=["standalone"])
    #
    # t.send_obj("afafsaf", "fsaf","1234567890", [c])
    # #t.receive_obj(c, "afafsaf", "fsaf")
    
    client = pulsar.Client('pulsar://192.168.200.88:26650')
    produce = client.create_producer('test_topic')

    # for i in range(10):
    #     produce.send(("hello_tesst-%d"%i).encode('utf-8'))
    #     time.sleep(1)
    # client.close()

    consumer = client.subscribe('test_topic', subscription_name='my-sub')
    #while True:
    msg = consumer.receive()
    print("Received message: '%s'" % msg.data())
    consumer.acknowledge(msg.message_id())
    time.sleep(0.1)
    client.close()
