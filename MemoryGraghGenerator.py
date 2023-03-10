# https://www.jianshu.com/p/88238e34c689
# https://littleround.cn/2019/01/04/Python%E5%88%B6%E4%BD%9C%E5%8A%A8%E6%80%81%E5%9B%BE-matplotlib.animation/

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches
# import os

'''
log tuple:
    
    (CPU, Addr, Size, OP_TYPE, BIG)
           ↑
        Order by
        
    @ CPU: CPU id
    @ Addr: MALLOC start addr
    @ Size: MALLOC size
    @ OP_TYPE: MALLOC / FREE / MALLOC_PAGE / FREE_PAGE / MALLOC_BIGMEM / FREE_BIGMEM
    @ BIG: bool, if true, means a PAGE / BIGMEM op

'''

# readEnd, writeEnd = os.pipe()
# readFile = os.fdopen(readEnd)
# firstLine = readFile.readline()

# c type enum def
MALLOC = 0
FREE = 1
MALLOC_PAGE = 2
FREE_PAGE = 3
MALLOC_BIGMEM = 4
FREE_BIGMEM = 5

mem_usage_list = []
# TODO: find a data structure

mem_start = 0
mem_end = 0x10000000
ncpu = 4

# now constuct the AxesSubplot objects (in a line)
fig, axs = plt.subplots(ncpu + 1, 1)

'''
[CPUx] Addr:0x???????? Size:???? allocate page
[CPUx] Addr:0x???????? Size:???? free page
[CPUx] Addr:0x???????? Size:???? allocate big mem
[CPUx] Addr:0x???????? Size:???? free big mem
[CPUx] Addr:0x???????? Size:???? allocate 
[CPUx] Addr:0x???????? Size:???? free 

->

Memory Allocator should output this to accelerate python exec
x 0x???????? ???? ?

'''

def log_parse():
    # read from pipe and parse
    # (CPU, Addr, Size, OP_TYPE, BIG)
    # TODO: parse ...
    mem_usage_list.append([0, 0, 0x1000000, 0, True])
    
def parse_single(line):
    args = line.split(' ')
    addr = int(args[1], 16)
    op_type = int(args[3])
    assert(0 <= op_type <= 5)
    if op_type == MALLOC or op_type == MALLOC_PAGE or op_type == MALLOC_BIGMEM:
        mem_usage_list.append([int(args[0]), addr, int(args[2]), op_type, 
                               op_type == MALLOC_PAGE or op_type == MALLOC_BIGMEM])
    else:
        # todo: use rb-tree order by Addr. O(logn) insert and remove complexity.
        assert(op_type == FREE or op_type == FREE_PAGE or op_type == FREE_BIGMEM)
        # now is O(n) insert and remove complexity
        for i, (_, addr_t, _, _, _) in enumerate(mem_usage_list):
            if addr_t == addr:
                mem_usage_list.pop(i)
        

# # clear the scene
def plot_init():
    for i in range(ncpu + 1):
        axs[i].clear()
        axs[i].set_xlim([mem_start, mem_end])
        axs[i].set_ylim([0, 1])
        axs[i].yaxis.set_ticks([])
        axs[i].xaxis.set_ticks([])
        # axs[i].xaxis.set_ticks([mem_start, mem_end])
        # axs[i].xaxis.set_major_formatter(ticker.FormatStrFormatter("0x%x"))
    fig.suptitle('Memory Usage Graph')
    


# read the pre-constructed numpy data
def update(n):
    # log_parse()
    # clear graph before draw
    for i in range(ncpu + 1):
        axs[i].clear()
        axs[i].set_xlim([mem_start, mem_end])
        axs[i].set_ylim([0, 1])
        axs[i].yaxis.set_ticks([])
        axs[i].xaxis.set_ticks([])
    # for i in range(ncpu+1):
    #     axs[i].clear()
    for [CPU, Addr, Size, OP_TYPE, isBIG] in mem_usage_list:
        assert(mem_start <= Addr <= mem_end)
        assert(mem_start <= Addr + Size <= mem_end)
        rect = patches.Rectangle((Addr, 0), Size, 1, facecolor='orange')
        axs[CPU+1].add_patch(rect)
        if isBIG == True:
            rect = patches.Rectangle((Addr, 0), Size, 1, facecolor='orange')
            axs[0].add_patch(rect)
    # # dynamic draw test.
    # if n==2:
    #     mem_usage_list.append([0, 0x3000000, 0x1000000, 0, True])
    # if n==3:
    #     mem_usage_list.pop(0)
    


if __name__ == '__main__':
    plot_init()
    # coroutine implement func?
    ani = FuncAnimation(fig, update, interval=1000, save_count=100) 
    # live show
    plt.show()
    i = 0
    # while True will stuck since update has no time to exec.
    while i % 5 == 0:
        log_parse()
        i = i + 1


