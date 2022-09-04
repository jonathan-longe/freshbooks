import json
import logging


def load_json_into_dict(file_name) -> dict:
    with open(file_name, 'r') as f:
        data = f.read()
    return json.loads(data)


def execute_pipeline(functions: list, **args):
    """
    Recursive function that calls each node in the list.
    Each node has a "try" function that is executed first. If the try
    function returns True, the next node in the list is returned.  If the
    try function returns False, the node's "fail" list is executed in the
    same way.

    example = dict({
            "rules": [
                {
                    "pass": success1,
                    "fail": [
                        {
                            "pass": failure1,
                            "fail": []
                        }
                    ],
                },
            ]
        })

    The middleware is called like this: middle_logic(example['rules'])
    """
    if functions:
        try_fail_node = functions.pop(0)
        logging.debug('calling try function: ' + try_fail_node['try'].__name__)
        flag, args = try_fail_node['try'](**args)
        logging.debug("result from {} is {}".format(try_fail_node['try'].__name__, flag))
        if flag:
            args = execute_pipeline(functions, **args)
        else:
            logging.debug('calling try function: ' + try_fail_node['try'].__name__)
            args = execute_pipeline(try_fail_node['fail'], **args)
    return args

