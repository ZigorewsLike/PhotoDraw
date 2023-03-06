import numpy as np

from .parameters import ctx, queue, cl

prg = cl.Program(ctx, open('src/core/gpu/cl/cl_files/apply_bright_and_contrast.cl').read()).build()


def set_bright_contrast(image: np.ndarray, bright: float, contrast: float) -> np.ndarray:
    if 0 in image.shape:   # noqa
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

    knl = prg.apply_bright_and_contrast
    knl_gray = prg.apply_bright_and_contrast_gray
    if image.ndim == 3:
        knl(queue, image.shape, None, rd_buf, wrt_buf, np.int32(image.shape[1]), np.float32(bright),
            np.int32(contrast)).wait()
    else:
        knl_gray(queue, image.shape, None, rd_buf, wrt_buf, np.int32(image.shape[1]), np.float32(bright),
                 np.int32(contrast)).wait()
    cl.enqueue_copy(queue, res_np, wrt_buf).wait()

    return res_np.astype(np.uint8)
