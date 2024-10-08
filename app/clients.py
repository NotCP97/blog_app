from elasticsearch import Elasticsearch

from config import REDIS_URL, ELASTICSEARCH_URL, QUEUE

from redis import Redis
from rq import Queue


class RedisHandler:
    """
    This class will handle all the redis operations
    """
    def __init__(self):
        self.redis = Redis.from_url(REDIS_URL)
        self.queue = Queue(connection=self.redis, name=QUEUE)

    def get_client(self):
        """
        return the redis client
        """
        return self.redis


    def add_job(self, func, *args, **kwargs):
        """
        This method will push data to redis queue

        :param queue: Redis queue
        :type queue: Queue
        :param func: Function to be executed
        :type func: function
        :param args: Function arguments
        :type args: tuple
        :param kwargs: Function keyword arguments
        :type kwargs: dict
        :return: Job
        :rtype: Job
        """
        return self.queue.enqueue(func, *args, **kwargs)




class ElasticsearchHandler:
    """
    This class will handle all the elasticsearch operations
    """
    def __init__(self):
        self.es = Elasticsearch([ELASTICSEARCH_URL])

    # write a method to search data in elasticsearch
    def get_results(self, index, body, size=10000) -> list:
        """
        This method will search data in elasticsearch with pagination
        
        :param index: Index name
        :type index: str
        :param body: Search query
        :type body: dict
        :param from_: Starting index for pagination
        :type from_: int
        :param size: Number of results to return
        :type size: int
        :return: Search results
        :rtype: list
        """
        search_results = self.es.search(index=index, body=body, size=size)


        return [result["_source"] for result in search_results["hits"]["hits"]]
    

    def index_doc(self, index, body, doc_id=None):
        """
        This method will index data in elasticsearch

        :param index: Index name
        :type index: str
        :param body: Data to be indexed
        :type body: dict
        :param doc_id: Document ID

        """
        if doc_id:
            return self.es.index(index=index, body=body, id=doc_id)
        self.es.index(index=index, body=body)
    
    def get_result_by_id(self, index, id):
        """
        This method will get data by ID from elasticsearch

        :param index: Index name
        :type index: str
        :param id: Document ID
        :type id: str
        :return: Document
        :rtype: dict
        """
        result =  self.es.get(index=index, id=id, ignore=404)

        if result.get("found"):
            return result["_source"]
        else:
            return {}
        
    def get_results_with_pagination(self, index, body, from_=0, size=10):
        """
        This method will search data in elasticsearch with pagination

        :param index: Index name
        :type index: str
        :param body: Search query
        :type body: dict
        :param from_: Starting index for pagination
        :type from_: int
        :param size: Number of results to return
        :type size: int
        :return: Search results
        :rtype: dict
        """
        body.update({"from": from_, "size": size})
        search_results = self.es.search(index=index, body=body)

        start = from_
        end = from_ + size if from_ + size < search_results["hits"]["total"]["value"] else from_+search_results["hits"]["total"]["value"]

        return {
            "data": [result["_source"] for result in search_results["hits"]["hits"]],
            "total_results": search_results["hits"]["total"]["value"],
            "from": start,
            "to": end
        }
    
    def update_doc_by_id(self, index, body, doc_id):
        """
        This method will update data in elasticsearch

        :param index: Index name
        :type index: str
        :param body: Data to be updated
        :type body: dict
        :param doc_id: Document ID
        """
        return self.es.update(index=index, body=body, id=doc_id)

    # write a method to close the elasticsearch connection
    def close(self):
        self.es.close()