from logging import warning
import time # 用于获取本地时间
import os # 用于获取文件路径和创建文件夹
import shutil # 用于复制粘贴文件
import json # 用于解析JSON
import sys # 用于接收命令行参数

# 获取当前时间
def get_time (format = '%Y-%m-%d %H:%M:%S'):
    value = time.localtime(int(time.time()))
    dt = time.strftime(format, value)
    return dt

# 自定义输出
def log (*args, **kwargs):
    dt = get_time('%Y/%m/%d %H:%M:%S')
    print (dt, *args, **kwargs )

# 设置cmd中的颜色
def set_color ():
    import ctypes
    # 标准输出的句柄
    STD_OUTPUT_HANDLE = -11
    # 获取句柄
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    # 设置颜色
    def set_cmd_text_color(color, handle=std_out_handle):
        Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
        return Bool
    return set_cmd_text_color

# 输出错误信息
def error (mess):
    # Windows CMD命令行 字体颜色定义 text colors
    FOREGROUND_BLUE = 0x09 # blue.
    FOREGROUND_GREEN = 0x0a # green.
    FOREGROUND_RED = 0x0c # red.
    set_cmd_text_color = set_color ()
    set_cmd_text_color(FOREGROUND_RED)
    #   sys.stdout.write(mess + '\n')
    log (mess)
    # 重置回白色
    set_cmd_text_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)

# 输出警告信息
def warning (mess):
    # Windows CMD命令行 字体颜色定义 text colors
    FOREGROUND_BLUE = 0x09 # blue.
    FOREGROUND_GREEN = 0x0a # green.
    FOREGROUND_RED = 0x0c # red.
    set_cmd_text_color = set_color ()
    set_cmd_text_color(FOREGROUND_RED | FOREGROUND_GREEN)
    #   sys.stdout.write(mess + '\n')
    log (mess)
    # 重置回白色
    set_cmd_text_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)

# 输出警告信息
def success (mess):
    # Windows CMD命令行 字体颜色定义 text colors
    FOREGROUND_BLUE = 0x09 # blue.
    FOREGROUND_GREEN = 0x0a # green.
    FOREGROUND_RED = 0x0c # red.
    set_cmd_text_color = set_color ()
    set_cmd_text_color( FOREGROUND_GREEN)
    #   sys.stdout.write(mess + '\n')
    log (mess)
    # 重置回白色
    set_cmd_text_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)

# 忽略文件
def ignore_file (ignoreRule):
    ignoreList = []
    for ir in ignoreRule:
        ignoreName = ir
        if ir.find('*.') != -1:
            ignoreName = ir.split('*.')[-1]
            log (f'在此文件夹中，需忽略后缀名{ignoreName}')
        elif ir.find('/') != -1:
            ignoreName = ir.split('/')[0]
            log (f'在此文件夹中，需忽略文件夹{ignoreName}')
        elif ir != '':
            log (f'在此文件夹中，需忽略文件{ignoreName}')
        ignoreList.append(ignoreName)
    return ignoreList

# 判断是否要被忽略
def is_ignore (fileName, ignoreList):
    yes_or_no = False
    for ignoreName in ignoreList:
        log (f'判断{fileName}与{ignoreName}')
        # 根据文件名判断
        if ignoreName.find('.') != -1:
            if fileName == ignoreName:
                log (f'{fileName}被忽略')
                yes_or_no = True
                break
        else:
            # 根据后缀名判断
            if fileName.find('.' + ignoreName) != -1:
                log (f'{fileName}被忽略')
                yes_or_no = True
                break
            # 文件夹情况
            elif fileName == ignoreName:
                log (f'{fileName}被忽略')
                yes_or_no = True
                break
    return yes_or_no

# 复制文件
def copy_file (fromPath, toPath, ignoreRule=[]):
    ignoreList = ignore_file(ignoreRule)
    # 获取fromPath下的文件列表并遍历fileName
    pathDir = os.listdir(fromPath)
    for fileName in pathDir:
        if is_ignore(fileName, ignoreList):
            continue
        # 处理文件
        if fileName.find('.') != -1:
            formFile = os.path.join(fromPath, fileName)
            # 若不存在，则创建目录
            if not os.path.isdir(toPath):
                os.makedirs(toPath)
                success (f'成功创建{toPath}')
            # shutil的copy()是复制到一个新的地方，创建时间、修改时间、访问时间都是新的
            # copy2()则是会创建时间、修改时间、访问时间这些也复制过去
            shutil.copy(formFile, toPath)
            success (f'成功复制{formFile}粘贴到{toPath}')
        # 处理文件夹
        else:
            log (f'{fileName}是一个文件夹')
            formFile = os.path.join(fromPath, fileName)
            # 这里要加fileName，否则会放到同一个文件夹下
            copy_file (formFile, toPath + '/' + fileName, ignoreRule)
            pass

# 版本管理
def zh_git (isPush, fromPath, commitPath, pushPath, ignoreRule=''):
    toPath = pushPath
    if isPush:
        if os.path.exists(toPath):
            error (f'{toPath}已存在')
        else:
            if not os.path.exists(commitPath):
                error (f'{commitPath}不存在，请先把本地代码提交至stage')
            else:
                copy_file(commitPath, toPath, ignoreRule)
                shutil.rmtree(commitPath)
    else:
        toPath = commitPath
        # 若存在，则删除
        if os.path.exists(toPath):
            shutil.rmtree(toPath)
        copy_file(fromPath, toPath, ignoreRule)

# 写入文件
def write_file (filePath, text):
    # 以utf-8的编码写入文件
    with open(filePath, 'w', encoding='utf-8') as f:
            f.write(text)
            log (f'成功往{filePath}里写入{text}')

# 读取文件
def read_file (filePath):
    try:
        # 以二进制的方式读取（为了应对图片）
        with open(filePath, 'r') as f:
            log (f'打开{filePath}')
            content = f.read()
    except:
        warning (f'错误：找不到{filePath}')
        content = -1
    finally:
        return content

# 获取配置
def read_config (fromPath):
    # 项目名
    def get_projectName (fromPath):
        projectName = fromPath
        if fromPath.find('/') != -1:
            projectName = fromPath.split('/')[-1]
        if fromPath.find('\\') != -1:
            projectName = fromPath.split('\\')[-1]
        return projectName
    
    # 读取配置文件
    def get_config (configPath):
        configStr = read_file(configPath)
        configJson = {}
        # 防止configStr为空
        try:
            configJson = json.loads(configStr)
        except:
            warning (f'{configStr}不能被解析成JSON')
        return configJson

    # 版本号（默认为V1.0.0）
    def get_version (configJson):
        version = 'V1.0.0'
        if ('version' in configJson):
            version = configJson['version']
        else: 
            warning ('zhconfig.json中没有version')
        return version
    
    # 忽略规则，如a.txt *.ini dir
    def get_ignore (configJson):
        ignore = []
        if ('ignore' in configJson):
            ignore = configJson['ignore']
        else: 
            warning ('zhconfig.json中没有ignore')
        return ignore
    
    projectName = get_projectName(fromPath)
    configPath = fromPath + '/zhconfig.json'
    configJson = get_config(configPath)
    version = get_version(configJson)
    ignore = get_ignore (configJson)
    # 更新时间（默认为当前时间）
    date = get_time('%Y-%m-%d-%H-%M-%S')
    # 生成配置
    config = dict(
        # 待复制的文件夹名称
        fromPath = fromPath,
        # 待粘贴的文件夹名称
        commitPath = 'D:/zzh/versionManage/' + projectName + '/stage',
        pushPath = 'D:/zzh/versionManage/' + projectName + '/' + version + '_' + date,
        # 待忽略的文件列表
        ignoreRule = ignore
    )
    # 更新配置文件
    configJson['version'] = version
    configJson['ignore'] = ignore
    newConfig = json.dumps(configJson)
    write_file (configPath, newConfig)
    # 返回
    return config

# 主函数入口
def main (*args):
    # 执行.py的本地路径
    localPath = os.path.abspath(__file__)
    print (localPath)
    # 项目名
    target = ''
    try:
        target = args[0][1]
    except:
        error ('错误：target为空')
    if not os.path.exists(target):
        error (f'找不到{target}文件夹，本次上传失败')
        return
    # 是否push（而非commit）
    isPush = False
    if len(args[0]) > 2:
        isP = str.lower(args[0][2])
        if isP == '-p':
            isPush = True
    # 读取配置文件（只要填项目文件夹）
    config = read_config(target)
    log (f'配置项{config}')
    # 上传版本
    zh_git(isPush, **config)

if __name__ == '__main__':
    main (sys.argv)