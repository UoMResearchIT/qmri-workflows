'''
_summary_
'''
from QbiPy.tools.runner import QbiRunner, bool_option

from QbiMadym import madym_T1

#---------------------------------------------------------
def add_options(runner):
    parser = runner.parser
    parser.add('--madym_config_file', type=str, nargs='?', required = False,
        help='')

#---------------------------------------------------------
def run_DCE_VFA_mapping(
        data_dir:str = None,
        madym_config_file:str = None
):
    print('Running run_DCE_VFA_mapping')
    madym_T1.run(
        working_directory=data_dir,
        config_file=madym_config_file
    )
#---------------------------------------------------------
def main(args = None):
    runner = QbiRunner()
    add_options(runner)
    runner.run(run_DCE_VFA_mapping, args)

#----------------------------------------------------------
if __name__ == '__main__':
    main()
