'''
_summary_
'''
from QbiPy.tools.runner import QbiRunner, bool_option

#---------------------------------------------------------
def add_options(runner):
    pass

#---------------------------------------------------------
def run_OE_DCE_hypoxia_mapping():
    print('Running run_OE_DCE_hypoxia_mapping')

#---------------------------------------------------------
def main(args = None):
    runner = QbiRunner()
    add_options(runner)
    runner.run(run_OE_DCE_hypoxia_mapping, args)

#----------------------------------------------------------
if __name__ == '__main__':
    main()
