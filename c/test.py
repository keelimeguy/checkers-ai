#! /bin/python

from structs import *
md = cdll.LoadLibrary('libtest.so')
md

md.print_board();