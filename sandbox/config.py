import configparser as ConfigParser
import argparse

argparser = argparse.ArgumentParser(
        prog='sandbox',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        conflict_handler='resolve'
        )

configparser = ConfigParser.ConfigParser()
configparser.optionxform = str

def load_config(config_file):
    configparser.read(config_file)
