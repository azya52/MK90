import sys
import argparse
import cv2
from LZ77 import LZ77Compressor

SCR_WIDTH = 120
SCR_HEIGHT = 64

DFLT_TRESH = 127
DFLT_BLOCK_SIZE = 21
DFLT_ERROR_DIV = 32
DFLT_MEAN_SUB = 5
DFLT_CLIP_LIM = 1
DFLT_TILE_W = 8
DFLT_TILE_H = 8

INTER = {
    "NEAREST": cv2.INTER_NEAREST,
    "LINEAR": cv2.INTER_LINEAR,
    "AREA": cv2.INTER_AREA,
    "CUBIC": cv2.INTER_CUBIC,
    "LANCZOS4": cv2.INTER_LANCZOS4,
}

def resize_image(img, screen_w, screen_h, interp, crop, aspect_ratio):   
    crop += [0, 0, 0]
    img = img[crop[0]:img.shape[0] - crop[1], crop[2]:img.shape[1] - crop[3]]
    h, w = img.shape[:2]
    
    if aspect_ratio == 'FIT':
        ratio = max(screen_w / w, screen_h / h)
    else:
        ratio = min(screen_w / w, screen_h / h)
    
    img = cv2.resize(img, (0, 0), fx = ratio, fy = ratio, interpolation = INTER[interp]) 

    if aspect_ratio == 'FIT':
       h, w = img.shape[:2]
       crop_x = (w - screen_w) // 2
       crop_y = (h - screen_h) // 2
       img = img[crop_y:crop_y + screen_h, crop_x:crop_x + screen_w]
    
    return img
   
def fixFrameSize(img, target_w, target_h):
    h, w = img.shape[:2]
    if h < target_h or w < target_w:
        crop_x = (target_w - w) // 2
        crop_y = (target_h - h) // 2
        img = cv2.copyMakeBorder(img, crop_y, target_h - crop_y - h, crop_x, target_w - crop_x - w, cv2.BORDER_CONSTANT, value = 255)
    return img
        
def get_bin(img):
    h, w = img.shape[:2]
    outfile = bytearray()
    for y in range(h):
        for x in range(0, w, 8):
            byte = 0
            for i in range(8):
                byte |= ~(img[y, x + i]) & (0x80 >> i)
            outfile.append(byte & 0xFF)
    return outfile

def get_mac(data, name):
    i = 0
    outfile = "\nframe" + name + ":"
    while i < len(data):
        if i % 20 == 0:
            outfile += "\n    .byte "
        outfile += str(data[i]) + ", "
        i += 1
    outfile += "\n"
    return outfile
       
def dithering(img, error_div):
    h, w = img.shape[:2]
    for y in range(h):
        for x in range(w):
            old = img[y, x]
            new = (old > 127) * 255 
            img[y, x] = new
            error = (old - new) / error_div
            if x + 1 < w: 
                img[y, x + 1] = max(min(img[y, x + 1] + error * 7, 255), 0)
            if y + 1 < h: 
                img[y + 1, x] = max(min(img[y + 1, x] + error * 5, 255), 0)
            if y + 1 < h and x > 0: 
                img[y + 1, x - 1] = max(min(img[y + 1, x - 1] + error * 3, 255), 0)
            if y < h - 1 and x < w - 1: 
                img[y + 1, x + 1] = max(min(img[y + 1, x + 1] + error, 255), 0)
    return img
        
def convert(args, compressor):           
    vidcap = cv2.VideoCapture(args.path_in)
    
    if not vidcap.isOpened():
        print("Video file cannot be opened")
        return
    
    fps = vidcap.get(cv2.CAP_PROP_FPS)
        
    if args.fps == None:
        args.fps = 512 / round(512 / fps)
    elif args.fps == 0:
        args.fps = fps
    elif args.fps:
        args.fps = 512 / round(512 / args.fps)
        
    fps_counter = int(512 / args.fps)
    fps_mul = fps / args.fps
        
    print("fps:", fps, '->', args.fps)
    
    last_frame = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT) - 1)
    start_frame = 0
    if args.e:
        last_frame = min(last_frame, args.e)
    if args.s:
        start_frame = min(last_frame, args.s)
            
    tresh = args.tresh_opt[0] if args.tresh_opt else DFLT_TRESH
    block_size = args.tresh_opt[0] | 0x1 if args.tresh_opt else DFLT_BLOCK_SIZE
    error_div = args.tresh_opt[0] if args.tresh_opt else DFLT_ERROR_DIV
    mean_subtract = args.tresh_opt[1] if args.tresh_opt and len(args.tresh_opt) > 1 else DFLT_MEAN_SUB
    
    args.ahe += [DFLT_TILE_W, DFLT_TILE_H] if args.ahe else [DFLT_CLIP_LIM, DFLT_TILE_W, DFLT_TILE_H]
        
    max_len = 0
    max_num = 0
    sum_len = 0       
    frame_count = 0
    new_frame = start_frame
    
    out_bin = bytearray()
    out_mac = ''
    
    while new_frame <= last_frame:
        vidcap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
        success, frame = vidcap.read()
        
        if not success:
            print("Frame read error\n")
            break
        
        frame = resize_image(frame, SCR_WIDTH, SCR_HEIGHT, args.interp, args.crop, args.ar)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if args.ahe:
            clahe = cv2.createCLAHE(clipLimit=float(args.ahe[0]), tileGridSize=(int(args.ahe[1]), int(args.ahe[2])))
            frame = clahe.apply(frame)
        
        if args.he:
            frame = cv2.equalizeHist(frame)

        if args.tresh == 'BINARY':
            ret, frame = cv2.threshold(frame, tresh, 255, cv2.THRESH_BINARY)
        elif args.tresh == 'OTSU':
            ret, frame = cv2.threshold(frame, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        elif args.tresh == 'TRIANGLE':
            ret, frame = cv2.threshold(frame, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_TRIANGLE)
        elif args.tresh == 'MEAN':
            frame = cv2.adaptiveThreshold(frame, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size, mean_subtract)
        elif args.tresh == 'GAUSSIAN':
            frame = cv2.adaptiveThreshold(frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, mean_subtract)
        elif args.tresh == 'DITHER':
            frame = dithering(frame, error_div)
                
        frame = fixFrameSize(frame, SCR_WIDTH, SCR_HEIGHT)
        
        data = compressor.compress(get_bin(frame));
        
        out_bin += data;
        if args.mac:
            out_mac += get_mac(data, str(new_frame))
        
        frame_len = len(data)
        if max_len < frame_len:
            max_len = frame_len
            max_num = new_frame
        sum_len += frame_len
    
        prc = round((new_frame - start_frame + 1) / (last_frame - start_frame + 1) * 100)
        print(prc, "% (", new_frame, "), size: ", sum_len, '(', frame_len, ') max: ', max_len, '(#', max_num, ')', sep='', end = '  \r')
        frame_count += 1
        new_frame = start_frame + round(frame_count * fps_mul)
        
    with open(args.path_out, 'wb') as bin_f:
        with open("videoPlayer%s.bin" % ("SMP" if sum_len < 9216 else ""), "rb") as f:
            bin_f.write(f.read())
        bin_f.write(bytes([frame_count & 0xFF, (frame_count >> 8) & 0xFF]))
        bin_f.write(bytes([fps_counter & 0xFF, (fps_counter >> 8) & 0xFF]))
        bin_f.write(out_bin);
    if args.mac:
        with open(args.path_out + ".mac", 'w') as mac_f:
            with open("videoPlayer%s.mac" % ("SMP" if sum_len < 9216 else ""), "r") as f:
                mac_f.write(f.read())
            mac_f.write('\n    .word %d' % frame_count)
            mac_f.write('\n    .word %d\n' % fps_counter)
            mac_f.write(out_mac)


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument("path_in", 
            help="path to source video"
        )
    parser.add_argument("path_out", 
            help="path to result files (.bin or/and .mac)"
        )
    parser.add_argument("-s", 
            type=int,
            help="first frame number"
        )
    parser.add_argument("-e", 
            type=int,
            help="last frame number"
        )
    parser.add_argument("-fps",
            type=float,
            help="change fps, 0 - save original"
        )
    parser.add_argument("-he",
            action='store_const',
            const=True,
            help="histogram equalization"
        )
    parser.add_argument("-ahe",
            nargs='*',
            default=[1.0],
            type=float,
            help="adaptive histogram equalization (clipLimit (1.0), tileGridWidth (8), tileGridHeight (8)"
        )
    parser.add_argument("-ar",
            choices=['KEEP', 'FIT'],
            default='FIT',
            help="aspect ratio, keep original or fit to screen (default)"
        )
    parser.add_argument("-c",
            type=int,
            dest="crop",
            nargs='+',
            default = [0],
            help="cropping the original frame in pixels (top, bottom, left, righ)"
        )
    parser.add_argument("-mac",
            action='store_const',
            const=True,
            help="provide the result as source code"
        )
    parser.add_argument('-i',
            dest="interp",
            choices=['NEAREST', 'LINEAR', 'AREA', 'CUBIC', 'LANCZOS4'],
            default = "AREA",
            help='interpolation method for frame scaling'
        )
    parser.add_argument('-t',
            dest="tresh",
            choices=['BINARY', 'OTSU', 'TRIANGLE', 'MEAN', 'GAUSSIAN', 'DITHER'],
            default = "OTSU",
            help='type of converting a grayscale image to binary'
        )
    parser.add_argument('-to',
            type=int,
            dest="tresh_opt",
            nargs='+',
            help='options for the selected converting type: for BINARY - just threshold (0 - 255), default - 127; for MEAN or GAUSSIAN - block size (3, 5, 7 ...) and constant subtracted from the mean (integer) default - 21 5; for DITHER - error divisor (positive) default - 32'
        )
            
    compressor = LZ77Compressor(16, 17)
    convert(parser.parse_args(), compressor)