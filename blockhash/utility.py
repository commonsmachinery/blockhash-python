def normalize_image(im):
    # convert indexed/grayscale images to RGB
    if im.mode == '1' or im.mode == 'L' or im.mode == 'P':
        return im.convert('RGB')
    elif im.mode == 'LA':
        return im.convert('RGBA')

    return im
