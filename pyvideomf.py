import glob
from posixpath import splitext
import subprocess as sp
import json
#from pprint import pprint
import os

vidcodec='h264_qsv'
audiocodec='aac'
extensions = ['avi', 'mp4', 'mkv', 'wmv', 'flv', 'mov']

def procesavideo(filename):
    
    archivo, archivo_extension = os.path.splitext(filename)
    
    codificavideo=""
    codificaaudio=""
    
    out = sp.run(['ffprobe','-of','json','-show_entries', 'format:stream', filename],\
                stdout=sp.PIPE, stderr=sp.PIPE, universal_newlines=True)
    results = json.loads(out.stdout)
    
    print("----------------------",filename)
    for stream in results['streams']:
        if (stream['codec_type']=='video'):
            ancho=int(stream['coded_width'])
            alto=int(stream['coded_height'])
            bitrate=int(stream['bit_rate'])
            fps=int(eval(stream['avg_frame_rate']))
            codec=stream['codec_name']
            print(F'Video {ancho}x{alto} {round(bitrate/1024,2)}k {fps}FPS')
            if (alto>720): # >HD
                codificavideo+=' -vf scale=1280:720 -c:v '+vidcodec+' -b:v 900k'
            elif (alto==720): # =HD
                if (bitrate>921600) or (codec!='h264'):
                    codec=stream['codec_name']
                    codificavideo+=' -vf scale=1280:720 -c:v '+vidcodec+' -b:v 900k'
                else:
                    codificavideo+=' -c:v copy'
            else: # <HD
                if (codec=='h264'): # codec h264
                    if (bitrate>716800): # h264 bitrate alto
                        codificavideo+=' -c:v '+vidcodec+' -b:v 700k'
                    else: #h264 bitrate bajo
                        codificavideo+=' -c:v copy'
                elif (bitrate>=716800): # NO264 bitrate alto
                    codificavideo+=' -c:v '+vidcodec+' -b:v 700k'
                else: #no264 bitrate bajo
                    codificavideo+=' -c:v '+vidcodec+' -b:v '+bitrate
            print(codificavideo)
        elif (stream['codec_type']=='audio'):
            codec=stream['codec_name']
            print(F'Audio {codec}')
            if (codec=='aac'):
                codificaaudio=' -c:a copy'
            else:
                codificaaudio=' -c:a '+audiocodec+' -b:a 128k'
            print(codificaaudio)
    print(F'ffmpeg -i "{filename}" {codificavideo} {codificaaudio} "salida\{archivo}.mp4"')
    os.system(F'ffmpeg -i "{filename}" {codificavideo} {codificaaudio} "salida\{archivo}.mp4"')
    
def main():
    targets = []
    target_dirs = ['%s/*.%s' % ('.', ext) for ext in extensions]
    for t in [glob.glob(d) for d in target_dirs]:
        targets += t

    if len(targets) == 0:
        return

    for d in targets:
        procesavideo(d)
        
main()