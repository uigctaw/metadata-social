#!/usr/bin/python3

import os
import pathlib
import subprocess
import yaml

THIS_FOLDER = pathlib.Path().joinpath(__file__).parent


if __name__ == '__main__':
    os.chdir(THIS_FOLDER)
    result = subprocess.run(
            ['terraform', 'output', '-json'],
            capture_output=True,
            )
    if result.stderr:
        raise RuntimeError(result.stderr)
    else:
        output = yaml.safe_load(result.stdout)
        name_ips_tuples = output['public_ips']['value']
        for name, ip in name_ips_tuples:
            print(name, ip)
