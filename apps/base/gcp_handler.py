from google.cloud import pubsub_v1

project_id = "clever-seat-313815"

def PublishMessagePUBSUB(topic_id, data_str, attributes = None):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    data = data_str.encode("utf-8")
    
    future = publisher.publish(
            topic_path, data, **attributes
        )

    print(future.result())

    print(f"Published messages with custom attributes to {topic_path}.")

def RebuildModelPUBSUB(attributes):
    topic = "cloudrun_recession_api_trigger"
    PublishMessagePUBSUB(topic, "Rebuild model", attributes)

# if __name__ == '__main__':
#     PublishMessagePUBSUB('cloudrun_recession_api_trigger','Message data',{'groups':'Unemployment,Monetary Policy'})