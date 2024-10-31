# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 20:20:26 2024

@author: MottaRS
"""

from transformers import pipeline


#$$$$$$$$$$$$$$$$$$$$$$
# TEST
import torch
print(torch.__version__)
import tensorflow
print(tensorflow.__version__)

from transformers import is_torch_available
from transformers import is_tf_available
print(is_torch_available())
print(is_tf_available())
#########################


pipe = pipeline("text-classification")
text_gen = pipeline("text-generation", model="distilgpt2")
ner = pipeline("ner", grouped_entities=True)

# feature-extraction : get the vector representation of a text.
# fill-mask: fill in a blank in a text.
# ner: Named Entity Recognition.
# question-answering
# sentiment-analysis
# summarization
# text-generation
# translation
# zero-shot-classification allows us to classify text into categories that were not part of the original data used to train the model. (more on that at the end).


text = 'Ficus is a startup created by members of the PADMEC research group from UFPE after about 20 years of research projects in the pipeline integrity assessment field. Its main objective is to bring advanced procedures indicated by the academy to the industry. Thus, a computational tool was developed with a minimal user interface, which aims to automatically evaluate anomalies obtained by line inspections (ILI) of pipelines, including future assessment. The tool uses multilevel advanced evaluation, where methods of different levels of complexity and computational effort are ordered and can be easily accessed. The options for pipeline metal loss assessment are: traditional levels 1 and 2 methods, quantitative assessment based on risk, through reliability analysis, mechanical simulation by FEA considering different geometry data and also includes AI assessment via an artificial neural network based on a large in-house generated database. It has also an advanced mapping strategy to compare ILI spreadsheets of different ages, obtain corrosion growth rates and automatically create maintenance schedule reports. Our mission at FICUS is to revolutionize pipeline safety assessments by leveraging modern tools to provide simple, intuitive, and automated solutions. We are committed to helping pipeline operators ensure the integrity and safety of their assets,, reducing costs by up to 25% and avoiding accidents, protecting the environment, and safeguarding communities'

ner(text)
out = pipe(text)

complete = text_gen(text, max_length = 300)
