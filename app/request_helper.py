import copy

from clarifai.client import ApiBadRequestError


class CuratorApiRequestHelper(object):
  """Helper to manage Curator API requests."""

  def __init__(self, collection_id=None, user_id=None):
    """Initialize for a collection.

    Args:
      collection_id: Identifier of the default collection to make requests about.
      user_id:
    """
    self.collection_id = collection_id
    self.user_id = user_id

  def base_request(self):
    request = {
      'collection_id': self.collection_id
      }
    if self.user_id:
      request['user_id'] = self.user_id
    return request

  def index_request(self):
    request = self.base_request()
    return request

  def index_request_for_put(self, settings, properties=None):
    num_docs = settings.get('max_num_docs')
    if not num_docs:
      raise ApiBadRequestError('Missing required param: settings.max_num_docs')
    collection = {
      'id': self.collection_id,
      'settings': settings
    }
    if properties:
      collection['properties'] = properties
    request = self.base_request()
    request['collection'] = collection
    return request

  def document_request(self, docid):
    request = self.base_request()
    request['document'] = {'docid': docid}
    return request

  def document_request_for_put(self, doc, options=None):
    request = self.base_request()
    if options:
      request['options'] = options
    request['document'] = doc
    return request


