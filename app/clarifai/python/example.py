"""
Simple example showing Clarifai Custom Model training and prediction

This example trains a concept classifier that recognizes photos of the band Phish.
"""

from clarifai_basic import ClarifaiCustomModel


# instantiate clarifai client
clarifai = ClarifaiCustomModel()

concept_name = 'piyali'

# find some positive and negative examples
PIYALI_POSITIVES = [
  'http://anshulkgupta.com/hackmit/piyali1.png',
  'http://anshulkgupta.com/hackmit/piyali2.png',
  'http://anshulkgupta.com/hackmit/piyali3.png',
  'http://anshulkgupta.com/hackmit/piyali4.png'
]

# add the positive example images to the model
for positive_example in PIYALI_POSITIVES:
  clarifai.positive(positive_example, concept_name)


# negatives are not required but will help if you want to discriminate between similar concepts
PIYALI_NEGATIVES = [
  'http://anshulkgupta.com/hackmit/anshul1.png',
  'http://anshulkgupta.com/hackmit/anshul2.png',
  'http://anshulkgupta.com/hackmit/annie1.png',
  'http://anshulkgupta.com/hackmit/annie2.png'
]

# add the negative example images to the model
for negative_example in PIYALI_NEGATIVES:
  clarifai.negative(negative_example, concept_name)

# train the model
clarifai.train(concept_name)


PIYALI_TEST = [
  'http://anshulkgupta.com/hackmit/piyali-test1.png'
]

NOT_PIYALI = [
  'http://anshulkgupta.com/hackmit/annie-test1.png',
  'http://anshulkgupta.com/hackmit/anshul-test1.png',
  'http://anshulkgupta.com/hackmit/anshul-test2.png'
]

# If everything works correctly, the confidence that true positive images are of Phish should be
# significantly greater than 0.5, which is the same as choosing at random. The confidence that true
# negative images are Phish should be significantly less than 0.5.

# use the model to predict whether the test images are Phish or not
for test in PIYALI_TEST + NOT_PIYALI:
  result = clarifai.predict(test, concept_name)
  print result['status']['message'], "%0.3f" % result['urls'][0]['score'], result['urls'][0]['url']

# Our output is the following. Your results will vary as there are some non-deterministic elements
# of the algorithms used.
