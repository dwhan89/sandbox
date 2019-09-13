import configparser as ConfigParser
import argparse
import os

argparser = argparse.ArgumentParser(
        prog='sandboxs',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        conflict_handler='resolve'
        )

configparser = ConfigParser.ConfigParser()
configparser.optionxform = str

def load_config(config_file):
    configparser.read(config_file)
