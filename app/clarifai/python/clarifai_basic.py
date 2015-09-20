# -*- coding: utf-8 -*-
"""Simple Clarifai Custom Model Training API Wrapper

This module provides a simple wrapper around the Clarifai API in order to
make it very easy to train your first custom model and then use it for
predictions.

"""
from __future__ import absolute_import

import json
import re
import uuid

from clarifai.client import ClarifaiApi, ApiError, ApiBadRequestError
from clarifai.client.client import API_VERSION
from request_helper import CuratorApiRequestHelper


def request(name, method='GET'):
  def decorator(get_body):
    def process_request(self, *args, **kwargs):
      argsnames = get_body.func_code.co_varnames[1:len(args)+1]
      arguments = dict(kwargs)
      arguments.update(zip(argsnames, args))
      url = self._url_for_op(name).format(**arguments)
      body = get_body(self, *args, **kwargs)
      kwargs = {'method': method}
      if body is not None:
        kwargs['data'] = body
      raw_response = self._get_raw_response(self._get_json_headers,
                                            self._get_json_response,
                                            url,
                                            kwargs)
      return self.check_status(raw_response)
    return process_request
  return decorator


def drop(dictionary, value=None):
  """drops items with given value"""
  return {k: v for k, v in dictionary.iteritems() if v != value}


class CuratorApiError(ApiError):
  def __init__(self, status):
    self.status = status

  def __str__(self):
    try:
      return '%s: %s' % (self.status['status'], self.status['message'])
    except:
      return 'Malformed API response, no status'


class CuratorApiClient(ClarifaiApi):
  def __init__(self, app_id='sKU_ax7BliXvEqfsutM5enhvkZ0ZSnWcnhEOuXxR', app_secret='x-Q4HeMzasp8p153TBwgBmk0PD5QgFWnKndvtNGr'):
    self._collection_id = 'hackmit'
    self.request_helper = CuratorApiRequestHelper(collection_id=self._collection_id)
    super(CuratorApiClient, self).__init__(app_id=app_id,
                                           app_secret=app_secret,
                                           base_url='https://api-alpha.clarifai.com',
                                           wait_on_throttle=True)

    self.add_url('document', 'curator/collections/%s/documents' % self._collection_id)
    self.add_url('collections', 'curator/collections')
    self.add_url('concepts', 'curator/concepts')
    self.add_url('concept', 'curator/concepts/{namespace}/{cname}')
    self.add_url('concept_predict', 'curator/concepts/{namespace}/{cname}/predict')
    self.add_url('concept_train', 'curator/concepts/{namespace}/{cname}/train')
    self.add_url('model_predict', 'curator/models/{name}/predict')

  def add_url(self, op, path):
    self._urls[op] = '/'.join([self._base_url, API_VERSION, path])

  def check_status(self, raw_response):
    response = json.loads(raw_response)
    try:
      ok = (response['status']['status'] == 'OK')
    except:
      raise ApiError('Malformed API response.')
    if not ok:
      raise CuratorApiError(response['status'])
    return response

  def add_document(self, doc, options=None):
    docid = doc.get('docid')
    if not docid:
      raise ApiBadRequestError('Missing required param: doc.docid')

    url = self._url_for_op('document')
    request_data = self.request_helper.document_request_for_put(doc, options=options)
    kwargs = {
      'data': request_data,
      'method': 'POST'
    }
    raw_response = self._get_raw_response(self._get_json_headers,
                                          self._get_json_response,
                                          url,
                                          kwargs)
    return self.check_status(raw_response)

  def create_collection(self, settings, properties=None):
    url = self._url_for_op('collections')
    request_data = self.request_helper.index_request_for_put(settings, properties=properties)
    kwargs = {
      'data': request_data,
      'method': 'POST'
    }
    raw_response = self._get_raw_response(self._get_json_headers,
                                          self._get_json_response,
                                          url, kwargs)
    return self.check_status(raw_response)

  @request('concepts', method='POST')
  def create_concept(self, namespace, cname, description=None, example=None, **kwargs):
    """
    Create a new concept

    Args:
      namespace: namespace for the concept
      cname: name of the concept
      description (Optional): description of the concept
      example (Optional): image url with an example of the concept
    """
    return drop({
      'namespace': namespace,
      'cname': cname,
      'description': description,
      'example': example
    }, value=None)

  @request('concept_train', method='POST')
  def train_concept(self, namespace, cname, collection_ids=None):
    if not re.match(r'^[A-Za-z0-09-_]+$', cname):
      raise ApiError('Concept name cannot contain whitespace or punctuation: "%s"' % cname)
    if collection_ids:
      return {'collection_ids': collection_ids}

  @request('concept_predict', method='POST')
  def predict_concept(self, namespace, cname, urls=None, documents=None):
    '''
    Predict scores for a single concept, specified by namespace and cname.
    '''
    return drop({
      'urls': urls,
      'documents': documents
    }, value=None)

  @request('model_predict', method='POST')
  def predict_model(self, name, urls=None, documents=None):
    '''
    Predict tags for the urls.

    Args:
      model_name:
        Namespace or model name. This will return predictions for all concepts
        in the model.  If a namespace, uses all concepts in the namespace.
      urls:
        List of urls to find tag predictions.
    '''
    return drop({
      'urls': urls,
      'documents': documents
    }, value=None)


class ClarifaiCustomModel(CuratorApiClient):
  """
  The ClarifaiCustomModel class provides a simple interface to the Clarifai custom training API
  """
  def __init__(self, app_id=None, app_secret=None):
    super(ClarifaiCustomModel, self).__init__(app_id=app_id, app_secret=app_secret)
    self._namespace = 'hackathon'
    try:
      self.create_collection({'max_num_docs': 1000})
    except:
      pass

  def positive(self, url, concept):
    doc = self._format_doc(url, concept, 1)
    self.add_document(doc)

  def negative(self, url, concept):
    doc = self._format_doc(url, concept, -1)
    self.add_document(doc)

  def train(self, concept):
    self.train_concept(namespace=self._namespace, cname=concept)

  def predict(self, url, concept):
    return self.predict_concept(namespace=self._namespace, cname=concept, urls=[url])

  def predict_all(self, url):
    return self.predict_model(name=self._namespace, urls=[url])

  def _format_doc(self, url, concept, score):
    return {
      "docid": str(uuid.uuid4()),
      "media_refs": [{
        "url": url,
        "media_type": "image"
      }],
      "annotation_sets": [{
        "namespace": self._namespace,
        "annotations": [{
          "score": score,
          "tag": {
            "cname": concept
          }
        }]
      }],
      'options': {
        'want_doc_response': True,
        'recognition_options': {
          'model': 'general-v1.2'
        }
      }
    }
