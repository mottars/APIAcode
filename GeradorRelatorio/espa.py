#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 17:17:05 2023

@author: pimentel
"""

arq = open('GeradorRelatorioAutomaticoPDFicus-saida.py', 'r')
arq2 = open('GeradorRelatorioAutomaticoPDFicus-saida2.py', 'w')
for i in arq:
    arq2.write(i.replace('\t', '\t'))
arq2.close()