import pyopencl as cl

platforms = cl.get_platforms()
platform = platforms[0]
devices = platform.get_devices(cl.device_type.GPU)

device: cl._cl.Device = devices[0]  # noqa

ctx = cl.Context([device])
queue = cl.CommandQueue(ctx)
