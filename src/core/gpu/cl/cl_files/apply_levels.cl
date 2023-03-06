__kernel void apply_levels(
    global uchar* a, global uchar* b, const int height, const int min_v, const int max_v, const int mid_tone,
    const float gamma, const int other_max_v, const int other_min_v)
{
    int y = get_global_id(0);
    int x = get_global_id(1);
    int z = get_global_id(2);

    float res = a[y*height*3 + x*3 + z] - min_v;
    res = 255.0 * (res < 0.0 ? 0.0 : res / (max_v - min_v));
    if (mid_tone != 128){
        res = 255.0 * pow((res / 255), gamma);
    }
    res = (res / 255.0) * (other_max_v - other_min_v) + other_min_v;

    b[y*height*3 + x*3 + z] = res > 255.0 ? 255.0 : (res < 0 ? 0 : res);
}

__kernel void apply_levels_gray(
    global uchar* a, global uchar* b, const int height, const int min_v, const int max_v, const int mid_tone,
    const float gamma, const int other_max_v, const int other_min_v)
{
    int y = get_global_id(0);
    int x = get_global_id(1);

    float res = a[y*height + x] - min_v;
    res = 255.0 * (res < 0.0 ? 0.0 : res / (max_v - min_v));
    if (mid_tone != 128){
        res = 255.0 * pow((res / 255), gamma);
    }
    res = (res / 255.0) * (other_max_v - other_min_v) + other_min_v;

    b[y*height + x] = res > 255.0 ? 255.0 : (res < 0 ? 0 : res);
}