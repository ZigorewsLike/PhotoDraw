__kernel void apply_bright_and_contrast(
    global uchar* a, global uchar* b, const int height, const float bright, const int contrast)
{
    int y = get_global_id(0);
    int x = get_global_id(1);
    int z = get_global_id(2);

    float res = a[y*height*3 + x*3 + z] * bright + (contrast - 255);

    b[y*height*3 + x*3 + z] = res > 255.0 ? 255.0 : (res < 0 ? 0 : res);
}

__kernel void apply_bright_and_contrast_gray(
    global uchar* a, global uchar* b, const int height, const float bright, const int contrast)
{
    int y = get_global_id(0);
    int x = get_global_id(1);

    float res = a[y*height + x] * bright + (contrast - 255);

    b[y*height + x] = res > 255.0 ? 255.0 : (res < 0 ? 0 : res);
}