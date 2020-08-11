#! /usr/bin/env python
# coding=utf-8

import getopt
import os
import subprocess
import sys
import time
import uuid
from configparser import ConfigParser


# 命令行类
class RunCmd(object):
    def __init__(self):
        self.cmd = ''

    def cmd_run(self, cmd):
        self.cmd = cmd
        return subprocess.call(self.cmd, shell=True)


# 读取配置文件
conf = ConfigParser()
conf.read('blog.config', encoding='UTF-8')

# 配置命令行
cmd = RunCmd()


def main(argv):
    warning = '请尝试使用一下命令操作 \n' \
              '创建博客：hugo.py -n \n' \
              '发布博客：hugo.py -p <发布博客信息>'

    try:
        opts, args = getopt.getopt(argv, "hnp:", ["new", "publish="])
        if len(opts) == 0:
            print(warning)
            sys.exit(1)
    except getopt.GetoptError:
        print('输入格式不正确，请按照一下格式输入▽ \nhugo.py -n | -p <发布博客>')
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-h':
            print('hugo.py -n | -p <发布博客>')
            sys.exit()
        elif opt in ("-n", "--new"):
            new_blog()
        elif opt in ("-p", "--publish"):
            publish_blog(arg)
        else:
            print(warning)
    print("END")


#  创建博客
def new_blog():
    print("创建博客")

    date = time.strftime("%Y", time.localtime())
    path = conf['blog']['path'] + '/' + date
    mkdir(path)

    month = time.strftime("%m", time.localtime())
    monthPath = path + '/' + month
    mkdir(monthPath)

    day = time.strftime("%d", time.localtime())
    blogName = day + str(uuid.uuid4().hex)

    blogPath = path + '/' + month + '/' + blogName + '.md'

    res = cmd.cmd_run('hugo new ' + blogPath + ' -s ' + conf['blog']['hugo_path'])
    if res != 0:
        sys.exit(1)
    if conf['blog']['open_auto'] == 'true':
        cmd.cmd_run('open ' + blogPath)


# 创建文件夹
def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        print("创建文件夹: " + path)
        os.makedirs(path)
    else:
        print("文件夹已经存在: " + path)


# 发布博客
def publish_blog(message):
    print("发布博客:" + message)

    print('开始删除旧文件')
    res = cmd.cmd_run('rm -rf %s/public/' % (conf['blog']['hugo_path']))
    if res != 0:
        sys.exit(1)

    print('开始编译静态页面')
    res = cmd.cmd_run('hugo -s {}'.format(conf['blog']['hugo_path']))
    if res != 0:
        sys.exit(1)

    print('开始提交代码修改到Github')
    res = cmd.cmd_run('cd {};git add . ;git commit -m {}'.format(conf['blog']['hugo_path'], message))
    if res > 1:
        sys.exit(1)

    print('PUSH代码到Github')
    res = cmd.cmd_run('cd {};git push'.format(conf['blog']['hugo_path']))
    if res != 0:
        sys.exit(1)

    print('远程执行服务的拉取代码')
    sshStr = "ssh {} 'cd {};git pull'".format(conf['blog']['host'], conf['blog']['host_path'])
    print(sshStr)
    res = cmd.cmd_run(sshStr)
    if res != 0:
        sys.exit(1)
    print('文章已经更新成功了')

    if conf['blog']['sonic_enabled'] == 'true':
        print('开始插入SONIC索引数据')
        sonicStr = '{} -c="{}"'.format(conf['blog']['sonic'], conf['blog']['sonic_conf'])
        print(sonicStr)
        res = cmd.cmd_run(sonicStr)
        if res != 0:
            sys.exit(1)
        print('索引数据更新完成')


if __name__ == "__main__":
    main(sys.argv[1:])
