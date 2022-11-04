import os
import pyopencl as cl  # noqa

from src.core.log import print_d

os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'


def print_all_device_info():
    print_d('\n' + '=' * 60 + '\nOpenCL Platforms and Devices')
    for platform in cl.get_platforms():
        print('=' * 60)
        print(f'Platform - Name:  {platform.name}')
        print(f'Platform - Vendor:  {platform.vendor}')
        print(f'Platform - Version:  {platform.version}')
        print(f'Platform - Profile:  {platform.profile}')

        for device in platform.get_devices():
            print('    ' + '-' * 56)
            print(f'    Device - Name:  {device.name}')
            print(f'    Device - Type:  {cl.device_type.to_string(device.type)}')
            print(f'    Device - Max Clock Speed:  {device.max_clock_frequency} Mhz')
            print(f'    Device - Compute Units:  {device.max_compute_units}')
            print(f'    Device - Local Memory:  {device.local_mem_size/1024.0:.0f} KB')
            print(f'    Device - Constant Memory:  {device.max_constant_buffer_size/1024.0:.0f} KB')
            print(f'    Device - Global Memory: {device.global_mem_size/1073741824.0:.0f} GB')
            print(f'    Device - Max Buffer/Image Size: {device.max_mem_alloc_size/1048576.0:.0f} MB')
            print(f'    Device - Max Work Group Size: {device.max_work_group_size:.0f}')
    print_d('\n')
