#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""
@author:abner
@file:tree_node.py
@ datetime:2020/10/30 8:45
@software: PyCharm

"""
class SentenceNode():
    def __init__(self,value,parent=None):
        self.value = value
        self.__children = {}
        self.__parent = parent

    @property
    def path(self):
        if self.__parent:
            return '%s %s' % (self.parent.path.strip(), self.name)
        else:
            return self.name
    def get_child(self,value,defval=None):
        return self.__children.get(value,defval)

    def get_parent(self):

        return self.__parent
    def add_child(self,value,children=None):

        if children and not isinstance(children,SentenceNode):
            raise ValueError("Only add SentenceNode")
        if children is None:
            children = SentenceNode(value)
        children.__parent = self
        self.__children[value] = children
        # self.__children.append(children)
    def set_parent(self,parent):
        self.__parent = parent

    def del_child(self,name):
        if name in self.__children:
            del self.__children[name]

    def find_child(self,path,create=False):
        path = path if isinstance(path,list) else path.split()
        cur = self
        for sub in path:
            obj = cur.get_child(sub)
            if obj is None and create:
                obj = cur.add_child(sub)
            if obj is None:
                break
            cur = obj
        return obj
    def itmes(self):
        return self.__children.items()

    def dump(self,indent = 0):
        tab = ' '*(indent-1) + '|-' if indent >0 else ''
        print('%s%s'%(tab,self.__ne__()))
        for name,obj in self.itmes():
            obj.dump(indent+1)


class SentenceTree():
    def __init__(self):
        self.value = 0
        self.Node = []

def pre_tree():
    print('root', root)
    if len(root.get_children()) == 0:
        print(root.value)
    else:
        children = root.get_children()
        sentence = ""
        for child in children:
            sentence += pre_tree(child)
        print(sentence)
if __name__ == '__main__':
    root = SentenceNode(0)
    # root.parent = 0

    res ={'籍祥（JiXiang）数据开发工程师': 0, '籍祥': 0, '从性价比角度来说，一般来说深度学习框架都有基于CUDA的优化版本，性能非常': '好，一块计算卡的加速性能超过CPU一个数量级是轻轻松松的',
     '好，一块计算卡的加速性能超过CPU一个数量级是轻轻松松的': 0, '10:04': 0, '纪锋涛（zhengtaoji）数据开发工程师': 0,
     'CPU是一个有多种功能的优秀领导者。它的优点在于调度、管理、协调能力强': '计算能力则位于其次。而GPU相当于一个接受CPU调度的“拥有大量计算能力',
     '计算能力则位于其次。而GPU相当于一个接受CPU调度的“拥有大量计算能力': '的员工', '的员工': 'CPU擅长统领全局等复杂操作，GPU擅长对大数据进行简单重复操作。CPU是从',
     'CPU擅长统领全局等复杂操作，GPU擅长对大数据进行简单重复操作。CPU是从': '事复杂脑力劳动的教授，而GPU是进行大量并行计算的体力劳动者', '事复杂脑力劳动的教授，而GPU是进行大量并行计算的体力劳动者': 0,
     '10:06': 0, '籍祥JiXiang）数据开发工程师': 0}

    for k,v in res.items():
        if v == 0:
            children = SentenceNode(k)
            root.add_child(k)

        else:
            c1 = root.add_child(k)

            children.set_children(res[v])
            root.set_children(children)
    root.pre_tree()
    children = root.get_children()







