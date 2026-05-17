from PIL import Image, ImageSequence#Image processing and sequencing from gif to bmp
from pathlib import Path#To effectively store the generated arrays ig
import argparse#Module for commnd line arguments to make it work in terminal


def bytes_to_C_array(data,var_name,per_line=12):
    '''
This function will basically converts Python byte data into the C style array we need
for our SH110X whatever OLED displays
data-the expected python byte object after parsing each frame of gif
var_name-name of the array(frame1,frame2,etc)
per_line-no. of characters per line for readability(if you want it)
'''
    hex_bytes=[f"0x{b:02X}" for b in data]#loops over every byte to turn it into C hex string
    lines=[]
    for i in range(0,len(hex_bytes),per_line):
        lines.append("    "+", ".join(hex_bytes[i:i+per_line]))
    body=",\n".join(lines)
    return f"static const unsigned char {var_name}[]={{\n{body}\n}};\n"

def sanitize(name):
    '''
This function exists to make the name of the C style header file that will have all our arrays contain only valid characters by converting them to _
'''
    return "".join(c if c.isalnum() or c=="_" else "_" for c in name)

#Now we can design the main function to take the GIF and process it into first Bitmap images
#And later into frame wise arrays. The earlier functions don't deal with that, they are for arranging and syntax correction


def gif_to_bmp(gif_loc,out,header="frames.h",mode="1"):
    '''
This is kind of our main function, the one that will deal with the conversion of GIF to BMP
gif_loc is the file location of the GIF File
out is the output path of the header file we will create
header is the user taken or default name of the header file that will contain arrays
mode-This will be the mode used by Pillow to convert the GIF into BMP. Since I am using the
monochrome OLED SH1106 display, I(the human programmer m8) chose to set the mode to 1 for 1 bit black and white
other modes are-
L-grayscale
RGB-3 bits per pixel for RGB
RGBA-4 bits per pixel
'''
    gif_path=Path(gif_loc)
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    #Here, we converted the address strings into Python Path objects and created the output
    #directory if it didn't exist prior
    img=Image.open(gif_path)
    frame_arrays=[]
    width,height=img.size#We are assuming that all frames are of same size and they can fit in our display
    for i,frame in enumerate(ImageSequence.Iterator(img)):
        #This was very imp as it just gave us each frame one by one to process
        frame=frame.convert(mode)
        bmp_path=out/f"frame_{i:03d}.bmp"#To make filenames like frame_000.bmp, frame_001.bmp, etc
        frame.save(bmp_path,format="BMP")
        raw=frame.tobytes()#This is the raw byte data of the frame after conversion to BMP
        var_name=f"frame_{i:03d}"#Variable name for the C array
        frame_arrays.append((var_name,raw))
    header_path=out/header
    guard=sanitize(header.upper().replace(".","_"))#To create a valid header guard name
    with open(header_path,"w",encoding="utf-8") as f:
        f.write(f"#ifndef {guard}\n#define {guard}\n\n")#Header guard start
        f.write(f"#define GIF_FRAME_COUNT {len(frame_arrays)}\n")#A Macro for frame count
        f.write(f"#define GIF_FRAME_WIDTH {width}\n")#A Macro for frame width
        f.write(f"#define GIF_FRAME_HEIGHT {height}\n")#A Macro for frame height
        for var_name,raw in frame_arrays:
            f.write(bytes_to_C_array(raw,var_name))#Writes each frame as a C array in the header file)
            f.write("\n")
        
        f.write("static const unsigned char* gif_frames[]={\n")
        for var_name,_ in frame_arrays:
            f.write(f"    {var_name},\n")#Writes an array of pointers to the frames for easy access in C}")
        f.write("};\n\n")
        f.write(f"#endif // {guard}\n")#Header guard end
        return header_path
if __name__=="__main__":
    parser=argparse.ArgumentParser(description="Convert a GIF file into BMP frames and C arrays for embedded use")
    parser.add_argument("gif_loc",help="Path to the input GIF file")
    parser.add_argument("--out",default="output_frames",help="Directory to save the output header file and BMP frames")
    parser.add_argument("--header",default="frames.h",help="Name of the output header file (default: frames.h)")
    parser.add_argument("--mode",default="1",choices=["1","L","RGB","RGBA"],help="Color mode for conversion (default: 1 for monochrome)")
    args=parser.parse_args()
    header_path=gif_to_bmp(args.gif_loc,args.out,args.header,args.mode)
    print(f"Conversion complete! Header file saved at: {header_path}")

    
    
