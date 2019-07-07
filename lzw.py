import numpy as np
from PIL import Image

#### FUNCTIONS ####

#Creates an input array for the compress function
#zero fills numbers to 3 digits and converts numbers to a joined string
def create_input(array):
    arr = []
    for i in array:
        arr.append(str(i))

    for i in range(len(arr)):
        arr[i] = arr[i].zfill(3)

    arr = ''.join(arr)
    return arr

#Converts a dictionary of numbers into binary values
def to_bin_dict(dictionary):
    bin_dict = dictionary.copy()
    i = 0
    for k in dictionary.keys():
        bin_dict[k] = format(i, 'b')
        i+=1
    return bin_dict

#Creates a dictionary of string numbers 0-255 in string format(keys and values are the same)
def create__rgb_dictionary():
    dictionary = {}
    for i in range(0,256):
        dictionary[str(i)] = str(i)
    return dictionary

#Returns number of bits in array
def num_bits(arr, bin_dict):
    num_bits = 0
    bit_string = ''
    for s in arr:
        if s in bin_dict.keys():
           # print(bin_dict[s])
            num_bits += len(bin_dict[s])
        else:
           # print(format(s, 'b'))
            num_bits +=  len(format(s, 'b'))
    return num_bits

#Creates dictionary of digits 0-9 in string format(keys and values are same)
def create_digit_dictionary():
    dictionary = {}
    for i in range(0,11):
        dictionary[str(i)] = str(i)
    return dictionary

#LZW compression
def compress(uncompressed):
    dict_size = 10
    dictionary = {chr(i): chr(i) for i in range(48,48+dict_size)}
   # dict_size = 256
   # dictionary = create_dictionary()
    dictionary = create_digit_dictionary()
   
    w = ''
    result = []
    for c in uncompressed:
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            result.append(dictionary[w])
            dictionary[wc] = dict_size
            dict_size += 1
            w = c
            
    if w:
        result.append(dictionary[w])

   # print(dictionary)
    return result

#LZW decompression
def decompress(compressed):
    dict_size = 10
   # dictionary = {chr(i): chr(i) for i in range(48,48+dict_size)}
   # dict_size = 256
    dictionary = create_digit_dictionary()

    w = compressed.pop(0)
    result = w
    
    for k in compressed:
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + w[0]
        else:
            raise ValueError('Bad compressed k: %s' % k)
        result+=entry

        dictionary[dict_size] = w + entry[0]
        dict_size += 1
        w = entry
    print('dictionary size: {}'.format(len(dictionary)))
    return result


###############################################
im = Image.open('frame.bmp')
imarray = np.asarray(im)
#Split image to r,g,b arrays and flatten
im_r = imarray[:,:,0]
im_r = im_r.flatten()
im_g = imarray[:,:,1]
im_g = im_g.flatten()
im_b = imarray[:,:,2]
im_b = im_b.flatten()

quantize50 = [[16,11,10,16,24,40,51,61],
              [12,12,14,19,26,58,60,55],
              [14,13,16,24,40,57,69,56],
              [14,17,22,29,51,87,80,62],
              [18,22,37,56,68,109,103,77],
              [24,35,55,64,81,104,116,92],
              [49,64,78,87,103,121,120,101],
              [72,92,95,98,112,100,103,99]]
quantize50 = np.asarray(quantize50).flatten(quantize50)
quantize50 = quantize50.tolist()
#Create r,g,b inputs
im_r = create_input(im_r)
im_g = create_input(im_g)
im_b = create_input(im_b)
print(im_r[0:100])
dictionary = create_digit_dictionary()


compress_r  = compress(im_r)
decompress_r = decompress(compress_r)
compress_g  = compress(im_g)
decompress_g = decompress(compress_g)
compress_b  = compress(im_b)
decompress_b = decompress(compress_b)




bin_dictionary = to_bin_dict(dictionary)



print('Num bits origial: {}'.format(num_bits(im_r, bin_dictionary)+num_bits(im_g, bin_dictionary)+num_bits(im_b, bin_dictionary)))
print('Num bits compressed: {}'.format(num_bits(compress_r, bin_dictionary)+num_bits(compress_g, bin_dictionary)+num_bits(compress_b, bin_dictionary)))
print('Compression ratio: {}'.format((num_bits(compress_r, bin_dictionary)+num_bits(compress_g, bin_dictionary)+num_bits(compress_b, bin_dictionary))/(num_bits(im_r, bin_dictionary)+num_bits(im_g, bin_dictionary)+num_bits(im_b, bin_dictionary))))


#Combine decompressed rgb arrays to image
combined_r = ''.join(decompress_r)
new=[]
for i in range(0, len(combined_r), 3):
    new.append(combined_r[i:i+3])
new = np.array(new)
new = new.reshape((1080,1920))
new_r = new

combined_g = ''.join(decompress_g)
new=[]
for i in range(0, len(combined_g), 3):
    new.append(combined_g[i:i+3])
new = np.array(new)
new = new.reshape((1080,1920))
new_g = new

combined_b = ''.join(decompress_b)
new=[]
for i in range(0, len(combined_b), 3):
    new.append(combined_b[i:i+3])
new = np.array(new)
new = new.reshape((1080,1920))
new_b = new


new_im = np.dstack((new_r,new_g,new_b))
Image.fromarray(np.uint8(new_im)).show()
