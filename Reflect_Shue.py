from collections import namedtuple
from math import sin, pi, cos, sqrt
from tkinter import Frame, Tk, BOTH, Text, Menu, END, messagebox as mb
from tkinter import filedialog
import re

Properties = namedtuple("Properties", "depth p_vel s_vel ro")


class Example(Frame):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.master.title("Reflect Shue")
        self.pack(fill=BOTH, expand=1)

        menubar = Menu(self.master)
        self.master.config(menu=menubar)

        fileMenu = Menu(menubar, tearoff=0)
        fileMenu.add_command(label="Открыть файл параметров модели", command=self.onOpen_param)
        fileMenu.add_command(label="Открыть файл с углами", command=self.onOpen_angles)
        fileMenu.add_command(label="Записать в файл", command=self.onSave)
        menubar.add_cascade(label="Файл", menu=fileMenu)
        menubar.add_command(label="Считать", command=self.onComp)

        self.txt = Text(self)
        self.txt.pack(fill=BOTH, expand=1)

    def onOpen_param(self):
        ftypes = [('Текстовые файлы', '.txt')]
        dlg = filedialog.Open(self, filetypes=ftypes)
        self.fl = dlg.show() #.fl - путь до файла
        if self.fl != '':
            text = self.readFile(self.fl)
            self.obj = Reflect(self.fl) #создаем объект класса Reflect и передаем путь до файла с парметрами
            self.txt.insert(END, text)

    def onOpen_angles(self):
        ftypes = [('Текстовые файлы', '.txt')]
        dlg = filedialog.Open(self, filetypes=ftypes)
        self.fl = dlg.show() #.fl - путь до файла
        if self.fl != '':
            text = self.readFile(self.fl)
            self.obj.init_ang(self.fl)
            self.txt.insert(END, text)

    def readFile(self, filename):
        with open(filename, "r") as f:
            text = f.read()
        return text

    def onSave(self):
        ftypes = [('Текстовые файлы', '.txt')]
        dlg = filedialog.asksaveasfile(title='Сохранить файл', defaultextension='.txt',
                                           filetypes=ftypes)
        self.fl = dlg.name
        if self.fl != '':
            self.obj.output(self.fl)
        msg = "Файл сохранен"
        mb.showinfo("Информация", msg)

    def onComp(self):
        Reflect.compute(self.obj)
        msg = "Данные посчитаны"
        mb.showinfo("Информация", msg)

class Reflect:

    def __init__(self,
                 file_path='text.txt', file_path_ang='Angles.txt'):
        self.r_ps, self.t_ps, self.r_pp, self.t_pp = ([] for i in range(4))
        self.x, self.t = ([] for i in range(2))
        with open(file_path, 'r') as f:
            self.NumbLayers = int(f.readline())
            self.layer = {}
            for i, row in enumerate(f.readlines()):
                self.layer[i + 1] = Properties(*map(float, row.split(" ")))

    def init_ang(self, file_path_ang='Angles.txt'):
        with open(file_path_ang) as f:
            self.NumbAng = int(f.readline())
            a = re.split(' |\t|,', f.readlines()[0])
            self.ang = []
            for i, ang_simp in enumerate(a):
                self.ang.append(float(ang_simp))

    def compute(self):
        v_sp, delta_vs, delta_vp, delta_ro, v_s, v_p, sr_r = ([] for i in range(7))
        for i in range(1, self.NumbLayers):
            v_sp.append(self.layer[i].p_vel / self.layer[i].s_vel)
            delta_vs.append(self.layer[i + 1].s_vel - self.layer[i].s_vel)
            delta_vp.append(self.layer[i + 1].p_vel - self.layer[i].p_vel)
            delta_ro.append(self.layer[i + 1].ro - self.layer[i].ro)
            v_s.append((self.layer[i + 1].s_vel + self.layer[i].s_vel) / 2)
            v_p.append((self.layer[i + 1].p_vel + self.layer[i].p_vel) / 2)
            sr_r.append((self.layer[i + 1].ro + self.layer[i].ro) / 2)
        for j in range(self.NumbLayers - 1):
            for i in range(self.NumbAng):
                self.r_ps.append(((1 / 2 + v_sp[j]) * (delta_ro[j] / sr_r[j]) + 2 * v_sp[j] * (delta_vs[j] / v_s[j])) * sin(
                    self.ang[i] * pi / 180) +
                            v_sp[j] * ((1 / 2 + (3 / 4) * v_sp[j]) * delta_ro[j] / sr_r[j] + (1 + 2 * v_sp[j]) *
                                       delta_vs[j] / v_s[j]) * pow(sin(self.ang[i] * pi / 180), 3) +
                            v_sp[j] * ((1 / 8 + (5 / 16) * pow(v_sp[j], 3)) * delta_ro[j] / sr_r[j] + (
                        1 / 4 + pow(v_sp[j], 3)) * delta_vs[j] / v_s[j]) * pow(sin(self.ang[i] * pi / 180), 5))

                self.t_ps.append(((1 / 2 - v_sp[j]) * (delta_ro[j] / sr_r[j]) - 2 * v_sp[j] * (delta_vs[j] / v_s[j])) * sin(
                    self.ang[i] * pi / 180) +
                            v_sp[j] * ((1 / 2 - (3 / 4) * v_sp[j]) * delta_ro[j] / sr_r[j] + (1 - 2 * v_sp[j]) *
                                       delta_vs[j] / v_s[j]) * pow(sin(self.ang[i] * pi / 180), 3) +
                            v_sp[j] * ((1 / 8 - (5 / 16) * pow(v_sp[j], 3)) * delta_ro[j] / sr_r[j] + (
                        1 / 4 - pow(v_sp[j], 3)) * delta_vs[j] / v_s[j]) * pow(sin(self.ang[i] * pi / 180), 5))

                self.r_pp.append((0.5 * (delta_ro[j] / sr_r[j] + delta_vp[j] / v_p[j]) + (0.5 * (delta_vp[j] / v_p[j]) -
                                                                                     4 * ((v_s[j] * v_s[j]) / (
                                v_p[j] * v_p[j])) * ((0.5 * (delta_ro[j] / sr_r[j])) + (delta_vs[j] / v_s[j]))) *
                             pow(sin(self.ang[i] * pi / 180), 2) + 0.5 * (delta_vp[j] / v_p[j]) * (
                                     pow(sin(self.ang[i] * pi / 180), 4) / 1 - pow(sin(self.ang[i] * pi / 180),
                                                                                   2))))

                self.t_pp.append(1 - self.r_pp[j * self.NumbAng + i])

        for j in range(1, self.NumbLayers):
            for i in range(self.NumbAng):
                self.x.append((2 * (cos((90 - self.ang[i]) * pi / 180) / self.layer[j].p_vel) * self.layer[j].p_vel *
                          self.layer[j].depth) /
                         (sqrt(1 - (pow(cos((90 - self.ang[i]) * pi / 180) /
                                        self.layer[j].p_vel, 2) * pow(self.layer[j].p_vel, 2)))))
                self.t.append((2 * self.layer[j].depth) /
                         (self.layer[j].p_vel * sqrt(1 - (pow((cos((90 - self.ang[i]) * pi / 180)) /
                                                              self.layer[j].p_vel, 2) * pow(self.layer[j].p_vel, 2)))))
    def output(self, file_path):
        with open(file_path, 'w') as f:
            j = 0
            for i in range(self.NumbAng * (self.NumbLayers - 1)):
                if j == len(self.ang):
                    j = 0
                    f.write('\n')
                f.write(f'{self.ang[j]} {self.r_ps[i]} {self.t_ps[i]} {self.r_pp[i]} {self.t_pp[i]} {2 * self.x[i]} {2 * self.t[i]} \n')
                j += 1


