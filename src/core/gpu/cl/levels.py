import numpy as np

from .parameters import ctx, queue, cl

prg = cl.Program(ctx, open('src/core/gpu/cl/cl_files/apply_levels.cl').read()).build()


def set_levels(image: np.ndarray, max_v: int, min_v: int, mid_v: int, gamma: float,
               other_max_v: int, other_min_v: int) -> np.ndarray:
    if 0 in image.shape:  # noqa
        return image
    res_np = np.zeros_like(image, dtype=np.uint8)

    rd_buf = cl.Buffer(
        ctx,
        cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
        hostbuf=image
    )
    wrt_buf = cl.Buffer(
        ctx,
        cl.mem_flags.WRITE_ONLY,
        res_np.nbytes
    )

    knl = prg.apply_levels
    knl_gray = prg.apply_levels_gray
    if image.shape[2] == 3:
        knl(queue, image.shape, None, rd_buf, wrt_buf, np.int32(image.shape[1]), np.int32(min_v),
            np.int32(max_v), np.int32(mid_v), np.float32(gamma), np.int32(other_max_v), np.int32(other_min_v)).wait()
    else:
        knl_gray(queue, image.shape, None, rd_buf, wrt_buf, np.int32(image.shape[1]), np.int32(min_v),
                 np.int32(max_v), np.int32(mid_v), np.float32(gamma), np.int32(other_max_v),
                 np.int32(other_min_v)).wait()
    cl.enqueue_copy(queue, res_np, wrt_buf).wait()

    return res_np.astype(np.uint8)
